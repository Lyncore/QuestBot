from os import getenv

import pyotp
from pyotp import TOTP
from telebot import TeleBot
from telebot.types import Message

from database.dao import get_otp, set_otp, get_admin, add_admin
from msg_locale import AuthMessages


def init_otp():
    otp_secret = getenv("OTP_SECRET") or get_otp()
    if not otp_secret:
        otp_secret = pyotp.random_base32()
        set_otp(otp_secret)
    print(f'OTP Secret: {otp_secret}')
    return pyotp.TOTP(otp_secret)


def register_auth_commands(bot: TeleBot, totp: TOTP):
    # Аутентификация администратора
    @bot.message_handler(commands=['setadmin'])
    def set_admin(message: Message):
        user_id = message.from_user.id
        if get_admin(user_id=user_id):
            bot.reply_to(message, AuthMessages.ALREADY_ADMIN)
            return
        msg = bot.reply_to(message, AuthMessages.ENTER_OTP)
        bot.register_next_step_handler(msg, process_otp, user_id)

    def process_otp(message: Message, user_id: int):
        if totp.verify(message.text):
            add_admin(user_id=user_id)
            bot.reply_to(message, AuthMessages.BECOME_ADMIN)
        else:
            bot.reply_to(message, AuthMessages.INVALID_OTP)
