# импортируем библиотеку для работы с базой данных
import sqlite3

# создали подключение к бд. если такой базы нет, то она создастся сама
con = sqlite3.connect(r"\db.db")
# создали курсор для запросов
cursor = con.cursor()
# создали таблицу users в базе, если она еще не существует
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS "users" ("id" INTEGER NOT NULL,"tg_id" INTEGER NOT NULL, primary key("id" AUTOINCREMENT));''')
# создаем таблицу categories в базе, если она еще не существует
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS "categories"(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL, value TEXT NOT NULL);''')

# cursor.execute(
#     '''INSERT INTO "categories"(name,value) VALUES("технологии","technology");''')
# создаем таблицу subscribes в базе, если она еще не существует
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS "subscribes"(user_id INTEGER, category_id INTEGER);''')
# cursor.execute(
#     '''DROP TABLE "subscribes"''')
# зафиксировали изменения в базе
con.commit()
# закрыли подключение
con.close()