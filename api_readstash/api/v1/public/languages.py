import fastapi as fa

from db.models.language import LanguageModel
from db.serializers.language import LanguageReadSerializer
from services.postgres.repository import SqlAlchemyRepositoryAsync, sqlalchemy_repo_async_read_dependency

router = fa.APIRouter()


@router.get("/",
            response_model=list[LanguageReadSerializer])
async def languages_list(
        repo: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_read_dependency),
):
    """list all languages"""
    return await repo.list_filtered(LanguageModel)
