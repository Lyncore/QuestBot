from os import getenv

import telebot
from dotenv import load_dotenv
from telebot import StateMemoryStorage, custom_filters
from telebot.states.sync import StateContext
from telebot.types import BotCommand, Message

from buttons import render_main_menu

load_dotenv()

from checks import check_admin
from commands.task_assign import register_task_assign_commands
from commands.quest import register_quest_commands
from commands.auth import register_auth_commands, init_otp
from database.database import create_tables
from msg_locale import CommonMessages, CommandDescription, ButtonMessages, QuestMessages
from commands.team import register_team_setting_commands, register_team_edit_commands
from commands.task import register_task_setting_commands, register_task_edit_commands
from commands.team_reset import register_team_reset_commands

from database.dao import join_team_via_invite_token, get_member, get_team_by_id, get_current_chain
from database.models import Task, Team

totp = init_otp()
state_storage = StateMemoryStorage()
bot = telebot.TeleBot(
    token=getenv('TELEGRAM_TOKEN'),
    state_storage=state_storage, use_class_middlewares=True,
    parse_mode="markdown"
)

# --- Обработчики команд ---
bot.set_my_commands(commands=[BotCommand(cmd, desc) for cmd, desc in CommandDescription.user_commands.items()])


@bot.message_handler(commands=['start'])
def start_message(message):
    print('Full text: ', message.text)
    user_id = message.from_user.id
    chat_id = message.chat.id
    args = message.text.split()
    invite_token = None

    if len(args)>1:
        try:
            invite_token = str(args[1])
            print(invite_token)
        except: 
            print("Invite token is none")
            invite_token = None
    is_admin = check_admin(bot, message, silent=True)

    def preprocess_task(message: Message, team: Team):

        current_chain = get_current_chain(team.id, team.current_chain_order)
        if current_chain:
            if team.current_chain_order == 0:
                task_assist_message = QuestMessages.FIRST_TASK_MESSAGE
                return current_chain
            else:
                task_assist_message = QuestMessages.CURRENT_TASK_MESSAGE
                bot.send_message(message.chat.id, task_assist_message)
                return current_chain
        else:
            print('current chain is false')
            bot.send_message(message.chat.id, QuestMessages.NO_ACTIVE_TASKS)
            return current_chain

    def send_task(chat_id: int, task: Task):
        bot.send_message(chat_id, QuestMessages.TASK_TEMPLATE.format(
            task_name=task.task_name,
            description=task.description
        ))
        if task.photo:
            bot.send_photo(chat_id, task.photo)
        if task.animation:
            bot.send_animation(chat_id, task.animation)
        if task.sticker:
            bot.send_sticker(chat_id, task.sticker)
        if task.location:
            bot.send_message(chat_id, QuestMessages.LOCATION_TEMPLATE.format(
                location=task.location
            ))

    if invite_token:
        print('invite_token')
        member = get_member(user_id)
        if member:
            team = get_team_by_id(member.team_id)
            bot.send_message(
                chat_id,
                QuestMessages.ALREADY_IN_TEAM.format(
                    team_name=team.team_name),
                    reply_markup=render_main_menu(is_admin, is_in_team=True)
                ) 
        else:
            team = join_team_via_invite_token(invite_token, user_id)
            
            bot.send_message(
                chat_id,
                QuestMessages.JOINED_TO_TEAM.format(
                    team_name=team.team_name
                ),
                reply_markup=render_main_menu(is_admin, is_in_team=True)
            )

            current_chain = preprocess_task(message, team)
            if not current_chain:
                print('not current chain')
                return
            send_task(chat_id, current_chain.task)

    else:   
        bot.send_message(
            message.chat.id,
            CommonMessages.WELCOME_MESSAGE, 
            reply_markup=render_main_menu(is_admin)
        )


@bot.message_handler(state="*", func=lambda m: m.text == CommonMessages.CANCEL)
def handle_cancel_commands(message: Message, state: StateContext):
    state.delete()
    bot.send_message(
        message.chat.id,
        CommonMessages.CANCEL_ACTION,
        reply_markup=render_main_menu(check_admin(bot, message, silent=True), is_in_team=True))


@bot.message_handler(func=lambda m: m.text == ButtonMessages.HELP)
def help_message(message):
    admin_commands_desc = '\n'.join([f'/{cmd} - {desc}' for cmd, desc in CommandDescription.admin_commands.items()])
    user_commands_desc = '\n'.join([f'/{cmd} - {desc}' for cmd, desc in CommandDescription.user_commands.items()])
    if check_admin(bot, message, silent=True):
        bot.send_message(message.chat.id, f'{admin_commands_desc}\n{user_commands_desc}')
    else:
        bot.send_message(message.chat.id, user_commands_desc)


register_auth_commands(bot, totp)
register_team_setting_commands(bot)
register_team_edit_commands(bot)
register_team_reset_commands(bot)
register_task_setting_commands(bot)
register_task_edit_commands(bot)
register_task_assign_commands(bot)
register_quest_commands(bot)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to( 
        message,
        CommonMessages.COMMON_MESSAGE,
        reply_markup=render_main_menu(check_admin(bot, message, silent=True), is_in_team=True)
    )


# Add custom filters
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())
bot.add_custom_filter(custom_filters.TextMatchFilter())

# necessary for state parameter in handlers.
from telebot.states.sync.middleware import StateMiddleware

bot.setup_middleware(StateMiddleware(bot))
# Запуск бота
if __name__ == '__main__':
    create_tables()
    bot.infinity_polling(skip_pending=True)
