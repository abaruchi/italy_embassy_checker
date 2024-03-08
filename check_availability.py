import datetime as dt
import logging
import os
import sys
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from notification import Notificator, notificator_builder

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)s:%(module)s %(funcName)s: %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)

DEFAULT_TIMEOUT_SEC = 10


def load_config() -> dict:
    """
    Load configuration values from environment variables.

    :return: A dictionary containing configuration values.
    """
    load_dotenv()
    ret_dict = dict()

    ret_dict['smtp_server'] = os.getenv('SMTP_SERVER')
    ret_dict['smtp_port'] = os.getenv('SMTP_PORT')
    ret_dict['smtp_username'] = os.getenv('SMTP_USERNAME')
    ret_dict['smtp_password'] = os.getenv('SMTP_PASSWORD')
    ret_dict['screenshot_dir'] = os.getenv('SCREENSHOT_DIR')
    ret_dict['embassy_username'] = os.getenv('EMBASSY_USERNAME')
    ret_dict['embassy_password'] = os.getenv('EMBASSY_PASSWORD')
    ret_dict['embassy_http_server'] = os.getenv('EMBASSY_HTTP_SERVER')

    return ret_dict

def create_timestamp(clock: dt.datetime) -> str:
    """
    Returns a formatted timestamp string based on the given clock time.

    :param clock: The datetime object representing the clock time.
    :return: The formatted timestamp string.
    """
    format_string = '%Y-%m-%d_%H:%M'
    return clock.strftime(format_string)


class CheckAvailability(object):

    def __init__(self, url: str, web_driver: webdriver, user_login: str, user_password: str, screenshot_dir: str,
                 notificator: Notificator):
        self.user_login = user_login
        self.user_password = user_password
        self.url = url
        self.web_driver = web_driver
        self.screenshot_dir = screenshot_dir
        self.notificator = notificator

        if not os.path.isdir(self.screenshot_dir):
            logging.info(f'directory {self.screenshot_dir} does not exist, creating')
            os.makedirs(self.screenshot_dir, exist_ok=True)

    def check_availability(self):
        logging.info(f'logging to url {self.url}')
        self.web_driver.get(self.url)
        self.web_driver.find_element(By.ID, "login-email").send_keys(self.user_login)
        self.web_driver.find_element(By.ID, "login-password").send_keys(self.user_password)
        time.sleep(5)
        self.web_driver.find_element(By.CLASS_NAME, "g-recaptcha").click()
        try:
            WebDriverWait(driver=self.web_driver, timeout=DEFAULT_TIMEOUT_SEC).until(
                EC.presence_of_element_located((By.ID, 'showImage'))
            )
        except Exception as e:
            logging.error(f'Could Not login, error: {e}')
            sys.exit(1)

        logging.info(f'landing page loaded')
        self.web_driver.find_element(By.ID, 'advanced').click()
        WebDriverWait(driver=self.web_driver, timeout=DEFAULT_TIMEOUT_SEC).until(
            EC.presence_of_element_located((By.ID, 'dataTableServices_wrapper'))
        )
        logging.info(f'service page loaded')

        self.web_driver.get('https://prenotami.esteri.it/Services/Booking/908')
        try:
            WebDriverWait(driver=self.web_driver, timeout=DEFAULT_TIMEOUT_SEC).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'jconfirm-content'))
            )
            msg = self._build_message('date_unavailable')
            self.notificator.send_notification(self.user_login, msg['subject'], msg['message'], [])
        except:
            logging.info(f'Dates Might be Available')
            timestamp = dt.datetime.now()
            ts = create_timestamp(timestamp)
            self.web_driver.save_screenshot(f'/tmp/{ts}_screenshot.png')
            logging.info(f'Saving screenshot to /tmp/{ts}_screenshot.png')
            msg = self._build_message('date_available')
            self.notificator.send_notification(self.user_login, msg['subject'], msg['message'],
                                               [f'/tmp/{ts}_screenshot.png'])
        self.web_driver.close()

    def _build_message(self, message_type: str) -> dict:
        """
        Build a message based on the given type.

        :param message_type: The type of message to build. Possible values are 'date_unavailable' and 'date_available'.
        :return: A dictionary containing the subject and message of the built message.
        """
        if message_type == 'date_unavailable':
            subject = 'Booking NOT Available'
            message = 'Booking dates not Available, please check later.'
            return {'subject': subject, 'message': message}

        if message_type == 'date_available':
            subject = 'Booking Dates AVAILABLE'
            message = 'Booking dates might be available, please check at the site.'
            return {'subject': subject, 'message': message}


def main():
    configuration = load_config()

    email_params = {
        'smtp_server': configuration['smtp_server'],
        'smtp_port': configuration['smtp_port'],
        'smtp_username': configuration['smtp_username'],
        'smtp_password': configuration['smtp_password']
    }
    email_notificator = notificator_builder('email', email_params)

    op = webdriver.ChromeOptions()
    # op.add_argument('headless')
    op.add_argument("--disable-gpu")
    op.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(op)
    driver.delete_all_cookies()

    checker_params = {
        'username': configuration['embassy_username'],
        'password': configuration['embassy_password'],
        'login_url': configuration['embassy_http_server']
    }

    availability_checker = CheckAvailability(
        url=checker_params['login_url'], web_driver=driver, user_login=checker_params['username'],
        notificator=email_notificator, screenshot_dir=configuration['screenshot_dir'],
        user_password=checker_params['password'])
    availability_checker.check_availability()


if __name__ == '__main__':
    main()
