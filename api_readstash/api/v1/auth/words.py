import fastapi as fa
import pydantic as pd

from core.enums import ChatGPTModelsEnum, OrderEnum, UserWordStatusEnum
from core.security import current_user_dependency, auth_head_or_admin, auth_head
from core.shared import pagination_params_dependency
from db.models.user import UserModel
from db.serializers.word import word_params_dependency, WordReadSerializer, WordCreateSerializer, WordOrderByEnum, \
    WordsPaginatedSerializer, WordUpdateSerializer
from services.word_manager.word_manager import WordManager, word_manager_dependency

router = fa.APIRouter()


@router.get("/my",
            response_model=WordsPaginatedSerializer)
async def words_list_my(
        word_manager: WordManager = fa.Depends(word_manager_dependency),
        word_params: dict = fa.Depends(word_params_dependency),
        status: UserWordStatusEnum = UserWordStatusEnum.to_learn,
        pagination_params: dict = fa.Depends(pagination_params_dependency),
        order_by: WordOrderByEnum = WordOrderByEnum.created_at,
        order: OrderEnum = OrderEnum.desc,
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    return await word_manager.list_filtered_paginated_users_words_by_status(current_user.uuid,
                                                                            word_params,
                                                                            pagination_params,
                                                                            order_by, order,
                                                                            status)


@router.get("/{word_uuid}",
            response_model=WordReadSerializer)
async def words_read(
        word_uuid: pd.UUID4,
        word_manager: WordManager = fa.Depends(word_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """get word by uuid"""
    return await word_manager.get_word(str(word_uuid))


@router.post("/add-to-my/{word_uuid}")
async def words_add_to_my_with_status(
        word_uuid: pd.UUID4,
        status: UserWordStatusEnum,
        word_manager: WordManager = fa.Depends(word_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """add to users words with status"""
    return await word_manager.add_to_users_words_with_status(current_user.uuid, str(word_uuid), status)


@router.post("", response_model=WordReadSerializer)
# @auth_head_or_admin
async def words_create(
        word_ser: WordCreateSerializer,
        gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_4,
        word_manager: WordManager = fa.Depends(word_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """create word by admin"""
    return await word_manager.create_word(word_ser, gpt_model)


@router.put("/identify-word-level-with-chatgpt/{word_uuid}", response_model=WordReadSerializer)
# @auth_head_or_admin
async def words_identify_word_level(
        word_uuid: pd.UUID4,
        gpt_model: ChatGPTModelsEnum = ChatGPTModelsEnum.gpt_3_5,
        word_manager: WordManager = fa.Depends(word_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """identify word level with chatgpt"""
    return await word_manager.identify_word_level_with_chatgpt(word_uuid, gpt_model)


@router.put("/{word_uuid}", response_model=WordReadSerializer)
@auth_head_or_admin
async def words_update(
        word_uuid: pd.UUID4,
        word_ser: WordUpdateSerializer,
        word_manager: WordManager = fa.Depends(word_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """update word manually"""
    return await word_manager.update_word(word_uuid, word_ser)


@router.delete("/{word_uuid}")
@auth_head
async def words_remove(
        word_uuid: pd.UUID4,
        word_manager: WordManager = fa.Depends(word_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """remove word"""
    return await word_manager.remove_word(str(word_uuid))
