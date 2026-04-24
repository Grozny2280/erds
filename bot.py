import asyncio
import logging
from datetime import datetime, timezone, timedelta

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, REMINDER_HOUR, REMINDER_MIN
from handlers import router
import database as db

logging.basicConfig(level=logging.INFO)
MSK = timezone(timedelta(hours=3))


async def send_reminders(bot: Bot):
    """Отправляет напоминание тем, кто ещё не отметился сегодня."""
    today = datetime.now(MSK).date().isoformat()
    for uid_str, user in db.all_users().items():
        if user.get("last_check") == today:
            continue
        d = db.days_count(user["start_date"])
        try:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            await bot.send_message(
                chat_id=int(uid_str),
                text=(
                    f"☀️ Доброе утро!\n\n"
                    f"Ты на пути уже *{d} дн.* — не забудь отметиться сегодня!"
                ),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📍 Отметиться", callback_data="check")]
                ]),
            )
        except Exception as e:
            logging.warning(f"remind {uid_str}: {e}")


async def reminder_scheduler(bot: Bot):
    """Ждёт нужного времени и запускает напоминания каждый день."""
    while True:
        now = datetime.now(MSK)
        target = now.replace(hour=REMINDER_HOUR + 3, minute=REMINDER_MIN, second=0, microsecond=0)
        # REMINDER_HOUR задан в UTC, переводим в МСК для сравнения
        target_utc = now.replace(hour=REMINDER_HOUR, minute=REMINDER_MIN, second=0, microsecond=0,
                                  tzinfo=timezone.utc).astimezone(MSK)
        if now >= target_utc:
            target_utc = target_utc + timedelta(days=1)
        wait = (target_utc - now).total_seconds()
        logging.info(f"Следующее напоминание через {wait:.0f}с ({target_utc.strftime('%d.%m %H:%M')} МСК)")
        await asyncio.sleep(wait)
        await send_reminders(bot)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    asyncio.create_task(reminder_scheduler(bot))

    logging.info("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
