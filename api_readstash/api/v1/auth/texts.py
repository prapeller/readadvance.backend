import fastapi as fa
import pydantic as pd

from core.enums import ChatGPTModelsEnum, UserTextStatusEnum
from core.security import current_user_dependency, auth_head_or_admin, auth_head
from db.models.user import UserModel
from db.serializers.text import TextReadContentSerializer, TextCreateSerializer, TextUpdateSerializer
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


@router.put("/identify-text-language-with-chatgpt/{text_uuid}", response_model=TextReadContentSerializer)
@auth_head_or_admin
async def texts_identify_text_language(
        text_uuid: pd.UUID4,
        gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_3_5,
        text_manager: TextManager = fa.Depends(text_manager_dependency),
):
    """identify text language with chatgpt and update it"""
    return await text_manager.identify_text_language_with_chatgpt(str(text_uuid), gpt_model)


@router.put("/identify-text-level-with-chatgpt/{text_uuid}", response_model=TextReadContentSerializer)
@auth_head_or_admin
async def texts_identify_text_level(
        text_uuid: pd.UUID4,
        gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_3_5,
        text_manager: TextManager = fa.Depends(text_manager_dependency),
):
    """identify text level with chatgpt and update it"""
    return await text_manager.identify_text_level_with_chatgpt(str(text_uuid), gpt_model)


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
