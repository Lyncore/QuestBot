from telebot import TeleBot
from telebot.types import Message

from database.dao import get_admin
from locale import AuthMessages


def check_admin(bot: TeleBot, message: Message, silent: bool = False):
    if not get_admin(message.from_user.id):
        if not silent:
            bot.reply_to(message, AuthMessages.NOT_ADMIN)
        return False
    else:
        return True
