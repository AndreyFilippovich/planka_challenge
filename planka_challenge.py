import requests
import logging
import random
import dictionaries
import datetime as dt
from time import sleep

import os

from telegram.ext import Updater, CommandHandler
from telegram import ReplyKeyboardMarkup

from dotenv import load_dotenv

'''Код является внутрянкой телеграм бота,
Он отправляет по командам котиков и мотивационные цитаты.
Каждый день в 4 утра по москве он отправляет время
сколько сегодня стоять в планке и стульчике
'''

load_dotenv()

secret_token = os.getenv('TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

URL = 'https://api.thecatapi.com/v1/images/search'

quotes = dictionaries.quotes

# тут мы получаем новые изображения котиков
def get_new_image():
    """Данная функция обращается к API с котиками и возвращает рандомное изображение.
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
    """Благодаря этой функции мы можем в боте вызывать команду с вызовом котиков.
    """
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image())

# Тут мы получаем мотивационные цитаты
def get_new_motivation():
    """Функция дает рандомную мотивационную цитату.
    В отдельном файле dictionaries.py расположены сотни цитат.
    Функция подгружает их и в рандомном порядке возвращает.
    """
    random_index = random.randint(0, len(quotes) - 1)
    random_quotes = quotes[random_index]
    return random_quotes

def new_motivation(update, context):
    """Функция позволяет вызывать мотивационную цитату в чате.
    """
    chat = update.effective_chat
    context.bot.send_message(chat.id, get_new_motivation())

# Эта функция отвечает за приветствие новых участников челленджа
def start(update, context):
    """С этого все начинается.
    При нажатии на кнопку /start функция выводит в диалоге приветственное сообщение.
    В приветственном сообщении к пользователю обращаемся по имени.
    Далее дается на выбор 4 кнопки (они расположены в buttons).
    """
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/newcat'], ['/newmotivation'], ['/help'], ['/time']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Рад видеть тебя в числе участников челленджа!\n'
             'Давай расскажу тебе, что умею: \n'
             '1- Каждый день в 04:00 по Московскому времени буду отправлять тебе время для планки и стульчика\n'
             '2- По команде /newmotivation отправлю тебе мотивационную цитату, чтобы были моральные силы\n'
             '3- По команде /newcat я отправлю тебе фотографию котика, чтобы поднять настроение\n'
             'Чтобы убедиться в моей правоте держи фоточку котика'.format(name),
        reply_markup=button
    )
    context.bot.send_photo(chat.id, get_new_image())

def timer(min = 0, sec = 0):
    """Это функция таймера.
    Он идет с шагом раз в секунду и прибавляет на каждом шагу +5sec.
    Каждые 30 и 60 секунд таймер отправляет то же значение 6 раз и после этого продолжает.
    При достижении 60sec таймер пишет вместо 60sec 1min.
    """
    seven_steps = 0

    timeloop = True
    while timeloop:
        print(str(min) + " Mins " + str(sec) + " Sec ")
        sleep(1)

        if sec != 30 and sec != 60:
            sec += 5

        elif sec == 30:
            while seven_steps != 6:
                print(str(min) + " Mins " + str(sec) + " Sec ")
                sleep(1)
                seven_steps += 1
                if seven_steps == 6:
                    sec += 5
                continue
         
        if sec == 60:
            sec = 0
            min += 1
            while seven_steps != 0:
                print(str(min) + " Mins " + str(sec) + " Sec ")
                sleep(1)
                seven_steps -= 1
                if seven_steps == -1:
                    seven_steps + 1
                    sec += 5
                continue
    how_much = str(min) + " Mins " + str(sec) + " Sec "
    return how_much

# 2 функции ниже это мои попытки хоть что-то сделать)))
def planka_timer(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat.id, timer())

def time():
    utc_time = dt.datetime.utcnow()
    return utc_time


def main():
    """Благодаря этим хэндлерам мы можем в боте нажимать на кнопки.
    Которые вызывают соответствующие функции.
    """
    updater = Updater(token=secret_token)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('newcat', new_cat))
    updater.dispatcher.add_handler(CommandHandler('newmotivation', new_motivation))
    updater.dispatcher.add_handler(CommandHandler('help', start))
    updater.dispatcher.add_handler(CommandHandler('time', planka_timer))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()


