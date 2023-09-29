# импортируем библиотеку для работы с базой данных
import sqlite3
from config import categories
from functions import *

# создали подключение к бд. если такой базы нет, то она создастся сама
con = sqlite3.connect(r"db.db")
# создали курсор для запросов
cursor = con.cursor()
# создали таблицу users в базе, если она еще не существует
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS "users" ("id" INTEGER NOT NULL,"tg_id" INTEGER NOT NULL, primary key("id" AUTOINCREMENT));''')
# создаем таблицу categories в базе, если она еще не существует
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS "categories"(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL, value TEXT NOT NULL);''')

# берем из таблицы значение категорий
table_categories=dict()
for k,n,v in get_all_categories(cursor):
    table_categories.update({v:n})
# сравниваем значения в таблице и значения массива и если они не совпадают, то
if categories.keys()-table_categories.keys() != set():
    # заполняем таблицу категории из массива категорий
    for v,n in categories.items():
        cursor.execute(
        '''INSERT INTO "categories"(name,value) VALUES(?,?);''',(n,v))

# создаем таблицу subscribes в базе, если она еще не существует
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS "subscribes"(user_id INTEGER, category_id INTEGER);''')
# cursor.execute(
#     '''DROP TABLE "subscribes"''')
# зафиксировали изменения в базе
con.commit()
# закрыли подключение
con.close()