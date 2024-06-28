from http import HTTPStatus
import logging
import os
import sys
import time

from dotenv import load_dotenv
import requests
import telebot

import exceptions


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


def check_tokens():
    """Checking the availability of environment variables."""
    token_flag = True

    if not PRACTICUM_TOKEN:
        token_flag = False
        logging.critical('PRACTICUM_TOKEN is not set')

    if not TELEGRAM_TOKEN:
        token_flag = False
        logging.critical('TELEGRAM_TOKEN is not set')

    if not TELEGRAM_CHAT_ID:
        token_flag = False
        logging.critical('TELEGRAM_CHAT_ID is not set')

    return token_flag
        

def send_message(bot, message):
    """Sends message to Telegram chat."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message)
        logging.debug('Message sent successfully')
        return True
    except (telebot.apihelper.ApiException,
            requests.RequestException) as error:
        return False
    

def get_api_answer(timestamp):
    """Returns the API answer."""
    try:
        homework_statuses = requests.get(ENDPOINT,
                                         headers=HEADERS,
                                         params={'from_date': timestamp})
    except requests.RequestException as error:
        return error

    if not homework_statuses.status_code == HTTPStatus.OK:
        raise exceptions.HTTPStatusIsNotOK('The response status is Not 200')

    return homework_statuses.json()

        
def check_response(response):
    """Checks params in the API response."""
    if not isinstance(response, dict):
        raise TypeError('Response is not an instance of a subtype of the dict type')

    if 'homeworks' not in response:
        raise KeyError('Response does not have valid params: homeworks')

    if not isinstance(response['homeworks'], list):
        raise TypeError('Param homeworks is not an instance of a subtype of the list type')


def parse_status(homework):
    """Returns the satus of last homework."""
    status = homework['status']

    if 'homework_name' not in homework:
        raise KeyError('homework_name is not in dict')

    if not status:
        raise exceptions.HomeworkStatusIsNotDocumented(
            'The homework does not have a status'
        )
    
    if status not in HOMEWORK_VERDICTS:
        raise exceptions.HomeworkStatusIsNotDocumented(
            'The status of homework is not documented'
        )

    homework_name = homework['homework_name']
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Main func of the bot."""
    if not check_tokens():
        sys.exit()
    bot = telebot.TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    status = 'send'
    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            homeworks = response['homeworks']
            if not homeworks:
                logging.debug('No status changes')
            else:
                homework = homeworks[0]
                new_status = homework['status']
                if new_status != status:
                    message = parse_status(homework)
                    if send_message(bot, message):
                        status = new_status
                    else:
                        logging.error('Error during sending the message')
        except Exception as error:
            message = f'Error while running the program: {error}'
            logging.error(message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
