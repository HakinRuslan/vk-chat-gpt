import os
from typing import List
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger


class Settings(BaseSettings):
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"
    CONFIRMATION_TOKEN: str
    SECRET_KEY: str
    group_access_token: str
    GROUP_ID: int
    url_for_send_operator: str
    openai_api_key: str
    url_redis: str
    operator_id: int
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    my_email: str
    my_password_for_email: str
    temps_dir: str = "app/temps"
    email_to: str
    email_to_another: str


    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        extra="ignore"
    )


settings = Settings()