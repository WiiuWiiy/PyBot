import pymysql
from dotenv import load_dotenv
import os

db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_name = os.getenv("db_name")

load_dotenv()
#def add(name:str, args):           
#    """
#    Функция на добавление информации в базу данных
#    Возвращает либо ошибку, либо "Сохранено"
#    """
#    return True
#
#def search(name:str, *args):  
#    """
#    Функция на поиск по базе данных
#    Возвращает либо информацию с базы, либо ошибку
#    """
#    return True

try:
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        charset='utf8mb4', # Важно для русского языка и эмодзи
        cursorclass=pymysql.cursors.DictCursor # Удобно: результаты приходят в виде словарей
    )
    
    print("✅ Успешно подключились к базе данных!")

except Exception as e:
    print("❌ Ошибка подключения или запроса:", e)

finally:
    if 'connection' in locals() and connection.open:
        connection.close()
        print("Соединение закрыто.")

