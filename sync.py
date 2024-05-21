#!/usr/bin/python3
import asyncio
from telethon import TelegramClient, events


class SyncBot:
    def __init__(self, api_id, api_hash, phone_number, session_path):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.session_path = session_path
        self.client = TelegramClient(session_path, api_id, api_hash)
        self.chats = []

    def set_chats(self, sources, targets):
        self.chats = sources
        self.targets = targets

    async def start_bot(self):
        await self.client.start(self.phone_number)
        self.client.add_event_handler(self.handle_new_message,
                                      events.NewMessage(chats=self.chats))
        await self.client.run_until_disconnected()

    async def stop_bot(self):
        await self.client.disconnect()

    async def handle_new_message(self, event):
        message = event.message.message
        for target in self.targets:
            await self.client.send_message(target, message)
