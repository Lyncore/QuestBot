from sqlalchemy.orm import Session
from telebot import TeleBot
from telebot.types import Message

from locale import AuthMessages
from models import Admin


def check_admin(bot: TeleBot, message: Message, session: Session, silent: bool = False):
    if not session.query(Admin).get(message.from_user.id):
        if not silent:
            bot.reply_to(message, AuthMessages.NOT_ADMIN)
        return False
    else:
        return True
