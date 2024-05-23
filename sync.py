import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.errors import ChatAdminRequiredError, ChannelPrivateError, ChatWriteForbiddenError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncBot:
    def __init__(self, api_id, api_hash, phone_number, session_path):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.session_path = session_path
        self.client = TelegramClient(session_path, api_id, api_hash)
        self.links = {}
        self.entity_map = {}
        self.handler_added = False

    async def start_client(self):
        await self.client.start(self.phone_number)

    def set_links(self, links):
        self.links = links
        logger.info(f"Links set: {self.links}")

    async def start_bot(self):
        await self.start_client()
        await self.map_usernames_to_entities()
        if not self.handler_added:
            self.client.add_event_handler(self.handle_new_message, events.NewMessage(chats=[entity.id for entity in self.entity_map.values()]))
            self.handler_added = True
            logger.info("Event handler added.")
        logger.info("Bot started.")
        await self.client.run_until_disconnected()

    async def stop_bot(self):
        await self.client.disconnect()
        logger.info("Bot stopped.")

    async def map_usernames_to_entities(self):
        dialogs = await self.client.get_dialogs()
        for dialog in dialogs:
            if dialog.is_channel or dialog.is_group:
                self.entity_map['-100' + str(dialog.entity.id)] = dialog.entity
                if dialog.entity.username:
                    self.entity_map[f"@{dialog.entity.username}"] = dialog.entity

        for identifier in self.links.keys():
            if identifier.startswith('@'):
                entity = await self.client.get_entity(identifier)
                self.entity_map[identifier] = entity
            else:
                entity_id = int(identifier.replace('-', '')[2:])
                if str(entity_id) not in self.entity_map:
                    entity = await self.client.get_entity(entity_id)
                    self.entity_map[str(entity_id)] = entity

        for targets in self.links.values():
            for t_identifier in targets:
                if t_identifier.startswith('@'):
                    entity = await self.client.get_entity(t_identifier)
                    self.entity_map[t_identifier] = entity
                else:
                    entity_id = int(t_identifier.replace('-', '')[2:])
                    if str(entity_id) not in self.entity_map:
                        entity = await self.client.get_entity(entity_id)
                        self.entity_map[str(entity_id)] = entity

        logger.info(f"Username/ID to entity mapping: {self.entity_map}")

    async def handle_new_message(self, event):
        message = event.message
        source_id = message.peer_id.channel_id

        for identifier, target_identifiers in self.links.items():
            if str(self.entity_map[identifier].id) == str(source_id):
                for target_identifier in target_identifiers:
                    target_entity = self.entity_map[target_identifier]
                    try:
                        logger.info(f"Forwarding message from {identifier} to {target_identifier}")
                        if message.is_reply:
                            reply_message = await message.get_reply_message()
                            if reply_message.media:
                                if isinstance(reply_message.media, MessageMediaPhoto):
                                    reply_sent_message = await self.client.send_file(target_entity, reply_message.media, caption=reply_message.message)
                                elif isinstance(reply_message.media, MessageMediaDocument):
                                    reply_sent_message = await self.client.send_file(target_entity, reply_message.media, caption=reply_message.message)
                                else:
                                    reply_sent_message = await self.client.send_message(target_entity, reply_message.message)
                            else:
                                reply_sent_message = await self.client.send_message(target_entity, reply_message.message)

                            if message.media:
                                if isinstance(message.media, MessageMediaPhoto):
                                    await self.client.send_file(target_entity, message.media, caption=message.message, reply_to=reply_sent_message.id)
                                elif isinstance(message.media, MessageMediaDocument):
                                    await self.client.send_file(target_entity, message.media, caption=message.message, reply_to=reply_sent_message.id)
                            else:
                                await self.client.send_message(target_entity, message.message, reply_to=reply_sent_message.id)
                        else:
                            if message.media:
                                if isinstance(message.media, MessageMediaPhoto):
                                    await self.client.send_file(target_entity, message.media, caption=message.message)
                                elif isinstance(message.media, MessageMediaDocument):
                                    await self.client.send_file(target_entity, message.media, caption=message.message)
                            else:
                                await self.client.send_message(target_entity, message.message)
                    except (ChatAdminRequiredError, ChannelPrivateError, ChatWriteForbiddenError) as e:
                        logger.error(f"Permission issue: Cannot forward message from {identifier} to {target_identifier}: {e}")
                    except Exception as e:
                        logger.error(f"Failed to forward message from {identifier} to {target_identifier}: {e}")
