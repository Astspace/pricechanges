import os
import telebot


bot = telebot.TeleBot(os.environ.get('BOT_TOKEN_KEY'))
bot.polling(none_stop=True)