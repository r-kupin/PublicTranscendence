import asyncio
from datetime import timedelta
from zoneinfo import ZoneInfo

from channels.db import database_sync_to_async
from django.urls import reverse
from django.utils import timezone
from django.apps import apps

from .game import Game
from .models import TournamentRecord, TournamentPlayerStat


class Tournament:
    current_tournament = None

    def __init__(self, initiator_id, starts_at, tournament_alias):
        self.initiator = self.init_initiator(initiator_id)
        self.chat = self.init_tournament_chat()
        self.subscribed = set()
        self.subscribed.add(self.initiator)
        self.player_aliases = {}
        if tournament_alias:
            self.player_aliases[initiator_id] = tournament_alias
        self.starts_at = starts_at
        self.tier = 0
        self.game_list = []
        self.tier_records_list = []
        self.all_records_list = []
        self.ranks = {}
        self.player_without_pair = None
        Tournament.current_tournament = self

    def init_initiator(self, initiator_id):
        Player = apps.get_model('mini_transcendence', 'Player')
        try:
            player = Player.objects.get(id=initiator_id)
            return player
        except Player.DoesNotExist:
            print(f'Player {initiator_id} does not exist')

    def init_tournament_chat(self):
        GroupChat = apps.get_model('chat', 'GroupChat')
        try:
            chat = GroupChat.objects.get(name=f'{self.initiator.user.username}`s Tournament')
            chat.delete()
        except GroupChat.DoesNotExist:
            pass
        try:
            chat = GroupChat.objects.create(
                name=f'{self.initiator.user.username}`s Tournament',
                admin=self.initiator)
            chat.add_member(self.initiator)
            return chat
        except Exception as e:
            print(f'Failed to create tournament GroupChat {str(e)}')

    async def init_ranklist(self, player):
        rank_record = {
            'username': player.user.username,
            'wins': 0,
            'total_scored': 0,
            'rank': 0,
        }
        if player.id in self.player_aliases:
            rank_record['tournament_alias'] = self.player_aliases[player.id]
        return rank_record

    @staticmethod
    def get():
        return Tournament.current_tournament

    @database_sync_to_async
    def post_message(self, msg_type, content):
        Message = apps.get_model('chat', 'Message')
        Message.objects.create(user=self.initiator.user, type=msg_type,
                               chat=self.chat, content=content)

    @database_sync_to_async
    def post_match_invite(self, id1, id2, actions):
        Message = apps.get_model('chat', 'Message')
        Player = apps.get_model('mini_transcendence', 'Player')
        player1_title = Player.objects.get(pk=id1).user.username
        if id1 in self.player_aliases:
            player1_title += f' aka \"{self.player_aliases[id1]}\"'
        player2_title = Player.objects.get(pk=id2).user.username
        if id2 in self.player_aliases:
            player2_title += f' aka \"{self.player_aliases[id2]}\"'

        content = f'{player1_title} VS {player2_title}'
        Message.objects.create(user=self.initiator.user, type='tournament_match_invite',
                               chat=self.chat, content=content, actions=actions)

    @database_sync_to_async
    def save_game_record_toblockchain(self, record):
        print('Saving game record')
        record.save_to_blockchain()

    @database_sync_to_async
    def save_tournament_to_db(self):
        Player = apps.get_model('mini_transcendence', 'Player')
        tournament_record = TournamentRecord.objects.create(name=self.chat.name)
        tournament_record.save()
        for player_id in self.ranks:
            player_records = []

            for tier_records in self.all_records_list:
                for game_record in tier_records:
                    if game_record.player1.id == player_id or game_record.player2.id == player_id:
                        player_records.append(game_record)

            stat = TournamentPlayerStat.objects.create(player=Player.objects.get(pk=player_id),
                                                       tournament=tournament_record,
                                                       rank=self.ranks[player_id]['rank'],
                                                       total_wins=self.ranks[player_id]['wins'],
                                                       total_score=self.ranks[player_id]['total_scored'])
            stat.records.set(player_records)
            if player_id in self.player_aliases:
                stat.tournament_alias = self.player_aliases[player_id]
            stat.save()

    async def start_background_task(self):
        asyncio.create_task(self.start())

    async def start(self):
        now = timezone.now().astimezone(ZoneInfo('Europe/Paris'))
        delay = (self.starts_at - now).total_seconds()
        while delay > 0:
            await asyncio.sleep(1)
            delay -= 1
        if len(self.subscribed) < 2:
            await self.post_message('message',
                                    'No one joined this tournament. The new one might now be created')
            Tournament.current_tournament = None
            return
        for player in self.subscribed:
            self.ranks[player.id] = await self.init_ranklist(player)
        while len(self.subscribed) > 1:
            tier_ends_on = timezone.now() + timedelta(minutes=10)
            current_tier = self.tier
            await self.post_message('message', f'Tier {self.tier} matches are ready!')
            await self.create_pair_list(tier_ends_on)
            await self.post_message('message', f'You have 10 minutes to finish your match! ')

            while current_tier == self.tier and timezone.now() < tier_ends_on:
                await asyncio.sleep(1)
            if len(self.tier_records_list) == 0:
                await self.post_message('message',
                                        f'Tier {self.tier} has no records. '
                                        f'Tournament stops here, no records will be submitted. '
                                        f'The new one might now be created')
                Tournament.current_tournament = None
                return
            if current_tier == self.tier:
                self.tier += 1
            await self.create_next_tier_players_set(self.tier_records_list)
            self.all_records_list.append(self.tier_records_list.copy())
            self.tier_records_list.clear()
            self.game_list.clear()
        await self.post_result()
        await self.save_tournament_to_db()
        Tournament.current_tournament = None

    async def create_pair_list(self, tier_ends_on):
        players = list(self.subscribed)
        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                game = await self.create_match(players[i], players[i + 1], tier_ends_on)
                self.game_list.append(game)
            else:
                self.player_without_pair = players[i]
        self.subscribed.clear()

    async def create_match(self, player1, player2, tier_ends_on):
        game = Game(initiator_id=player1.id, invited_id=player2.id, tournament=self, time_cap=tier_ends_on)
        game.invite_confirmed = True
        actions = {
            'proceed_link': reverse('proceed', args=[game.id])
        }
        await self.post_match_invite(player1.id, player2.id, actions)
        return game

    def add_record(self, record):
        self.tier_records_list.append(record)
        if len(self.tier_records_list) == len(self.game_list):
            self.tier += 1

    def subscribe(self, player, tournament_alias):
        if self.starts_at <= timezone.now().astimezone(ZoneInfo('Europe/Paris')):
            return 400, 'Tournament already started, it`s too late to subscribe'
        elif player in self.subscribed:
            return 200, 'You already subscribed'
        if tournament_alias:
            for id in self.player_aliases:
                if self.player_aliases[id] == tournament_alias:
                    return 400, 'This tournament alias is already taken. Try another one'
            self.player_aliases[player.id] = tournament_alias
        self.subscribed.add(player)
        self.chat.players.add(player)
        self.chat.save()
        return 201, 'Subscribed successfully'

    async def create_next_tier_players_set(self, list):
        for record in list:
            self.subscribed.add(record.winner)
            self.ranks[record.player1.id]['total_scored'] += record.player1_score
            self.ranks[record.player2.id]['total_scored'] += record.player2_score
            self.ranks[record.winner.id]['wins'] += 1
            self.ranks[record.player2.id]['rank'] = self.tier
            self.ranks[record.player1.id]['rank'] = self.tier
            await self.save_game_record_toblockchain(record)
        if self.player_without_pair:
            self.subscribed.add(self.player_without_pair)
            self.player_without_pair = None

    async def post_result(self):
        ranked_list = []
        winner = self.subscribed.pop()
        for rank_record in self.ranks:
            if rank_record == winner.id:
                self.ranks[rank_record]['rank'] = 1
            else:
                self.ranks[rank_record]['rank'] = self.tier - self.ranks[rank_record]['rank'] + 2
            ranked_list.append(self.ranks[rank_record])
        sorted_ranked_list = sorted(ranked_list, key=lambda x: x['rank'])

        resulting_record_msg = "Tournament is over!\nResults:\n"
        for record in sorted_ranked_list:
            username = record['username']
            wins = record['wins']
            score = record['total_scored']
            rank = record['rank']
            if 'tournament_alias' in record:
                alias = record['tournament_alias']
                resulting_record_msg += f'{rank}. {username} aka {alias} wins: {wins}, score: {score}\n'
            else:
                resulting_record_msg += f'{rank}. {username} wins: {wins}, score: {score}\n'
        print(resulting_record_msg)
        await self.post_message(msg_type='message', content=resulting_record_msg)
