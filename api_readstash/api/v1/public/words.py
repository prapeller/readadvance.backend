import fastapi as fa

from core.enums import OrderEnum, ChatGPTModelsEnum
from core.security import current_user_dependency
from core.shared import pagination_params_dependency
from db.models.user import UserModel
from db.serializers.translations import TranslWordInSerializer
from db.serializers.word import word_params_dependency, WordOrderByEnum, \
    WordsPaginatedSerializer
from services.word_manager.word_manager import WordManager, word_manager_dependency

router = fa.APIRouter()


@router.get("",
            response_model=WordsPaginatedSerializer)
async def words_list(
        word_manager: WordManager = fa.Depends(word_manager_dependency),
        word_params: dict = fa.Depends(word_params_dependency),
        pagination_params: dict = fa.Depends(pagination_params_dependency),
        order_by: WordOrderByEnum = WordOrderByEnum.created_at,
        order: OrderEnum = OrderEnum.desc,
):
    """list words for a language"""
    return await word_manager.list_filtered_paginated_words(word_params,
                                                            pagination_params,
                                                            order_by, order)


@router.post("/get-analyzed-word-translation-with-nlp-api")
async def translations_translate_word_with_gpt(
        transl_word_in_ser: TranslWordInSerializer,
        word_manager: WordManager = fa.Depends(word_manager_dependency),
):
    """get word translation with nlp api"""
    return await word_manager.get_analyzed_word_translation_with_nlp_api(transl_word_in_ser)