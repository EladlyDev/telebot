#!/usr/bin/python3
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_polling
from sync import SyncBot

TOKEN = os.getenv('TOKEN')
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE')
session_path = 'new_session'
sync = SyncBot(api_id, api_hash, phone_number, session_path)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

monitoring = False
targets = []
sources = []

# Helper message
HELP_MESSAGE = """
I can help you get messages and updates from outer channels and post them to your channel.

Use these commands to control me:

*Target Channels*
/addt <username>
/removet <username>
/listt - list all target channels

*Source Channels*
/adds <username>
/removes <username>
/lists - list all source channels

*Bot Settings*
/start\_monitoring
/stop\_monitoring
"""

# /help command handler
@dp.message_handler(commands=['help', 'start'])
async def help_command(message: types.Message):
    await message.reply(HELP_MESSAGE, parse_mode='Markdown')

# Unknown command handler
@dp.message_handler(lambda message: message.text.split(' ')[0] not in ['/start_monitoring', '/stop_monitoring', '/listt', '/lists', '/addt', '/adds', '/removet', '/removes'] and monitoring == False)
async def unknown_command(message: types.Message):
    await message.reply(f"🔴 Unknown command.\n{HELP_MESSAGE}", parse_mode='Markdown')

# Targets
@dp.message_handler(commands=['addt'])
async def addt(message: types.Message):
    if len(message.text.split(' ')) < 2:
        await message.reply("Usage: /addt @channel_name")
        return
    new_target = message.text.split(' ')[1]
    if not new_target.startswith('@'):
        await message.reply("🔴 Invalid target, it should start with @")
        return
    if new_target in targets:
        await message.reply("🟢 Target already added")
        return
    targets.append(new_target)
    sync.set_chats(sources, targets)
    await message.reply(f"🟢 The target {new_target} is successfully added")

@dp.message_handler(commands=['removet'])
async def removet(message: types.Message):
    if len(message.text.split(' ')) < 2:
        await message.reply("Usage: /removet @channel_name")
        return
    target = message.text.split(' ')[1]
    if target not in targets:
        await message.reply("🔴 Target not found")
        return
    targets.remove(target)
    sync.set_chats(sources, targets)
    await message.reply(f"🟢 The target {target} is successfully removed")

@dp.message_handler(commands=['listt'])
async def listt(message: types.Message):
    if len(targets) == 0:
        await message.reply("🔴 No targets added")
        return
    await message.reply(f"Targets: {', '.join(targets)}")

# Sources
@dp.message_handler(commands=['adds'])
async def adds(message: types.Message):
    if len(message.text.split(' ')) < 2:
        await message.reply("Usage: /adds @channel_name")
        return
    new_source = message.text.split(' ')[1]
    if not new_source.startswith('@'):
        await message.reply("🔴 Invalid source, it should start with @")
        return
    if new_source in sources:
        await message.reply("🟢 Source already added")
        return
    sources.append(new_source)
    sync.set_chats(sources, targets)
    await message.reply(f"🟢 The source {new_source} is successfully added")

@dp.message_handler(commands=['removes'])
async def removes(message: types.Message):
    if len(message.text.split(' ')) < 2:
        await message.reply("Usage: /removes @channel_name")
        return
    source = message.text.split(' ')[1]
    if source not in sources:
        await message.reply("🔴 Source not found")
        return
    sources.remove(source)
    sync.set_chats(sources, targets)
    await message.reply(f"🟢 The source {source} is successfully removed")

@dp.message_handler(commands=['lists'])
async def lists(message: types.Message):
    if len(sources) == 0:
        await message.reply("🔴 No sources added")
        return
    await message.reply(f"Sources: {', '.join(sources)}")

# Monitoring
@dp.message_handler(commands=['start_monitoring'])
async def start_monitoring(message: types.Message):
    global monitoring
    if len(sources) == 0:
        await message.reply("🔴 No sources added, add sources first")
        return
    if len(targets) == 0:
        await message.reply("🔴 No targets added, add targets first")
        return
    if monitoring:
        await message.reply("🟢 Monitoring already started.")
        return

    sync.set_chats(sources, targets)
    asyncio.create_task(sync.start_bot())
    monitoring = True
    await message.reply("🟢 Monitoring started.\n[note] if you sent a message to the bot it will be forwarded to the targets if the bot is an admin there")

@dp.message_handler(commands=['stop_monitoring'])
async def stop_monitoring(message: types.Message):
    global monitoring
    if not monitoring:
        await message.reply("🟢 Monitoring already stopped")
        return

    asyncio.create_task(sync.stop_bot())
    monitoring = False
    await message.reply("🟢 Monitoring stopped")

# Message handler during monitoring
@dp.message_handler(lambda message: True)
async def handle_message(message: types.Message):
    global monitoring
    if not monitoring:
        return
    if len(sources) == 0 or len(targets) == 0:
        monitoring = False
        await message.reply("🔴 No sources or targets, monitoring stopped")
        return
    for target in targets:
        await bot.send_message(target, message.text)
    await message.reply(f"🟢 Message sent")

if __name__ == '__main__':
    start_polling(dp, skip_updates=True)
