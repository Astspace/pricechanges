from main.services import processors as pr
from tgbot.bot import bot


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
    user = pr.search_user_by_username(message.from_user.text)
    if user:
        pr.create_user_tgbot(user_id=user.id, telegram_id=message.from_user.id)
        bot.send_message(message.chat.id, f'Теперь Ваш телеграм привязан к профилю сайта! Имя профиля: {user.username}')
    else:
        bot.send_message(message.chat.id, f'Введенный Вами профиль {message.from_user.text} не существует! Введите корректное имя профиля:')
        bot.register_next_step_handler(message, binding_site_user_tgbot)
