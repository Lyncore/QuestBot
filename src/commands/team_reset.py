from telebot import TeleBot
from telebot.types import Message, CallbackQuery

from buttons import render_team_buttons, render_yes_no_buttons
from checks import check_admin
from database.dao import get_teams, update_team, delete_team_members, get_team_by_id
from msg_locale import TeamMessages, CommonMessages, ButtonMessages


def register_team_reset_commands(bot: TeleBot):

    # Сброс учсников команды
    @bot.message_handler(func=lambda m: m.text == ButtonMessages.RESET_TEAM_MEMBERS)
    def reset_members_list(message: Message):
        if not check_admin(bot, message):
            return

        teams = get_teams()
        if not teams:
            bot.reply_to(message, TeamMessages.NO_TEAMS)
            return

        markup = render_team_buttons(
            teams,
            callback_finish='reset_members',
            callback_cancel='cancel_members_reset_list'
        )
        bot.send_message(message.chat.id, TeamMessages.RESET_TEAM_MEMBERS_SELECT, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_members_reset_list'))
    def cancel_members_reset_list(call: CallbackQuery):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        bot.edit_message_text(CommonMessages.CANCEL_ACTION, chat_id, message_id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('reset_members_'))
    def process_reset_members(call: CallbackQuery):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        team_id = int(call.data.split('_')[-1])
        team = get_team_by_id(team_id)
        

        bot.delete_message(chat_id, call.message.message_id)
        bot.send_message(
            chat_id = chat_id,
            text = TeamMessages.TEAM_MEMBERS_RESET_YES_NO.format(team_name=team.team_name),
            reply_markup = render_yes_no_buttons(
                callback_yes = "reset_team_members",
                callback_no = "cancel_reset_team_members",
                team_id = team_id
            )
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("reset_team_members_"))
    def reset_team_members_finally(call: CallbackQuery):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        team_id = int(call.data.split('_')[-1])
        team = get_team_by_id(team_id)
        
        if not delete_team_members(team_id):
            bot.delete_message(chat_id, call.message.message_id)
            bot.send_message(
                chat_id=chat_id,
                text=CommonMessages.ERROR_TEMPLATE.format(
                    error = ' '
                )
            )
        
        bot.edit_message_text(TeamMessages.RESET_TEAM_MEMBERS_SUCCESS.format(team_name=team.team_name), chat_id, message_id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_reset_team_members"))
    def cancel_reset_team_members(call: CallbackQuery):
        chat_id = call.message.chat.id

        bot.delete_message(chat_id,  call.message.message_id)
        bot.send_message(chat_id, CommonMessages.CANCEL_ACTION)

    
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
    