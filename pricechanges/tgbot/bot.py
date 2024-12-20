import os
import telebot
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pricechanges.settings')
django.setup()

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN_KEY'))

@bot.message_handler()
def bot_main(message):
    bot.send_message(message.chat.id, 'df55dfdfd')

bot.register_message_handler(bot_main)

try:
    bot.polling(none_stop=True)
except Exception as e:
    print(f"Ошибка: {e}")