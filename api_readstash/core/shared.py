import base64
import datetime as dt
import re
import uuid
from enum import Enum

from core import config
from core.config import settings
from core.enums import ResponseDetailEnum
from core.exceptions import NotValidPlaceholdersException, UnprocessableEntityException
from db.models.file_storage import FileIndexModel


def singleton_decorator(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


async def custom_serialize(
        obj: dict | bytes | str | Enum | list | None) -> dict | list | str | int | float | dt.datetime | None:
    if obj is None \
            or isinstance(obj, str) \
            or isinstance(obj, int) \
            or isinstance(obj, float) \
            or isinstance(obj, dt.datetime):
        return obj
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    elif isinstance(obj, Enum) \
            or isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, list):
        for x in obj:
            x = await custom_serialize(x)
        return obj
    elif isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = await custom_serialize(value)
        return obj
    else:
        raise NotImplementedError(f'not implemented for {type(obj)}')


def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def validate_placeholders(text: str, PlaceholdersEnum: type[Enum]):
    """validate if placeholders in text are from passed Enum only
    if any others found - raise corresponding error
    """
    valid_placeholders = [p.value for p in PlaceholdersEnum]
    if text:
        found_placeholders = re.findall(r'\{\{.*?}}', text)
        if found_placeholders:
            not_valid_placeholders = []
            for p in found_placeholders:
                if p not in valid_placeholders:
                    not_valid_placeholders.append(p)
            if not_valid_placeholders:
                detail = f"{ResponseDetailEnum.not_valid_placeholders} {not_valid_placeholders}"
                raise NotValidPlaceholdersException(detail)
    else:
        detail = f'text must be not empty, with any of the following placeholders: {valid_placeholders}'
        raise UnprocessableEntityException(detail)


def generate_file_url(bg_image_file_index: FileIndexModel) -> str:
    if config.DEBUG:
        return (f'{settings.API_MENU_STATIC_FILES_PUBLIC_URL}:{settings.API_MENU_PORT}'
                f'/api/v1/files/{bg_image_file_index.uuid}')
    else:
        return (f'{settings.API_MENU_STATIC_FILES_PUBLIC_URL}'
                f'/api/v1/files/{bg_image_file_index.uuid}')


async def pagination_params_dependency(limit: int = 50, offset: int = 0):
    return {
        'limit': limit,
        'offset': offset
    }
