import string
from os import getenv
from dotenv import load_dotenv
from collections import defaultdict
from telebot import TeleBot
from telebot import TeleBot
from telebot.types import Message
from telebot.states import StatesGroup, State
from telebot.states.sync import StateContext

load_dotenv()

from database.dao import get_member, get_team_by_code, update_team, get_current_chain, get_team_by_id, join_team_via_code, get_user_ids_by_team, join_team_via_invite_token
from database.models import Team, Task

from msg_locale import QuestMessages, ButtonMessages, CommonMessages

from buttons import render_cancel_button, render_main_menu

from checks import check_admin



bot_username = getenv('BOT_USERNAME')


class TaskCodeState(StatesGroup):
    waiting_for_task_code = State()

class TeamCodeState(StatesGroup):
    waiting_for_team_code = State()

def register_quest_commands(bot: TeleBot):
    temp_data = defaultdict(dict)

    # Проверяет валидный ли токен (8 латинских букв/цифр)
    def is_valid_invite_token(s: str) -> bool:
        return len(s) == 8 and all(c in set(string.ascii_letters+string.digits) for c in s)
    

    def extract_invite_token_from_text(text: str) -> str | None:
        stripped = text.strip()
        print(f'stripped: {stripped}')

        # invite_token
        if is_valid_invite_token(stripped):
            print(f'just a token: {stripped}')
            return stripped

        # /start <invite_token>
        if stripped.startswith("/start "):
            print(f'/start <invite_token>: {stripped}')
            candidate = stripped[7:].strip()  # 7 = len("/start ")
            print(f'candidate: {candidate}')
            if is_valid_invite_token(candidate):
                return candidate

        #?start=
        if "?start=" in stripped:
            print(f'?start')
           
            start_pos = stripped.find("?start=") + 7  
            token_part = stripped[start_pos:]
            print(f'token part: {token_part}')

            clean_token = ""
            for char in token_part:
                if char in set(string.ascii_letters+string.digits):
                    clean_token += char
                else:
                    break  

            if is_valid_invite_token(clean_token):
                print(f'clean token: {clean_token}')
                return clean_token

        return None
    
    # Присоединение к команде
    @bot.message_handler(func=lambda m: m.text == ButtonMessages.JOIN_TEAM)
    def join_team(message: Message, state = StateContext):
        chat_id = message.chat.id


        member = get_member(message.from_user.id)
        if member:
            team = get_team_by_id(team_id=member.team_id)
            bot.reply_to(
                message, 
                QuestMessages.ALREADY_IN_TEAM.format(
                    team_name=team.team_name
                ),
                reply_markup = render_main_menu(
                    is_admin=check_admin(bot, message, silent=True),
                    is_in_team=True
                )
            )
            return
        

        state.set(TeamCodeState.waiting_for_team_code)
        bot.reply_to(message, QuestMessages.ENTER_CODE_WORD, reply_markup = render_cancel_button())

    @bot.message_handler(state=TeamCodeState.waiting_for_team_code)
    def process_team_join(message: Message, state: StateContext):
        print('Full join team text: ', message.text)
        user_id = message.from_user.id
        chat_id = message.chat.id
        text = message.text


        is_admin = check_admin(bot, message, silent=True)

        invite_token = extract_invite_token_from_text(text)
        print(f'Invite token join team: {invite_token}')

        if invite_token:
            team = join_team_via_invite_token(invite_token, user_id)
            
            if team: 
                bot.send_message(
                    chat_id,
                    QuestMessages.JOINED_TO_TEAM.format(
                        team_name=team.team_name
                    ),
                    reply_markup=render_main_menu(is_admin, is_in_team=True)
                )

                state.delete()

                # Отправка первого задания
                current_chain = preprocess_task(message)
                if not current_chain:
                    return
                send_task(message.chat.id, current_chain.task)
                return
            else:
                bot.reply_to(message, QuestMessages.TEAM_NOT_FOUND)
                return
            

        code_word = text.strip()
        team = get_team_by_code(code_word)
        if not team:
            bot.reply_to(
                message, 
                QuestMessages.TEAM_NOT_FOUND, 
                reply_markup = render_main_menu(
                    is_admin=check_admin(bot, message, silent=True),
                    is_in_team=True
                )
            )

        else:
            join_team_via_code(code_word, user_id=message.from_user.id)
            bot.reply_to(
                message, team.welcome_message, 
                reply_markup = render_main_menu(
                    is_admin=check_admin(bot, message, silent=True),
                    is_in_team=True
                )
            )
        state.delete()


        # Отправка первого задания
        current_chain = preprocess_task(message)
        if not current_chain:
            return
        send_task(message.chat.id, current_chain.task)

    def preprocess_task(message: Message):
        member = get_member(message.from_user.id)
        team = get_team_by_id(member.team_id)

        current_chain = get_current_chain(team.id, team.current_chain_order)
        if current_chain:
            if team.current_chain_order == 0:
                task_assist_message = QuestMessages.FIRST_TASK_MESSAGE
            else:
                task_assist_message = QuestMessages.CURRENT_TASK_MESSAGE
            bot.send_message(message.chat.id, task_assist_message)
        else:
            print('current chain is false')
            bot.send_message(message.chat.id, QuestMessages.NO_ACTIVE_TASKS, reply_markup = render_main_menu(check_admin(bot, message, silent=True), is_in_team=True))
        return current_chain
    
    # Отправка задания пользователю
    def send_task(chat_id: int, task: Task):
        bot.send_message(chat_id, QuestMessages.TASK_TEMPLATE.format(
            task_name=task.task_name,
            description=task.description
        ))
        if task.photo:
            bot.send_photo(chat_id, task.photo)
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
        member = get_member(message.from_user.id)
        if not member:
            bot.reply_to(message, QuestMessages.NOT_IN_TEAM, reply_markup = render_main_menu(check_admin(bot, message, silent=True)))
            return
        current_chain = preprocess_task(message)
        if not current_chain:
            return
        send_task(message.chat.id, current_chain.task)

    # Обработка перехода к следующему заданию
    @bot.message_handler(func=lambda m: m.text == ButtonMessages.NEXT_TASK)
    def next_task(message: Message, state: StateContext):
        chat_id = message.chat.id
        user_id = message.from_user.id


        member = get_member(user_id)
        if not member:
            bot.reply_to(message, QuestMessages.NOT_IN_TEAM)
            return
        
        
        team = get_team_by_id(member.team_id)
        current_chain = get_current_chain(team.id, team.current_chain_order)


        if not current_chain:
            print('not_current_chain')
            bot.reply_to(message, QuestMessages.NO_ACTIVE_TASKS, )
            return
        
        state.set(TaskCodeState.waiting_for_task_code)


        temp_data[chat_id]["team_id"] = team.id
        temp_data[chat_id]["chain_order"] = current_chain.order


        bot.reply_to(
            message, QuestMessages.ENTER_TASK_CODE,
            reply_markup=render_cancel_button()
        )


    # Обработка ввода кодового слова
    @bot.message_handler(state=TaskCodeState.waiting_for_task_code)
    def process_next_task(message: Message, state: StateContext):
        chat_id = message.chat.id
        
        team_id = temp_data[chat_id].get("team_id")
        chain_order = temp_data[chat_id].get("chain_order")


        team = get_team_by_id(team_id)
        current_chain = get_current_chain(team_id, chain_order)

        if not team or not current_chain:
            bot.reply_to(message, QuestMessages.TEAM_NOT_FOUND)
            state.delete()
            return
        
        ok = check_task_code(message, team, current_chain.task)
        

        if not ok:
            return
        
        temp_data.pop(chat_id, None)
        state.delete()
        

    def check_task_code(message: Message, team: Team, current_team_task: Task):
        if current_team_task.code_word.lower() not in message.text.lower():
            bot.reply_to(message, QuestMessages.WRONG_TASK_CODE)
            return False

        who_solved = message.from_user.id
        next_order = team.current_chain_order + 1
        update_team(team_id=team.id, current_chain_order=next_order)


        all_members = get_user_ids_by_team(team.id)
        next_chain = get_current_chain(team.id, next_order)


        if not next_chain:
            for user_id in all_members:
                try:
                    bot.send_message(
                        user_id, 
                        team.final_message or QuestMessages.QUEST_COMPLETED,
                        reply_markup=render_main_menu(check_admin(bot, message, silent=True), is_in_team=True)
                    )
                except Exception as e:
                    print(f"Не удалось отправить финальное сообщение пользователю {user_id}: {e}")    
            return True
            
        task = next_chain.task
        bot.reply_to(
            message,
            QuestMessages.TEAM_NEXT_TASK_MESSAGE, 
            reply_markup=render_main_menu(check_admin(bot, message, silent=True), is_in_team=True)
        )
        send_task(who_solved, task)

        for user_id in all_members:
            try:
                if user_id != who_solved:
                    bot.send_message(user_id, QuestMessages.TEAM_ADVANCED_MESSAGE)
                    send_task(user_id, task)
            except Exception as e:
                print(f"Не удалось отправить задание пользователю {user_id}: {e}")
        return True