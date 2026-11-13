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
    callback_query
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


def kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Заменить", callback_data="replace"),
            InlineKeyboardButton(text="Оставить старую",
                                 callback_data="cancel")
        ]
    ])
    return kb


dp = Dispatcher()
router = Router()


def common(message: Message) -> dict:
    return dict(
        chat_id=message.chat.id,
    )


def hidden(message: Message) -> dict:
    return dict(
        chat_id=message.chat.id,
        ephemeral_message_parameters=EphemeralMessageParameters(
            receiver_user_id=message.from_user.id
        ),
    )


WHERE = re.compile(r'^Где\s+(?P<subject>\S+)$', re.I)
FWHERE = re.compile(r'^Где\s+(?P<subject>\S+)\s+(?P<number>\d+)$', re.I)

THIS = re.compile(r'^Это\s+(?P<subject>\S+)$', re.I)
FTHIS = re.compile(r'^Это\s+(?P<subject>\S+)\s+(?P<number>\d+)$', re.I)


async def on_startup(bot: Bot) -> None:
    await bot.send_message(chat_id=STARTCHAT, text="Готов к работе!")


@router.message(F.text.lower() == "кто я")
async def who_am_i(message: Message, bot: Bot):
    is_admin = False
    if message.from_user.id in ADMIN_ID:
        is_admin = True

    status = "Право имеющий" if is_admin else f"Чудо"

    await bot.send_message( 
        **common(message),
        text=f"{status}"
    )

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

@router.message(F.reply_to_message, F.text.regexp(THIS).as_("match"))
@router.message(F.reply_to_message, F.text.regexp(FTHIS).as_("match"))
async def handle_add(message: Message, match: re.Match, bot: Bot):

    data = match.groupdict()
    subject = data["subject"]

    original = message.reply_to_message
    link = original.message_id

    if "number" in data:
        if (await database.add_material(
            data["subject"],
            int(data["number"]),
            message.chat.id,
            link,
            database.get_db_path()
        )
        ):
            await bot.send_message(
                **common(message),
                text=f'Фиксирую {data["subject"]}, по индексу {data["number"]}'
            )
        else:
            await bot.send_message(
                **hidden(message),
                text="Данная ячейка уже занята, хочешь её заменить?",
                reply_markup=kb()
            )
    else:
        await bot.send_message(
            **common(message),
            text=f'Фиксирую {data["subject"]}'
        )


@router.callback_query()
async def handle_choose(callback: CallbackQuery):
    await Callback.answer()




@router.message(F.text.regexp(FWHERE).as_("match"))
@router.message(F.text.regexp(WHERE).as_("match"))
async def handle_search(message: Message, match: re.Match, bot: Bot):
    data = match.groupdict()

    if "number" in data:
        await bot.send_message(
            **hidden(message),
            text=f'Ищу {data["subject"]}, по индексу {data["number"]}'
        )
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )
    else:
        await bot.send_message(
            **hidden(message),
            text=f'Ищу {data["subject"]}'
        )


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
            **hidden(message),
            text=f"message.chat.id = {message.chat.id}"
        )
    else:
        await bot.send_message(
            **common(message),
            text=f"Привет дружок пирожок, как дела у тебя?) \
            \n\nТвой номер {message.from_user.id}"
        )


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
образно, логика работы бота такая:
приходит сообщение с файлами, или с изображением.
бот автоматически видет что сообщение с файлами, и спрашивает, что это
пользователь пишет 
""название учебного предмета" [номер по порядку данного материала]"
Бот проверяет на правильность данных (при неправильном написании,
или отсуствии данной категории он предлагает автоматический выбор из списка,
непосредственно из существующих тэгов, или сохраняет новый).
Проверив, он сохраняет данные в данную категорию с ссылкой на сообщение.

Спустя время, пользователь может отправить сообщение "Где "название предмета" "номер""
 и бот должен отправить ссылку на сообщение с данной подписью
или "Где "учебный предмет"" и он автоматически создаст пронумерованный список из ссылок на сообщения

'''
