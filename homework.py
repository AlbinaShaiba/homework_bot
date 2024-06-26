import requests
import os
import sys
import logging
import time
from dotenv import load_dotenv
from pprint import pprint

from telebot import TeleBot

from http import HTTPStatus

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}



logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    encoding='utf-8',
    filemode='w'
)


class VarIsNotAvailable(Exception):
    pass


class FormatAnswerIsNotValid(Exception):
    pass

class ResponseDontHaveValidParams(Exception):
    pass

class HTTPStatusIsNotOK(Exception):
    pass

class HomeworkStatusIsNotDocumented(Exception):
    pass

class MessageNotSent(Exception):
    pass


def check_tokens():
    """Checking the availability of environment variables"""
    if not (PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID):
        logging.critical('Env variables are not set')
        sys.exit()
        


def send_message(bot, message):
    """Sends message to Telegram chat"""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message)
        logging.debug(f'Message sent successfully')
    except:
        logging.error(f'Error during sending the message')
        raise MessageNotSent



def get_api_answer(timestamp):
    """Returns the API answer"""
    try:
        homework_statuses = requests.get(ENDPOINT,
                                     headers=HEADERS,
                                     params={'from_date': timestamp})

        response = homework_statuses.json()
        if not type(response) is dict:
            raise FormatAnswerIsNotValid('The format is not valid')
    
        if not homework_statuses.status_code == 200:
            raise HTTPStatusIsNotOK
    except requests.RequestException:
        logging.error('Something went wrong')
    return response


def check_response(response):
    """Checks params in the API response"""

    if not type(response) is dict:
        raise TypeError
    
    if not 'homeworks' in response:
        raise KeyError
    
    if not type(response['homeworks']) is list:
        raise TypeError
    
    if response['homeworks'] == []:
        logging.debug('No status changes')
    
    



def parse_status(homework):
    """Returns the satus of last homework"""
    if 'homework_name' not in homework:
        raise KeyError('homework_name отсутсвует в словаре')
    
    if not homework['status'] or homework['status'] not in HOMEWORK_VERDICTS:
        raise HomeworkStatusIsNotDocumented
    

    last_homework_status = homework['status']
    homework_name = homework['homework_name']
    verdict = HOMEWORK_VERDICTS[last_homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    status = 'send'
    bot = TeleBot(token=TELEGRAM_TOKEN)
    #timestamp = int(time.time())
    timestamp = 10000000
    
    
    while True:
        try:
            check_tokens()
            response = get_api_answer(timestamp)
            check_response(response)
            homework = response['homeworks'][0]
            new_status = homework['status']
            if new_status != status:
                message = parse_status(homework)
                send_message(bot, message)
                status = new_status
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
        time.sleep(RETRY_PERIOD)
    

if __name__ == '__main__':
    main()
