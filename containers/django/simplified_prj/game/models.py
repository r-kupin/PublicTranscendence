from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from game.blockchain import save_game_score_


class GameRecord(models.Model):
    player1 = models.ForeignKey("mini_transcendence.Player", related_name='player1_games', on_delete=models.CASCADE)
    player1_score = models.IntegerField(default=0)
    player2 = models.ForeignKey("mini_transcendence.Player", related_name='player2_games', on_delete=models.CASCADE)
    player2_score = models.IntegerField(default=0)
    winner = models.ForeignKey("mini_transcendence.Player", related_name='won_games', on_delete=models.CASCADE,
                               null=True, blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    hash = models.TextField(blank=True)

    def __str__(self):
        return self.player1.user.username + "-" + self.player2.user.username

    # def get_absolute_url(self):
    #     return reverse("game_detail", args=[self.id])

    def to_dict(self):
        data = {
            'id': self.id,
            'player1_score': self.player1_score,
            'player2_score': self.player2_score,
            'player1_username': self.player1.user.username,
            'player2_username': self.player2.user.username,
            'player1_link': reverse('players:get-player-info', args=[self.player1.id]),
            'player2_link': reverse('players:get-player-info', args=[self.player2.id]),
            'timestamp': self.creation_time,
        }
        if self.hash:
            data['hash'] = self.hash
        if self.winner:
            data['winner'] = self.winner.user.username
        return data

    def save_to_blockchain(self):
        try:
            receipt = save_game_score_(self.player1.user.username, self.player2.user.username,
                                       self.player1_score, self.player2_score)
            if (receipt is None or receipt['status'] != 'success' or
                    not 'receipt' in receipt or
                    not 'transactionHash' in receipt['receipt']):
                print('Saving game record tp blockchain failed.')
                return
            self.hash = receipt['receipt']['transactionHash']
            self.save()
            print('Saving game record tp blockchain successful.')
        except Exception as e:
            print(str(e))


class TournamentPlayerStat(models.Model):
    player = models.ForeignKey("mini_transcendence.Player", related_name='tournament_stats', on_delete=models.CASCADE)
    tournament = models.ForeignKey("TournamentRecord", related_name='stats', on_delete=models.CASCADE)
    records = models.ManyToManyField(GameRecord, related_name='tournament_stats', blank=True)
    rank = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    tournament_alias = models.TextField(blank=True)

    def to_dict(self):
        data = {
            'tournament_id': self.tournament.id,
            'tournament_get': reverse('tournament-info', args=[self.tournament.id]),
            'player_id': self.player.id,
            'player_username': self.player.user.username,
            'total_wins': self.total_wins,
            'total_score': self.total_score,
            'rank': self.rank,
            'game_records': []
        }
        if self.tournament_alias:
            data['tournament_alias'] = self.tournament_alias
        if self.records:
            data['game_records'] = [reverse('get-record-info', args=[record.id])
                                    for record in self.records.all()]
        return data

    def to_dict_player_data_only(self):
        data = {
            'player_id': self.player.id,
            'player_username': self.player.user.username,
            'total_wins': self.total_wins,
            'total_score': self.total_score,
            'rank': self.rank,
            'game_records': []
        }
        if self.tournament_alias:
            data['tournament_alias'] = self.tournament_alias
        if self.records:
            data['game_records'] = [reverse('get-record-info', args=[record.id])
                                    for record in self.records.all()]
        return data


class TournamentRecord(models.Model):
    name = models.CharField(max_length=100)
    creation_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def to_dict(self):
        data = {
            'id': self.id,
            'timestamp': self.creation_time,
            'participants': [stat.to_dict_player_data_only() for stat in self.stats.all()]
        }
        return data
