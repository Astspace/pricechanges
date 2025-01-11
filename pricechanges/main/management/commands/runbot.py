import time
import telebot
from django.core.management.base import BaseCommand
from telebot.types import Message, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
import os
from main.models import Items
from main.services import processors as pr
from main.services.processors import get_item_list_tgbot, get_image_graph_actual_price_tgbot


bot = telebot.TeleBot(os.environ.get('BOT_TOKEN_KEY'), threaded=False)

button_list_item = KeyboardButton(text="Список товаров")
keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button_list_item)


def generate_inline_keyboard_menu_items(telegram_id: int) -> InlineKeyboardMarkup | str:
    items_list = pr.get_item_list_tgbot(telegram_id)
    if isinstance(items_list, str):
        return items_list
    inline_keyboard = InlineKeyboardMarkup()
    for item in items_list:
        name_item = item.name_for_user if item.name_for_user else item.name
        inline_button = telebot.types.InlineKeyboardButton(name_item, callback_data=f"{name_item}//{item.id}")
        inline_keyboard.row(inline_button)
    return inline_keyboard


def generate_inline_keyboard_data_item(item_id: int) -> InlineKeyboardMarkup:
    inline_button_analysis_price = telebot.types.InlineKeyboardButton('Анализ цены товара',
                                                                      callback_data=f"analysis_price^{item_id}")
    inline_button_history_item = telebot.types.InlineKeyboardButton('Просмотр истории товара',
                                                                    callback_data=f"history_item^{item_id}")
    inline_button_item_goback = telebot.types.InlineKeyboardButton('Вернуться к просмотру списка товаров',
                                                                   callback_data=f"goback_items")
    inline_button_list = [inline_button_analysis_price, inline_button_history_item, inline_button_item_goback]
    inline_keyboard_item = InlineKeyboardMarkup()
    for button in inline_button_list:
        inline_keyboard_item.row(button)
    return inline_keyboard_item


def check_inline_keyboard_menu_items_for_message(inline_keyboard_menu_items: InlineKeyboardMarkup, user_id: int) -> None:
    if isinstance(inline_keyboard_menu_items, str):
        bot.send_message(user_id, inline_keyboard_menu_items, reply_markup=keyboard)
    else:
        bot.send_message(user_id, f'Ваши отслеживаемые товары:', reply_markup=inline_keyboard_menu_items)


@bot.message_handler(func=lambda message: message.text == "Список товаров")
def inline_keyboard_items(message: Message) -> None:
    telegram_id = message.from_user.id
    inline_keyboard_menu_items = generate_inline_keyboard_menu_items(telegram_id)
    check_inline_keyboard_menu_items_for_message(inline_keyboard_menu_items, telegram_id)


@bot.callback_query_handler(func=lambda callback: '//' in callback.data)
def callback_handler(callback: CallbackQuery) -> None:
    id_item = callback.data.split('//')[1]
    name_item = callback.data.split('//')[0]
    item = pr.get_item_data(id_item)
    bot.send_message(callback.message.chat.id,
                     create_message_item(item, name_item),
                     reply_markup=generate_inline_keyboard_data_item(item.id),
                     parse_mode="HTML")


def create_message_item(item: Items, name_item: str) -> str:
    message_item = (f'Наименование товара: <u>{name_item}</u>\n'
                    f'--------------------------\n'
                    f'Изначальная цена: {item.price}\n'
                    f'Текущая цена: {'<b>Товар закончился!</b>' if item.out else item.last_price}\n'
                    f'--------------------------\n'
                    f'Маркетплейс: {item.mtplace.name}\n'
                    f'Бренд: {item.brand if item.brand else 'данные отсутствуют'}\n'
                    f'Количество отзывов: {item.feedbacks}\n'
                    f'Рейтинг: {item.rating}\n'
                    f'Остатки на складе: {item.volume if item.volume else 'данные отсутствуют'}\n\n'
                    f'<a href="{item.item_url}">Посмотреть товар на маркетплейсе</a>\n')
    return message_item

@bot.callback_query_handler(func=lambda callback: 'analysis_price^' in callback.data)
def callback_handler(callback: CallbackQuery):
    item_id, telegram_id, item, mktplace_item_id = get_item_data_from_callback(callback)
    image = get_image_graph_actual_price_tgbot(mktplace_item_id, telegram_id)
    if image:
        with open(image, 'rb') as image:
            bot.send_photo(callback.message.chat.id, image, reply_markup=generate_inline_keyboard_data_item(item.id))
    else:
        bot.send_message(callback.message.chat.id, 'Товар с указанным id Вы не отслеживаете!',
                         reply_markup=generate_inline_keyboard_data_item(item.id))


@bot.callback_query_handler(func=lambda callback: 'history_item^' in callback.data)
def callback_handler(callback: CallbackQuery):
    item_id, telegram_id, item, mktplace_item_id = get_item_data_from_callback(callback)
    item_history = pr.get_list_history_item_tgbot(mktplace_item_id, telegram_id)
    if item_history:
        bot.send_message(callback.message.chat.id, 'История товара найдена!',
                         reply_markup=generate_inline_keyboard_data_item(item.id))


def get_item_data_from_callback(callback: CallbackQuery) -> tuple:
    item_id = callback.data.split('^')[1]
    telegram_id = callback.from_user.id
    item = pr.get_item_data(item_id)
    mktplace_item_id = item.id_item
    return item_id, telegram_id, item, mktplace_item_id


@bot.callback_query_handler(func=lambda callback: True)
def callback_handler(callback: CallbackQuery) -> None:
    telegram_id = callback.from_user.id
    if callback.data == 'goback_items':
        inline_keyboard_menu_items = generate_inline_keyboard_menu_items(telegram_id)
        check_inline_keyboard_menu_items_for_message(inline_keyboard_menu_items, telegram_id)


@bot.message_handler()
def main_handler(message: Message) -> None:
    telegram_id = message.from_user.id
    user = pr.check_user_register_bot(telegram_id)
    if user:
        bot.send_message(message.chat.id, f'Имя Вашего профиля: {user.username}.\nВыберите пункт меню.',
                         reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Ваш телеграм не привязан к профилю сайта! Введите имя профиля:')
        bot.register_next_step_handler(message, binding_site_user_tgbot)


def binding_site_user_tgbot(message: Message) -> None:
    user = pr.search_user_by_username(message.text)
    if user:
        pr.create_user_tgbot(user_id=user.id, telegram_id=message.from_user.id)
        bot.send_message(message.chat.id,
                         f'Теперь Ваш телеграм привязан к профилю сайта! Имя профиля: {user.username}',
                         reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id,
                         f'Введенный Вами профиль {message.text} не существует! Введите корректное имя профиля:')
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
        while True:
            try:
                bot.polling(non_stop=True, timeout=90)
            except Exception as e:
                print(e)
                time.sleep(5)
                continue
