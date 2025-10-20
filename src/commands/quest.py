from telebot import TeleBot
from telebot import TeleBot
from telebot.types import Message

from database.dao import get_member, get_team_by_code, update_team, get_current_chain, get_team_by_id, join_team_via_code
from database.models import Team, Task
from msg_locale import QuestMessages, ButtonMessages


def register_quest_commands(bot: TeleBot):
    # Присоединение лидера к команде
    @bot.message_handler(func=lambda m: m.text == ButtonMessages.JOIN_TEAM)
    def join_team(message: Message):
        print('join_team start')
        member = get_member(message.from_user.id)
        
        if member:
            team = get_team_by_id(team_id=member.team_id)
            bot.reply_to(message, QuestMessages.ALREADY_IN_TEAM.format(
                team_name=team.team_name
            ))
            return

        msg = bot.reply_to(message, QuestMessages.ENTER_CODE_WORD)
        bot.register_next_step_handler(msg, process_team_join)
        print('join_team end')

    def process_team_join(message: Message):
        print('process_team_join start')
        code_word = message.text
        team = get_team_by_code(code_word)
        if not team:
            bot.reply_to(message, QuestMessages.TEAM_NOT_FOUND)
            return

        # if team.leader_id and team.leader_id != message.from_user.id:
        #     bot.reply_to(message, QuestMessages.ALREADY_HAS_LEADER)
        #     return
        else:
            join_team_via_code(code_word, user_id=message.from_user.id)
            bot.reply_to(message, team.welcome_message)

        # Отправка первого задания
        current_chain = preprocess_task(message)
        if not current_chain:
            return
        send_task(message, current_chain.task)
        print('process_team_join end')

    def preprocess_task(message: Message):
        print('process_task start')
        member = get_member(message.from_user.id)
        team = get_team_by_id(member.team_id)
        # if not team:
        #     bot.reply_to(message, QuestMessages.NOT_LEADER)
        #     return

        current_chain = get_current_chain(team.id, team.current_chain_order)
        if current_chain:
            if team.current_chain_order == 0:
                task_assist_message = QuestMessages.FIRST_TASK_MESSAGE
            else:
                task_assist_message = QuestMessages.CURRENT_TASK_MESSAGE
            bot.send_message(message.chat.id, task_assist_message)
        else:
            bot.send_message(message.chat.id, QuestMessages.NO_ACTIVE_TASKS)
        print('process_task end')
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

    @bot.message_handler(func=lambda m: m.text == ButtonMessages.CURRENT_TASK)
    def get_task(message: Message):
        current_chain = preprocess_task(message)
        if not current_chain:
            return
        send_task(message, current_chain.task)

    # Обработка перехода к следующему заданию
    @bot.message_handler(func=lambda m: m.text == ButtonMessages.NEXT_TASK)
    def next_task(message: Message):
        team = get_team_by_id(message.from_user.id)
        if not team:
            bot.reply_to(message, QuestMessages.NOT_LEADER)
            return

        current_chain = get_current_chain(team.id, team.current_chain_order)
        if not current_chain:
            bot.reply_to(message, QuestMessages.NO_ACTIVE_TASKS)
            return

        msg = bot.reply_to(message, QuestMessages.ENTER_TASK_CODE)
        bot.register_next_step_handler(msg, check_task_code, team, current_chain.task)

    def check_task_code(message: Message, team: Team, current_team_task: Task):
        if current_team_task.code_word.lower() not in message.text.lower():
            bot.reply_to(message, QuestMessages.WRONG_TASK_CODE)
            return

        next_order = team.current_chain_order + 1
        update_team(team_id=team.id, current_chain_order=next_order)

        next_chain = get_current_chain(team.id, next_order)
        if next_chain:
            bot.reply_to(message, QuestMessages.NEXT_TASK_MESSAGE)
            send_task(message, next_chain.task)
        else:
            bot.reply_to(message, team.final_message or QuestMessages.QUEST_COMPLETED)
