# функция регистрации пользователя
def registration(connection, cursor, user_id):
    if find_user(cursor, user_id):
        connection.close()
    else:
        cursor.execute(
            '''INSERT INTO users(tg_id) VALUES (?) ;''', ([user_id]))
        connection.commit()
        connection.close()


# функция получения id пользователя
def find_user(cursor, user_id):
    return cursor.execute('''SELECT id FROM users WHERE tg_id=?;''', ([user_id])).fetchone()


# функция просмотра подписок пользователя
def get_subscribes(cursor, user_id):
    return cursor.execute(
        f'''SELECT categories.id,categories.name, categories.value FROM subscribes JOIN categories ON categories.id = subscribes.category_id JOIN users ON users.tg_id=subscribes.user_id WHERE users.tg_id=?;''',
        (user_id,)).fetchall()


# функция просмотра всех категорий
def get_all_categories(cursor):
    return cursor.execute('''SELECT id,name,value FROM categories;''').fetchall()


#
def do_sub(con, cursor, user_id, category_id):
    cursor.execute('''INSERT INTO subscribes(user_id,category_id) VALUES (?,?);''', (user_id, category_id,))
    con.commit()
    con.close()
    return True

def dont_sub(con, cursor, user_id, category_id):
    cursor.execute(
        '''DELETE FROM subscribes WHERE user_id=? AND category_id=?;''', (user_id, category_id,))
    con.commit()
    con.close()
    return True

# функция подписки
def subscribe(con, user_id, category_id):
    cursor = con.cursor()
    # получаем подписки пользователя
    users_subs = dict(cursor.execute(
        f'''SELECT categories.id,categories.value FROM subscribes JOIN categories ON categories.id = subscribes.category_id JOIN users ON users.tg_id=subscribes.user_id WHERE users.tg_id=?;''',
        (user_id,)).fetchall())
    # проверяем если есть подписки
    if len(users_subs) > 0:
            # ищем в массиве с подписками выбранну категорию, если нашли то выводим False
            if len({key: val for key, val in users_subs.items() if key in (category_id,)}) > 0:
                return False
            # если юзер еще не подписан на категорию, то подписываем и возвращаем True
            else:
                return do_sub(con, cursor, user_id, category_id)

    # если массив с подписками пустой, то подписываем юзера
    else:
        return do_sub(con, cursor, user_id, category_id)


# функция отписки от категории
def unsubscribe(con, user_id, category_id):
    cursor = con.cursor()
    # получаем подписки пользователя
    users_subs = dict(cursor.execute(
        f'''SELECT categories.id,categories.value FROM subscribes JOIN categories ON categories.id = subscribes.category_id JOIN users ON users.tg_id=subscribes.user_id WHERE users.tg_id=?;''',
        (user_id,)).fetchall())

    # проверяем если есть подписки
    if len(users_subs) > 0:
        return dont_sub(con, cursor, user_id, category_id)
    # если массив с подписками пустой
    else:
        return False
