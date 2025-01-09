import telebot
from django.core.management.base import BaseCommand
from telebot.types import Message
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from main.models import Items
from main.services import processors as pr
from main.services.processors import get_item_list_tgbot, get_image_graph_actual_price_tgbot

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN_KEY'), threaded=False)

button_list_item = KeyboardButton(text="Список товаров")
button_analysis_item = KeyboardButton(text="Анализ цены товара")
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(button_list_item, button_analysis_item)


@bot.message_handler(func=lambda message: message.text == "Список товаров")
def inline_keyboard_items(message: Message):
    telegram_id = message.from_user.id
    items_list = get_item_list_tgbot(telegram_id)
    inline_keyboard = telebot.types.InlineKeyboardMarkup()
    if isinstance(items_list, str):
        bot.send_message(message.chat.id, items_list, reply_markup=keyboard)
    else:
        for item in items_list:
            name_item = item.name_for_user if item.name_for_user else item.name
            inline_button = telebot.types.InlineKeyboardButton(name_item, callback_data=f"{name_item}_{item.id}")
            inline_keyboard.add(inline_button)
        bot.send_message(message.chat.id, f'Ваши отслеживаемые товары:', reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda callback: True)
def callback_handler(callback):
    call_item_id = callback.data.split('_')[1]
    item = pr.get_item_data(int(call_item_id))
    inline_keyboard_item = telebot.types.InlineKeyboardMarkup()
    message_item = (f'Наименование товара: {item.name_for_user if item.name_for_user else item.name}\n'
                    f'Бренд: {item.brand if item.brand else 'отсутствует'}\n')
    bot.send_message(callback.message.chat.id, "Вы выбрали действие 1.")


@bot.message_handler(func=lambda message: message.text == "Анализ цены товара")
def analysis_price_item(message: Message) -> None:
    bot.send_message(message.chat.id, 'Введите id отслеживаемого товара с маркетплейса:')
    bot.register_next_step_handler(message, get_image_price_item)


def get_image_price_item(message: Message) -> None:
    mktplace_item_id = message.text
    telegram_id = message.from_user.id
    image = get_image_graph_actual_price_tgbot(mktplace_item_id, telegram_id)
    if image:
        with open(image, 'rb') as image:
            bot.send_photo(message.chat.id, image, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Товар с указанным id Вы не отслеживаете!', reply_markup=keyboard)


@bot.message_handler()
def main_handler(message: Message) -> None:
    telegram_id = message.from_user.id
    user = pr.check_user_register_bot(telegram_id)
    if user:
        bot.send_message(message.chat.id, f'Имя Вашего профиля: {user.username}.\nВыберите пункт меню.', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Ваш телеграм не привязан к профилю сайта! Введите имя профиля:')
        bot.register_next_step_handler(message, binding_site_user_tgbot)


def binding_site_user_tgbot(message: Message) -> None:
    user = pr.search_user_by_username(message.text)
    if user:
        pr.create_user_tgbot(user_id=user.id, telegram_id=message.from_user.id)
        bot.send_message(message.chat.id, f'Теперь Ваш телеграм привязан к профилю сайта! Имя профиля: {user.username}', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, f'Введенный Вами профиль {message.text} не существует! Введите корректное имя профиля:')
        bot.register_next_step_handler(message, binding_site_user_tgbot)


def price_change_message(telegram_id: int, last_price: int, actual_price: int, item: Items) -> None:
    name_item = item.name_for_user if item.name_for_user else item.name
    bot.send_message(telegram_id,
                     f'Цена на товар {name_item} изменилась:'
                     f'старая цена: {last_price}, новая цена: {actual_price}')


def price_change_message_item_out(telegram_id: int, last_price: int, item: Items) -> None:
    name_item = item.name_for_user if item.name_for_user else item.name
    bot.send_message(telegram_id,
                     f'Товар {name_item} закончился.'
                     f'Последняя  цена: {last_price}')


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        bot.enable_save_next_step_handlers(delay=2)
        bot.load_next_step_handlers()
        bot.infinity_polling()
