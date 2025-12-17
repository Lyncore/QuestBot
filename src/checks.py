from telebot import TeleBot
from telebot.types import Message

from database.dao import get_admin, get_member
from msg_locale import AuthMessages


def check_admin(bot: TeleBot, message: Message, silent: bool = False):
    if not get_admin(message.from_user.id):
        if not silent:
            bot.reply_to(message, AuthMessages.NOT_ADMIN)
        return False
    else:
        return True
    
def check_user_team(bot: TeleBot, message: Message):
    user_id = message.from_user.id
    member = get_member(user_id)

    if member is not None:
        return True
    else:
        return False
