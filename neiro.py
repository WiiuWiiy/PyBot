import asyncio
import logging
import re
import sys

from aiogram import Bot, Dispatcher, Router, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

with open('key.txt', 'r', encoding='utf-8') as f:
    TOKEN = f.read().strip()

# Регулярка:
# ^Где\s+     — начало строки, слово "Где" и пробелы
# "([^"]+)"   — 1-я группа: текст в кавычках (параметр1)
# \s+         — пробелы
# (\d+)       — 2-я группа: целое число (ЧисленныйПараметр2)
# $           — конец строки

dp = Dispatcher()
router = Router()
FPATTERN = r'^Где\s+(.+?)\s+(\d+)$'
PATTERN = r'^Где\s+(.+?)'


@dp.message(F.text.regexp(FPATTERN).as_("match"))
async def handle_query(message: Message, match: re.Match):
    param1 = match.group(1)
    param2 = int(match.group(2))
    await message.answer(f"Ищу: <b>{param1}</b>, число: <b>{param2}</b>")

@dp.message(F.text.regexp(PATTERN).as_("match"))
async def handle_query(message: Message, match: re.Match):
    param1 = match.group(1)
    param2 = int(match.group(2))
    await message.answer(f"Ищу: <b>{param1}</b>")

@router.message(F.text.lower() == "меню")
async def text_menu(message: Message):
    await message.answer("Вы написали 'меню' без слэша, и я отреагировал!")

@router.message(F.text.lower() == "рестарт")
async def text_menu(message: Message):
    await message.answer("Перезапуск принят")
    await dp.stop_polling()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Приветики!")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.include_router(router)          
    asyncio.run(main())