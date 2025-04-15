import logging
from loguru import logger
from pathlib import Path
import asyncio

import emails
from emails.template import JinjaTemplate

from config import *

password_reset_jwt_subject = "preset"

async def send_email_with_appl_async(appls: str, email_to: str):
    # Выполняем синхронную функцию в фоновом потоке
    await asyncio.to_thread(send_email_with_appl, appls, email_to)

def send_email_fn(email_to: str, subject_template="", html_template="", environment={}):
    assert True, "no provided configuration for email variables"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.my_email),
    )
    smtp_options = {"host": settings.smtp_host, "port": settings.smtp_port}
    smtp_options["tls"] = True
    smtp_options["user"] = settings.my_email
    smtp_options["password"] = settings.my_password_for_email
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logger.info(f"send email result: {response}")


def send_email_with_appl(appls: str, email_to):
    template_str = None
    subject = "Заявка"
    template_path = Path(__file__).resolve().parent.parent / "temps" / "send_appls.html"

    with open(template_path, encoding="utf-8") as f:
        template_str = f.read()
    send_email_fn(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "appls": appls,
        }
    )
