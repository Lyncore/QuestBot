from collections import defaultdict

from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from buttons import render_task_assign_buttons, render_team_buttons
from checks import check_admin
from database.dao import get_teams, get_tasks, delete_chains_by_team, add_chains, get_team_by_id, get_tasks_by_team, get_user_ids_by_team
from database.models import Chain
from msg_locale import TaskMessages, CommonMessages, ButtonMessages


def register_task_assign_commands(bot: TeleBot):
    temp_data = defaultdict(dict)

    @bot.message_handler(func=lambda m: m.text == ButtonMessages.ASSIGN_TASK)
    def assign_task(message: Message):
        if not check_admin(bot, message):
            return

        teams = get_teams()
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
        bot.send_message(chat_id, CommonMessages.CANCEL_ACTION)
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

        tasks = get_tasks()
        if not tasks:
            bot.answer_callback_query(call.id, TaskMessages.NO_TASKS)
            return
        selected_tasks = temp_data[chat_id]['selected_tasks']
        markup = render_task_assign_buttons(
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
        tasks = get_tasks()
        selected_tasks = temp_data[chat_id]['selected_tasks']
        markup = render_task_assign_buttons(
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
            bot.send_message(chat_id, CommonMessages.CANCEL_ACTION)
            return

        if not temp_data[chat_id]['selected_tasks']:
            bot.answer_callback_query(call.id, TaskMessages.TASK_ASSIGN_EMPTY)
            return

        # Сохраняем цепочку заданий
        team_id = temp_data[chat_id]['team_id']

        # Удаляем старые привязки
        delete_chains_by_team(team_id)

        # Добавляем новые задания с правильным порядком
        selected_tasks = enumerate(temp_data[chat_id]['selected_tasks'])
        chains = [Chain(team_id=team_id, task_id=task_id, order=order) for order, task_id in selected_tasks]

        add_chains(chains)

        # Рассылка о добавлении заданий всем участникам команды
        user_ids = get_user_ids_by_team(team_id)
        tasks = get_tasks_by_team(team_id)

        if tasks:
            task_list = "\n".join(f"• *{task.task_name}*" for task in tasks)
            notification_text = (
                f"🆕 В вашей команде появилось новое задание!\n\n"
                f"{task_list}\n\n"
                f"Напишите на кнопку {ButtonMessages.LIST_TASK}, чтобы начать."
            )
        else:
            notification_text = f"🆕 В вашей команде обновлены задания. Нажмите на кнопку {ButtonMessages.LIST_TASK}, чтобы посмотреть."
        
        for user_id in user_ids:
            try:
                bot.send_message(
                    chat_id=user_id,
                    text=notification_text,
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Не удалось отправить уведомление пользователю {user_id}: {e}")

        # Получаем информацию для отчета
        team = get_team_by_id(team_id)
        

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

        del temp_data[chat_id]
