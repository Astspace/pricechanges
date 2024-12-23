from django.core.management.base import BaseCommand
from telebot import TeleBot
import os

from main.models import Items
from main.services import processors as pr


bot = TeleBot(os.environ.get('BOT_TOKEN_KEY'), threaded=False)

@bot.message_handler()
def main_handler(message):
    telegram_id = message.from_user.id
    user = pr.check_user_register_bot(telegram_id)
    if user:
        bot.send_message(message.chat.id, f'Ваш телеграм привязан к профилю сайта! Имя профиля: {user.username}')
    else:
        bot.send_message(message.chat.id, 'Ваш телеграм не привязан к профилю сайта! Введите имя профиля:')
        bot.register_next_step_handler(message, binding_site_user_tgbot)


def binding_site_user_tgbot(message):
    user = pr.search_user_by_username(message.text)
    if user:
        pr.create_user_tgbot(user_id=user.id, telegram_id=message.from_user.id)
        bot.send_message(message.chat.id, f'Теперь Ваш телеграм привязан к профилю сайта! Имя профиля: {user.username}')
    else:
        bot.send_message(message.chat.id, f'Введенный Вами профиль {message.text} не существует! Введите корректное имя профиля:')
        bot.register_next_step_handler(message, binding_site_user_tgbot)


def price_change_message(telegram_id: int, last_price: int, actual_price: int, item: Items):
    name_item = item.name_for_user if item.name_for_user else item.name
    bot.send_message(telegram_id,
                     f'Цена на товар {name_item} изменилась:'
                     f'старая цена: {last_price}, новая цена: {actual_price}')


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        bot.enable_save_next_step_handlers(delay=2)
        bot.load_next_step_handlers()
        bot.infinity_polling()
