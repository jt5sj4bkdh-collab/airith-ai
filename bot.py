import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from config import settings
from ai_engine import generate_post
from market import get_market_snapshot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("airith")

bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()


def is_owner(message: Message) -> bool:
    return message.from_user is not None and message.from_user.id == settings.owner_id


@dp.message(Command("start"))
async def start(message: Message):
    if not is_owner(message):
        await message.answer("AIRITH AI: доступ ограничен.")
        return

    await message.answer(
        "AIRITH AI запущен.\n\n"
        "/status — состояние бота\n"
        "/market — текущий рынок\n"
        "/draft — AI подготовит пост\n"
        "/publish — AI подготовит и опубликует пост\n"
        "/help — команды"
    )


@dp.message(Command("help"))
async def help_cmd(message: Message):
    if not is_owner(message):
        return
    await message.answer(
        "/status — статус\n"
        "/market — BTC/ETH + OI + funding\n"
        "/draft — создать черновик\n"
        "/publish — создать и опубликовать\n"
    )


@dp.message(Command("status"))
async def status(message: Message):
    if not is_owner(message):
        return
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    await message.answer(
        f"🧠 AIRITH AI\n\n"
        f"Статус: ONLINE\n"
        f"Время сервера: {now}\n"
        f"Автопубликация: {'ON' if settings.auto_post_enabled else 'OFF'}\n"
        f"Канал: {settings.channel_id}"
    )


@dp.message(Command("market"))
async def market(message: Message):
    if not is_owner(message):
        return
    try:
        snapshot = await get_market_snapshot()
        await message.answer(snapshot.to_text())
    except Exception:
        logger.exception("Market error")
        await message.answer("Не удалось получить рыночные данные.")


@dp.message(Command("draft"))
async def draft(message: Message):
    if not is_owner(message):
        return
    try:
        snapshot = await get_market_snapshot()
        post = await generate_post(snapshot)
        await message.answer("ЧЕРНОВИК AIRITH:\n\n" + post)
    except Exception:
        logger.exception("Draft error")
        await message.answer("Не удалось создать черновик.")


@dp.message(Command("publish"))
async def publish(message: Message):
    if not is_owner(message):
        return
    try:
        snapshot = await get_market_snapshot()
        post = await generate_post(snapshot)
        await bot.send_message(settings.channel_id, post)
        await message.answer("Опубликовано в канале.")
    except Exception:
        logger.exception("Publish error")
        await message.answer("Не удалось опубликовать пост.")


async def main():
    logger.info("AIRITH AI starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
