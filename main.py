from os import getenv
import telebot
from dotenv import load_dotenv
from telebot.types import BotCommand

from checks import check_admin
from commands.task_assign import register_task_assign_commands
from commands.quest import register_quest_commands
from commands.auth import register_auth_commands, init_otp
from src.models import *
from commands.team import register_team_setting_commands
from commands.task import register_task_setting_commands
from commands.team_reset import register_team_reset_commands

load_dotenv()
session = init_session()
totp = init_otp(session)
bot = telebot.TeleBot(getenv('TELEGRAM_TOKEN'), parse_mode="markdown")

# --- Обработчики команд ---
bot.set_my_commands(commands=[
    BotCommand('start', 'Запуск бота'),
    BotCommand('help', 'Помощь'),
    BotCommand('join', 'Присоединиться к команде'),
    BotCommand('task', 'Текущее задание'),
    BotCommand('next', 'Следующее задание'),
])


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добро пожаловать!')


@bot.message_handler(commands=['help'])
def help_message(message):
    admin_commands = '''
/createteam Создать команду
/listteam Список команд
/createtask Создать задание
/listtask Список заданий
/assigntask Привязка заданий
/resetleader Сброс лидера команды
/resettask Сброс прогресса команды
    '''
    user_commands = '''
/join Присоединиться к команде
/next Следующее задание
    '''
    if check_admin(bot, message, session, silent=True):
        bot.send_message(message.chat.id, admin_commands + user_commands)
    else:
        bot.send_message(message.chat.id, user_commands)


register_auth_commands(bot, session, totp)
register_team_setting_commands(bot, session)
register_team_reset_commands(bot, session)
register_task_setting_commands(bot, session)
register_task_assign_commands(bot, session)
register_quest_commands(bot, session)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, 'Похоже, вы заблудились :(')


# Запуск бота
if __name__ == '__main__':
    bot.infinity_polling()
