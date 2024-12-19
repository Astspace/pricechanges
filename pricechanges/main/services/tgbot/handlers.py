from main.services import processors
from main.services.tgbot.bot import bot


@bot.message_handler()
def main(message):
    telegram_id = message.from_user.id
    user_profile = processors.check_user_register_bot(telegram_id)
    # if user_profile:
    #     bot.send_message(message.chat.id, f'Ваш телеграм привязан к профилю! Имя профиля: {user_profile.}')