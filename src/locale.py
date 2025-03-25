# описание команд
class CommandDescription:
    user_commands = {
        'start': '▶️ Запуск бота'
    }
    admin_commands = {}


# Общее
class CommonMessages:
    CANCEL = "❌ Отмена"
    CANCEL_CREATION = "❌ Создание отменено"
    CANCEL_EDIT = "❌ Редактирование отменено"
    CANCEL_ACTION = "❌ Действие отменено"
    SELECT_FINISH = "✅ Завершить выбор"
    SKIP = "▶️Пропустить"
    NO = "Нет"
    YES = "Есть"
    ERROR_TEMPLATE = "❌ Ошибка: {error}"
    WELCOME_MESSAGE = '''
Мяу-привет! 🐾 Я Пиксель, и мне срочно нужна твоя помощь! 🙀

Дело в том, что я хотел бы разобраться кто работает в IT. Тут столько разных направлений – веб-разработка, анализ данных, кибербезопасность...  Мои лапки и усы в замешательстве! 🤯

Может, ты поможешь мне разобраться,  какие IT-профессии бывают и какие из них подошли бы такому умному и пушистому коту, как я?  😼 чтобы стать самым крутым IT-котиком! 🚀

Вместе мы точно найдем идеальную IT-специальность для кота, такого как я!  Мурр-р-р-р и жду помощи! 🙏

Твой друг и будущий IT-котик,
Пиксель. 💻🐈

А теперь выбери "Присоединиться к команде" для начала IT приключений!🙀'''
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
    ALREADY_IN_TEAM = '🤩 Вы уже присоединились к команде "{team_name}". Используйте кнопку "Текущее задание" для получения текущего задания'
    ENTER_CODE_WORD = '''
Пу пу пу

Все не так просто😉
У каждой команды есть свой секретный код👀

Введи свой код...💻🐾'''
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
    ENTER_MEDIA = "🖼 Отправьте фото, GIF или стикер:"
    ENTER_LOCATION = "🏠 Введите место прохождения задания:"
    ENTER_CODE_WORD = "🔑 Введите кодовое слово для задания:"
    TASK_CREATED = "✅ Задание создано!"
    EDIT_TASK_SELECT = "🏁 Выберите задание для редактирования:"
    EDIT_NAME = "📝 Введите новое название задания:"
    EDIT_DESCRIPTION = "📝 Введите новое описание:"
    EDIT_MEDIA = "🖼 Отправьте новое фото/GIF/стикер:"
    EDIT_LOCATION = "🏠 Введите новую локацию:"
    EDIT_CODE = "🔑 Введите новое кодовое слово:"
    TASK_UPDATED = "✅ Задание успешно обновлено!"
    LIST_TASKS_HEADER = "Список заданий:\n"
    TASK_ITEM_TEMPLATE = """
*Задание #{id}:* {task_name}
🖼Описание: {description}
📸Фото: {photo}
🫡Стикер: {sticker}
🎁Гифка: {animation}
🏠Локация: {location}
🔑Кодовое слово: {code_word}\n"""
    NO_TASKS = "Вы еще не добавили задания."
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
    TEAM_NAME_EXISTS = "❌ Команда с таким названием уже есть."
    TEAM_CREATED = "✅ Команда «{team_name}» создана! ID: {id}"
    EDIT_TEAM_SELECT = "🏁 Выберите команду для редактирования:"
    EDIT_NAME = "📝 Введите новое название команды (или /cancel):"
    EDIT_DESCRIPTION = "📝 Введите новое описание команды (или /skip /cancel):"
    EDIT_WELCOME = "👋 Введите новое приветственное сообщение (или /skip /cancel):"
    EDIT_FINAL = "👋 Введите новое финальное сообщение (или /skip /cancel):"
    EDIT_CODE = "🏷 Введите новый кодовое слово (или /cancel):"
    TEAM_UPDATED = "✅ Команда успешно обновлена!"
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
    RESET_LEADER_EMPTY = "😱 Пока нету команд с лидером("
    RESET_LEADER_SUCCESS = "😱 Лидер команды «{team_name}» сброшен."
    RESET_TASK_SELECT = "🏁 Выберите команду для сброса прогресса:"
    RESET_TASK_EMPTY = "😱 Ни одна команда еще не начала квест"
    RESET_TASK_SUCCESS = "😱 Прогресс команды «{team_name}» сброшен."


#
class ButtonMessages:
    TEAM_BUTTON = 'Команда "{name}" (код: {code})'
    TASK_BUTTON = "{name}..."
    CREATE_TEAM = '➕Создать команду'
    EDIT_TEAM = '✏️ Редактировать команду'
    LIST_TEAM = '📋 Просмотр команд'
    CREATE_TASK = '➕ Создать задание'
    EDIT_TASK = '✏️ Редактировать задание'
    LIST_TASK = '📋 Просмотр заданий'
    ASSIGN_TASK = '🔗 Привязка заданий'
    RESET_LEADER = '🔄 Сброс лидера'
    RESET_TASK = '🔄 Сброс прогресса'
    HELP = '❓ Помощь'
    JOIN_TEAM = '🏁 Присоединиться к команде'
    CURRENT_TASK = '📋 Текущее задание'
    NEXT_TASK = '⏩ Следующее задание'
