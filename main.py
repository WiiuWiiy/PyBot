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
from aiogram.types import (
    Message,
    EphemeralMessageParameters,
    ReplyParameters,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("key")
DEV_ID = int(os.getenv("id"))
STARTCHAT = int(os.getenv("startid"))
ADMIN_ID = {
    int(x.strip())
    for x in os.getenv("ADMIN_ID", "").split(",")
    if x.strip()
}


async def add_note(data: str,
                   number: int,
                   id: int,
                   link: int,
                   dp_path) -> dict | bool:
    result = await database.add_material(
        data,
        number,
        id,
        link,
        dp_path)
    return result


dp = Dispatcher()
router = Router()

WHERE = re.compile(r'^Где\s+(?P<subject>\S+)$', re.I)
FWHERE = re.compile(r'^Где\s+(?P<subject>\S+)\s+(?P<number>\d+)$', re.I)

THIS = re.compile(r'^Это\s+(?P<subject>\S+)$', re.I)
FTHIS = re.compile(r'^Это\s+(?P<subject>\S+)\s+(?P<number>\d+)$', re.I)


def common(message: Message) -> dict:
    return dict(
        chat_id=message.chat.id,
        message_id=message.message_id
    )



def kb(link: int, id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Заменить",
                callback_data=f"replace:{link}:{id}"
            ),
            InlineKeyboardButton(text="Оставить старую",
                                 callback_data="cancel")
        ]
    ])
    return kb


async def delete_fingerprint(bot: Bot, message: Message,botsend: Message):
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await asyncio.sleep(5)
    await bot.delete_message(chat_id=botsend.chat.id,
                             message_id=botsend.message_id)


@router.message(F.text.lower() == "кто я")
async def who_am_i(message: Message, bot: Bot):
    is_admin = False
    if message.from_user.id in ADMIN_ID:
        is_admin = True

    status = "Право имеющий" if is_admin else f"Чудо"

    await bot.send_message(
        chat_id=message.chat.id,
        text=f"{status}"
    )


@router.message(F.reply_to_message, F.text.regexp(THIS).as_("match"))
@router.message(F.reply_to_message, F.text.regexp(FTHIS).as_("match"))
async def handle_add(message: Message, match: re.Match, bot: Bot):

    data = match.groupdict()
    subject = data["subject"].upper()

    original = message.reply_to_message
    link = original.message_id
    if "number" in data:
        result = await add_note(subject,
                                int(data["number"]),
                                message.chat.id,
                                link,
                                database.get_db_path())
        if (result is True):
            send = await bot.send_message(
                chat_id=message.chat.id,
                text=f'Фиксирую {data["subject"]}, по индексу {data["number"]}'
            )
        else:
            send = await bot.send_message(
                chat_id=message.chat.id,
                text="Данная ячейка уже занята, хочешь её заменить?",
                reply_markup=kb(link, result)
            )
    else:
        send = await bot.send_message(
            chat_id=message.chat.id,
            text=f'Фиксирую {data["subject"]}... \
            \n\nно не вижу номера, повтори с номером пожалуйста <3'
        )
    asyncio.create_task(delete_fingerprint(bot, message, send))

@router.callback_query(F.data.startswith("replace:"))
async def handle_replace(callback: CallbackQuery, bot: Bot, message: Message):
    await callback.answer()
    parts = callback.data.split(":")
    link = int(parts[1])
    old_id = int(parts[2])
    await database.update_material(link, old_id, database.get_db_path())
    send = await callback.bot.send_message(
        chat_id=message.chat.id,
        text=f'Я заменил данные!'
    )
    asyncio.create_task(delete_fingerprint(bot, message, send))


@router.callback_query(F.data == "cancel")
async def handle_cancel(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()


@router.message(F.text.regexp(FWHERE).as_("match"))
@router.message(F.text.regexp(WHERE).as_("match"))
async def handle_search(message: Message, match: re.Match, bot: Bot):
    data = match.groupdict()

    if "number" in data:
        print("it in if")
        result = await database.search_material(data["subject"].upper(),
                                                data["number"],
                                                message.chat.id,
                                                database.get_db_path())
        if (result is not None):
            db_msg_id = result["link"]
            try:
                send = await bot.send_message(
                    chat_id=message.chat.id,
                    text=f'Я нашёл \
                    {data["subject"].upper()} - \
                    {data["number"]}',
                    reply_to_message_id=db_msg_id
                )
            except Exception as e:
                send = await bot.send_message(
                    chat_id=message.chat.id,
                    text=f"Ошибка: {e.message}"
                )
        else:
            send = await bot.send_message(
                chat_id=message.chat.id,
                text=f'Я нашёл... \
                ничего...')
    else:
        print("it in else")
        if True:
            send = await bot.send_message(
                chat_id=message.chat.id,
                text=f'Ищу {data["subject"]}'
            )
        else:
            send = await bot.send_message(
                chat_id=message.chat.id,
                text=f'Не нашёл {data["subject"]}'
            )
    asyncio.create_task(delete_fingerprint(bot, message, send))


@router.message(F.text.lower() == "ребут")
async def admin_stop(message: Message):
    if message.from_user.id in ADMIN_ID:
        await message.answer("System: REBOOT SEQUENCE")
        await dp.stop_polling()


@router.message(CommandStart())
async def command_start_handler(message: Message, bot: Bot) -> None:
    is_admin = message.from_user.id in ADMIN_ID

    if is_admin:
        await bot.send_message(
            **common(message),
            text=f"Администратор не в ответе за сохранность бота!"
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"Привет дружок пирожок, как дела у тебя?) \
            \n\nТвой номер {message.from_user.id}"
        )


async def on_startup(bot: Bot) -> None:
    await database.init_db(database.get_db_path())
    await bot.send_message(chat_id=STARTCHAT, text="Готов к работе!")


async def main() -> None:
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.startup.register(on_startup)
    dp.include_router(router)
    asyncio.run(main())


'''
@router.message(F.photo)
async def handle_photo(message: Message):
    if message.media_group_id:
        await message.answer(f"Это группа фоток, \
        их id{message.media_group_id}")
    else:
        await message.answer("Логика добавления")
'''

'''
cursor = await db.execute(
            "INSERT INTO InfoTable (Tag, element_id, user_chat, link) \
            VALUES (?, ?, ?, ?)",
            (subject, number, chat_id, message_id))
        new_id = cursor.lastrowid
'''
