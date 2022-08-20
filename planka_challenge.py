from operator import truediv
import requests
import logging
import random
import dictionaries
import datetime as dt
import schedule
from multiprocessing.context import Process

import os

from telegram.ext import Updater, CommandHandler
from telegram import ReplyKeyboardMarkup

from dotenv import load_dotenv

'''Тут очень много нужно доделывать.
намешано 3 кода, обычный с котиками, отправка сообщений по расписанию
и мои попытки добавить еще одну кнопку.
А еще в файле quotes первые наработки для мотивационных цитат
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
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image())

# Тут мы получаем мотивационные цитаты
def get_new_motivation():
    random_index = random.randint(0, len(quotes) - 1)
    random_quotes = quotes[random_index]
    return random_quotes

def new_motivation(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat.id, get_new_motivation())

# Эта функция отвечает за приветствие новых участников челленджа
def start(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/newcat'], ['/newmotivation'], ['/help']], resize_keyboard=True)
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

# Эта функция считает время сколько нужно стоять в планке и стульчике
def time():
    utc_time = dt.datetime.utcnow()
    return utc_time

def timer():
    sec = 0
    min = 0

    timeloop = True
    while timeloop:
        sec += 5
        print(str(min) + " Mins " + str(sec) + " Sec ")
        time.sleep(1)
        if sec == 60:
            sec = 0
            min += 1
        if sec == 30:
            a = 0
            while a < 35:
                a += 5
        elif min == 1 or 2 or 3 or 4 or 5 or 6 or 7:
            a = 0
            while a < 35:
                a += 5

schedule.every().day.at("04:00").do(timer)
 
 
class ScheduleMessage():
    def try_send_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)
 
    def start_process():
        p1 = Process(target=ScheduleMessage.try_send_schedule, args=())
        p1.start()  


def static():
    pass



def main():
    updater = Updater(token=secret_token)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('newcat', new_cat))
    updater.dispatcher.add_handler(CommandHandler('newmotivation', new_motivation))
    updater.dispatcher.add_handler(CommandHandler('help', start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()


