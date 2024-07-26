import asyncio
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        self.user = self.scope['user']
        self.chat_msg_tracking = {}
        self.connected = True
        player_chats = await self.get_player_chats()
        for chat in player_chats:
            self.chat_msg_tracking[chat.id] = await self.count_chat_messages(chat)
        asyncio.create_task(self.update_msg_tracker())

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'messages_checked':
            self.chat_msg_tracking[data['chat_id']] = data['seen_messages']

    async def disconnect(self, code):
        self.connected = False

    @database_sync_to_async
    def get_player_chats(self):
        print(f'{self.user.username} fetches chats')
        Player = apps.get_model('mini_transcendence', 'Player')
        return Player.objects.get(user=self.user).get_chats()

    @database_sync_to_async
    def count_chat_messages(self, chat):
        return chat.get_messages().count()

    async def update_msg_tracker(self):
        try:
            while self.connected:
                await asyncio.sleep(1)
                player_chats = await self.get_player_chats()
                for chat in player_chats:
                    messages_in_chat = await self.count_chat_messages(chat)
                    if chat.id not in self.chat_msg_tracking:
                        self.chat_msg_tracking[chat.id] = messages_in_chat
                    elif self.chat_msg_tracking[chat.id] < messages_in_chat:
                        await self.send(text_data=json.dumps({
                            'type': 'unred_messages',
                            'chat_id': chat.id,
                            'amount_unseen': messages_in_chat - self.chat_msg_tracking[chat.id],
                            'amount_total': messages_in_chat,
                        }))
        except asyncio.CancelledError:
            pass

