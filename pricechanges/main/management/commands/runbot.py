from django.core.management.base import BaseCommand
from telebot import TeleBot
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from main.models import Items
from main.services import processors as pr
from main.services.processors import get_item_list_tgbot, get_image_graph_actual_price_tgbot

bot = TeleBot(os.environ.get('BOT_TOKEN_KEY'), threaded=False)

button_list_item = KeyboardButton(text="Список товаров")
button_analysis_item = KeyboardButton(text="Анализ цены товара")
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(button_list_item, button_analysis_item)


@bot.message_handler(func=lambda message: message.text == "Список товаров")
def list_item_tgbot(message):
    telegram_id = message.from_user.id
    items_list = get_item_list_tgbot(telegram_id)
    name_items_str = ''
    for i in items_list:
        name_items_str += str(i.name_for_user) + '\n'
    bot.send_message(message.chat.id, f'Список Ваших товаров:\n\n{name_items_str}', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "Анализ цены товара")
def analysis_price_item(message):
    bot.send_message(message.chat.id, 'Введите id отслеживаемого товара с маркетплейса:')
    bot.register_next_step_handler(message, get_image_price_item)


def get_image_price_item(message):
    mktplace_item_id = message.text
    telegram_id = message.from_user.id
    image = get_image_graph_actual_price_tgbot(mktplace_item_id, telegram_id)
    if image:
        with open(image, 'rb') as image:
            bot.send_photo(message.chat.id, image, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Товар с указанным id Вы не отслеживаете!', reply_markup=keyboard)


@bot.message_handler()
def main_handler(message):
    telegram_id = message.from_user.id
    user = pr.check_user_register_bot(telegram_id)
    if user:
        bot.send_message(message.chat.id, f'Имя Вашего профиля: {user.username}.\nВыберите пункт меню.', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Ваш телеграм не привязан к профилю сайта! Введите имя профиля:')
        bot.register_next_step_handler(message, binding_site_user_tgbot)


def binding_site_user_tgbot(message):
    user = pr.search_user_by_username(message.text)
    if user:
        pr.create_user_tgbot(user_id=user.id, telegram_id=message.from_user.id)
        bot.send_message(message.chat.id, f'Теперь Ваш телеграм привязан к профилю сайта! Имя профиля: {user.username}', reply_markup=keyboard)
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
