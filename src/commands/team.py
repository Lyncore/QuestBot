from sqlalchemy.orm import Session
from telebot import TeleBot
from telebot.types import Message

from checks import check_admin
from models import Team


def register_team_setting_commands(bot: TeleBot, session: Session):
    # Создание команды (только для админов)
    @bot.message_handler(commands=['createteam'])
    def create_team(message: Message):
        if not check_admin(bot, message, session):
            return
        msg = bot.reply_to(message, '👀 Введите название команды:')
        bot.register_next_step_handler(msg, process_team_name)

    def process_team_name(message: Message):
        team = Team(team_name=message.text)
        msg = bot.reply_to(message, '🙏Введите описание команды (или /skip)')
        bot.register_next_step_handler(msg, process_team_description, team)

    def process_team_description(message: Message, team: Team):
        if not message.text.startswith('/skip'):
            team.description = message.text
        msg = bot.reply_to(message, '👋 Введите приветственное сообщение для команды (или /skip):')
        bot.register_next_step_handler(msg, process_team_welcome, team)

    def process_team_welcome(message: Message, team: Team):
        if not message.text.startswith('/skip'):
            team.welcome_message = message.text
        msg = bot.reply_to(message, '👋 Введите финальное сообщение для команды (или /skip):')
        bot.register_next_step_handler(msg, process_team_final, team)

    def process_team_final(message: Message, team: Team):
        if not message.text.startswith('/skip'):
            team.final_message = message.text
        msg = bot.reply_to(message, '🏷 Введите кодовое слово для команды:')
        bot.register_next_step_handler(msg, process_team_code, team)

    def process_team_code(message: Message, team: Team):
        team.code_word = message.text
        session.add(team)
        session.commit()
        bot.reply_to(message, f'✅ Команда \"{team.team_name}\" создана! ID: {team.id}')

    @bot.message_handler(commands=['listteam'])
    def list_team(message: Message):
        if not check_admin(bot, message, session):
            return
        teams = session.query(Team).all()
        if len(teams) == 0:
            bot.reply_to(message, 'Вы еще не добавили команды. Используйте /createteam 🥺')
        else:
            msg = "Список команд:\n"

            for team in teams:
                current_task = (team.current_chain_order + 1) if list(
                    filter(lambda x: x.order == team.current_chain_order,
                           team.chains)) else 'Все задания пройдены'
                msg += \
                    f'''
*Команда #{team.id}*
👀Название: {team.team_name}
🙏Описание: {team.description or "Нет"}
👋Приветственное сообщение: {team.welcome_message or "Нет"}
👋Финальное сообщение: {team.final_message or "Нет"}
📝Текущий номер задания: {current_task}
🏷Кодовое слово: {team.code_word}
\n
'''
            bot.reply_to(message, msg)
