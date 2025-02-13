from os import getenv

import telebot
from dotenv import load_dotenv

load_dotenv()
from telebot.types import BotCommand

from checks import check_admin
from commands.task_assign import register_task_assign_commands
from commands.quest import register_quest_commands
from commands.auth import register_auth_commands, init_otp
from database.database import create_tables
from locale import CommonMessages, CommandDescription
from commands.team import register_team_setting_commands
from commands.task import register_task_setting_commands
from commands.team_reset import register_team_reset_commands

totp = init_otp()
bot = telebot.TeleBot(getenv('TELEGRAM_TOKEN'), parse_mode="markdown")

# --- Обработчики команд ---
bot.set_my_commands(commands=[BotCommand(cmd, desc) for cmd, desc in CommandDescription.user_commands.items()])


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, CommonMessages.WELCOME_MESSAGE)


@bot.message_handler(commands=['help'])
def help_message(message):
    admin_commands_desc = '\n'.join([f'/{cmd} - {desc}' for cmd, desc in CommandDescription.admin_commands.items()])
    user_commands_desc = '\n'.join([f'/{cmd} - {desc}' for cmd, desc in CommandDescription.user_commands.items()])
    if check_admin(bot, message, silent=True):
        bot.send_message(message.chat.id, f'{admin_commands_desc}\n{user_commands_desc}')
    else:
        bot.send_message(message.chat.id, user_commands_desc)


register_auth_commands(bot, totp)
register_team_setting_commands(bot)
register_team_reset_commands(bot)
register_task_setting_commands(bot)
register_task_assign_commands(bot)
register_quest_commands(bot)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, CommonMessages.COMMON_MESSAGE)


# Запуск бота
if __name__ == '__main__':
    create_tables()
    bot.infinity_polling(skip_pending=True)
