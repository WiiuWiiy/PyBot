import aiosqlite
import os
import asyncio
from dotenv import load_dotenv


def get_db_path() -> str:
    load_dotenv()
    return os.getenv("DB_PATH", "info.db")


async def init_db(db_path):
    connection = None
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS InfoTable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_chats INTEGER NOT NULL,
                Tag TEXT NOT NULL,
                element_id INTEGER NOT NULL
            )
        """)
        await db.commit()
    pass


async def add_material(
    subject: str,
    number: int,
    chat_id: int,
    message_id: int,
    db_path
) -> str:
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "INSERT INTO InfoTable (subject_id, number, chat_id, message_id) \
            VALUES (?, ?, ?, ?)",
            (subject, number, chat_id, message_id))
        new_id = cursor.lastwordid
        await db.commit()
        return "Saved"


async def update_material(
    subject: str,
    number: int,
    chat_id: int,
    message_id: int
):
    return "SavedNew"


if __name__ == "__main__":
    asyncio.run(init_db(get_db_path()))
