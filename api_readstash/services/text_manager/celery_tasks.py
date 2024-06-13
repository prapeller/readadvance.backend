import asyncio

import backoff

from celery_app import celery_app
from core.enums import TasksNamesEnum, ChatGPTModelsEnum
from db import SessionLocalAsync
from db.models.language import LanguageModel
from db.models.level import LevelModel
from db.models.text import TextModel
from db.serializers.text import TextUpdateSerializer
from services.chatgpt.text_identifier import get_text_level_chatgpt, get_text_language_chatgpt
from services.postgres.repository import SqlAlchemyRepositoryAsync
from services.text_manager.logger_setup import logger


async def identify_text_level(text_uuid: str, gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4):
    async with SessionLocalAsync() as session:
        repo = SqlAlchemyRepositoryAsync(session)
        try:
            text = await repo.get(TextModel, raise_if_not_found=True, uuid=text_uuid)
            level_code = await get_text_level_chatgpt(text.content, gpt_model)
            level = await repo.get(LevelModel, cefr_code=level_code)
            text = await repo.update(text, TextUpdateSerializer(level_uuid=level.uuid))
            logger.debug(f'updated {text=} level to {level=}')
        except Exception as e:
            detail = (f'{TasksNamesEnum.texts_identify_language_and_level_task} failed with {text_uuid=}: '
                      f'identify_text_level_async: {e.__class__.__name__}: {e}')
            logger.error(detail)
            # notify admin in future
            raise e


async def identify_text_language(text_uuid: str, gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4):
    async with SessionLocalAsync() as session:
        repo = SqlAlchemyRepositoryAsync(session)
        try:
            text = await repo.get(TextModel, raise_if_not_found=True, uuid=text_uuid)
            lang_iso2 = await get_text_language_chatgpt(text.content, gpt_model)
            language = await repo.get(LanguageModel, iso2=lang_iso2)
            text = await repo.update(text, TextUpdateSerializer(language_uuid=language.uuid))
            logger.debug(f'updated {text=} language to {language=}')
        except Exception as e:
            detail = (f'{TasksNamesEnum.texts_identify_language_and_level_task} failed with {text_uuid=}: '
                      f'identify_text_language_async {e.__class__.__name__}: {e}')
            logger.error(detail)
            # notify admin in future
            raise e


async def identify_text_language_and_level(text_uuid: str,
                                           gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4):
    await identify_text_language(text_uuid, gpt_model)
    await identify_text_level(text_uuid, gpt_model)


@celery_app.task(name=TasksNamesEnum.texts_identify_language_and_level_task)
@backoff.on_exception(backoff.constant, Exception, max_tries=5)
def texts_identify_language_and_level_task(text_uuid: str, gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4):
    logger.debug(f'{TasksNamesEnum.texts_identify_language_and_level_task} started with {text_uuid=}')

    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(identify_text_language_and_level(text_uuid, gpt_model))
    else:
        loop.run_until_complete(identify_text_language_and_level(text_uuid, gpt_model))


@celery_app.task(name=TasksNamesEnum.texts_identify_language_task)
@backoff.on_exception(backoff.constant, Exception, max_tries=5)
def texts_identify_language_task(text_uuid: str, gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4):
    logger.debug(f'{TasksNamesEnum.texts_identify_language_task} started with {text_uuid=}')

    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(identify_text_language(text_uuid, gpt_model))
    else:
        loop.run_until_complete(identify_text_language(text_uuid, gpt_model))


@celery_app.task(name=TasksNamesEnum.texts_identify_level_task)
@backoff.on_exception(backoff.constant, Exception, max_tries=5)
def texts_identify_level_task(text_uuid: str, gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4):
    logger.debug(f'{TasksNamesEnum.texts_identify_level_task} started with {text_uuid=}')

    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(identify_text_level(text_uuid, gpt_model))
    else:
        loop.run_until_complete(identify_text_level(text_uuid, gpt_model))
