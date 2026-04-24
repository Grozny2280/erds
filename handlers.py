from datetime import date

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

import database as db
from keyboards import main_kb, back_kb, confirm_reset_kb

router = Router()


# ─── /start ───────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(msg: Message):
    user = db.get_user(msg.from_user.id)
    name = msg.from_user.first_name or "друг"

    if user:
        d = db.days_count(user["start_date"])
        text = f"С возвращением, {name}!\nТвой счётчик: *{d} дн.* 💪"
    else:
        text = (
            f"Привет, {name}! 👋\n\n"
            "Этот бот считает дни без зависимости и каждое утро "
            "напоминает отметиться.\n\n"
            "Нажми *Начать* — и поехали!"
        )
    await msg.answer(text, parse_mode="Markdown", reply_markup=main_kb(user))


# ─── Кнопки ───────────────────────────────────────────────────────────────────

@router.callback_query()
async def on_callback(call: CallbackQuery):
    uid = call.from_user.id
    action = call.data
    await call.answer()

    if action == "noop":
        return

    elif action == "begin":
        today = date.today().isoformat()
        db.set_user(uid, {"start_date": today, "last_check": today})
        await call.message.edit_text(
            f"✅ *День 1 начался!*\n\n"
            f"Дата старта: {date.today().strftime('%d.%m.%Y')}\n"
            "Каждое утро в 9:00 МСК буду напоминать тебе отметиться. 🌅",
            parse_mode="Markdown",
            reply_markup=main_kb(db.get_user(uid)),
        )

    elif action == "check":
        user = db.get_user(uid)
        if not user:
            await call.message.edit_text("Сначала нажми /start")
            return
        if db.checked_today(user):
            await call.answer("Уже отмечено сегодня!", show_alert=True)
            return
        user["last_check"] = date.today().isoformat()
        db.set_user(uid, user)
        d = db.days_count(user["start_date"])
        await call.message.edit_text(
            f"✅ *День {d} — отмечен!*\n\nТак держать! 💪",
            parse_mode="Markdown",
            reply_markup=main_kb(user),
        )

    elif action == "stats":
        user = db.get_user(uid)
        if not user:
            await call.message.edit_text("Сначала нажми /start")
            return
        d = db.days_count(user["start_date"])
        start = date.fromisoformat(user["start_date"]).strftime("%d.%m.%Y")
        today_mark = "✅ да" if db.checked_today(user) else "❌ ещё нет"
        await call.message.edit_text(
            f"📊 *Твой прогресс*\n\n"
            f"📅 Начало: {start}\n"
            f"⏳ Дней на пути: *{d}*\n"
            f"Сегодня отмечен: {today_mark}",
            parse_mode="Markdown",
            reply_markup=back_kb(),
        )

    elif action == "reset_ask":
        await call.message.edit_text(
            "⚠️ Сбросить счётчик?\n\nСрыв — не конец пути. Важно продолжать.",
            reply_markup=confirm_reset_kb(),
        )

    elif action == "reset_do":
        today = date.today().isoformat()
        db.set_user(uid, {"start_date": today, "last_check": today})
        await call.message.edit_text(
            "🔄 Счётчик сброшен. День 1 — сегодня.\nТы не сдался(ась). Продолжай! 💪",
            reply_markup=main_kb(db.get_user(uid)),
        )

    elif action == "back":
        user = db.get_user(uid)
        d = db.days_count(user["start_date"]) if user else 0
        await call.message.edit_text(
            f"Счётчик: *{d} дн.* 💪" if user else "Нажми /start",
            parse_mode="Markdown",
            reply_markup=main_kb(user),
        )
