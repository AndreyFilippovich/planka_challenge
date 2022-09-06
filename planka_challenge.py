import datetime as dt
import logging
import os
import random
import sqlite3

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater

import dictionaries

'''Код является внутрянкой телеграм бота,
Он отправляет по командам котиков и мотивационные цитаты.
Каждый день в 4 утра по москве он отправляет время
сколько сегодня стоять в планке и стульчике
'''

load_dotenv()

secret_token = os.getenv('TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

URL = 'https://api.thecatapi.com/v1/images/search'

QUOTES = dictionaries.quotes
REPEATING_TIMES = 30
REPEATING_COUNT = 7 - 1
INCREMENT = 5

AT_A_TIME = dt.time(6, 0, 0)  # 06:00AM Everyday


# тут мы получаем новые изображения котиков
def get_new_image():
    """Данная функция обращается к API с котиками и возвращает рандомное
    изображение.
    Если API с котиками не работает, то обращаемся к API с собачками.
    """
    try:
        response = requests.get(URL)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)

    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


def new_cat(update, context):
    """Благодаря этой функции мы можем в боте вызывать команду с вызовом
    котиков.
    """
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image())


# Тут мы получаем мотивационные цитаты
def get_new_motivation():
    """Функция дает рандомную мотивационную цитату.
    В отдельном файле dictionaries.py расположены сотни цитат.
    Функция подгружает их и в рандомном порядке возвращает.
    """
    random_index = random.randint(0, len(QUOTES) - 1)
    random_quotes = QUOTES[random_index]
    return random_quotes


def new_motivation(update, context):
    """Функция позволяет вызывать мотивационную цитату в чате.
    """
    chat = update.effective_chat
    context.bot.send_message(chat.id, get_new_motivation())


# Эта функция отвечает за приветствие новых участников челленджа
def start(update, context):
    """С этого все начинается.
    При нажатии на кнопку /start функция выводит в диалоге приветственное
    сообщение.
    В приветственном сообщении к пользователю обращаемся по имени.
    Далее дается на выбор 4 кнопки (они расположены в buttons).
    """
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup(
        [['/newcat'], ['/newmotivation'], ['/help'], ['/time']],
        resize_keyboard=True,
    )
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Рад видеть тебя в числе участников челленджа!\n'
        'Давай расскажу тебе, что умею: \n'
        '1- Каждый день в 04:00 по Московскому времени буду отправлять тебе '
        'время для планки и стульчика\n'
        '2- По команде /newmotivation отправлю тебе мотивационную цитату, '
        'чтобы были моральные силы\n'
        '3- По команде /newcat я отправлю тебе фотографию котика, чтобы '
        'поднять настроение\n'
        'Чтобы убедиться в моей правоте держи фоточку котика'.format(name),
        reply_markup=button,
    )
    context.bot.send_photo(chat.id, get_new_image())


def timers_updater(context):
    db_conn = sqlite3.connect(
        'db.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
    )
    cursor = db_conn.cursor()
    now = dt.datetime.now()
    cursor.execute(f"SELECT * FROM timers")
    rows = cursor.fetchall()
    for row in rows:
        uid = row[0]
        new_time = row[2]  # колонка timer в БД
        repeating_step = row[3]  # колонка repeat в БД
        # Если шаг повторения больше количества шагов повтороения или время
        # не кратно REPEATING_TIMES (30 по умолчанию),
        # то добавляет INCREMENT секунд ко времени
        # иначе добавляет шаг, сохраняя текущее время.
        if (
            repeating_step >= REPEATING_COUNT
            or new_time % REPEATING_TIMES != 0
        ):
            new_time += INCREMENT
            repeating_step = 0
        else:
            repeating_step += 1
        # Сохраняет текущее значение в БД
        cursor.execute(
            f"UPDATE timers SET "
            f"timer = {new_time}, "
            f"repeat = {repeating_step},"
            f"last_updated = '{now}' "
            f"WHERE uid = {uid}"
        )
        db_conn.commit()
        # Если пользователь подписался на уведомления, то ему придет
        # сообщение
        if row[4] == 1:
            context.bot.send_message(uid, format_message(new_time))
    db_conn.close()


def get_user_timer(uid):
    """Получает значение таймера для юзера из базы"""
    db_conn = sqlite3.connect(
        'db.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
    )
    cursor = db_conn.cursor()
    now = dt.datetime.now()
    cursor.execute(f"SELECT * FROM timers WHERE uid={uid}")
    row = cursor.fetchone()
    # Если таймер в БД не найден, то это новый юзер, добавляем его со значением
    # по умолчанию.
    if row is None:
        cursor.execute(
            f"INSERT INTO timers "
            f"(uid, last_updated) VALUES "
            f"({uid}, '{now}')"
        )
        db_conn.commit()
        db_conn.close()
        return None
    return row[2]  # Поле timer в БД


def format_message(time):
    # Формирует сообщение в зависимости от времени
    # Если секунд меньше 60, то выводим в формате 20 sec.
    # Если больше минуты, то в формате 01 min. 25 sec.
    if time < 60:
        time_text = str(time) + ' sec.'
    else:
        m, s = divmod(time, 60)
        time_text = f'{m:02d} min. {s:02d} sec.'
    return time_text


def send_user_timer(context, uid, user_timer):
    if user_timer == INCREMENT:
        # TODO /unsubscribe не реализован
        message = (
            'Добро пожаловать в челенж! Начинаем с 5 секунд. Вы '
            'подписаны на автоматические обновления, бот будет '
            'присылать сообщение о вашем времени в планке каждое '
            'утро. Отписаться можно в любой момент '
            'командой /unsubscribe'
        )
    else:
        formatted_time = format_message(user_timer)
        message = f'Ваш таймер для планки на сегодня: {formatted_time}'
    context.bot.send_message(uid, message)


def planka_timer(update, context):
    chat = update.effective_chat
    user_timer = get_user_timer(chat.id) or INCREMENT
    send_user_timer(context, chat.id, user_timer)


def main():
    updater = Updater(token=secret_token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('newcat', new_cat))
    updater.dispatcher.add_handler(
        CommandHandler('newmotivation', new_motivation)
    )
    updater.dispatcher.add_handler(CommandHandler('help', start))
    updater.dispatcher.add_handler(CommandHandler('time', planka_timer))

    # Обновляем таймеры всех юзеров раз в сутки в 04:00
    job_queue = updater.job_queue
    job_once_a_day = job_queue.run_daily(
        timers_updater, time=AT_A_TIME
    )

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
