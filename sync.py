#!/usr/bin/python3
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument


class SyncBot:
    def __init__(self, api_id, api_hash, phone_number, session_path):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.session_path = session_path
        self.client = TelegramClient(session_path, api_id, api_hash)
        self.chats = []
        self.targets = []

    def set_chats(self, sources, targets):
        self.chats = sources
        self.targets = targets

    async def start_bot(self):
        await self.client.start(self.phone_number)
        self.client.add_event_handler(self.handle_new_message, events.NewMessage(chats=self.chats))
        await self.client.run_until_disconnected()

    async def stop_bot(self):
        await self.client.disconnect()

    async def handle_new_message(self, event):
        message = event.message

        for target in self.targets:
            if message.is_reply:
                reply_message = await message.get_reply_message()

                if reply_message.media:
                    if isinstance(reply_message.media, MessageMediaPhoto):
                        reply_sent_message = await self.client.send_file(target, reply_message.media, caption=reply_message.message)
                    elif isinstance(reply_message.media, MessageMediaDocument):
                        reply_sent_message = await self.client.send_file(target, reply_message.media, caption=reply_message.message)
                    else:
                        reply_sent_message = await self.client.send_message(target, reply_message.message)
                else:
                    reply_sent_message = await self.client.send_message(target, reply_message.message)

                if message.media:
                    if isinstance(message.media, MessageMediaPhoto):
                        await self.client.send_file(target, message.media, caption=message.message, reply_to=reply_sent_message.id)
                    elif isinstance(message.media, MessageMediaDocument):
                        await self.client.send_file(target, message.media, caption=message.message, reply_to=reply_sent_message.id)
                else:
                    await self.client.send_message(target, message.message, reply_to=reply_sent_message.id)

            else:
                if message.media:
                    if isinstance(message.media, MessageMediaPhoto):
                        await self.client.send_file(target, message.media, caption=message.message)
                    elif isinstance(message.media, MessageMediaDocument):
                        await self.client.send_file(target, message.media, caption=message.message)
                else:
                    await self.client.send_message(target, message.message)