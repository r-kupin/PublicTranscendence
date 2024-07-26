import datetime
import math
import uuid
import asyncio
import random

from django.apps import apps
from channels.db import database_sync_to_async
from django.utils import timezone

from .models import GameRecord


class Game:
    games = {}

    def __init__(self, initiator_id, invited_id, tournament, time_cap):
        self.id = str(uuid.uuid4())

        self.initiator_id = initiator_id
        self.invited_id = invited_id

        self.invite_confirmed = False
        self.initiator_ready = False
        self.invited_ready = False
        self.initiator_left = False
        self.invited_left = False
        self.tier_finished = False
        self.game_ended = False
        self.tournament = tournament
        self.time_cap = time_cap

        self.width = 640
        self.height = 480
        self.wall_width = 12
        self.paddle_width = 12
        self.paddle_height = 60
        self.velocity = 200
        self.dt = 0.0005
        self.velocity_increment = 10
        self.ballRadius = 5

        self.condition = asyncio.Condition()

        self.state = {
            'initiator_id': self.initiator_id,
            'invited_id': self.invited_id,

            'initiator_score': 0,
            'invited_score': 0,

            'initiator_paddle_y': (self.height - self.paddle_height) / 2,
            'invited_paddle_y': (self.height - self.paddle_height) / 2,

            'ball_position_x': self.height / 2,
            'ball_position_y': self.width / 2,
            'ball_direction_y': 0.0,
            'ball_direction_x': 0.0,
        }
        self.random_direction()
        if self.tournament:
            self.state['tournament'] = True
            self.update_time_left(timezone.now())
        else:
            self.state['tournament'] = False
        Game.games[self.id] = self

    def update_time_left(self, now):
        time_rest = self.time_cap - now
        total_seconds = int(time_rest.total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        self.state['minutes_left'] = minutes
        self.state['seconds_left'] = seconds

    @staticmethod
    def get(game_id):
        return Game.games.get(game_id)

    async def wait_for_both_ready(self):
        async with self.condition:
            while not (self.initiator_ready and self.invited_ready):
                await self.condition.wait()

    async def time_step(self):
        await asyncio.sleep(2.5)
        while True:
            await asyncio.sleep(self.dt)
            now = timezone.now()
            async with self.condition:
                if self.tournament:
                    if now >= self.time_cap:
                        self.tier_finished = True
                    else:
                        self.update_time_left(now)

                if self.initiator_left or self.invited_left or self.tier_finished:
                    self.game_ended = True
                else:
                    self.calculate_ball_position()

                if (self.state['initiator_score'] >= 5 or
                        self.state['invited_score'] >= 5):
                    self.game_ended = True

                self.condition.notify_all()
                if self.game_ended:
                    break
        await self.save_game_record()

    async def update_readiness(self, player_id):
        async with self.condition:
            if player_id == self.initiator_id:
                self.initiator_ready = True
            elif player_id == self.invited_id:
                self.invited_ready = True
            if self.initiator_ready and self.invited_ready:
                asyncio.create_task(self.time_step())
                self.condition.notify_all()

    async def update_presence(self, player_id):
        async with self.condition:
            if player_id == self.initiator_id:
                self.initiator_left = True
            elif player_id == self.invited_id:
                self.invited_left = True
            self.condition.notify_all()

    async def update_paddle(self, player_id, paddle_y):
        async with self.condition:
            if player_id == self.initiator_id:
                if self.state['initiator_paddle_y'] > (self.height - self.paddle_height):
                    self.state['initiator_paddle_y'] = self.height - self.paddle_height
                elif self.state['initiator_paddle_y'] < self.wall_width:
                    self.state['initiator_paddle_y'] = self.wall_width
                else:
                    self.state['initiator_paddle_y'] = paddle_y
            elif player_id == self.invited_id:
                if self.state['invited_paddle_y'] > (self.height - self.paddle_height):
                    self.state['invited_paddle_y'] = self.height - self.paddle_height
                elif self.state['invited_paddle_y'] < self.wall_width:
                    self.state['invited_paddle_y'] = self.wall_width
                else:
                    self.state['invited_paddle_y'] = paddle_y
            self.condition.notify_all()

    def calculate_ball_position(self):
        # reflect from upper / lower bound
        if ((self.state['ball_position_y'] <= self.wall_width) or
                (self.state['ball_position_y'] >= (self.height - self.wall_width))):
            self.state['ball_direction_y'] *= -1

        # reflect from paddle
        if ((self.state['ball_position_x'] <= self.paddle_width) and
                (self.state['ball_position_y'] >= self.state['initiator_paddle_y']) and
                (self.state['ball_position_y'] <= self.state['initiator_paddle_y'] + self.paddle_height)):
            self.state['ball_direction_x'] = abs(self.state['ball_direction_x'])
        elif (((self.state['ball_position_x'] >= self.width - self.paddle_width) and
               (self.state['ball_position_y'] >= self.state['invited_paddle_y']) and
               (self.state['ball_position_y'] <= self.state['invited_paddle_y'] + self.paddle_height))):
            self.state['ball_direction_x'] = -abs(self.state['ball_direction_x'])
        # goal
        elif (self.state['ball_position_x'] + self.ballRadius) < self.paddle_width:
            self.state['invited_score'] += 1
            self.state['ball_position_y'] = self.height / 2
            self.state['ball_position_x'] = self.width / 2
            self.random_direction()
        elif (self.state['ball_position_x'] - self.ballRadius) > (self.width - self.paddle_width):
            self.state['initiator_score'] += 1
            self.state['ball_position_y'] = self.height / 2
            self.state['ball_position_x'] = self.width / 2
            self.random_direction()
        self.state['ball_position_x'] += self.state['ball_direction_x'] * self.velocity * self.dt
        self.state['ball_position_y'] += self.state['ball_direction_y'] * self.velocity * self.dt
        self.velocity += self.velocity_increment * self.dt

    def random_direction(self):
        while (abs(self.state['ball_direction_x']) >= 0.8 or
               abs(self.state['ball_direction_x']) <= 0.5):
            heading = random.uniform(0, 2 * 3.14)
            self.state['ball_direction_y'] = math.sin(heading)
            self.state['ball_direction_x'] = math.cos(heading)
        self.velocity = 500

    async def wait_for_update(self):
        async with self.condition:
            await self.condition.wait()
            if self.game_ended:
                return {
                    'type': 'game_ended',
                    'initiator_score': self.state['initiator_score'],
                    'invited_score': self.state['invited_score'],
                    'initiator_id': self.initiator_id,
                }
            else:
                return {
                    'type': 'game_state_update',
                    'state': self.state
                }

    @database_sync_to_async
    def save_game_record(self):
        Player = apps.get_model(app_label='mini_transcendence', model_name='Player')
        invited = Player.objects.get(pk=self.invited_id)
        initiator = Player.objects.get(pk=self.initiator_id)

        initiator_score = self.state['initiator_score']
        invited_score = self.state['invited_score']

        if not self.initiator_left and not self.invited_left:
            if initiator_score > invited_score:
                record = GameRecord.objects.create(player1=initiator,
                                                   player2=invited,
                                                   winner=initiator,
                                                   player1_score=initiator_score,
                                                   player2_score=invited_score)
            elif invited_score > initiator_score:
                record = GameRecord.objects.create(player1=initiator,
                                                   player2=invited,
                                                   winner=invited,
                                                   player1_score=initiator_score,
                                                   player2_score=invited_score)
        elif self.initiator_left and not self.invited_left:
            record = GameRecord.objects.create(player1=initiator,
                                               player2=invited,
                                               winner=invited,
                                               player1_score=0,
                                               player2_score=invited_score)
        elif self.invited_left and not self.initiator_left:
            record = GameRecord.objects.create(player1=initiator,
                                               player2=invited,
                                               winner=initiator,
                                               player1_score=initiator_score,
                                               player2_score=0)
        elif self.tier_finished:
            record = GameRecord.objects.create(player1=initiator,
                                               player2=invited,
                                               player1_score=initiator_score,
                                               player2_score=invited_score)
        if self.tournament and not self.tier_finished:
            self.tournament.add_record(record)
        if self.id in Game.games:
            del Game.games[self.id]
