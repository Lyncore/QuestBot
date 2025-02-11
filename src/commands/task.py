from sqlalchemy.orm import Session
from telebot import TeleBot
from telebot.types import Message

from checks import check_admin
from locale import TaskMessages, CommonMessages
from models import Task


def register_task_setting_commands(bot: TeleBot, session: Session):
    # Создание задания (админ)
    @bot.message_handler(commands=['createtask'])
    def create_task(message: Message):
        if not check_admin(bot, message, session):
            return
        msg = bot.reply_to(message, TaskMessages.ENTER_TASK_NAME)
        bot.register_next_step_handler(msg, process_task_name)

    def process_task_name(message: Message):
        task = Task(task_name=message.text)
        msg = bot.reply_to(message, TaskMessages.ENTER_DESCRIPTION)
        bot.register_next_step_handler(msg, process_task_description, task)

    def process_task_description(message: Message, task: Task):
        task.description = message.text
        msg = bot.reply_to(message, TaskMessages.ENTER_MEDIA)
        bot.register_next_step_handler(msg, process_task_media, task)

    def process_task_media(message: Message, task: Task):
        if message.photo:
            task.photo = message.photo[-1].file_id
        elif message.sticker:
            task.sticker = message.sticker.file_id
        elif message.animation:
            task.animation = message.animation.file_id

        msg = bot.reply_to(message, TaskMessages.ENTER_LOCATION)
        bot.register_next_step_handler(msg, process_task_location, task)

    def process_task_location(message: Message, task: Task):

        task.location = message.text

        msg = bot.reply_to(message, TaskMessages.ENTER_CODE_WORD)
        bot.register_next_step_handler(msg, process_task_code, task)

    def process_task_code(message: Message, task: Task):
        task.code_word = message.text

        session.add(task)
        session.commit()
        bot.reply_to(message, TaskMessages.TASK_CREATED)

    @bot.message_handler(commands=['listtask'])
    def list_task(message: Message):
        if not check_admin(bot, message, session):
            return
        tasks = session.query(Task).all()
        if len(tasks) == 0:
            bot.reply_to(message, TaskMessages.NO_TASKS)
        else:
            msg = TaskMessages.LIST_TASKS_HEADER
            for task in tasks:
                msg += TaskMessages.TASK_ITEM_TEMPLATE.format(
                    id=task.id,
                    task_name=task.task_name,
                    description=task.description,
                    photo=CommonMessages.YES if task.photo else CommonMessages.NO,
                    sticker=CommonMessages.YES if task.sticker else CommonMessages.NO,
                    animation=CommonMessages.YES if task.animation else CommonMessages.NO,
                    location=task.location,
                    code_word=task.code_word
                )
                if len(task.chains) > 0:
                    msg += TaskMessages.ASSIGNED_TEAMS_HEADER
                    for chain in task.chains:
                        msg += TaskMessages.ASSIGNED_TEAMS_TEMPLATE.format(
                            team_name=chain.team.team_name,
                            task_chain_order=chain.order + 1
                        )

            bot.reply_to(message, msg)
