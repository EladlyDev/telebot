import telebot
import os

TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def welcome(message) :
    bot.reply_to(message, 
                    """Hi!
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

@bot.message_handler(func=lambda message: True)
def echo(message) :
    bot.reply_to(message, message.text)


bot.infinity_polling()
