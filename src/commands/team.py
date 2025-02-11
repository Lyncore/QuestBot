from sqlalchemy.orm import Session
from telebot import TeleBot
from telebot.types import Message

from checks import check_admin
from locale import TeamMessages, CommonMessages
from models import Team


def register_team_setting_commands(bot: TeleBot, session: Session):
    # Создание команды (только для админов)
    @bot.message_handler(commands=['createteam'])
    def create_team(message: Message):
        if not check_admin(bot, message, session):
            return
        msg = bot.reply_to(message, TeamMessages.ENTER_TEAM_NAME)
        bot.register_next_step_handler(msg, process_team_name)

    def process_team_name(message: Message):
        team = Team(team_name=message.text)
        msg = bot.reply_to(message, TeamMessages.ENTER_DESCRIPTION)
        bot.register_next_step_handler(msg, process_team_description, team)

    def process_team_description(message: Message, team: Team):
        if not message.text.startswith('/skip'):
            team.description = message.text
        msg = bot.reply_to(message, TeamMessages.ENTER_WELCOME)
        bot.register_next_step_handler(msg, process_team_welcome, team)

    def process_team_welcome(message: Message, team: Team):
        if not message.text.startswith('/skip'):
            team.welcome_message = message.text
        msg = bot.reply_to(message, TeamMessages.ENTER_FINAL)
        bot.register_next_step_handler(msg, process_team_final, team)

    def process_team_final(message: Message, team: Team):
        if not message.text.startswith('/skip'):
            team.final_message = message.text
        msg = bot.reply_to(message, TeamMessages.ENTER_CODE)
        bot.register_next_step_handler(msg, process_team_code, team)

    def process_team_code(message: Message, team: Team):
        team.code_word = message.text
        session.add(team)
        session.commit()
        bot.reply_to(message, TeamMessages.TEAM_CREATED.format(
            team_name=team.team_name,
            id=team.id
        ))

    @bot.message_handler(commands=['listteam'])
    def list_team(message: Message):
        if not check_admin(bot, message, session):
            return
        teams = session.query(Team).all()
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
