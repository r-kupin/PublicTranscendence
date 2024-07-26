from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.apps import apps

from game.tournament import Tournament


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    intra_login = models.CharField(max_length=20, null=True)
    intra_token = models.CharField(max_length=200, null=True)
    games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    loses = models.IntegerField(default=0)
    friendlist = models.ManyToManyField("self", related_name="friends", blank=True, symmetrical=False)
    blocklist = models.ManyToManyField("self", related_name="blocked_players", blank=True, symmetrical=False)
    records = models.ManyToManyField("game.GameRecord", related_name="players", blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')

    def __str__(self):
        return self.user.username

    # def get_absolute_url(self):
    #     return reverse("user_detail", args=[self.user.id])

    def get_dialogues(self):
        Dialogue = apps.get_model('chat', 'Dialogue')
        dialogues = Dialogue.objects.filter(models.Q(player1=self) | models.Q(player2=self))
        return list(dialogues)

    def get_group_chats(self):
        GroupChat = apps.get_model('chat', 'GroupChat')
        group_chats = GroupChat.objects.filter(players=self)
        return list(group_chats)

    def get_chats(self):
        Dialogue = apps.get_model('chat', 'Dialogue')
        GroupChat = apps.get_model('chat', 'GroupChat')

        # Get dialogues where this player is either player1 or player2
        dialogues = Dialogue.objects.filter(models.Q(player1=self) | models.Q(player2=self))

        # Get all group chats where this player is a member
        group_chats = GroupChat.objects.filter(players=self)

        # Combine both querysets into one list
        all_chats = list(dialogues) + list(group_chats)

        return all_chats

    def get_chat(self, chat_id):
        Dialogue = apps.get_model('chat', 'Dialogue')
        GroupChat = apps.get_model('chat', 'GroupChat')
        Chat = apps.get_model('chat', 'Chat')

        dialogues = Dialogue.objects.filter(models.Q(player1=self) | models.Q(player2=self))
        group_chats = GroupChat.objects.filter(players=self)
        if dialogues.filter(id=chat_id).exists():
            return Dialogue.objects.get(id=chat_id)
        if group_chats.filter(id=chat_id).exists():
            return GroupChat.objects.get(id=chat_id)
        if get_object_or_404(Chat, pk=chat_id):
            return "Forbidden"
        return None

    def has_player_in_blocklist(self, player):
        try:
            player_in_list = Player.objects.get(id=player.id)
            if player_in_list in self.blocklist.all():
                return True
        except User.DoesNotExist:
            return False
        except Player.DoesNotExist:
            return False
        return False

    def has_player_as_friend(self, player):
        try:
            player_in_list = Player.objects.get(id=player.id)
            if player_in_list in self.friendlist.all():
                return True
        except User.DoesNotExist:
            return False
        except Player.DoesNotExist:
            return False
        return False

    def avg_score(self):
        total_score = 0
        total_games = 0

        player1_games = self.player1_games.all()
        player2_games = self.player2_games.all()

        # iterate all games where current player is player1
        for game in player1_games:
            total_score += game.player1_score
            total_games += 1
        # iterate all games where current player is player2
        for game in player2_games:
            total_score += game.player2_score
            total_games += 1

        if total_games == 0:
            return 0

        return round(total_score / total_games, 1)  # Limit to 1 digit after the dot

    def get_dialogue_with(self, other_player):
        Dialogue = apps.get_model('chat', 'Dialogue')
        if other_player.has_player_in_blocklist(self):
            return None
        try:
            return Dialogue.objects.get(
                (models.Q(player1=self) & models.Q(player2=other_player)) |
                (models.Q(player1=other_player) & models.Q(player2=self))
            )
        except Dialogue.DoesNotExist:
            return None

    def get_or_create_dialogue_with(self, other_player):
        Dialogue = apps.get_model('chat', 'Dialogue')
        if other_player.has_player_in_blocklist(self):
            return None
        try:
            return Dialogue.objects.get(
                (models.Q(player1=self) & models.Q(player2=other_player)) |
                (models.Q(player1=other_player) & models.Q(player2=self))
            )
        except Dialogue.DoesNotExist:
            return Dialogue.objects.create(player1=self, player2=other_player)

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.user.username,
            'games': self.games,
            'wins': self.wins,
            'loses': self.loses,
            'avatar_url': self.avatar.url,
            'records': [],
            'friendlist': [],
            'blocklist': [],
            'tournament_stats': []
        }
        if self.records:
            data['records'] = [reverse('get-record-info', args=[record.id])
                               for record in self.records.all()]
        if self.friendlist:
            data['friendlist'] = [reverse('players:get-related-player-info', args=[friend.id])
                                  for friend in self.friendlist.all()]
        if self.friendlist:
            data['blocklist'] = [reverse('players:get-related-player-info', args=[blocked_one.id])
                                 for blocked_one in self.blocklist.all()]
        if self.intra_login:
            data['intra_login'] = self.intra_login

        if self.tournament_stats:
            data['tournament_stats'] = [reverse('tournament-player-stat', args=[stat.tournament.id, self.id])
                                        for stat in self.tournament_stats.all()]
        return data

    def to_dict_relative(self, player):
        data = self.to_dict()
        data['i_am_his_friend'] = self.has_player_as_friend(player)
        data['he_is_my_friend'] = player.has_player_as_friend(self)
        data['i_am_blocked'] = self.has_player_in_blocklist(player)
        data['he_is_blocked'] = player.has_player_in_blocklist(self)
        data['actions_link'] = reverse('players:get-available-actions', args=[self.id])
        dialogue = self.get_dialogue_with(player)
        if dialogue:
            data['has_dialogue_with_me'] = reverse('get-my-chat', args=[dialogue.id])
        return data

    def send_tournament_invite(self, other_player):
        Message = apps.get_model('chat', 'Message')
        dialogue_with = self.get_or_create_dialogue_with(other_player)
        if dialogue_with:
            Message.objects.create(user=self.user, type='tournament_subscription_invite',
                                   chat=dialogue_with,
                                   content=f'The tournament will start at {Tournament.get().starts_at.strftime("%I:%M %p")}.'
                                           f' Subscribe, while it`s not too late',
                                   actions={'subscribe_link': reverse('subscribe_tournament')})

    def accept_invite(self, other_player, game_id):
        Message = apps.get_model('chat', 'Message')
        Message.objects.create(user=self.user, type='invite_accepted',
                               chat=self.get_or_create_dialogue_with(other_player),
                               content='Your invite is accepted!',
                               actions={'proceed_link': reverse('proceed', args=[game_id])})

    def decline_invite(self, other_player):
        Message = apps.get_model('chat', 'Message')
        Message.objects.create(user=self.user, type='invite_declined',
                               chat=self.get_or_create_dialogue_with(other_player),
                               content='Your invite was declined!', )

    def invite_for_a_match(self, invited, game_id):
        Message = apps.get_model('chat', 'Message')
        Message.objects.create(user=self.user, type='invite_received',
                               chat=self.get_or_create_dialogue_with(invited),
                               content='You are invited to a match!',
                               actions={'check_link': reverse('check', args=[game_id]),
                                        'accept_link': reverse('accept', args=[game_id]),
                                        'decline_link': reverse('decline', args=[game_id])})
