from collections import defaultdict
from telebot import TeleBot
from telebot.states import StatesGroup, State
from telebot.states.sync import StateContext
from telebot.types import Message, CallbackQuery, InputMedia, InputMediaAnimation, InputMediaPhoto

from buttons import render_cancel_button, render_main_menu, render_task_buttons, render_task_edit_buttons
from checks import check_admin
from database.dao import add_task, edit_task, get_tasks, get_task_by_id
from database.models import Task
from msg_locale import TaskMessages, CommonMessages, ButtonMessages, QuestMessages, EditTaskButtonMessages


class TaskCreateState(StatesGroup):
    name = State()
    desc = State()
    media = State()
    location = State()
    code = State()

class TaskEditState(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_media = State()
    waiting_for_location = State()
    waiting_for_code = State()

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
        state.delete()

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

# --------- Редактирование задачи ---------
def register_task_edit_commands(bot: TeleBot):
    temp_data = defaultdict(dict)

    # Сообщение со всем списком задач для изменения
    @bot.message_handler(func=lambda m: m.text == ButtonMessages.EDIT_TASK)
    def update_task_info(message: Message):
        is_admin = check_admin(bot, message)
        if not is_admin:
            return
        
        tasks = get_tasks()
        if not tasks:
            bot.reply_to(message, TaskMessages.NO_TASKS)

        markup = render_task_buttons(
            tasks,
            callback_finish='edit_task',
            callback_cancel='cancel_task_edit'
        )
        bot.send_message(message.chat.id, TaskMessages.EDIT_TASK_SELECT, reply_markup=markup)

    # Сохранения id выбранного задания
    # Вывод клавиатуры с атрибутами команды, которые можно изменить: название, описание, медиа(стикер, гифка или фото), локация, кодовое слово
    @bot.callback_query_handler(func=lambda call: call.data.startswith('edit_task_'))
    def process_task_selection(call:CallbackQuery):
        chat_id = call.message.chat.id
        task_id = int(call.data.split('_')[-1])

        task = get_task_by_id(task_id)
        if not task:
            bot.answer_callback_query(call.id, QuestMessages.TASK_NOT_FOUND)
            return      
        # Сохрание id задачи
        temp_data[chat_id]["task_id"] = task_id

        bot.delete_message(chat_id, call.message.message_id)
        bot.send_message(
            chat_id=chat_id,
            text=EditTaskButtonMessages.CHOOSE_PROPERTY.format(task_name = task.task_name),
            reply_markup=render_task_edit_buttons(task_id)
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_task_edit'))
    def cancel_task_edit_list(call: CallbackQuery): 
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        bot.edit_message_text(CommonMessages.CANCEL_ACTION, chat_id, message_id)

    # ======== Обработчики для каждой кнопки ========

    # Установка состояния для редактирования НАЗВАНИЯ задания
    @bot.message_handler(func=lambda m: m.text == EditTaskButtonMessages.NAME)
    def edit_task_name(message: Message, state: StateContext):
        chat_id = message.chat.id
        # Проверка выбрана ли задача
        if chat_id not in temp_data or "task_id" not in temp_data[chat_id]:
            bot.send_message(chat_id, EditTaskButtonMessages.TASK_NOT_SET)
            return
        
        # Установка состояния
        state.set(TaskEditState.waiting_for_name)
        bot.send_message(chat_id, EditTaskButtonMessages.EDIT_NAME)

    # Cохранение значения в БД
    @bot.message_handler(state=TaskEditState.waiting_for_name, content_types=['text', 'animation', 'sticker', 'photo', 'video'])
    def process_edit_name(message: Message, state: StateContext):
        chat_id = message.chat.id
        task_id = temp_data[chat_id].get("task_id")

        if not task_id:
            bot.send_message(chat_id, EditTaskButtonMessages.TASK_NOT_FOUND)
            state.delete()
            return
        
        # Проверка на тип контента
        if message.content_type == 'text':
        
            edit_task(task_id, "task_name", message.text)
            
            bot.send_message(
                chat_id, 
                CommonMessages.SAVED_DATA, 
                reply_markup=render_main_menu(is_admin=True)
            )
            # Очистка состояния и временных данных 
            state.delete()
            temp_data.pop(chat_id, None)
        else:
            bot.send_message(chat_id, EditTaskButtonMessages.INVALID_TEXT)


    # Установка состояния для редактирования ОПИСАНИЯ задания
    @bot.message_handler(func=lambda m: m.text == EditTaskButtonMessages.DESCRIPTION)
    def edit_task_description(message: Message, state: StateContext):
        chat_id = message.chat.id
        if chat_id not in temp_data or "task_id" not in temp_data[chat_id]:
            bot.send_message(chat_id, EditTaskButtonMessages.TASK_NOT_SET)
            return
            
        state.set(TaskEditState.waiting_for_description)
        bot.send_message(chat_id, EditTaskButtonMessages.EDIT_DESCRIPTION)

    

    # Сохранение описания в БД
    @bot.message_handler(state=TaskEditState.waiting_for_description, content_types=['text', 'animation', 'sticker', 'photo', 'video'])
    def process_edit_description(message: Message, state: StateContext):
        chat_id = message.chat.id
        task_id = temp_data[chat_id].get("task_id")

        if not task_id:
            bot.send_message(chat_id, EditTaskButtonMessages.TASK_NOT_FOUND)
            state.delete()
            return
        
        # Проверка на тип контента
        if message.content_type == 'text':
            edit_task(task_id, "description", message.text)
            
            bot.send_message(
                chat_id, 
                CommonMessages.SAVED_DATA, 
                reply_markup=render_main_menu(is_admin=True)
            )

            # Очистка состояния и временных данных
            state.delete()
            temp_data.pop(chat_id, None)
        else:
            bot.send_message(chat_id, EditTaskButtonMessages.INVALID_TEXT)

    # Установка состояния для редактирования МЕДИА задания
    @bot.message_handler(func=lambda m: m.text == EditTaskButtonMessages.MEDIA)
    def edit_task_media(message: Message, state: StateContext):
        chat_id = message.chat.id
        if chat_id not in temp_data or "task_id" not in temp_data[chat_id]:
            bot.send_message(chat_id, EditTaskButtonMessages.TASK_NOT_SET)
            return
            
        state.set(TaskEditState.waiting_for_media)
        bot.send_message(chat_id, EditTaskButtonMessages.EDIT_MEDIA)

    # Сохранение в бд и обработка медиа (фото, стикер, гифка)
    @bot.message_handler(
        state=TaskEditState.waiting_for_media,
        content_types=['photo', 'sticker', 'animation']
    )
    def process_edit_media(message: Message, state: StateContext):
        chat_id = message.chat.id
        task_id = temp_data[chat_id].get("task_id")

        if not task_id:
            bot.send_message(chat_id, EditTaskButtonMessages.TASK_NOT_FOUND)
            state.delete()
            return
        
        # Очистка всех полей для медиа сохранением нового
        edit_task(task_id, "photo", None)
        edit_task(task_id, "sticker", None)
        edit_task(task_id, "animation", None)
        
        # Сохрание новое медиа в соответствующее поле
        if message.photo:
            file_id = message.photo[-1].file_id
            edit_task(task_id, "photo", file_id)
        elif message.sticker:
            file_id = message.sticker.file_id
            edit_task(task_id, "sticker", file_id)
        elif message.animation:
            file_id = message.animation.file_id
            edit_task(task_id, "animation", file_id)
        
        bot.send_message(
            chat_id, 
            CommonMessages.SAVED_DATA, 
            reply_markup=render_main_menu(is_admin=True)    
        )
        
        state.delete()
        temp_data.pop(chat_id, None)

    # Установка состояния для редактирования ЛОКАЦИИ задания
    @bot.message_handler(func=lambda m: m.text == EditTaskButtonMessages.LOCATION)
    def edit_task_location(message: Message, state: StateContext):
        chat_id = message.chat.id
        if chat_id not in temp_data or "task_id" not in temp_data[chat_id]:
            bot.send_message(chat_id, EditTaskButtonMessages.TASK_NOT_SET)
            return
            
        state.set(TaskEditState.waiting_for_location)
        bot.send_message(chat_id, EditTaskButtonMessages.EDIT_LOCATION)

    # Сохранение локации в БД
    @bot.message_handler(state=TaskEditState.waiting_for_location, content_types=['text', 'animation', 'sticker', 'photo', 'video'])
    def process_edit_location(message: Message, state: StateContext):
        chat_id = message.chat.id
        task_id = temp_data[chat_id].get("task_id")

        if not task_id:
            bot.send_message(chat_id, EditTaskButtonMessages.TASK_NOT_FOUND)
            state.delete()
            return
        
        if message.content_type == 'text':
            edit_task(task_id, "location", message.text)
            
            bot.send_message(
                chat_id, 
                CommonMessages.SAVED_DATA, 
                reply_markup=render_main_menu(is_admin=True)
            )
            
            state.delete()
            temp_data.pop(chat_id, None)
        else:
            bot.send_message(chat_id, EditTaskButtonMessages.INVALID_TEXT)

    # Установка состояния для редактирования КОДОВОГО СЛОВА задания
    @bot.message_handler(func=lambda m: m.text == EditTaskButtonMessages.CODE_WORD)
    def edit_task_code_word(message: Message, state: StateContext):
        chat_id = message.chat.id
        if chat_id not in temp_data or "task_id" not in temp_data[chat_id]:
            bot.send_message(chat_id, EditTaskButtonMessages.TASK_NOT_SET)
            return
            
        state.set(TaskEditState.waiting_for_code)
        bot.send_message(chat_id, EditTaskButtonMessages.EDIT_CODE_WORD)

    # Сохранение кодового слова в БД
    @bot.message_handler(state=TaskEditState.waiting_for_code, content_types=['text', 'animation', 'sticker', 'photo', 'video'])
    def process_edit_code_word(message: Message, state: StateContext):
        chat_id = message.chat.id
        task_id = temp_data[chat_id].get("task_id")

        if not task_id:
            bot.send_message(chat_id, EditTaskButtonMessages.TASK_NOT_FOUND)
            state.delete()
            return
        
        if message.content_type == 'text':
            edit_task(task_id, "code_word", message.text)
            
            bot.send_message(
                chat_id, 
                CommonMessages.SAVED_DATA, 
                reply_markup=render_main_menu(is_admin=True)
            )
            
            state.delete()
            temp_data.pop(chat_id, None)
        else:
            bot.send_message(chat_id, EditTaskButtonMessages.INVALID_TEXT)

    # Обработка некорректного ввода для медиа
    @bot.message_handler(state=TaskEditState.waiting_for_media)
    def process_invalid_media(message: Message):
        bot.send_message(message.chat.id, EditTaskButtonMessages.INVALID_MEDIA)

    @bot.message_handler(func=lambda m:m.text == CommonMessages.CANCEL)
    def cancel_task_edit(message: Message, state: StateContext):
        chat_id = message.chat.id
        bot.send_message(
            chat_id,
            CommonMessages.CANCEL_EDIT,
            reply_markup=render_main_menu(is_admin=True)
        )

        state.delete()
        temp_data.pop(chat_id, None)