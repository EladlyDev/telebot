#!/usr/bin/python3
import asyncio
import os
import logging
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
links = {}

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper message
HELP_MESSAGE = """
I can help you get messages and updates from outer channels and post them to your channel.

Use these commands to control me:

*Target Channels*
/addt <username>
/removet <username>
/targets - list all target channels

*Source Channels*
/adds <username>
/removes <username>
/sources - list all source channels

*Linking*
/link <source> <target>
/unlink <source> <target>
/showlinks - show all links

*Bot Settings*
/start\_monitoring
/stop\_monitoring
"""

# /help command handler
@dp.message_handler(commands=['help', 'start'])
async def help_command(message: types.Message):
    """
    Handle the /help and /start commands.
    Send the help message to the user.
    """
    await message.reply(HELP_MESSAGE, parse_mode='Markdown')

# Unknown command handler
@dp.message_handler(lambda message: message.text.split(' ')[0] not in ['/start_monitoring', '/stop_monitoring', '/targets', '/sources', '/addt', '/adds', '/removet', '/removes', '/link', '/unlink', '/showlinks'] and monitoring == False)
async def unknown_command(message: types.Message):
    """
    Handle unknown commands when monitoring is not active.
    Send an error message and the help message to the user.
    """
    await message.reply(f"🔴 Unknown command.\n{HELP_MESSAGE}", parse_mode='Markdown')


@dp.message_handler(lambda message: monitoring)
async def unknown_command_monitoring(message: types.Message):
    """
    Handle unknown commands when monitoring is active.
    Send an error message to the user.
    """
    await message.reply("🔴 Monitoring is active, use /stop_monitoring to stop it")

# Targets
@dp.message_handler(commands=['addt'])
async def addt(message: types.Message):
    """
    Handle the /addt command.
    Add a target channel to the list of targets.
    """
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
    await message.reply(f"🟢 The target {new_target} is successfully added")


@dp.message_handler(commands=['removet'])
async def removet(message: types.Message):
    """
    Handle the /removet command.
    Remove a target channel from the list of targets.
    """
    if len(message.text.split(' ')) < 2:
        await message.reply("Usage: /removet @channel_name")
        return
    target = message.text.split(' ')[1]
    if target not in targets:
        await message.reply("🔴 Target not found")
        return
    targets.remove(target)
    await message.reply(f"🟢 The target {target} is successfully removed")


@dp.message_handler(commands=['targets'])
async def listt(message: types.Message):
    """
    Handle the /targets command.
    Send a list of target channels to the user.
    """
    if len(targets) == 0:
        await message.reply("🔴 No targets added")
        return
    await message.reply(f"Targets: {', '.join(targets)}")


# Sources
@dp.message_handler(commands=['adds'])
async def adds(message: types.Message):
    """
    Handle the /adds command.
    Add a source channel to the list of sources.
    """
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
    await message.reply(f"🟢 The source {new_source} is successfully added")


@dp.message_handler(commands=['removes'])
async def removes(message: types.Message):
    """
    Handle the /removes command.
    Remove a source channel from the list of sources.
    """
    if len(message.text.split(' ')) < 2:
        await message.reply("Usage: /removes @channel_name")
        return
    source = message.text.split(' ')[1]
    if source not in sources:
        await message.reply("🔴 Source not found")
        return
    sources.remove(source)
    await message.reply(f"🟢 The source {source} is successfully removed")


@dp.message_handler(commands=['sources'])
async def lists(message: types.Message):
    """
    Handle the /sources command.
    Send a list of source channels to the user.
    """
    if len(sources) == 0:
        await message.reply("🔴 No sources added")
        return
    await message.reply(f"Sources: {', '.join(sources)}")


# Linking
@dp.message_handler(commands=['link'])
async def link(message: types.Message):
    """
    Handle the /link command.
    Create a link between a source channel and a target channel.
    """
    if len(message.text.split(' ')) < 3:
        await message.reply("Usage: /link @source_channel @target_channel")
        return
    source = message.text.split(' ')[1]
    target = message.text.split(' ')[2]
    if source not in sources:
        await message.reply("🔴 Source not found, add it first with /adds")
        return
    if target not in targets:
        await message.reply("🔴 Target not found, add it first with /addt")
        return
    if source in links:
        if target in links[source]:
            await message.reply("🟢 Link already exists")
            return
        links[source].append(target)
    else:
        links[source] = [target]
    await message.reply(f"🟢 Link from {source} to {target} created")


@dp.message_handler(commands=['unlink'])
async def unlink(message: types.Message):
    """
    Handle the /unlink command.
    Remove a link between a source channel and a target channel.
    """
    if len(message.text.split(' ')) < 3:
        await message.reply("Usage: /unlink @source_channel @target_channel")
        return
    source = message.text.split(' ')[1]
    target = message.text.split(' ')[2]
    if source not in links or target not in links[source]:
        await message.reply("🔴 Link not found")
        return
    links[source].remove(target)
    if len(links[source]) == 0:
        del links[source]
    await message.reply(f"🟢 Link from {source} to {target} removed")


@dp.message_handler(commands=['showlinks'])
async def showlinks(message: types.Message):
    """
    Handle the /showlinks command.
    Send a list of all links to the user.
    """
    if len(links) == 0:
        await message.reply("🔴 No links found")
        return
    response = "Links:\n"
    for source, targets in links.items():
        response += f"{source} -> {', '.join(targets)}\n"
    await message.reply(response)


# Monitoring
@dp.message_handler(commands=['start_monitoring'])
async def start_monitoring(message: types.Message):
    """
    Handle the /start_monitoring command.
    Start the monitoring process.
    """
    global monitoring
    if len(sources) == 0:
        await message.reply("🔴 No sources added, add sources first")
        return
    if len(targets) == 0:
        await message.reply("🔴 No targets added, add targets first")
        return
    if not links:
        await message.reply("🔴 No links added, add links first")
        return
    if monitoring:
        await message.reply("🟢 Monitoring already started.")
        return

    sync.set_links(links)
    asyncio.create_task(sync.start_bot())
    monitoring = True
    logger.info("Monitoring started.")
    await message.reply("🟢 Monitoring started.")


@dp.message_handler(commands=['stop_monitoring'])
async def stop_monitoring(message: types.Message):
    """
    Handle the /stop_monitoring command.
    Stop the monitoring process.
    """
    global monitoring
    if not monitoring:
        await message.reply("🟢 Monitoring already stopped")
        return

    asyncio.create_task(sync.stop_bot())
    monitoring = False
    logger.info("Monitoring stopped.")
    await message.reply("🟢 Monitoring stopped")

if __name__ == '__main__':
    start_polling(dp, skip_updates=True)
