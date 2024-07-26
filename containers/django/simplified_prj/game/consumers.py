import asyncio
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps

from game.game import Game


class GameConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

        match_id = self.scope['url_route']['kwargs']['match_id']
        self.game = Game.get(match_id)
        self.user = self.scope['user']

        asyncio.create_task(self.wait_for_start())
        asyncio.create_task(self.listen_for_updates())

    async def receive(self, text_data):
        data = json.loads(text_data)
        player = await self.get_player()

        if data['type'] == 'report_ready':
            await self.game.update_readiness(player.id)
        elif data['type'] == 'paddle_position_update':
            await self.game.update_paddle(player.id, data['position'])
        elif data['type'] == 'report_left':
            await self.game.update_presence(player.id)

    async def disconnect(self, close_code):
        player = await self.get_player()
        await self.game.update_presence(player.id)

    @database_sync_to_async
    def get_player(self):
        Player = apps.get_model('mini_transcendence', 'Player')
        return Player.objects.get(user=self.user)

    async def wait_for_start(self):
        await self.game.wait_for_both_ready()
        await self.send(text_data=json.dumps({'type': 'game_starts'}))

    async def listen_for_updates(self):
        while True:
            state = await self.game.wait_for_update()
            await self.send(json.dumps(state))
            if state['type'] == 'game_ended':
                break
