from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Chat(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def get_messages(self):
        return self.message_set.all()

    def get_dict_messages(self):
        return [msg.to_dict() for msg in self.get_messages()]

    def to_dict(self):
        return {
            'chat_id': self.id,
            'created_at': self.created_at,
            'link_to_messages': reverse('get-messages-form-chat', args=[self.id]),
            'players_in_chat': [],
        }

    def clear_messages(self):
        Message.objects.filter(chat=self).delete()

    def can_post_message(self, player):
        try:
            dialog = Dialogue.objects.get(id=self.id)
            if dialog.player1.id == player.id:
                dial_partner = dialog.player2
                me = dialog.player1
            else:
                dial_partner = dialog.player1
                me = dialog.player2
            if dial_partner.has_player_in_blocklist(me):
                return {
                    'result': 'no',
                    'reason': f'Logged in player is blocked by {dial_partner.user.username}'
                }
            elif me.has_player_in_blocklist(dial_partner):
                return {
                    'result': 'no',
                    'reason': f'{dial_partner.user.username} is blocked by me, I have to unblock him first'
                }
            else:
                return {'result': 'yes'}
        except Dialogue.DoesNotExist:
            try:
                chat = GroupChat.objects.get(id=self.id)
                if chat.is_player_blocked(player):
                    return {
                        'result': 'no',
                        'reason': 'Blocked by admin'
                    }
                else:
                    return {'result': 'yes'}
            except GroupChat.DoesNotExist:
                return {
                    'result': 'no',
                    'reason': 'requested chat dous not exist'
                }

    def should_show_msg_from(self, player, me):
        try:
            dialog = Dialogue.objects.get(id=self.id)
            if me.has_player_in_blocklist(player):
                return False
            else:
                return True
        except Dialogue.DoesNotExist:
            try:
                chat = GroupChat.objects.get(id=self.id)
                if (me.has_player_in_blocklist(player) or
                        chat.is_player_blocked(player)):
                    return False
                else:
                    return True
            except GroupChat.DoesNotExist:
                return False


class Dialogue(Chat):
    player1 = models.ForeignKey('mini_transcendence.Player', related_name='dialogues1', on_delete=models.CASCADE)
    player2 = models.ForeignKey('mini_transcendence.Player', related_name='dialogues2', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('player1', 'player2')

    def __str__(self):
        return f"Dialogue between {self.player1.user.username} and {self.player2.user.username}"

    def to_dict_authorised(self, player):
        if self.player1.id == player.id:
            dial_partner = self.player2
            me = self.player1
        else:
            dial_partner = self.player1
            me = self.player2
        data = self.to_dict()
        name = 'Me with ' + str(dial_partner.user.username)
        data['i_am_blocked'] = dial_partner.has_player_in_blocklist(me)
        data['type'] = 'Dialogue'
        data['name'] = name
        data['players_in_chat'].append({
            'username': dial_partner.user.username,
            'link': reverse('players:get-related-player-info', args=[dial_partner.id]),
            'is_blocked': me.has_player_in_blocklist(dial_partner)
        })
        if me.has_player_in_blocklist(dial_partner):
            data['players_in_chat'][0]['unblock'] = reverse('players-action:unblock-player', args=[dial_partner.id])
        else:
            data['players_in_chat'][0]['block'] = reverse('players-action:block-player', args=[dial_partner.id])
        data['players_amount'] = 1
        data['action_links'] = {
            'post_message': reverse('post-message', args=[self.id]),
            'delete_chat': reverse('players-action:remove-dialogue', args=[dial_partner.id]),
        }
        return data


class GroupChat(Chat):
    name = models.CharField(max_length=255, unique=True)
    admin = models.ForeignKey('mini_transcendence.Player', related_name='admin_chats', on_delete=models.CASCADE)
    players = models.ManyToManyField('mini_transcendence.Player', related_name="group_chats", blank=True)
    blocked_players = models.ManyToManyField('mini_transcendence.Player', related_name="blocked_in_group_chats",
                                             blank=True)

    def __str__(self):
        return self.name

    def add_member(self, player):
        self.players.add(player)

    def remove_member(self, player):
        if player != self.admin:
            self.players.remove(player)

    def is_member(self, player):
        return self.players.filter(id=player.id).exists()

    def is_player_blocked(self, player):
        return self.blocked_players.filter(id=player.id).exists()

    def player_related_to_chat(self, me, player):
        player_data = {
            'username': player.user.username,
            'link': reverse('players:get-related-player-info', args=[player.id]),
        }
        if self.blocked_players.filter(id=player.id).exists():
            player_data['is_blocked'] = True
        else:
            player_data['is_blocked'] = False
        if player.id == self.admin.id:
            player_data['is_admin'] = True
        else:
            player_data['is_admin'] = False
        if me.id == self.admin.id:
            if self.blocked_players.filter(id=player.id).exists():
                player_data['unblock'] = reverse('unblock-player', args=[self.id, player.id])
            else:
                player_data['block'] = reverse('block-player', args=[self.id, player.id])
            player_data['remove'] = reverse('remove-player', args=[self.id, player.id])
        return player_data

    def to_dict_authorised(self, player):
        players_in_chat = self.players.exclude(id=player.id)
        data = self.to_dict()
        data['type'] = 'GroupChat'
        data['name'] = self.name
        data['i_am_blocked'] = self.is_player_blocked(player)
        for p_in_chat in players_in_chat:
            data['players_in_chat'].append(self.player_related_to_chat(player, p_in_chat))
        data['players_amount'] = players_in_chat.count()
        data['action_links'] = {
            'post_message': reverse('post-message', args=[self.id]),
        }
        if player.id == self.admin.id:
            data['i_am_admin'] = True
            data['action_links']['delete_chat'] = reverse('delete-chat', args=[self.id])
        else:
            data['i_am_admin'] = False
            data['action_links']['leave_chat'] = reverse('leave-chat', args=[self.id])
            data['admin'] = {
                'username': self.admin.user.username,
                'link': reverse('players:get-related-player-info', args=[self.admin.id]),
            }
        return data


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    content = models.TextField()
    type = models.CharField(max_length=200, default='message')
    timestamp = models.DateTimeField(auto_now_add=True)
    actions = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Message by {self.user.username} in {self.chat.id}"

    def to_dict(self):
        dictionary = {
            'sender_username': self.user.username,
            'sender_link': reverse('players:get-player-info', args=[self.user.player.id]),
            'chat': reverse('get-my-chat', args=[self.chat.id]),
            'content': self.content,
            'type': self.type,
            'timestamp': self.timestamp,
        }
        if self.actions:
            dictionary['actions'] = self.actions
        return dictionary


class PageView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    page = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.page}"
