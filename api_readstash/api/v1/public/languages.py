import fastapi as fa

from core.constants import LANGUAGES_DICT

router = fa.APIRouter()


@router.get('')
async def languages_list(
):
    """list all languages"""
    return LANGUAGES_DICT
