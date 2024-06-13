import fastapi as fa
import pydantic as pd

from core.constants import CELERY_TASK_PRIORITIES
from core.enums import ChatGPTModelsEnum, UserTextStatusEnum, TasksNamesEnum, QueueNamesEnum
from core.security import current_user_dependency, auth_head_or_admin, auth_head
from db.models.user import UserModel
from db.serializers._shared import TaskReadSerializer
from db.serializers.text import TextReadContentSerializer, TextCreateSerializer, TextUpdateSerializer, \
    TextReadNoContentSerializer
from services.text_manager.celery_tasks import texts_identify_level_task, texts_identify_language_task
from services.text_manager.text_manager import TextManager, text_manager_dependency

router = fa.APIRouter()


@router.get("/{text_uuid}",
            response_model=TextReadContentSerializer)
async def texts_read(
        text_uuid: pd.UUID4,
        text_manager: TextManager = fa.Depends(text_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """get text by uuid"""
    return await text_manager.get_text(str(text_uuid))


@router.post("/add-to-my/{text_uuid}")
async def texts_add_to_my_with_status(
        text_uuid: pd.UUID4,
        status: UserTextStatusEnum,
        text_manager: TextManager = fa.Depends(text_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """add to users texts with status"""
    return await text_manager.add_to_users_texts_with_status(current_user.uuid, str(text_uuid), status)


@router.post("/", response_model=TextReadContentSerializer)
async def texts_create(
        text_ser: TextCreateSerializer,
        gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4,
        text_manager: TextManager = fa.Depends(text_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """create text by admin"""
    text_ser.user_uuid = current_user.uuid
    return await text_manager.create_text(text_ser, gpt_model)


@router.put("/identify-level-sync/{text_uuid}", response_model=TextReadNoContentSerializer)
@auth_head_or_admin
async def texts_identify_text_level(
        text_uuid: pd.UUID4,
        gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4,
        text_manager: TextManager = fa.Depends(text_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """identify text level with chatgpt"""
    return await text_manager.identify_text_level(text_uuid, gpt_model)


@router.put("/identify-language-sync/{text_uuid}", response_model=TextReadNoContentSerializer)
@auth_head_or_admin
async def texts_identify_text_language(
        text_uuid: pd.UUID4,
        gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4,
        text_manager: TextManager = fa.Depends(text_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """identify text level with chatgpt"""
    return await text_manager.identify_text_language(text_uuid, gpt_model)


@router.put("/identify-level/{text_uuid}", response_model=TaskReadSerializer)
async def texts_identify_text_level(
        text_uuid: pd.UUID4,
        gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4,
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """identify text level with chatgpt as background task"""
    task = texts_identify_level_task.apply_async(
        args=[text_uuid, gpt_model],
        queue=QueueNamesEnum.default,
        priority=CELERY_TASK_PRIORITIES[TasksNamesEnum.texts_identify_level_task])
    return TaskReadSerializer(task_id=task.task_id)


@router.put("/identify-language/{text_uuid}", response_model=TaskReadSerializer)
async def texts_identify_text_language(
        text_uuid: pd.UUID4,
        gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4,
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """identify text level with chatgpt"""
    task = texts_identify_language_task.apply_async(
        args=[text_uuid, gpt_model],
        queue=QueueNamesEnum.default,
        priority=CELERY_TASK_PRIORITIES[TasksNamesEnum.texts_identify_language_task])
    return TaskReadSerializer(task_id=task.task_id)


@router.put("/{text_uuid}", response_model=TextReadContentSerializer)
@auth_head_or_admin
async def texts_update(
        text_uuid: pd.UUID4,
        text_ser: TextUpdateSerializer,
        text_manager: TextManager = fa.Depends(text_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """update text manually"""
    return await text_manager.update_text(text_uuid, text_ser)


@router.delete("/{text_uuid}")
@auth_head
async def texts_remove(
        text_uuid: pd.UUID4,
        text_manager: TextManager = fa.Depends(text_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """remove text"""
    return await text_manager.remove_text(str(text_uuid))
