import logging
import smtplib
import ssl
from abc import ABC, abstractmethod
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Notificator(ABC):
    @abstractmethod
    def send_notification(self, dest: str, subject: str, message: str, attachments: list):
        pass


class EmailNotificator(Notificator):

    def __init__(self, smtp_server: str, smtp_port: int, smtp_username: str,
                 smtp_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_addr = 'automation@abaruchi.dev'

    def send_notification(self, dest: str, subject: str, message: str, attachments: list):
        msg = MIMEMultipart()
        msg['From'] = self.from_addr
        msg['To'] = dest
        msg['Subject'] = subject
        msg.attach(MIMEText(message))

        logging.debug(f'number of attachments: {len(attachments)}')
        for i, file_to_attach in enumerate(attachments):
            attach_name = f'attachment-{i}.png'
            bin_file = open(file_to_attach, 'rb')
            payload = MIMEBase('application', 'octet-stream', Name=attach_name)
            payload.set_payload(bin_file.read())
            encoders.encode_base64(payload)
            payload.add_header('Content-Disposition', 'attachment', filename=attach_name)
            msg.attach(payload)

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
            server.login(self.smtp_username, self.smtp_password)
            logging.info(f'Sending email to {dest}')
            server.sendmail(
                self.from_addr, dest, msg.as_string()
            )


def notificator_builder(type: str, params: dict) -> Notificator:
    """
    Builds a notificator based on the given type and parameters.

    :param type: The type of notificator to build. Currently supported types are "email".
    :param params: The parameters required to build the notificator. For "email" type, the following
                   parameters are required: "smtp_server", "smtp_port", "smtp_username", "smtp_password".
    :return: The built notificator instance.
    """

    if type == "email":
        return EmailNotificator(
            params['smtp_server'], params['smtp_port'], params['smtp_username'], params['smtp_password']
        )
