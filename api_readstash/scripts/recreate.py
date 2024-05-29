from core.constants import LANGUAGES_DICT, LEVEL_SYSTEM_ORDERS_CODES
from core.enums import LanguagesISO2NamesEnum, UserRolesEnum, LevelOrderEnum, LevelSystemNamesEnum
from db import SessionLocalAsync
from db.models.language import LanguageModel
from db.models.level import LevelModel
from db.serializers.language import LanguageCreateSerializer
from db.serializers.level import LevelCreateSerializer
from db.serializers.user import UserCreateSerializer
from services.postgres.repository import SqlAlchemyRepositoryAsync
from services.user_manager.user_manager import UserManager

test_users = [
    {
        'email': 'head_test@mail.ru',
        'name': 'head_test',
        'password': 'test',
        'roles': [UserRolesEnum.head],
    },
]


async def recreate_test_users():
    """
    Recreate test users in Keycloak and Local DB.
    """
    async with SessionLocalAsync() as session:
        repo_write = SqlAlchemyRepositoryAsync(session)
        user_manager = UserManager(repo_write)
        for user in test_users:
            user_ser = UserCreateSerializer(email=user['email'], first_name=user['name'], roles=user['roles'])
            await user_manager.get_or_create_or_update_user(user_ser, password=user['password'])


async def recreate_languages():
    async with SessionLocalAsync() as session:
        repo = SqlAlchemyRepositoryAsync(session)
        await repo.get_or_create_many(
            LanguageModel, [
                LanguageCreateSerializer(iso2=iso2name, name=LANGUAGES_DICT[iso2name][1])
                for iso2name in LanguagesISO2NamesEnum
            ]
        )


async def recreate_levels():
    async with SessionLocalAsync() as session:
        repo = SqlAlchemyRepositoryAsync(session)
        for lang in await repo.list_filtered(LanguageModel):
            for order in LevelOrderEnum:
                cefr_code = LEVEL_SYSTEM_ORDERS_CODES[LevelSystemNamesEnum.CEFR].get(order)
                await repo.get_or_create(LevelModel, LevelCreateSerializer(language_uuid=lang.uuid,
                                                                           order=order,
                                                                           cefr_code=cefr_code))
