#!/usr/bin/python3
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncBot:
    """
    A Telegram bot that synchronizes messages between different channels.

    Args:
        api_id (int): The API ID of the Telegram application.
        api_hash (str): The API hash of the Telegram application.
        phone_number (str): The phone number associated with the Telegram account.
        session_path (str): The path to store the session file.

    Attributes:
        api_id (int): The API ID of the Telegram application.
        api_hash (str): The API hash of the Telegram application.
        phone_number (str): The phone number associated with the Telegram account.
        session_path (str): The path to store the session file.
        client (TelegramClient): The Telegram client instance.
        links (dict): A dictionary mapping source usernames or IDs to target usernames or IDs.
        username_to_id (dict): A dictionary mapping usernames to their corresponding IDs.
    """

    def __init__(self, api_id, api_hash, phone_number, session_path):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.session_path = session_path
        self.client = TelegramClient(session_path, api_id, api_hash)
        self.links = {}
        self.username_to_id = {}

    async def start_client(self):
        """
        Start the Telegram client.
        """
        await self.client.start(self.phone_number)

    def set_links(self, links):
        """
        Set the links between source and target usernames or IDs.

        Args:
            links (dict): A dictionary mapping source usernames or IDs to target usernames or IDs.
        """
        self.links = links
        logger.info(f"Links set: {self.links}")

    async def start_bot(self):
        """
        Start the bot and add the event handler for new messages.
        """
        await self.start_client()
        await self.map_usernames_to_ids()
        self.client.add_event_handler(self.handle_new_message, events.NewMessage(chats=list(self.username_to_id.values())))
        logger.info("Bot started and event handler added.")
        await self.client.run_until_disconnected()

    async def stop_bot(self):
        """
        Stop the bot and disconnect the client.
        """
        await self.client.disconnect()
        logger.info("Bot stopped.")

    async def map_usernames_to_ids(self):
        """
        Map source usernames or IDs to their corresponding IDs.
        """
        for identifier in self.links.keys():
            if identifier.startswith('@'):
                entity = await self.client.get_entity(identifier)
                self.username_to_id[identifier] = entity.id
            else:
                self.username_to_id[identifier] = int(identifier.replace('-', '')[2:])
        logger.info(f"Username/ID to ID mapping: {self.username_to_id}")

    async def handle_new_message(self, event):
        """
        Handle new incoming messages and forward them to the target usernames or IDs.

        Args:
            event (telethon.events.NewMessage.Event): The new message event.
        """
        message = event.message
        source_id = message.peer_id.channel_id

        for identifier, target_identifiers in self.links.items():
            if self.username_to_id[identifier] == source_id:
                for target_identifier in target_identifiers:
                    try:
                        logger.info(f"Forwarding message from {identifier} to {target_identifier}")
                        if message.is_reply:
                            reply_message = await message.get_reply_message()

                            if reply_message.media:
                                if isinstance(reply_message.media, MessageMediaPhoto):
                                    reply_sent_message = await self.client.send_file(target_identifier, reply_message.media, caption=reply_message.message)
                                elif isinstance(reply_message.media, MessageMediaDocument):
                                    reply_sent_message = await self.client.send_file(target_identifier, reply_message.media, caption=reply_message.message)
                                else:
                                    reply_sent_message = await self.client.send_message(target_identifier, reply_message.message)
                            else:
                                reply_sent_message = await self.client.send_message(target_identifier, reply_message.message)

                            if message.media:
                                if isinstance(message.media, MessageMediaPhoto):
                                    await self.client.send_file(target_identifier, message.media, caption=message.message, reply_to=reply_sent_message.id)
                                elif isinstance(message.media, MessageMediaDocument):
                                    await self.client.send_file(target_identifier, message.media, caption=message.message, reply_to=reply_sent_message.id)
                            else:
                                await self.client.send_message(target_identifier, message.message, reply_to=reply_sent_message.id)
                        else:
                            if message.media:
                                if isinstance(message.media, MessageMediaPhoto):
                                    await self.client.send_file(target_identifier, message.media, caption=message.message)
                                elif isinstance(message.media, MessageMediaDocument):
                                    await self.client.send_file(target_identifier, message.media, caption=message.message)
                            else:
                                await self.client.send_message(target_identifier, message.message)
                    except Exception as e:
                        logger.error(f"Failed to forward message from {identifier} to {target_identifier}: {e}")
