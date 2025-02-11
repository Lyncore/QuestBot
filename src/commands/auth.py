from os import getenv

import pyotp
from pyotp import TOTP
from sqlalchemy.orm import Session
from telebot import TeleBot
from telebot.types import Message

from locale import AuthMessages
from models import Admin, OTPKey


def init_otp(session: Session):
    otp_secret = getenv("OTP_SECRET") or session.query(OTPKey).first().secret
    if not otp_secret:
        otp_secret = pyotp.random_base32()
        otp_key = OTPKey(secret=otp_secret)
        session.add(otp_key)
        session.commit()
    print(f'OTP Secret: {otp_secret}')
    return pyotp.TOTP(otp_secret)


def register_auth_commands(bot: TeleBot, session: Session, totp: TOTP):
    # Аутентификация администратора
    @bot.message_handler(commands=['setadmin'])
    def set_admin(message: Message):
        user_id = message.from_user.id
        if session.query(Admin).get(user_id):
            bot.reply_to(message, AuthMessages.ALREADY_ADMIN)
            return
        msg = bot.reply_to(message, AuthMessages.ENTER_OTP)
        bot.register_next_step_handler(msg, process_otp, user_id)

    def process_otp(message: Message, user_id: int):
        if totp.verify(message.text):
            session.add(Admin(user_id=user_id))
            session.commit()
            bot.reply_to(message, AuthMessages.BECOME_ADMIN)
        else:
            bot.reply_to(message, AuthMessages.INVALID_OTP)
