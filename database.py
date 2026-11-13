import aiosqlite
import os
import asyncio
from dotenv import load_dotenv

def dbdata() -> dict:


def get_db_path() -> str:
    load_dotenv()
    return os.getenv("DB_PATH", "info.db")

async def init_db(db_path):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS InfoTable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link INTEGER NOT NULL,
                user_chat INTEGER NOT NULL,
                Tag TEXT NOT NULL,
                element_id INTEGER NOT NULL
            )
        """)
        await db.commit()


async def add_material(
    subject: str,
    number: int,
    chat_id: int,
    message_id: int,
    db_path
) -> int | bool:
    async with aiosqlite.connect(db_path) as db:
        if (search_material(subject, number, chat_id) is None):
            cursor = await db.execute(
                "UPDATE InfoTable SET link = ?, user_chat = ? "
                "WHERE Tag = ? AND element_id = ?",
                (message_id, chat_id, subject, number))
            new_id = cursor.lastrowid
            await db.commit()
            return new_id
        else:
            return False


async def update_material(
    message_id: int,
    old_id: int
) -> int:
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "UPDATE InfoTable SET id = ?, element_id = message_id",
            (old_id, message_id))
        await db.commit()
    return old_id


async def search_material(
    subject: str,
    number: int,
    chat_id: int
) -> dict | None:
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "SELECT id FROM InfoTable WHERE Tag = ? "
            "AND element_id = ? AND user_chat = ?",
            (subject, number, chat_id)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        else:
            return dict(row)


if __name__ == "__main__":
    asyncio.run(init_db(get_db_path()))
