from collections import defaultdict

from sqlalchemy.orm import Session
from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from buttons import render_task_buttons, render_team_buttons
from checks import check_admin
from locale import TaskMessages, CommonMessages
from models import Team, Task, Chain


def register_task_assign_commands(bot: TeleBot, session: Session):
    temp_data = defaultdict(dict)

    @bot.message_handler(commands=['assigntask'])
    def assign_task(message: Message):
        if not check_admin(bot, message, session):
            return

        teams = session.query(Team).all()
        if not teams:
            bot.reply_to(message, TaskMessages.NO_TASKS)
            return

        markup = render_team_buttons(teams, callback_finish='assign_team', callback_cancel='cancel_team_selection')
        bot.send_message(message.chat.id, TaskMessages.TASK_ASSIGN_SELECT_TEAM, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == 'cancel_team_selection')
    def process_team_selection_cancel(call: CallbackQuery):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, CommonMessages.SELECT_CANCEL)
        return

    @bot.callback_query_handler(func=lambda call: call.data.startswith('assign_team_'))
    def process_team_selection(call: CallbackQuery):
        team_id = int(call.data.split('_')[-1])
        chat_id = call.message.chat.id

        temp_data[chat_id] = {
            'team_id': team_id,
            'selected_tasks': [],
            'message_id': call.message.message_id
        }

        tasks = session.query(Task).all()
        if not tasks:
            bot.answer_callback_query(call.id, TaskMessages.NO_TASKS)
            return
        selected_tasks = temp_data[chat_id]['selected_tasks']
        markup = render_task_buttons(
            tasks,
            selected_tasks,
            callback_select='task',
            callback_finish='finish_selection',
            callback_cancel='cancel_selection'
        )

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=TaskMessages.TASK_ASSIGN_SELECT_TASK,
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('task_'))
    def process_task_selection(call: CallbackQuery):
        chat_id = call.message.chat.id
        task_id = int(call.data.split('_')[-1])

        if task_id in temp_data[chat_id]['selected_tasks']:
            temp_data[chat_id]['selected_tasks'].remove(task_id)
        else:
            temp_data[chat_id]['selected_tasks'].append(task_id)

        # Обновляем клавиатуру с отметками выбранных заданий
        tasks = session.query(Task).all()
        selected_tasks = temp_data[chat_id]['selected_tasks']
        markup = render_task_buttons(
            tasks,
            selected_tasks,
            callback_select='task',
            callback_finish='finish_selection',
            callback_cancel='cancel_selection'
        )

        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data in ['finish_selection', 'cancel_selection'])
    def process_finish_selection(call: CallbackQuery):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        if call.data == 'cancel_selection':
            del temp_data[chat_id]
            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, CommonMessages.SELECT_CANCEL)
            return

        if not temp_data[chat_id]['selected_tasks']:
            bot.answer_callback_query(call.id, TaskMessages.TASK_ASSIGN_EMPTY)
            return

        # Сохраняем цепочку заданий
        team_id = temp_data[chat_id]['team_id']
        try:
            # Удаляем старые привязки
            session.query(Chain).filter_by(team_id=team_id).delete()

            # Добавляем новые задания с правильным порядком
            for order, task_id in enumerate(temp_data[chat_id]['selected_tasks']):
                chain = Chain(team_id=team_id, task_id=task_id, order=order)
                session.add(chain)

            session.commit()

            # Получаем информацию для отчета
            team = session.query(Team).get(team_id)
            tasks = session.query(Task).filter(Task.id.in_(temp_data[chat_id]['selected_tasks'])).all()

            task_list = '\n'.join([f'{i + 1}. {task.task_name[:30]}...' for i, task in enumerate(tasks)])

            report = TaskMessages.TASK_ASSIGNMENT_REPORT.format(
                team_name=team.team_name,
                code_word=team.code_word,
                count=len(tasks),
                task_list=task_list
            )

            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=report
            )

        except Exception as e:
            session.rollback()
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=CommonMessages.ERROR_TEMPLATE.format(
                    error=str(e)
                )
            )

        finally:
            del temp_data[chat_id]
