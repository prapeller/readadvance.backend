import os
from pathlib import Path

import pydantic as pd
import pydantic_settings as ps


class Settings(ps.BaseSettings):
    API_READSTASH_HOST: str
    API_READSTASH_PORT: int

    PROJECT_NAME: str
    DOCS_URL: str = 'docs'

    SMTP_HOST: str
    SMTP_PORT: int
    EMAILS_FROM_EMAIL: pd.EmailStr

    # postgres_readstash
    # write (operations to master (or read-write if read from master before write))
    POSTGRES_READSTASH_HOST: str
    POSTGRES_READSTASH_PORT: int
    POSTGRES_READSTASH_USER: str
    POSTGRES_READSTASH_DB: str
    POSTGRES_READSTASH_PASSWORD: str

    # read (operations to slave)
    POSTGRES_READSTASH_READ_HOST: str
    POSTGRES_READSTASH_READ_PORT: int
    POSTGRES_READSTASH_READ_USER: str
    POSTGRES_READSTASH_READ_DB: str
    POSTGRES_READSTASH_READ_PASSWORD: str

    # postgres_object_storage
    # write (operations to master (or read-write if read from master before write))
    POSTGRES_OBJECT_STORAGE_HOST: str
    POSTGRES_OBJECT_STORAGE_PORT: int
    POSTGRES_OBJECT_STORAGE_USER: str
    POSTGRES_OBJECT_STORAGE_DB: str
    POSTGRES_OBJECT_STORAGE_PASSWORD: str

    # read (operations to slave)
    POSTGRES_OBJECT_STORAGE_READ_HOST: str
    POSTGRES_OBJECT_STORAGE_READ_PORT: int
    POSTGRES_OBJECT_STORAGE_READ_USER: str
    POSTGRES_OBJECT_STORAGE_READ_DB: str
    POSTGRES_OBJECT_STORAGE_READ_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int

    KEYCLOAK_BASE_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_REDIRECT_URL: pd.AnyHttpUrl
    KEYCLOAK_ADMIN: str
    KEYCLOAK_ADMIN_PASSWORD: str
    KEYCLOAK_CLIENT_SECRET: str

    OPENAI_API_KEY: str

    INTER_SERVICE_SECRET: str

    API_HEAD_USER_EMAIL: pd.EmailStr
    API_HEAD_USER_NAME: str
    API_HEAD_USER_PASSWORD: str

    class Config:
        extra = 'allow'

    def __init__(self, DOCKER, DEBUG, BASE_DIR):
        if DEBUG and DOCKER:
            super().__init__(_env_file=[BASE_DIR / '../.envs/.docker-compose-local/.api_readstash',
                                        BASE_DIR / '../.envs/.docker-compose-local/.postgres_readstash',
                                        BASE_DIR / '../.envs/.docker-compose-local/.postgres_object_storage',
                                        BASE_DIR / '../.envs/.docker-compose-local/.redis_readstash',
                                        ])
        elif DEBUG and not DOCKER:
            super().__init__(_env_file=[BASE_DIR / '../.envs/.local/.api_readstash',
                                        BASE_DIR / '../.envs/.local/.postgres_readstash',
                                        BASE_DIR / '../.envs/.local/.postgres_object_storage',
                                        BASE_DIR / '../.envs/.local/.redis_readstash',
                                        ])
        else:
            super().__init__(_env_file=[BASE_DIR / '../.envs/.docker-compose-prod/.api_readstash',
                                        BASE_DIR / '../.envs/.docker-compose-prod/.postgres_readstash',
                                        BASE_DIR / '../.envs/.docker-compose-prod/.postgres_object_storage',
                                        BASE_DIR / '../.envs/.docker-compose-prod/.redis_readstash',
                                        ])


DEBUG = os.getenv('DEBUG', False) == 'True'
DOCKER = os.getenv('DOCKER', False) == 'True'
BASE_DIR = Path(__file__).resolve().parent.parent

settings = Settings(DOCKER, DEBUG, BASE_DIR)

POSTGRES_DEBUG = os.getenv('POSTGRES_DEBUG', False) == 'True'
ACCEPTABLE_HMAC_TIME_SECONDS = 10
REDIS_CACHE_EXPIRES_IN_SECONDS = 5 * 60
