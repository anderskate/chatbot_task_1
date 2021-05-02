import requests
import telegram
import logging
import os
import time
from inspect import cleandoc
from dotenv import load_dotenv


logger = logging.getLogger(__file__)


DEVMAN_URL = 'https://dvmn.org'


class LogsHandler(logging.Handler):
    """Log handler that redirects log messages to telegram chat."""
    def __init__(self, level):
        self.bot_token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TG_ADMIN_CHAT_ID')
        self.bot = telegram.Bot(token=self.bot_token)
        super().__init__(level)

    def emit(self, record):
        """Get formatting log message and send it to telegram chat."""
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)


def send_message_to_telegram(attempt_info, bot_token, chat_id):
    """Send a message about a verified attempt to pass the lesson.

    Send a message to the user in telegram about
    a successful or unsuccessful attempt to pass the lesson.
    """
    lesson_title = attempt_info.get('lesson_title')
    is_negative_result = attempt_info.get('is_negative')
    lesson_url = f'{DEVMAN_URL}{attempt_info.get("lesson_url")}'

    if is_negative_result:
        decision_comment = 'К сожалению, в работе нашлись ошибки.'
    else:
        decision_comment = '''Преподавателю всё понравилось,
                           можно приступать к следущему уроку!'''

    msg = cleandoc(
        f'''У вас проверили работу "{lesson_title}"
        {decision_comment}
        Посмотреть работу можно по ссылке:
        {lesson_url}'''
    )

    bot = telegram.Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=msg)


def wait_for_verification_info(url, api_token, timeout=9, pause=30):
    """Expect devman api to verify lessons.

    Upon successful receipt of a request from the api,
    send the verification information in telegram to the user.
    """

    headers = {
        'Authorization': f'Token {api_token}'
    }
    payload = {}

    bot_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')

    # Pause to try to send a repeat request
    default_pause = 0

    while True:
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout,
                params=payload
            )
            response.raise_for_status()
            response_data = response.json()
            if 'error' in response_data:
                raise requests.exceptions.HTTPError(response_data['error'])
            logger.info(f'New data:\n {response_data}')

            if response_data.get('status') == 'found':
                payload['timestamp'] = response_data.get(
                    'last_attempt_timestamp'
                )
                new_attempts = response_data.get('new_attempts')
                for attempt in new_attempts:
                    send_message_to_telegram(attempt, bot_token, chat_id)
            else:
                payload['timestamp'] = response_data.get(
                    'timestamp_to_request'
                )
        except requests.exceptions.ReadTimeout:
            logger.debug(
                'Request timeout. Try to send request again.')
        except requests.exceptions.ConnectionError:
            logger_msg = cleandoc(
                f'''Problems accessing the site.
                Try to send request again after
                pause in {default_pause} sec.'''
            )

            logger.warning(logger_msg)

            # The first attempt to send a repeated request is instant,
            # then the pause value is set from the function parameters.
            time.sleep(default_pause)
            default_pause = pause
        except requests.exceptions.HTTPError as e:
            logger.warning(e)
        except Exception as e:
            logger.exception(e)


def main():
    load_dotenv()

    logging.basicConfig(
        format='%(levelname)s:%(filename)s:%(message)s',
        level=logging.DEBUG,
    )
    logs_handler = LogsHandler(level=logging.INFO)
    logger.addHandler(logs_handler)

    url = f'{DEVMAN_URL}/api/long_polling'
    api_token = os.getenv('DEVMAN_USER_TOKEN')

    wait_for_verification_info(url, api_token)


if __name__ == '__main__':
    main()
