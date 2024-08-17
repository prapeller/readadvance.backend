import asyncio
import backoff

from celery_app import celery_app
from core.enums import TasksNamesEnum, ChatGPTModelsEnum
from db import SessionLocalAsync
from db.models.word import WordModel
from db.serializers.word import WordUpdateSerializer
from services.postgres.repository import SqlAlchemyRepositoryAsync
from services.word_manager.chatgpt_helpers import identify_word_level_chatgpt
from services.word_manager.logger_setup import logger


@celery_app.task(name=TasksNamesEnum.words_identify_level_task)
@backoff.on_exception(backoff.constant, Exception, max_tries=5)
def words_identify_level_task(word_uuid: str, gpt_model: ChatGPTModelsEnum):
    logger.debug(f'{TasksNamesEnum.words_identify_level_task} started with {word_uuid=}')

    async def identify_word_level_async(word_uuid: str, gpt_model: ChatGPTModelsEnum):
        async with SessionLocalAsync() as session:
            repo = SqlAlchemyRepositoryAsync(session)
            try:
                word = await repo.get(WordModel, raise_if_not_found=True, uuid=word_uuid)
                level_cefr_code = await identify_word_level_chatgpt(word.characters, word.language_iso_2, gpt_model)
                word = await repo.update(word, WordUpdateSerializer(level_cefr_code=level_cefr_code))
                logger.debug(f'updated {word=} level to {level_cefr_code=}')
            except Exception as e:
                detail = f'{TasksNamesEnum.words_identify_level_task} failed with {word_uuid=}: {e.__class__.__name__}: {e}'
                logger.error(detail)
                # notify admin in future
                raise e

    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(identify_word_level_async(word_uuid, gpt_model))
    else:
        loop.run_until_complete(identify_word_level_async(word_uuid, gpt_model))
