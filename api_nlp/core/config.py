import os
from pathlib import Path

import pydantic_settings as ps


class Settings(ps.BaseSettings):
    API_NLP_HOST: str
    API_NLP_PORT: int

    PROJECT_NAME: str
    DOCS_URL: str = 'docs'

    INTER_SERVICE_SECRET: str

    class Config:
        extra = 'allow'

    def __init__(self, DOCKER, DEBUG, BASE_DIR):
        if DEBUG and DOCKER:
            super().__init__(_env_file=[
                BASE_DIR / '../.envs/.docker-compose-local/.api_nlp',
            ])
        elif DEBUG and not DOCKER:
            super().__init__(_env_file=[
                BASE_DIR / '../.envs/.local/.api_nlp',
            ])
        else:
            super().__init__(_env_file=[
                BASE_DIR / '../.envs/.docker-compose-prod/.api_nlp',
            ])


DEBUG = os.getenv('DEBUG', False) == 'True'
DOCKER = os.getenv('DOCKER', False) == 'True'
BASE_DIR = Path(__file__).resolve().parent.parent

settings = Settings(DOCKER, DEBUG, BASE_DIR)

POSTGRES_DEBUG = os.getenv('POSTGRES_DEBUG', False) == 'True'
ACCEPTABLE_HMAC_TIME_SECONDS = 10
