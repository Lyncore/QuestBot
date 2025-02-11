# описание команд
class CommandDescription:
    user_commands = {
        'start': 'Запуск бота',
        'help': 'Помощь',
        'join': 'Присоединиться к команде',
        'task': 'Текущее задание',
        'next': 'Следующее задание',
    }
    admin_commands = {
        'createteam': 'Создать команду',
        'listteam': 'Список команд',
        'createtask': 'Создать задание',
        'listtask': 'Список заданий',
        'assigntask': 'Привязка заданий',
        'resetleader': 'Сброс лидера команды',
        'resettask': 'Сброс прогресса команды',
    }

# Общее
class CommonMessages:
    CANCEL = "❌ Отмена"
    SELECT_CANCEL = "❌ Выбор отменен"
    SELECT_FINISH = "✅ Завершить выбор"
    NO = "Нет"
    YES = "Есть"
    ERROR_TEMPLATE = "❌ Ошибка: {error}"
    WELCOME_MESSAGE = "Добро пожаловать!"
    COMMON_MESSAGE = "Похоже, вы заблудились :("


# Авторизация
class AuthMessages:
    NOT_ADMIN = "❌ Вы не администратор!"
    ALREADY_ADMIN = "❌ Вы уже администратор!"
    ENTER_OTP = "🔑 Введите код из приложения:"
    BECOME_ADMIN = "✅ Вы стали администратором!"
    INVALID_OTP = "❌ Неверный код!"


# Прохождение квеста
class QuestMessages:
    ALREADY_IN_TEAM = '🤩 Вы уже присоединились к команде "{team_name}". Используйте /task для получения текущего задания'
    ENTER_CODE_WORD = "✍️ Введите кодовое слово:"
    TEAM_NOT_FOUND = "❌ Команда не найдена!"
    ALREADY_HAS_LEADER = "❌ У вас уже есть лидер!"
    BECOME_LEADER_DEFAULT = "✅ Вы стали лидером команды!"
    NOT_LEADER = "❌ Вы не лидер команды!"
    NO_ACTIVE_TASKS = "🥲 Нет активных заданий."
    FIRST_TASK_MESSAGE = "🥹 Вот ваше первое задание:"
    CURRENT_TASK_MESSAGE = "🥹 Вот ваше текущее задание:"
    NEXT_TASK_MESSAGE = "🥹 Вот ваше следующее задание:"
    TASK_TEMPLATE = "*{task_name}*\n{description}"
    LOCATION_TEMPLATE = "📍 Локация: {location}"
    ENTER_TASK_CODE = "🔢 Введите кодовое слово текущего задания:"
    WRONG_TASK_CODE = "❌ Неверное кодовое слово!"
    QUEST_COMPLETED = "🎉 Квест пройден!"


# Настройка заданий
class TaskMessages:
    ENTER_TASK_NAME = "📝 Введите название задания:"
    ENTER_DESCRIPTION = "📝 Введите описание задания:"
    ENTER_MEDIA = "🖼 Отправьте фото, GIF или стикер (или /skip):"
    ENTER_LOCATION = "🏠 Введите место прохождения задания:"
    ENTER_CODE_WORD = "🔑 Введите кодовое слово для задания:"
    TASK_CREATED = "✅ Задание создано!"
    LIST_TASKS_HEADER = "Список заданий:\n"
    TASK_ITEM_TEMPLATE = """
*Задание #{id}:* {task_name}
🖼Описание: {description}
📸Фото: {photo}
🫡Стикер: {sticker}
🎁Гифка: {animation}
🏠Локация: {location}
🔑Кодовое слово: {code_word}\n"""
    NO_TASKS = "Вы еще не добавили задания. Используйте /createtask 🥺"
    ASSIGNED_TEAMS_HEADER = "Задание присвоено командам:\n"
    ASSIGNED_TEAMS_TEMPLATE = """
*Команда «{team_name}»*
Задание #{task_chain_order}\n"""
    TASK_ASSIGN_SELECT_TEAM = "🏁 Выберите команду для привязки заданий:"
    TASK_ASSIGN_SELECT_TASK = "📝 Выберите задания для команды (множественный выбор):"
    TASK_ASSIGN_EMPTY = "❌ Не выбрано ни одного задания!"
    TASK_ASSIGNMENT_REPORT = """✅ Задания успешно привязаны к команде «{team_name}»!
Кодовое слово: {code_word}
Количество заданий: {count}
Список заданий:
{task_list}"""


# Настройка команд
class TeamMessages:
    ENTER_TEAM_NAME = "👀 Введите название команды:"
    ENTER_DESCRIPTION = "🙏 Введите описание команды (или /skip):"
    ENTER_WELCOME = "👋 Введите приветственное сообщение (или /skip):"
    ENTER_FINAL = "👋 Введите финальное сообщение (или /skip):"
    ENTER_CODE = "🏷 Введите кодовое слово:"
    TEAM_CREATED = "✅ Команда «{team_name}» создана! ID: {id}"
    LIST_TEAMS_HEADER = "Список команд:\n"
    NO_TEAMS = "Вы еще не добавили команды. Используйте /createteam 🥺"
    TEAM_ITEM_TEMPLATE = """
*Команда #{id}*
👀 Название: {team_name}
🙏 Описание: {description}
👋 Приветствие: {welcome}
👋 Финал: {final}
📝 Текущее задание: {current_task}
🏷 Код: {code}\n"""
    TEAM_TASKS_COMPLETED = "Все задания пройдены"
    RESET_LEADER_SELECT = "🏁 Выберите команду для сброса лидера"
    RESET_TASK_SELECT = "🏁 Выберите команду для сброса прогресса:"
    RESET_LEADER_SUCCESS = "😱 Лидер команды «{team_name}» сброшен."
    RESET_TASK_SUCCESS = "😱 Прогресс команды «{team_name}» сброшен."


#
class ButtonMessages:
    TEAM_BUTTON = 'Команда "{name}" (код: {code})'
    TASK_BUTTON = "{name}..."
