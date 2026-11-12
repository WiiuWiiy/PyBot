import asyncio
import logging
import re
import sys
import os
import database

from aiogram import Bot, Dispatcher, Router, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, EphemeralMessageParameters
from dotenv import load_dotenv

media_groups = {}  # временное хранилище

load_dotenv()

TOKEN = os.getenv("key")
DEV_ID = int(os.getenv("id"))

dp = Dispatcher()
router = Router()

PATTERN  = re.compile(r'^Где\s+(\S+)$',        re.I)
FPATTERN = re.compile(r'^Где\s+(\S+)\s+(\d+)$', re.I)
THIS     = re.compile(r'^Это\s+(\S+)$',        re.I)
FTHIS    = re.compile(r'^Это\s+(\S+)\s+(\d+)$', re.I)

#Start
async def on_startup(bot: Bot) -> None:
    await bot.send_message(chat_id=DEV_ID, text="Готов к работе!")

@router.message(F.text == "кто я")
async def who_am_i(message: Message, bot: Bot):
    is_admin = message.from_user.id == DEV_ID
    status = "Право имеющий" if is_admin else "Чудо"
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"{status}",
        receiver_user_id=message.from_user.id,
    )

@router.message(F.photo)
async def handle_photo(message: Message):
    if message.media_group_id:
        await message.answer(f"Это группа фоток, их id{message.media_group_id}")
    else:
        await message.answer("Хочешь добавить его в базу данных?")

@router.message(F.text.regexp(FTHIS).as_("match"))
async def handle_query(message: Message, match: re.Match, bot: Bot):
    if message.reply_to_message is not None:
        param1 = match.group(1)
        param2 = int(match.group(2))
        await message.answer(f"фиксирую: <b>{param1}</b>, число: <b>{param2}</b>")

@router.message(F.text.regexp(THIS).as_("match"))
async def handle_query(message: Message, match: re.Match, bot: Bot):
    if message.reply_to_message is not None:
        param1 = match.group(1)
        await message.answer(f"Фиксирую: <b>{param1}</b>")

@router.message(F.text.regexp(FPATTERN).as_("match"))
async def handle_query(message: Message, match: re.Match, bot: Bot):
    param1 = match.group(1)
    param2 = int(match.group(2))
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Ищу {param1}, по индексу {param2}, message_id {message.message_id}",
        receiver_user_id=message.from_user.id,
    )

@router.message(F.text.regexp(PATTERN).as_("match"))
async def handle_query(message: Message, match: re.Match, bot: Bot):
    param1 = match.group(1)
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Ищу {param1}",
        receiver_user_id=message.from_user.id,
    )

@router.message(F.from_user.id == DEV_ID, F.text == "ребут")
async def admin_stop(message: Message):
    await message.answer("System: REBOOT SEQUENCE")
    await dp.stop_polling()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Приветики!, я работаю)")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.startup.register(on_startup)
    dp.include_router(router)          
    asyncio.run(main())



#образно, логика работы бота такая:
#приходит сообщение с файлами, или с изображением.
#бот автоматически видет что сообщение с файлами, и спрашивает, что это
#пользователь пишет ""название учебного предмета" [номер по порядку данного материала]"
#Бот проверяет на правильность данных (при неправильном написании, или отсуствии данной категории он предлагает автоматический выбор из списка, непосредственно из существующих тэгов, или сохраняет новый).
#Проверив, он сохраняет данные в данную категорию с ссылкой на сообщение.
#
#Спустя время, пользователь может отправить сообщение "Где "название предмета" "номер"" и бот должен отправить ссылку на сообщение с данной подписью
#или "Где "учебный предмет"" и он автоматически создаст пронумерованный список из ссылок на сообщения