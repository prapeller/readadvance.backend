from core.config import settings
from core.constants import LANGUAGES_DICT, LEVEL_SYSTEM_ORDERS_CODES
from core.enums import LanguagesISO2NamesEnum, UserRolesEnum, LevelOrderEnum, LevelSystemNamesEnum
from db import SessionLocalAsync
from db.models.language import LanguageModel
from db.models.level import LevelModel
from db.serializers.language import LanguageCreateSerializer
from db.serializers.level import LevelCreateSerializer
from db.serializers.user import UserCreateSerializer, UserUpdateSerializer
from services.keycloak.keycloak import KCAdmin, kc_admin_dependency
from services.postgres.repository import SqlAlchemyRepositoryAsync


async def recreate_head_user_in_kc():
    """recreates head user in keycloak if it does not exist or sync with kc if it does exist with the same email"""

    head_email = settings.API_HEAD_USER_EMAIL
    head_name = settings.API_HEAD_USER_NAME
    head_password = settings.API_HEAD_USER_PASSWORD
    head_roles = [UserRolesEnum.head]

    kc_admin_async: KCAdmin = kc_admin_dependency()
    kc_user = await kc_admin_async.get_user_by_email_async(head_email)

    if kc_user is None:
        kc_user = await kc_admin_async.create_user_async(
            user_ser=UserCreateSerializer(email=head_email, first_name=head_name, last_name=''))
        await kc_admin_async.set_password_async(kc_user.uuid, head_password)
    elif kc_user:
        await kc_admin_async.update_user_names_async(kc_user.uuid,
                                                     UserUpdateSerializer(first_name=head_name, last_name=''))
        await kc_admin_async.update_user_roles_async(kc_user.uuid, UserUpdateSerializer(roles=head_roles))
    await kc_admin_async.verify_async(kc_user.uuid)


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
