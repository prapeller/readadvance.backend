import asyncio

import backoff

from celery_app import celery_app
from core.enums import TasksNamesEnum, ChatGPTModelsEnum
from db import SessionLocalAsync
from db.models.text import TextModel
from db.serializers.text import TextUpdateSerializer
from services.postgres.repository import SqlAlchemyRepositoryAsync
from services.text_manager.chatgpt_helpers import identify_text_language_chatgpt, identify_text_level_chatgpt
from services.text_manager.logger_setup import logger


async def identify_text_level(text_uuid: str, gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4):
    async with SessionLocalAsync() as session:
        repo = SqlAlchemyRepositoryAsync(session)
        try:
            text = await repo.get(TextModel, raise_if_not_found=True, uuid=text_uuid)
            level_cefr_code = await identify_text_level_chatgpt(text.content, gpt_model)
            text = await repo.update(text, TextUpdateSerializer(level_cefr_code=level_cefr_code))
            logger.debug(f'updated {text=} level to {level_cefr_code=}')
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
            language_iso_2 = await identify_text_language_chatgpt(text.content, gpt_model)
            text = await repo.update(text, TextUpdateSerializer(language_iso_2=language_iso_2))
            logger.debug(f'updated {text=} language to {language_iso_2=}')
        except Exception as e:
            detail = (f'{TasksNamesEnum.texts_identify_language_and_level_task} failed with {text_uuid=}: '
                      f'{e.__class__.__name__}: {e}')
            logger.error(detail)
            # notify admin in future
            raise e


async def identify_text_language_and_level(text_uuid: str,
                                           gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4):
    await identify_text_language(text_uuid, gpt_model)
    await identify_text_level(text_uuid, gpt_model)


# async def create_words_from_text(text_uuid: str, gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4):
#     async with SessionLocalAsync() as session:
#         repo = SqlAlchemyRepositoryAsync(session)
#         word_manager = WordManager(repo)
#         try:
#             text = await repo.get(TextModel, raise_if_not_found=True, uuid=text_uuid)
#             words = await word_manager.get_lemma(text.content, text.language.iso2)
#             for word_characters in words:
#                 await word_manager.create_word_if_not_exists(WordCreateSerializer(characters=word_characters,
#                                                                                   language_uuid=text.language_uuid))
#         except Exception as e:
#             detail = (f'{TasksNamesEnum.texts_create_words_from_text} failed with {text_uuid=}: '
#                       f'{e.__class__.__name__}: {e}')
#             logger.error(detail)
#             # notify admin in future
#             raise e
#
# @celery_app.task(name=TasksNamesEnum.texts_create_words_from_text)
# @backoff.on_exception(backoff.constant, Exception, max_tries=5)
# def texts_create_words_from_text_task(text_uuid: str):
#     logger.debug(f'{TasksNamesEnum.texts_create_words_from_text} started with {text_uuid=}')
#
#     loop = asyncio.get_event_loop()
#     if loop.is_running():
#         asyncio.ensure_future(create_words_from_text(text_uuid))
#     else:
#         loop.run_until_complete(create_words_from_text(text_uuid))

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
