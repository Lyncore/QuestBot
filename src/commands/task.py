from telebot import TeleBot
from telebot.states import StatesGroup, State
from telebot.states.sync import StateContext
from telebot.types import Message, CallbackQuery, InputMedia, InputMediaAnimation, InputMediaPhoto

from buttons import render_cancel_button, render_main_menu, render_task_buttons
from checks import check_admin
from database.dao import add_task, get_tasks, get_task_by_id
from database.models import Task
from msg_locale import TaskMessages, CommonMessages, ButtonMessages


class TaskCreateState(StatesGroup):
    name = State()
    desc = State()
    media = State()
    location = State()
    code = State()


def register_task_setting_commands(bot: TeleBot):
    # Создание задания (админ)
    @bot.message_handler(func=lambda m: m.text == ButtonMessages.CREATE_TASK)
    def create_task(message: Message, state: StateContext):
        if not check_admin(bot, message):
            return
        state.set(TaskCreateState.name)
        bot.reply_to(message, TaskMessages.ENTER_TASK_NAME, reply_markup=render_cancel_button())

    @bot.message_handler(state=TaskCreateState.name)
    def process_task_name(message: Message, state: StateContext):
        state.set(TaskCreateState.desc)
        state.add_data(task_name=message.text)
        bot.reply_to(message, TaskMessages.ENTER_DESCRIPTION, reply_markup=render_cancel_button())

    @bot.message_handler(state=TaskCreateState.desc)
    def process_task_description(message: Message, state: StateContext):
        state.set(TaskCreateState.media)
        state.add_data(description=message.text, reply_markup=render_cancel_button())
        bot.reply_to(message, TaskMessages.ENTER_MEDIA, reply_markup=render_cancel_button(add_skip=True))

    @bot.message_handler(state=TaskCreateState.media, content_types=['photo', 'sticker', 'animation'])
    def process_task_media(message: Message, state: StateContext):
        state.set(TaskCreateState.location)
        if message.photo:
            state.add_data(photo=message.photo[-1].file_id)
        elif message.sticker:
            state.add_data(sticker=message.sticker.file_id)
        elif message.animation:
            state.add_data(animation=message.animation.file_id)

        bot.reply_to(message, TaskMessages.ENTER_LOCATION, reply_markup=render_cancel_button())

    @bot.message_handler(state=TaskCreateState.media)
    def process_wrong_media(message: Message):
        bot.reply_to(message, TaskMessages.ENTER_MEDIA, reply_markup=render_cancel_button())

    @bot.message_handler(state=TaskCreateState.location)
    def process_task_location(message: Message, state: StateContext):
        state.set(TaskCreateState.code)
        state.add_data(location=message.text)

        bot.reply_to(message, TaskMessages.ENTER_CODE_WORD, reply_markup=render_cancel_button())

    @bot.message_handler(state=TaskCreateState.code)
    def process_task_code(message: Message, state: StateContext):
        with state.data() as data:
            task = Task()
            task.task_name = data.get('task_name')
            task.description = data.get('description')
            task.photo = data.get('photo')
            task.sticker = data.get('sticker')
            task.animation = data.get('animation')
            task.location = data.get('location')
            task.code_word = message.text
            add_task(task)

        bot.reply_to(
            message,
            TaskMessages.TASK_CREATED,
            reply_markup=render_main_menu(check_admin(bot, message, silent=True))
        )

    @bot.message_handler(func=lambda m: m.text == ButtonMessages.LIST_TASK)
    def list_task(message: Message):
        if not check_admin(bot, message):
            return
        tasks = get_tasks()
        if len(tasks) == 0:
            bot.reply_to(message, TaskMessages.NO_TASKS)
        else:
            msg = TaskMessages.LIST_TASKS_HEADER

            markup = render_task_buttons(tasks, "list_task", "cancel_list_task")

            bot.reply_to(message, msg, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("list_task"))
    def process_list_task(call: CallbackQuery):
        task_id = int(call.data.split('_')[-1])
        task = get_task_by_id(task_id)

        msg = TaskMessages.TASK_ITEM_TEMPLATE.format(
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
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        bot.edit_message_text(msg, chat_id, message_id)
        if task.photo:
            bot.send_photo(chat_id, task.photo)
        if task.sticker:
            bot.send_sticker(chat_id, task.sticker)
        if task.animation:
            bot.send_animation(chat_id, task.animation)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_list_task"))
    def cancel_team_list(call: CallbackQuery):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        bot.edit_message_text(CommonMessages.CANCEL_ACTION, chat_id, message_id)
