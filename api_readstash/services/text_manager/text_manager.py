import fastapi as fa

from core.constants import CELERY_TASK_PRIORITIES
from core.enums import ChatGPTModelsEnum, ResponseDetailEnum, DBSessionModeEnum, UserTextStatusEnum, \
    TasksNamesEnum
from core.exceptions import AlreadyExistsException
from db.models.association import UserTextStatusAssoc
from db.models.text import TextModel
from db.models.word import WordModel
from db.serializers.association import UserTextStatusCreateSerializer, UserTextStatusUpdateSerializer
from db.serializers.text import TextUpdateSerializer, TextCreateSerializer
from services.postgres.repository import SqlAlchemyRepositoryAsync, sqlalchemy_repo_async_dependency, \
    sqlalchemy_repo_async_read_dependency
from services.text_manager.celery_tasks import texts_identify_language_and_level_task
from services.text_manager.chatgpt_helpers import identify_text_language_chatgpt, identify_text_level_chatgpt
from services.text_manager.logger_setup import logger


class TextManager:
    def __init__(self,
                 repo_write: SqlAlchemyRepositoryAsync,
                 repo_read: SqlAlchemyRepositoryAsync = None):
        self.repo_write = repo_write
        self.repo_read = repo_read

    async def get_text(self,
                       uuid: str,
                       session_mode: DBSessionModeEnum = DBSessionModeEnum.r,
                       raise_if_not_found=True,
                       ) -> TextModel:

        if session_mode == DBSessionModeEnum.r:
            assert self.repo_read is not None, 'repo_read must be provided'
            text = await self.repo_read.get(TextModel, raise_if_not_found=raise_if_not_found, uuid=uuid)
        else:  # session_mode == DBSessionModeEnum.rw:
            text = await self.repo_write.get(TextModel, raise_if_not_found=raise_if_not_found, uuid=uuid)
        return text

    async def create_text(self,
                          text_ser: TextCreateSerializer,
                          gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4):
        is_created, text = await self.repo_write.get_or_create(TextModel, text_ser)
        if not is_created:
            raise AlreadyExistsException(f'this text already exists')
        logger.debug(f'Created {text=}, starting celery {TasksNamesEnum.texts_identify_language_and_level_task}...')

        texts_identify_language_and_level_task.apply_async(
            args=[text.uuid, gpt_model],
            queue='default',
            priority=CELERY_TASK_PRIORITIES[TasksNamesEnum.texts_identify_language_and_level_task]
        )
        return text

    async def update_text(self, text_uuid: str, text_ser: TextUpdateSerializer,
                          exclude_none=True, exclude_unset=True) -> WordModel:
        text = await self.repo_write.get(TextModel, raise_if_not_found=True, uuid=text_uuid)
        text = await self.repo_write.update(text, text_ser, exclude_none=exclude_none, exclude_unset=exclude_unset)
        logger.debug(f'updated {text=}')
        return text

    async def remove_text(self, text_uuid):
        res = await self.repo_write.remove_by_uuid(TextModel, text_uuid)
        logger.debug(f'removed {text_uuid=}')
        return res

    async def identify_text_language_with_chatgpt(
            self,
            text_uuid: str,
            gpt_model: ChatGPTModelsEnum,
    ) -> TextModel:
        text = await self.get_text(text_uuid, session_mode=DBSessionModeEnum.rw)
        language_iso_2 = await identify_text_language_chatgpt(text.content, gpt_model)
        text = await self.repo_write.update(text, TextUpdateSerializer(language_iso_2=language_iso_2))
        return text

    async def identify_text_level_with_chatgpt(
            self,
            text_uuid: str,
            gpt_model: ChatGPTModelsEnum,
    ) -> TextModel:
        text = await self.get_text(text_uuid, session_mode=DBSessionModeEnum.rw)
        level_cefr_code = await identify_text_level_chatgpt(text.content, gpt_model)
        text = await self.repo_write.update(text, TextUpdateSerializer(level_cefr_code=level_cefr_code))
        return text

    async def add_to_users_texts_with_status(self,
                                             user_uuid: str,
                                             text_uuid: str,
                                             status: UserTextStatusEnum,
                                             ) -> dict:
        """add word to user_text_status if not exists, or update status"""

        assoc = await self.repo_write.get(UserTextStatusAssoc, text_uuid=text_uuid, user_uuid=user_uuid)
        if assoc is None:
            await self.repo_write.create(UserTextStatusAssoc,
                                         UserTextStatusCreateSerializer(text_uuid=text_uuid,
                                                                        user_uuid=user_uuid,
                                                                        status=status))
        else:
            await self.repo_write.update(assoc, UserTextStatusUpdateSerializer(status=status))
        return {"detail": ResponseDetailEnum.ok}


async def text_manager_dependency(
        repo_write: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_dependency),
        repo_read: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_read_dependency),
) -> TextManager:
    return TextManager(repo_write=repo_write, repo_read=repo_read)
