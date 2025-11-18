from os import getenv
from dotenv import load_dotenv
from collections import defaultdict
import secrets
import string
from telebot import TeleBot
from telebot.states import StatesGroup, State
from telebot.states.sync import StateContext
from telebot.types import Message, CallbackQuery

from buttons import render_team_buttons, render_cancel_button, render_main_menu, render_team_edit_buttons
from checks import check_admin
from database.dao import add_team, get_teams, update_team, get_team_by_id, get_team_by_name, edit_team, get_all_teams
from database.models import Team
from msg_locale import TeamMessages, CommonMessages, ButtonMessages, EditTeamButtonMessages



load_dotenv()


bot_username = getenv('BOT_USERNAME')


class TeamCreateState(StatesGroup):
    name = State()
    desc = State()
    welcome = State()
    final = State()
    code = State()

class TeamEditState(StatesGroup):
    name = State()
    desccription = State()
    welcome = State()
    final = State()
    codeword = State()
    
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

    def generate_invite_token(length: int):
        alphabet = string.ascii_letters + string.digits
        return str(''.join(secrets.choice(alphabet) for _ in range(length)))
    
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
                team.invite_token = generate_invite_token(8)
                add_team(team)
        escaped_username = bot_username.replace('_', r'\_')[1:]
        team_link = f"https://t.me/{escaped_username}?start={team.invite_token}"
        bot.reply_to(
            message,
            TeamMessages.TEAM_CREATED.format(
                team_name=team.team_name,
                id=team.id
            )+"\n"+TeamMessages.TEAM_LINK.format(
                team_link=team_link
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

            markup = render_team_buttons(teams, 'list_team', 'cancel_list_team')
            bot.reply_to(message, msg, reply_markup = markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("list_team_"))
    def process_team_list(call: CallbackQuery):
        team_id = int(call.data.split('_')[-1])

        team = get_team_by_id(team_id)
        # Генерация токена для команд у которых его нет
        if team.invite_token is None:
            invite_token = generate_invite_token(8)
            edit_team(team_id, 'invite_token', invite_token)


        current_task = (team.current_chain_order + 1) if list(
            filter(lambda x: x.order == team.current_chain_order,
                   team.chains)) else TeamMessages.TEAM_TASKS_COMPLETED
        
        escaped_username = bot_username.replace('_', r'\_')[1:]
        team_link = f"https://t.me/{escaped_username}?start={invite_token}"
        msg = TeamMessages.TEAM_ITEM_TEMPLATE.format(
            id=team.id,
            team_name=team.team_name,
            description=team.description,
            welcome=team.welcome_message or CommonMessages.NO,
            final=team.final_message or CommonMessages.NO,
            current_task=current_task,
            code=team.code_word,
            link = team_link
        )
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        bot.edit_message_text(msg, chat_id, message_id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_list_team"))
    def cancel_team_list(call: CallbackQuery):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        bot.edit_message_text(CommonMessages.CANCEL_ACTION, chat_id, message_id)


# --------- Редактирование команды ---------
def register_team_edit_commands(bot: TeleBot):
    temp_data = defaultdict(dict)


    @bot.message_handler(func=lambda m: m.text == ButtonMessages.EDIT_TEAM)
    def update_team_info(message: Message, state: StateContext):

        is_admin = check_admin(bot, message)
        if not is_admin:
            return
        teams = get_teams()
        if not teams:
            bot.reply_to(message, TeamMessages.NO_TEAMS)
            return

        markup = render_team_buttons(
            teams,
            callback_finish='edit_team',
            callback_cancel='cancel_team_edit'
        )
        bot.send_message(message.chat.id, TeamMessages.EDIT_TEAM_SELECT, reply_markup=markup)

    # Отмена выбора
    @bot.message_handler(func=lambda m: m.text == CommonMessages.CANCEL)
    def cancel_edit_team(message: Message):
        chat_id = message.chat.id
        bot.delete_message(chat_id, message.message_id)
        bot.send_message(
            chat_id, CommonMessages.CANCEL_ACTION,
            reply_markup=render_main_menu(is_admin=True)
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('edit_team_'))
    def process_team_selection(call: CallbackQuery, state: StateContext):
        chat_id = call.message.chat.id
        team_id = int(call.data.split('_')[-1])

        team = get_team_by_id(team_id)
        if not team:
            bot.answer_callback_query(call.id, "Команда не найдена")
            return
        
        temp_data[chat_id]["team_id"] = team_id
        temp_data[chat_id]["state"] = None

        bot.delete_message(chat_id, call.message.message_id)
        bot.send_message(
            chat_id=call.message.chat.id,
            text=EditTeamButtonMessages.CHOOSE_PROPERTY.format(team_name=team.team_name),
            reply_markup=render_team_edit_buttons(team_id),
            parse_mode=""
        )

       
# ============ Блок обработчиков изменения атрибутов команды ============

    # Кнопка ввода нового названия команды
    @bot.message_handler(func=lambda m: m.text == EditTeamButtonMessages.NAME)
    def edit_team_name(message: Message):
        chat_id = message.chat.id
        temp_data[chat_id]['state'] = 'name'
        bot.send_message(
            message.chat.id,
            EditTeamButtonMessages.EDIT_NAME
        )

    # Кнопка ввода нового описания команды
    @bot.message_handler(func=lambda m: m.text == EditTeamButtonMessages.DESCRIPTION)
    def edit_team_description(message: Message):
        chat_id = message.chat.id
        temp_data[chat_id]['state'] = 'description'
        bot.send_message(
            message.chat.id,
            EditTeamButtonMessages.EDIT_DESCRIPTION
        )

    # Кнопка ввода нового (Welcome)Приветственного сообщения команды
    @bot.message_handler(func=lambda m: m.text == EditTeamButtonMessages.WELCOOME)
    def edit_team_welcome(message: Message):
        chat_id = message.chat.id
        temp_data[chat_id]['state'] = "welcome"
        bot.send_message(
            message.chat.id,
            EditTeamButtonMessages.EDIT_WELCOME
        )

    # Кнопка ввода нового (Final)Финального сообщения команды
    @bot.message_handler(func=lambda m: m.text == EditTeamButtonMessages.FINAL)
    def edit_team_final(message: Message):
        chat_id = message.chat.id
        temp_data[chat_id]['state'] = 'final'
        bot.send_message(
            message.chat.id,
            EditTeamButtonMessages.EDIT_FINAL
        )

    # Кнопка ввода нового кодового слова команды
    @bot.message_handler(func=lambda m: m.text == EditTeamButtonMessages.CODE_WORD)
    def edit_team_codeword(message: Message):
        chat_id = message.chat.id
        temp_data[chat_id]['state'] = 'code_word'
        bot.send_message(
            message.chat.id,
            EditTeamButtonMessages.EDIT_CODEWORD
        )


    @bot.message_handler(func=lambda m: True)
    def process_edit(message: Message):
        chat_id = message.chat.id
        
        state = temp_data[chat_id].get("state")
        if not state:
            return

        team_id = temp_data[chat_id].get("team_id")
        new_value = message.text
        if not team_id:
            bot.send_message(chat_id, "Ошибка: команда не выбрана.")
            temp_data.pop(chat_id, None)
            return

        # обновление в зависимости от состояния
        if state == "name":
            edit_team(team_id, "team_name", new_value)

        elif state == "description":
            edit_team(team_id, "description", new_value)

        elif state == "welcome":
            edit_team(team_id, "welcome_message", new_value)

        elif state == "final":
            edit_team(team_id, "final_message", new_value)

        elif state == "code_word":
            edit_team(team_id, "code_word", new_value)

        bot.send_message(chat_id, "Изменение сохранено.", reply_markup=render_team_edit_buttons(team_id))

        # Очистка состояния
        # temp_data.pop(chat_id, None)