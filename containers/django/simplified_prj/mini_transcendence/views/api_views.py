from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from ..models import Player


def get_all_players(request):
    players = [player.to_dict() for player in Player.objects.all()]
    return JsonResponse({'players': players})


@login_required
def all_players_except_me(request):
    players = [player.to_dict_relative(request.user.player) for player in Player.objects.all()
               if player.id != request.user.player.id]
    return JsonResponse({'players': players})


def players_online(request):
    threshold = timezone.now() - timedelta(minutes=1)
    users_online = User.objects.filter(last_login__gte=threshold)
    online_players = [user.player.to_dict() for user in users_online
                      if Player.objects.filter(user=user).exists()]
    return JsonResponse({'online_players': online_players})


@login_required
def players_online_except_me(request):
    threshold = timezone.now() - timedelta(minutes=5)
    users_online = User.objects.filter(last_login__gte=threshold)
    me = request.user.player
    online_players = [user.player.to_dict_relative(me) for user in users_online
                      if (Player.objects.filter(user=user).exists()) and (user.player.id != me.id)]
    return JsonResponse({'online_players': online_players})


# GET Particular player
@login_required
def get_my_info(request):
    my_data = request.user.player.to_dict()
    my_data['chats_link'] = reverse('get-my-chats')
    return JsonResponse({'player': my_data})


def get_player_info(request, player_id):
    requested_player = Player.objects.get(id=player_id)
    return JsonResponse({'player': requested_player.to_dict()})


@login_required
def get_related_played_info(request, player_id):
    current_player = request.user.player
    requested_player = Player.objects.get(id=player_id)
    return JsonResponse({'player': requested_player.to_dict_relative(current_player)})


@login_required
def get_available_actions(request, player_id):
    current_player = request.user.player
    found_player = get_object_or_404(Player, pk=player_id)
    if current_player == found_player:
        return JsonResponse({'actions': {'get_player_data': reverse('players:get-my-info')}})
    else:
        actions = {
            'get_player_data': reverse('players:get-related-player-info', args=[found_player.id]),
            'invite_for_match': reverse('invite', args=[found_player.id]),
        }
        if current_player.has_player_as_friend(found_player):
            actions['remove_from_friendlist'] = reverse('players-action:remove-from-friendlist', args=[found_player.id])
        else:
            actions['add_to_friendlist'] = reverse('players-action:add-to-friendlist', args=[found_player.id])
        dialogue = current_player.get_dialogue_with(found_player)
        if dialogue:
            actions['goto_dialogue'] = reverse('get-my-chat', args=[dialogue.id])
            actions['remove_dialogue'] = reverse('players-action:remove-dialogue', args=[found_player.id])
        else:
            actions['create_dialogue'] = reverse('players-action:create-dialogue', args=[found_player.id])
        if current_player.has_player_in_blocklist(found_player):
            actions['unblock_player'] = reverse('players-action:unblock-player', args=[found_player.id])
        else:
            actions['block_player'] = reverse('players-action:block-player', args=[found_player.id])
    return JsonResponse({'actions': actions})


# ----------API Player actions to perform
@login_required
@require_POST
@csrf_protect
def add_to_friendlist(request, player_id):
    me = request.user.player
    player = get_object_or_404(Player, pk=player_id)
    if player.id == me.id:
        return JsonResponse({'error': "Can't add myself to my friendlist"}, status=400)
    if not me.has_player_as_friend(player):
        me.friendlist.add(player)
        me.save()
        return JsonResponse({'message': "friendlist successfully updated"}, status=201)
    return JsonResponse({'message': "already in the friendlist"}, status=200)


@login_required
@require_POST
@csrf_protect
def remove_from_friendlist(request, player_id):
    me = request.user.player
    player = get_object_or_404(Player, pk=player_id)
    if player.id == me.id:
        return JsonResponse({'error': "Can't remove myself to my friendlist"}, status=400)
    if me.has_player_as_friend(player):
        me.friendlist.remove(player)
        me.save()
        return JsonResponse({'message': "friendlist successfully updated"}, status=201)
    else:
        return JsonResponse({'message': "player isn't present in friendlist"}, status=200)


@login_required
@require_POST
@csrf_protect
def remove_dialogue(request, player_id):
    me = request.user.player
    try:
        player = Player.objects.get(id=player_id)
    except Player.DoesNotExist:
        return JsonResponse({'error': "player does not exist"}, status=404)
    dialogue = me.get_dialogue_with(player)
    if dialogue:
        dialogue.clear_messages()
        dialogue.delete()
        return JsonResponse({'message': 'Dialogue removed successfully.'}, status=201)
    else:
        return JsonResponse({'message': "dialogue doesn't exist"}, status=200)


@login_required
@require_POST
@csrf_protect
def create_dialogue(request, player_id):
    me = request.user.player
    dial_partner = get_object_or_404(Player, id=player_id)
    if me == dial_partner:
        return JsonResponse({'error': 'Cannot create dialogue with myself'}, status=400)
    created = me.get_or_create_dialogue_with(dial_partner)
    if created:
        return JsonResponse({'message': 'Dialogue created successfully.'}, status=201)
    else:
        return JsonResponse({'message': 'Dialogue already exists.'}, status=200)


@login_required
@require_POST
@csrf_protect
def block_player(request, player_id):
    me = request.user.player
    player = get_object_or_404(Player, pk=player_id)
    if player.id == me.id:
        return JsonResponse({'error': "Can't block myself"}, status=400)
    if not me.has_player_in_blocklist(player):
        me.blocklist.add(player)
        me.save()
        return JsonResponse({'message': "blocklist successfully updated"}, status=201)
    return JsonResponse({'message': "already in the blocklist"}, status=200)


@login_required
@require_POST
@csrf_protect
def unblock_player(request, player_id):
    me = request.user.player
    player = get_object_or_404(Player, pk=player_id)
    if player.id == me.id:
        return JsonResponse({'error': "Can't unblock myself"}, status=400)
    if me.has_player_in_blocklist(player):
        me.blocklist.remove(player)
        me.save()
        return JsonResponse({'message': "blocklist successfully updated"}, status=201)
    return JsonResponse({'message': "player isn't present in blocklist"}, status=200)

