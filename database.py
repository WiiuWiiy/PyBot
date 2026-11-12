import sqlite3
from dotenv import load_dotenv
import os

# 1. СНАЧАЛА загружаем .env, ПОТОМ читаем переменные
load_dotenv()

db_path = os.getenv("db_path", "app.db")
connection = None

try:
    # 3. Подключаемся к файлу (если файла нет — он создастся)
    connection = sqlite3.connect(db_path)

    # 4. Аналог DictCursor из pymysql — строки как словари
    connection.row_factory = sqlite3.Row

    print(f"✅ Успешно подключились к базе данных: {db_path}")

    # Пример запроса — создаём таблицу, если её нет
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    connection.commit()

except Exception as e:
    print("❌ Ошибка подключения или запроса:", e)

finally:
    if connection is not None:
        connection.close()
        print("Соединение закрыто.")