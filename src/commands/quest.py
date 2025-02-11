from asyncio import current_task

from sqlalchemy.orm import Session
from telebot import TeleBot
from telebot.types import Message

from locale import QuestMessages
from models import Chain, Team, Task


def register_quest_commands(bot: TeleBot, session: Session):
    # Присоединение лидера к команде
    @bot.message_handler(commands=['join'])
    def join_team(message: Message):
        team = session.query(Team).filter_by(leader_id=message.from_user.id).first()
        if team:
            bot.reply_to(message, QuestMessages.ALREADY_IN_TEAM.format(
                team_name=team.team_name
            ))
            return

        msg = bot.reply_to(message, QuestMessages.ENTER_CODE_WORD)
        bot.register_next_step_handler(msg, process_team_join)

    def process_team_join(message: Message):
        code_word = message.text
        team = session.query(Team).filter_by(code_word=code_word).first()
        if not team:
            bot.reply_to(message, QuestMessages.TEAM_NOT_FOUND)
            return

        if team.leader_id and team.leader_id != message.from_user.id:
            bot.reply_to(message, QuestMessages.ALREADY_HAS_LEADER)
            return
        else:
            team.leader_id = message.from_user.id
            session.commit()
            bot.reply_to(message, team.welcome_message or QuestMessages.BECOME_LEADER_DEFAULT)

        # Отправка первого задания
        current_chain = preprocess_task(message)
        if not current_chain:
            return
        send_task(message, current_chain.task)

    def preprocess_task(message: Message):
        team = session.query(Team).filter_by(leader_id=message.from_user.id).first()
        if not team:
            bot.reply_to(message, QuestMessages.NOT_LEADER)
            return

        current_chain = session.query(Chain).filter_by(team_id=team.id, order=team.current_chain_order).first()
        if current_chain:
            if team.current_chain_order == 0:
                task_assist_message = QuestMessages.FIRST_TASK_MESSAGE
            else:
                task_assist_message = QuestMessages.CURRENT_TASK_MESSAGE
            bot.send_message(message.chat.id, task_assist_message)
        else:
            bot.send_message(message.chat.id, QuestMessages.NO_ACTIVE_TASKS)
        return current_chain

    # Отправка задания пользователю
    def send_task(message: Message, task: Task):
        chat_id = message.chat.id

        bot.send_message(chat_id, QuestMessages.TASK_TEMPLATE.format(
            task_name=task.task_name,
            description=task.description
        ))
        if task.photo:
            bot.send_photo(chat_id, task.photo, caption=task.description)
        if task.animation:
            bot.send_animation(chat_id, task.animation)
        if task.sticker:
            bot.send_sticker(chat_id, task.sticker)
        if task.location:
            bot.send_message(chat_id, QuestMessages.LOCATION_TEMPLATE.format(
                location=task.location
            ))

    @bot.message_handler(commands=['task'])
    def get_task(message: Message):
        current_chain = preprocess_task(message)
        if not current_chain:
            return
        send_task(message, current_chain.task)

    # Обработка перехода к следующему заданию
    @bot.message_handler(commands=['next'])
    def next_task(message: Message):
        team = session.query(Team).filter_by(leader_id=message.from_user.id).first()
        if not team:
            bot.reply_to(message, QuestMessages.NOT_LEADER)
            return

        current_chain = session.query(Chain).filter_by(team_id=team.id, order=team.current_chain_order).first()
        if not current_chain:
            bot.reply_to(message, QuestMessages.NO_ACTIVE_TASKS)
            return

        msg = bot.reply_to(message, QuestMessages.ENTER_TASK_CODE)
        bot.register_next_step_handler(msg, check_task_code, team, current_chain.task)

    def check_task_code(message: Message, team: Team, current_team_task: Task):
        if message.text != current_team_task.code_word:
            bot.reply_to(message, QuestMessages.WRONG_TASK_CODE)
            return

        team.current_chain_order += 1
        session.commit()

        next_chain = session.query(Chain).filter_by(team_id=team.id, order=team.current_chain_order).first()
        if next_chain:
            bot.reply_to(message, QuestMessages.NEXT_TASK_MESSAGE)
            send_task(message, next_chain.task)
        else:
            bot.reply_to(message, team.final_message or QuestMessages.QUEST_COMPLETED)
