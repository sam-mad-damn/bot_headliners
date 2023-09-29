from bd import *
from newsapi import NewsApiClient
import sqlite3
from config import *
import telebot
from telebot import types
from functions import *
import requests
from datetime import date, timedelta

# объявляем бота
bot = telebot.TeleBot(key_tg, parse_mode=None)


# объявляем обработчик сообщений бота. Все сообщения, содержащие слово "начать/помощь"
@bot.message_handler(commands=['start', 'начать'])
# запускают функцию "отправить приветствие"
def send_welcome(message):
    # добавление пользователя в базу данных
    con = sqlite3.connect(r"db.db")
    registration(con, con.cursor(), message.from_user.id)

    # клавиатура навигации в боте
    markup = types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = types.KeyboardButton('Подписаться на категорию новостей')
    itembtn2 = types.KeyboardButton('Посмотреть новости по своим подпискам')
    itembtn3 = types.KeyboardButton('Отписаться от категории новостей')
    markup.add(itembtn1, itembtn2, itembtn3)

    # бот отправляет сообщение с указанным текстом
    bot.send_message(message.chat.id, "Приветствую в новостном боте!\nВыберите, что вы хотите сделать:", reply_markup=markup)


# обработчик входящих сообщений
@bot.message_handler(content_types=["text"])
# работа с кнопками
def news_work(message):
    if message.chat.type == "private":
        chat_id = message.chat.id

        if message.text == "Подписаться на категорию новостей":
            # создаем клавиатуру с категориями новостей
            markup = types.InlineKeyboardMarkup(row_width=3)

            # берем из базы словарь всех категорий
            categories = get_all_categories(sqlite3.connect(r"db.db").cursor())
            print(categories)
            for k, n, v in categories:
                # создаем нужное кол-во кнопок под категории
                btn = types.InlineKeyboardButton(f"{n}", callback_data=f"sub{v}")
                markup.add(btn)

            bot.send_message(chat_id, "Выберите категорию, на которую хотите подписаться:", reply_markup=markup)

        elif message.text == "Посмотреть новости по своим подпискам":
            # получаем подписки юзера
            subscribes = get_subscribes(sqlite3.connect(r"db.db").cursor(),
                                             message.from_user.id)

            # вывод массива с подписками пользователя из базы
            if len(subscribes) > 0:
                # создаем клавиатуру с категориями новостей
                markup = types.InlineKeyboardMarkup(row_width=3)

                for k, n,v in subscribes:
                    # создаем нужное кол-во кнопок под категории
                    btn = types.InlineKeyboardButton(f"{n}", callback_data=f"{v}")
                    markup.add(btn)

                bot.send_message(chat_id, f"Вы подписаны на следующие категории:", reply_markup=markup)
                bot.send_message(chat_id, "👆")
                bot.send_message(chat_id, f"Чтобы посмотреть новости категории, просто нажмите на неё")

            else:
                bot.send_message(chat_id, "Вы еще никуда не подписаны")
                bot.send_message(chat_id, "🙀")

        elif message.text == "Отписаться от категории новостей":
            # получаем подписки юзера
            subscribes = get_subscribes(sqlite3.connect(r"db.db").cursor(),
                                             message.from_user.id)

            # вывод массива с подписками пользователя из базы
            if len(subscribes) > 0:
                # создаем клавиатуру с категориями новостей
                markup = types.InlineKeyboardMarkup(row_width=3)

                for k, n, v in subscribes:
                    # создаем нужное кол-во кнопок под категории
                    btn = types.InlineKeyboardButton(f"{n}", callback_data=f"del{v}")
                    markup.add(btn)

                bot.send_message(chat_id, f"Нажмите на категорию, от которой хотите отписаться:", reply_markup=markup)
            else:
                bot.send_message(chat_id, "Вы еще никуда не подписаны")
                bot.send_message(chat_id, "🙀")

# обработчик сообщений с инлайн-клавиатуры
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            # работа непосредственно с новостными категориями
            categories = get_all_categories(sqlite3.connect(r"db.db").cursor())
            for k, n, v in categories:
                # если мы выбирали действие "подписаться"
                if call.data == f"sub{v}":
                    sub = subscribe(sqlite3.connect(r"db.db"), call.from_user.id,
                                    k)
                    print(sub)
                    if sub:
                        markup = types.InlineKeyboardMarkup(row_width=2)
                        btn = types.InlineKeyboardButton("Смотреть новости", callback_data=f"{v}")
                        markup.add(btn)
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="👍", reply_markup=None)
                        bot.send_message(call.message.chat.id,
                                         f"Вы успешно подписаны на категорию '{n}'. Чтобы посмотреть новости по этой категории, жмите на кнопку 👇",
                                         reply_markup=markup)
                    else:
                        markup = types.InlineKeyboardMarkup(row_width=2)
                        btn = types.InlineKeyboardButton("Смотреть новости", callback_data=f"{v}")
                        markup.add(btn)
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text=f"Вы уже подписаны на категорию '{n}'. Чтобы посмотреть новости по этой категории, жмите на кнопку 👇",
                                              reply_markup=markup)

                # если мы выбирали "отписаться"
                elif call.data == f"del{v}":
                    unsub = unsubscribe(sqlite3.connect(r"db.db"),
                                        call.from_user.id, k)
                    if unsub:
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text="😔",
                                              reply_markup=None)
                        bot.send_message(call.message.chat.id, f"Вы успешно отписаны от категории '{n}'")
                    else:
                        bot.send_message(call.message.chat.id, "Вы еще никуда не подписаны")
                        bot.send_message(call.message.chat.id, "🙀")

                # посмотреть новости категории
                elif call.data == f"{v}":
                    bot.send_message(call.message.chat.id,f"Новости категории '{n}':")
                    newsapi = NewsApiClient(api_key=f'{key_news}')
                    news=newsapi.get_top_headlines(category=f'{v}',
                                              language='ru',
                                              country='ru',
                                              page_size=3)

                    # получаем словарь dict
                    for i in news['articles']:
                        bot.send_message(call.message.chat.id, f"{i['title']}\n{i['url']}")

    except Exception as e:
        print(repr(e))

# запуск бота
bot.infinity_polling()
