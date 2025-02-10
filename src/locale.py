class Localization:
    # Authentication Messages
    ALREADY_ADMIN = '❌ Вы уже администратор!'
    OTP_PROMPT = '🔑 Введите код из приложения:'
    ADMIN_SUCCESS = '✅ Вы стали администратором!'
    INVALID_OTP = '❌ Неверный код!'

    # Team Join Messages
    ALREADY_IN_TEAM = '🤩 Вы уже присоединились к команде "{team_name}. Используйте /task для получения текущего задания'
    CODE_WORD_PROMPT = '✍️ Введите кодовое слово:'
    TEAM_NOT_FOUND = '❌ Команда не найдена!'
    TEAM_HAS_LEADER = '❌ У вас уже есть лидер!'
    WELCOME_DEFAULT = '✅ Вы стали лидером команды!'
    NOT_TEAM_LEADER = '❌ Вы не лидер команды!'
    NO_ACTIVE_TASKS = '🥲 Нет активных заданий.'
    FIRST_TASK_PROMPT = '🥹 Вот ваше первое задание:'
    CURRENT_TASK_PROMPT = '🥹 Вот ваше текущее задание:'

    # Task Progression Messages
    TASK_CODE_PROMPT = '🔢 Введите кодовое слово текущего задания:'
    INVALID_TASK_CODE = '❌ Неверное кодовое слово!'
    NEXT_TASK_PROMPT = '🥹 Вот ваше следующее задание:'
    QUEST_COMPLETED = '🎉 Квест пройден!'

    # Task Creation Messages
    TASK_NAME_PROMPT = '📝 Введите название задания:'
    TASK_DESCRIPTION_PROMPT = '📝 Введите описание задания:'
    TASK_MEDIA_PROMPT = '🖼 Отправьте фото, GIF или стикер (или /skip):'
    TASK_LOCATION_PROMPT = '🏠 Введите место прохождения задания:'
    TASK_CODE_WORD_PROMPT = '🔑 Введите кодовое слово для задания:'
    TASK_CREATED = '✅ Задание создано!'
    NO_TASKS_ADDED = 'Вы еще не добавили задания. Используйте /createtask 🥺'

    # Task List Messages
    TASK_LIST_HEADER = 'Список заданий:\n'
    TASK_LIST_ITEM = '''
*Задание #{task_id}:* {task_name}
🖼Описание: {description}
📸Фото: {photo_status}
🫡Стикер: {sticker_status}
🎁Гифка: {animation_status}
🏠Локация: {location}
🔑Кодовое слово: {code_word}
'''
    TASK_ASSIGNED_TEAMS = 'Задание присвоено командам:\n'
    TEAM_ASSIGNED_TASK = '*Команда "{team_name}"*\nЗадание #{order}\n'

    # Team Creation Messages
    TEAM_NAME_PROMPT = '👀 Введите название команды:'
    TEAM_DESCRIPTION_PROMPT = '🙏Введите описание команды (или /skip)'
    TEAM_WELCOME_PROMPT = '👋 Введите приветственное сообщение для команды (или /skip):'
    TEAM_FINAL_PROMPT = '👋 Введите финальное сообщение для команды (или /skip):'
    TEAM_CODE_PROMPT = '🏷 Введите кодовое слово для команды:'
    TEAM_CREATED = '✅ Команда "{team_name}" создана! ID: {team_id}'
    NO_TEAMS_ADDED = 'Вы еще не добавили команды. Используйте /createteam 🥺'

    # Team List Messages
    TEAM_LIST_ITEM = '''
*Команда #{team_id}*
👀Название: {team_name}
🙏Описание: {description}
👋Приветственное сообщение: {welcome_message}
👋Финальное сообщение: {final_message}
📝Текущий номер задания: {current_task}
🏷Кодовое слово: {code_word}
'''

    # Team Reset Messages
    TEAM_RESET_PROMPT = '🏁 Выберите команду для сброса прогресса:'
    LEADER_RESET = '😱 Лидер команды "{team_name}" сброшен.'
    TASK_RESET = '😱 Прогресс команды "{team_name}" сброшен.'
    RESET_CANCELED = '❌ Выбор отменен'

    # Admin Check Messages
    NOT_ADMIN = '❌ Вы не администратор!!'

    # Task Assignment Messages
    TASK_ASSIGNMENT_TEAM_PROMPT = '🏁 Выберите команду для привязки заданий:'
    TASK_SELECTION_PROMPT = '📝 Выберите задания для команды (множественный выбор):'
    NO_TASKS_SELECTED = '❌ Не выбрано ни одного задания!'
    TASK_ASSIGNMENT_SUCCESS = '''
✅ Задания успешно привязаны к команде #{team_id}!

Кодовое слово команды: {code_word}
Количество заданий: {task_count}

Список заданий:
{task_list}
'''
    ASSIGNMENT_ERROR = '❌ Ошибка: {error}'


def get_text(key, **kwargs):
    """
    Retrieve localized text with optional formatting

    :param key: Key from Localization class
    :param kwargs: Formatting arguments
    :return: Formatted localized text
    """
    text = getattr(Localization, key, key)
    return text.format(**kwargs) if kwargs else text