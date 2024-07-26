from datetime import timedelta
from zoneinfo import ZoneInfo

from asgiref.sync import async_to_sync
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .models import GameRecord, TournamentRecord, TournamentPlayerStat
from .game import Game
from .tournament import Tournament

import json


@login_required
def solo(request):
    return HttpResponse(loader.get_template('pong_solo.html').render({}, request))


def get_record_info(request, record_id):
    record = get_object_or_404(GameRecord, pk=record_id)
    return JsonResponse({'record': record.to_dict()})


@login_required
def game(request):
    return HttpResponse(loader.get_template('game.html').render({}, request))


@login_required
def check(request, game_id):
    game = Game.get(game_id)
    me = request.user.player
    if not game:
        return JsonResponse({'error': 'Game not found'}, status=404)
    if game.invited_id != me.id:
        return JsonResponse({'error': 'This invitation is not for you'}, status=403)
    return JsonResponse({'message': 'OK'}, status=200)


@login_required
@require_POST
@csrf_protect
def invite(request, player_id):
    Player = apps.get_model(app_label='mini_transcendence', model_name='Player')
    me = request.user.player
    invited = get_object_or_404(Player, pk=player_id)
    if invited.user == me:
        return JsonResponse({'error': 'You cannot invite yourself'}, status=400)
    if invited.has_player_in_blocklist(me):
        return JsonResponse({'error': 'You are blocked by a player you tried to invite'}, status=403)
    if me.has_player_in_blocklist(invited):
        return JsonResponse({'error': 'You are blocked the player you tried to invite. Unblock him first'}, status=403)
    game = Game(initiator_id=me.id, invited_id=invited.id, tournament=None, time_cap=None)
    me.invite_for_a_match(invited, game.id)
    return JsonResponse({'message': 'Invitation sent successfully', 'game_id': game.id}, status=201)


@login_required
@require_POST
@csrf_protect
def accept(request, game_id):
    game = Game.get(game_id)
    me = request.user.player
    if not game:
        return JsonResponse({'error': 'Game not found'}, status=404)
    if game.invited_id != me.id:
        return JsonResponse({'error': 'This invitation is not for you'}, status=403)
    Player = apps.get_model(app_label='mini_transcendence', model_name='Player')
    initiator = Player.objects.get(pk=game.initiator_id)
    if not initiator:
        return JsonResponse({'error': 'Player that invited you is not found'}, status=404)
    if game.invite_confirmed:
        return JsonResponse({'error': 'This invite is already accepted'}, status=403)
    game.invite_confirmed = True
    me.accept_invite(initiator, game.id)
    return HttpResponse(loader.get_template('pong.html').render({
        'game': game,
        'me': json.dumps(me.to_dict()),
        'opponent': json.dumps(initiator.to_dict_relative(me)),
    }, request))


@login_required
@require_POST
@csrf_protect
def decline(request, game_id):
    game = Game.get(game_id)
    me = request.user.player
    if not game:
        return JsonResponse({'error': 'Game not found'}, status=404)
    if game.invited_id != me.id:
        return JsonResponse({'error': 'You cannot decline an invitation that is not for you'}, status=403)
    if game.invite_confirmed:
        return JsonResponse({'error': 'You have already accepted this invitation'}, status=400)
    
    Player = apps.get_model(app_label='mini_transcendence', model_name='Player')
    initiator = Player.objects.get(pk=game.initiator_id)
    del game
    Game.games[game_id] = None
    me.decline_invite(initiator)
    return JsonResponse({'message': 'Game invite declined successfully'}, status=201)


@login_required
@require_POST
@csrf_protect
def proceed(request, game_id):
    game = Game.get(game_id)
    me = request.user.player
    if not game:
        return JsonResponse({'error': 'Game not found'}, status=404)
    if not game.tournament:
        # if game.initiator_id != me.id:
        #     return JsonResponse({'error': 'You cant proceed to the game which you did not initiate'}, status=403)
        if not game.invite_confirmed:
            return JsonResponse({'error': 'You cant proceed to the game, invite was not accepted'}, status=403)
        return goto_match_page(game, game.invited_id, me, request)
    else:
        if game.initiator_id == me.id:
            return goto_match_page(game, game.invited_id, me, request)
        elif game.invited_id == me.id:
            return goto_match_page(game, game.initiator_id, me, request)
        else:
            return JsonResponse({'error': 'this match is not for you'}, status=403)


def goto_match_page(game, opponent_id, me, request):
    Player = apps.get_model(app_label='mini_transcendence', model_name='Player')
    try:
        opponent = Player.objects.get(pk=opponent_id)
    except Player.DoesNotExist:
        return JsonResponse({'error': 'match partner not found'}, status=404)
    return HttpResponse(loader.get_template('pong.html').render({
        'game': game,
        'me': json.dumps(me.to_dict()),
        'opponent': json.dumps(opponent.to_dict_relative(me)),
    }, request))


@login_required
@require_POST
@csrf_protect
def create_tournament(request):
    if Tournament.get():
        return JsonResponse({'message': 'Tournament already exists'}, status=200)
    try:
        data = json.loads(request.body)
        starts_at = data.get('starts_at')

        if not starts_at:
            return JsonResponse({'error': 'starts_at field is required'}, status=400)

        timestamp = parse_datetime(starts_at)
        if not timestamp:
            return JsonResponse({'error': 'Invalid timestamp format. Here`s the expected example: '
                                          '2024-05-23T14:37:29.700'}, status=400)
        timestamp = timestamp.astimezone(ZoneInfo('Europe/Paris'))
        now = timezone.now().astimezone(ZoneInfo('Europe/Paris'))
        if timestamp <= now + timedelta(minutes=1):
            return JsonResponse({'error': 'The timestamp must be at least 1 minute in the future'}, status=400)
        elif timestamp >= now + timedelta(hours=1):
            return JsonResponse({'error': 'The timestamp must be no more than 1 hour in the future'}, status=400)

        me = request.user.player
        Player = apps.get_model(app_label='mini_transcendence', model_name='Player')
        tournament_alias = data.get('tournament_alias')
        if tournament_alias:
            tournament = Tournament(initiator_id=me.id, starts_at=timestamp, tournament_alias=tournament_alias)
        else:
            tournament = Tournament(initiator_id=me.id, starts_at=timestamp, tournament_alias=None)
        async_to_sync(tournament.start_background_task)()
        for player in Player.objects.all():
            if player.id != me.id:
                me.send_tournament_invite(player)
        return JsonResponse({'message': 'Tournament created successfully'}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(str(e))


@login_required
@require_POST
@csrf_protect
def subscribe_tournament(request):
    me = request.user.player
    tournament = Tournament.get()
    if not tournament:
        return JsonResponse({
            'error': 'There is no ongoing tournament right now. Want to create one?',
            'action': reverse('create_tournament')
        }, status=400)
    if request.body:
        data = json.loads(request.body)
        tournament_alias = data.get('tournament_alias')
        if tournament_alias:
            code, message = tournament.subscribe(me, tournament_alias)
        else:
            code, message = tournament.subscribe(me, None)
    else:
        code, message = tournament.subscribe(me, None)
    if code > 201:
        return JsonResponse({'error': message}, status=code)
    else:
        return JsonResponse({'message': message}, status=code)


def get_tournament_info(request, record_id):
    tournament = get_object_or_404(TournamentRecord, pk=record_id)
    return JsonResponse({'tournament_record': tournament.to_dict()})


def get_tournament_player_stat(request, record_id, player_id):
    Player = apps.get_model(app_label='mini_transcendence', model_name='Player')
    player = get_object_or_404(Player, pk=player_id)
    tournament = get_object_or_404(TournamentRecord, pk=record_id)
    try:
        record = tournament.stats.get(player=player)
        return JsonResponse({'player_tournament_record': record.to_dict()})
    except TournamentRecord.DoesNotExist:
        return JsonResponse({'error': 'Tournament record does not exist'}, status=404)
    except TournamentPlayerStat.DoesNotExist:
        return JsonResponse({'error': 'Tournament player stats object does not exist'}, status=404)
