import asyncio
import logging
import re
import sys

from aiogram import Bot, Dispatcher, Router, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

with open('key.env', 'r', encoding='utf-8') as f:
    TOKEN = f.read().strip()
with open('id.env', 'r', encoding='utf-8') as m:
    DEVID = int(m.read())

# Регулярка:
# ^Где\s+     — начало строки, слово "Где" и пробелы
# "([^"]+)"   — 1-я группа: текст в кавычках (параметр1)
# \s+         — пробелы
# (\d+)       — 2-я группа: целое число (ЧисленныйПараметр2)
# $           — конец строки

dp = Dispatcher()
router = Router()
PATTERN = re.compile(r'^Где\s+(.+?)\s+', re.I)
FPATTERN = re.compile(r'^Где\s+(.+?)\s+(\d+)$', re.I)

async def on_startup(bot: Bot) -> None:
    await bot.send_message(chat_id=DEVID, text="System: ONLINE")

@dp.message(F.text.regexp(FPATTERN).as_("match"))
async def handle_query(message: Message, match: re.Match):
    param1 = match.group(1)
    param2 = int(match.group(2))
    await message.answer(f"Ищу: <b>{param1}</b>, число: <b>{param2}</b>")

@dp.message(F.text.regexp(PATTERN).as_("match"))
async def handle_query(message: Message, match: re.Match):
    param1 = match.group(1)
    await message.answer(f"Ищу: <b>{param1}</b>")

@router.message(F.from_user.id == DEVID, F.text == "ребут")
async def admin_stop(message: Message):
    await message.answer("System: REBOOT SEQUENCE")
    await dp.stop_polling()

@dp.message()
async def echo_handler(message: Message) -> None:
    if (F.from_user.id == DEVID):
        await message.answer("Бать, я не понял")
    else:
        await message.answer("I missunderstood you.")


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Приветики!")

@dp.message(message: Message)
    await message.answer("попробуй ещё раз?")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.startup.register(on_startup)
    dp.include_router(router)          
    asyncio.run(main())