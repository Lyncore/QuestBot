from telebot import TeleBot
from telebot.types import Message, CallbackQuery

from buttons import render_team_buttons
from checks import check_admin
from database.dao import get_teams, update_team
from locale import TeamMessages, CommonMessages, ButtonMessages


def register_team_reset_commands(bot: TeleBot):
    @bot.message_handler(func=lambda m: m.text == ButtonMessages.RESET_LEADER)
    def reset_leader(message: Message):
        if not check_admin(bot, message):
            return

        teams = get_teams(leader_only=True)
        if not teams:
            bot.reply_to(message, TeamMessages.RESET_LEADER_EMPTY)
            return

        markup = render_team_buttons(
            teams,
            callback_finish='reset_team_leader',
            callback_cancel='cancel_team_reset'
        )
        bot.send_message(message.chat.id, TeamMessages.RESET_LEADER_SELECT, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('reset_team_leader_'))
    def process_reset_team_leader(call: CallbackQuery):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        team_id = int(call.data.split('_')[-1])
        team = update_team(team_id=team_id, leader_id=None)

        bot.edit_message_text(TeamMessages.RESET_LEADER_SUCCESS.format(team_name=team.team_name), chat_id, message_id)

    @bot.message_handler(func=lambda m: m.text == ButtonMessages.RESET_TASK)
    def reset_task(message: Message):
        if not check_admin(bot, message):
            return

        teams = get_teams(started_only=True)
        if not teams:
            bot.reply_to(message, TeamMessages.RESET_TASK_EMPTY)
            return

        markup = render_team_buttons(
            teams,
            callback_finish='reset_team_task',
            callback_cancel='cancel_team_reset'
        )
        bot.send_message(message.chat.id, TeamMessages.RESET_TASK_SELECT, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('reset_team_task_'))
    def process_reset_team_task(call: CallbackQuery):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        team_id = int(call.data.split('_')[-1])
        team = update_team(team_id=team_id, current_chain_order=0)

        bot.edit_message_text(TeamMessages.RESET_TASK_SUCCESS.format(team_name=team.team_name), chat_id, message_id)

    @bot.callback_query_handler(func=lambda call: call.data == 'cancel_team_reset')
    def process_team_reset_cancel(call: CallbackQuery):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, CommonMessages.CANCEL_ACTION)
        return
