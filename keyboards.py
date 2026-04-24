from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import checked_today


def main_kb(user: dict | None) -> InlineKeyboardMarkup:
    if user is None:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Начать", callback_data="begin")]
        ])

    check_btn = (
        InlineKeyboardButton(text="✅ Уже отмечено", callback_data="noop")
        if checked_today(user) else
        InlineKeyboardButton(text="📍 Отметиться", callback_data="check")
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [check_btn],
        [InlineKeyboardButton(text="📊 Мой счётчик", callback_data="stats")],
        [InlineKeyboardButton(text="🔄 Сбросить счётчик", callback_data="reset_ask")],
    ])


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")]
    ])


def confirm_reset_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, сбросить", callback_data="reset_do"),
            InlineKeyboardButton(text="Нет", callback_data="back"),
        ]
    ])
