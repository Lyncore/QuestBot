from sqlalchemy.orm import Session
from telebot import TeleBot
from telebot.types import Message

from checks import check_admin
from models import Task


def register_task_setting_commands(bot: TeleBot, session: Session):
    # Создание задания (админ)
    @bot.message_handler(commands=['createtask'])
    def create_task(message: Message):
        if not check_admin(bot, message, session):
            return
        msg = bot.reply_to(message, '📝 Введите название задания:')
        bot.register_next_step_handler(msg, process_task_name)

    def process_task_name(message: Message):
        task = Task(task_name=message.text)
        msg = bot.reply_to(message, '📝 Введите описание задания:')
        bot.register_next_step_handler(msg, process_task_description, task)

    def process_task_description(message: Message, task: Task):
        task.description = message.text
        msg = bot.reply_to(message, '🖼 Отправьте фото, GIF или стикер (или /skip):')
        bot.register_next_step_handler(msg, process_task_media, task)

    def process_task_media(message: Message, task: Task):
        if message.photo:
            task.photo = message.photo[-1].file_id
        elif message.sticker:
            task.sticker = message.sticker.file_id
        elif message.animation:
            task.animation = message.animation.file_id

        msg = bot.reply_to(message, '🏠 Введите место прохождения задания:')
        bot.register_next_step_handler(msg, process_task_location, task)

    def process_task_location(message: Message, task: Task):

        task.location = message.text

        msg = bot.reply_to(message, '🔑 Введите кодовое слово для задания:')
        bot.register_next_step_handler(msg, process_task_code, task)

    def process_task_code(message: Message, task: Task):
        task.code_word = message.text

        session.add(task)
        session.commit()
        bot.reply_to(message, '✅ Задание создано!')

    @bot.message_handler(commands=['listtask'])
    def list_task(message: Message):
        if not check_admin(bot, message, session):
            return
        tasks = session.query(Task).all()
        if len(tasks) == 0:
            bot.reply_to(message, 'Вы еще не добавили задания. Используйте /createtask 🥺')
        else:
            msg = "Список заданий:\n"
            for task in tasks:
                msg += \
                    f'''
*Задание #{task.id}:* {task.task_name}
🖼Описание: {task.description}
📸Фото: {'Есть' if task.photo else 'Нет'}
🫡Стикер: {'Есть' if task.sticker else 'Нет'}
🎁Гифка: {'Есть' if task.animation else 'Нет'}
🏠Локация: {task.location}
🔑Кодовое слово: {task.code_word}
\n'''
                if len(task.chains) > 0:
                    msg += 'Задание присвоено командам:\n'
                    for chain in task.chains:
                        msg += f'*Команда "{chain.team.team_name}"*\n'
                        msg += f'Задание #{chain.order + 1}\n'
            bot.reply_to(message, msg)
