from typing import Type

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

from database.models import Task, Team
from msg_locale import CommonMessages, ButtonMessages, EditTeamButtonMessages, EditTaskButtonMessages


def render_main_menu(is_admin: bool = False):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if is_admin:
        markup.add(
            ButtonMessages.CREATE_TEAM,
            ButtonMessages.CREATE_TASK,
            ButtonMessages.EDIT_TEAM,
            ButtonMessages.EDIT_TASK,
            ButtonMessages.LIST_TEAM,
            ButtonMessages.LIST_TASK,

        )
        markup.add(
            ButtonMessages.ASSIGN_TASK,
            ButtonMessages.RESET_LEADER,
            ButtonMessages.RESET_TASK,
            row_width=1
        )
    else:
        markup.add(
            ButtonMessages.JOIN_TEAM,
            ButtonMessages.CURRENT_TASK,
            ButtonMessages.NEXT_TASK,
            ButtonMessages.HELP
        )
    return markup


def render_cancel_button(add_skip: bool = False, inline: bool = False):
    
    if inline:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(CommonMessages.CANCEL, callback_data="cancel"))

        return markup

    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(CommonMessages.CANCEL)
        if add_skip:
            markup.add(CommonMessages.SKIP)
        return markup


def render_team_buttons(
        teams: list[Type[Team]],
        callback_finish: str,
        callback_cancel: str,
        page: int = 0,
        total_pages: int = 0,
        total_teams: int = 0
):
    markup = InlineKeyboardMarkup(row_width=1)
    for team in teams:
        markup.add(InlineKeyboardButton(
            text=ButtonMessages.TEAM_BUTTON.format(
                name=team.team_name,
                code=team.code_word
            ),
            callback_data=f'{callback_finish}_{team.id}'
        ))
    markup.add(InlineKeyboardButton(CommonMessages.CANCEL, callback_data=callback_cancel))
    return markup

# reply клавиатура для выбора атрибутов команды которые вы хотите изменить
def render_team_edit_buttons(team_id: int):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        EditTeamButtonMessages.NAME,
        EditTeamButtonMessages.DESCRIPTION
    )
    markup.add(
        EditTeamButtonMessages.WELCOOME,
        EditTeamButtonMessages.FINAL
    )
    markup.add(
        EditTeamButtonMessages.CODE_WORD,
        CommonMessages.CANCEL
    )

    return markup

def render_task_buttons(
        tasks: list[Type[Task]],
        callback_finish: str,
        callback_cancel: str
):
    markup = InlineKeyboardMarkup(row_width=1)
    for task in tasks:
        markup.add(InlineKeyboardButton(
            text=ButtonMessages.TASK_BUTTON.format(
                name=task.task_name[:20]
            ),
            callback_data=f'{callback_finish}_{task.id}'
        ))
    markup.add(InlineKeyboardButton(CommonMessages.CANCEL, callback_data=callback_cancel))
    return markup

def render_task_edit_buttons(task_id: int):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        EditTaskButtonMessages.NAME,
        EditTaskButtonMessages.DESCRIPTION
    )
    markup.add(
        EditTaskButtonMessages.PHOTO,
        EditTaskButtonMessages.STICKER
    )
    markup.add(
        EditTaskButtonMessages.STICKER,
        EditTaskButtonMessages.ANIMATION
    )
    markup.add(
        EditTaskButtonMessages.CODE_WORD,
        CommonMessages.CANCEL
    )

    return markup

def render_task_assign_buttons(
        tasks: list[Type[Task]],
        selected_tasks: list[int],
        callback_select: str,
        callback_finish: str,
        callback_cancel: str
):
    markup = InlineKeyboardMarkup(row_width=1)
    for task in tasks:
        btn_text = ButtonMessages.TASK_BUTTON.format(
            name=task.task_name[:20]
        )
        if task.id in selected_tasks:
            index = selected_tasks.index(task.id)
            btn_text += f' (#{index + 1})'
        markup.add(InlineKeyboardButton(
            text=btn_text,
            callback_data=f'{callback_select}_{task.id}'
        ))
    markup.row(
        InlineKeyboardButton(CommonMessages.SELECT_FINISH, callback_data=callback_finish),
        InlineKeyboardButton(CommonMessages.CANCEL, callback_data=callback_cancel)
    )
    return markup
