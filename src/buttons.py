from typing import Type

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.models import Task, Team
from locale import CommonMessages, ButtonMessages


def render_team_buttons(
        teams: list[Type[Team]],
        callback_finish: str,
        callback_cancel: str
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


def render_task_buttons(
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
