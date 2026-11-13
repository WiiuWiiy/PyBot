import sqlite3
import os
from dotenv import load_dotenv

def get_db_path() -> str:
    load_dotenv()
    return os.getenv("DB_PATH", "app.db")


def init_db(db_path: str) -> None:
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS InfoTable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_chats 
            )
        """)
        connection.commit()
    except Exception as e:
        print("❌ Ошибка подключения или запроса:", e)
    finally:
        if connection is not None:
            connection.close()
            print("Соединение закрыто.")


if __name__ == "__main__":
    init_db(get_db_path())