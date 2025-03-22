from telebot import TeleBot
from telebot.states import StatesGroup, State
from telebot.states.sync import StateContext
from telebot.types import Message, CallbackQuery

from buttons import render_team_buttons, render_cancel_button, render_main_menu
from checks import check_admin
from database.dao import add_team, get_teams, update_team, get_team_by_id, get_team_by_name
from database.models import Team
from locale import TeamMessages, CommonMessages, ButtonMessages


class TeamCreateState(StatesGroup):
    name = State()
    desc = State()
    welcome = State()
    final = State()
    code = State()


class TeamSelectState(State):
    pass


def register_team_setting_commands(bot: TeleBot):
    # Создание команды (только для админов)
    @bot.message_handler(func=lambda m: m.text == ButtonMessages.CREATE_TEAM)
    def create_team(message: Message, state: StateContext):
        if not check_admin(bot, message):
            return
        state.set(TeamCreateState.name)
        bot.reply_to(message, TeamMessages.ENTER_TEAM_NAME, reply_markup=render_cancel_button())

    @bot.message_handler(state=TeamCreateState.name)
    def process_team_name(message: Message, state: StateContext):
        team = get_team_by_name(message.text)
        if team:
            bot.reply_to(message, TeamMessages.TEAM_NAME_EXISTS, reply_markup=render_cancel_button())
            return
        state.set(TeamCreateState.desc)
        state.add_data(team_name=message.text)
        bot.reply_to(message, TeamMessages.ENTER_DESCRIPTION, reply_markup=render_cancel_button(add_skip=True))

    @bot.message_handler(state=TeamCreateState.desc)
    def process_team_description(message: Message, state: StateContext):
        state.set(TeamCreateState.welcome)
        if message.text != CommonMessages.SKIP:
            state.add_data(description=message.text)
        bot.reply_to(message, TeamMessages.ENTER_WELCOME, reply_markup=render_cancel_button(add_skip=True))

    @bot.message_handler(state=TeamCreateState.welcome)
    def process_team_welcome(message: Message, state: StateContext):
        state.set(TeamCreateState.final)
        if message.text != CommonMessages.SKIP:
            state.add_data(welcome_message=message.text)
        bot.reply_to(message, TeamMessages.ENTER_FINAL, reply_markup=render_cancel_button(add_skip=True))

    @bot.message_handler(state=TeamCreateState.final)
    def process_team_final(message: Message, state: StateContext):
        state.set(TeamCreateState.code)
        if message.text != CommonMessages.SKIP:
            state.add_data(final_message=message.text)
        bot.reply_to(message, TeamMessages.ENTER_CODE, reply_markup=render_cancel_button())

    @bot.message_handler(state=TeamCreateState.code)
    def process_team_code(message: Message, state: StateContext):

        with state.data() as data:
            team_id = data.get('team_id')
            if team_id:
                team = get_team_by_id(team_id)

                pass
            else:
                team = Team()
                team.team_name = data.get('team_name')
                team.description = data.get('description')
                team.welcome_message = data.get('welcome_message')
                team.final_message = data.get('final_message')
                team.code_word = message.text
                add_team(team)

        bot.reply_to(
            message,
            TeamMessages.TEAM_CREATED.format(
                team_name=team.team_name,
                id=team.id
            ),
            reply_markup=render_main_menu(check_admin(bot, message, silent=True))
        )
        state.delete()

    @bot.message_handler(func=lambda m: m.text == ButtonMessages.LIST_TEAM)
    def list_team(message: Message):
        if not check_admin(bot, message):
            return
        teams = get_teams()
        if len(teams) == 0:
            bot.reply_to(message, TeamMessages.NO_TEAMS)
        else:
            msg = TeamMessages.LIST_TEAMS_HEADER

            for team in teams:
                current_task = (team.current_chain_order + 1) if list(
                    filter(lambda x: x.order == team.current_chain_order,
                           team.chains)) else TeamMessages.TEAM_TASKS_COMPLETED

                msg += TeamMessages.TEAM_ITEM_TEMPLATE.format(
                    id=team.id,
                    team_name=team.team_name,
                    description=team.description,
                    welcome=team.welcome_message or CommonMessages.NO,
                    final=team.final_message or CommonMessages.NO,
                    current_task=current_task,
                    code=team.code_word
                )
            bot.reply_to(message, msg)

