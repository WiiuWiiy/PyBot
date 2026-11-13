import aiosqlite
import os
import asyncio
from dotenv import load_dotenv


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
        if (await search_material(subject, number, chat_id, db_path) is None):
            cursor = await db.execute(
                "INSERT INTO InfoTable (link, user_chat, Tag, element_id) \
                VALUES (?, ?, ?, ?)",
                (message_id, chat_id, subject, number))
            new_id = cursor.lastrowid
            await db.commit()
            return True
        else:
            search = await search_material(subject, number, chat_id, db_path)
            return search["id"]


async def update_material(
    message_id: int,
    id: int,
    db_path
) -> int:
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "UPDATE InfoTable SET link = ? WHERE id = ?",
            (message_id, id))
        await db.commit()
    return id


async def search_material(
    subject: str,
    number: int,
    chat_id: int,
    db_path
) -> dict | None:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, link "
            "FROM InfoTable WHERE Tag = ? "
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
