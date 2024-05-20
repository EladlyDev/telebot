import telebot
import os

TOKEN = os.getenv('TOKEN')
targets = []
sources = []
bot = telebot.TeleBot(TOKEN)
monitoring = False


@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.reply_to(message,
"""
Hi!
- Handle the targets (you channels)
    /add_target to add a new target
    /remove_target to remove a target
    /list_targets to show the current targets
- Handle the sources (where the messages come)
    /add_source to add a new source
    /remove_source to remove a source
    /list_sources to show the current sources
- Manage the bot
    /start_monitoring to start monitoring
    /stop_monitoring to stop monitoring
""")


# Targets
@bot.message_handler(commands=['add_target'])
def add_target(message):
    if len(message.text.split(' ')) < 2:
        bot.reply_to(message, "Usage: /add_target `@channel_name`")
        return
    new_target = message.text.split(' ')[1]
    if not new_target.startswith('@'):
        bot.reply_to(message, "Invalid target, it should start with @")
        return
    if new_target in targets:
        bot.reply_to(message, "Target already added")
        return
    targets.append(new_target)
    bot.reply_to(message, f"{new_target} Successfully added")


@bot.message_handler(commands=['remove_target'])
def remove_target(message):
    if len(message.text.split(' ')) < 2:
        bot.reply_to(message, "Usage: /remove_target `@channel_name`")
        return
    target = message.text.split(' ')[1]
    if target not in targets:
        bot.reply_to(message, "Target not found")
        return
    targets.remove(target)
    bot.reply_to(message, f"{target} Successfully removed")


@bot.message_handler(commands=['list_targets'])
def list_targets(message):
    if len(targets) == 0:
        bot.reply_to(message, "No targets added")
        return
    bot.reply_to(message, f"Targets: {', '.join(targets)}")


# Sources
@bot.message_handler(commands=['add_source'])
def add_source(message):
    if len(message.text.split(' ')) < 2:
        bot.reply_to(message, "Usage: /add_source `@channel_name`")
        return
    new_source = message.text.split(' ')[1]
    if not new_source.startswith('@'):
        bot.reply_to(message, "Invalid source, it should start with @")
        return
    if new_source in sources:
        bot.reply_to(message, "Source already added")
        return
    sources.append(new_source)
    bot.reply_to(message, f"{new_source} Successfully added")


@bot.message_handler(commands=['remove_source'])
def remove_source(message):
    if len(message.text.split(' ')) < 2:
        bot.reply_to(message, "Usage: /remove_source `@channel_name`")
        return
    source = message.text.split(' ')[1]
    if source not in sources:
        bot.reply_to(message, "Source not found")
        return
    sources.remove(source)
    bot.reply_to(message, f"{source} Successfully removed")


@bot.message_handler(commands=['list_sources'])
def list_sources(message):
    if len(sources) == 0:
        bot.reply_to(message, "No sources added")
        return
    bot.reply_to(message, f"Sources: {', '.join(sources)}")

# Monitoring
@bot.message_handler(commands=['start_monitoring'])
def start_monitoring(message):
    global monitoring
    if len(sources) == 0:
        bot.reply_to(message, "No sources added, continued for testing purposes")
    monitoring = True
    bot.reply_to(message, "Monitoring started")


@bot.message_handler(commands=['stop_monitoring'])
def stop_monitoring(message):
    global monitoring
    monitoring = False
    bot.reply_to(message, "Monitoring stopped")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not monitoring:
        return
    for target in targets:
        bot.send_message(target, message.text)


bot.infinity_polling()
