from core.constants import LANGUAGES_DICT, LEVEL_ORDERS_CODES
from core.enums import LanguagesISO2NamesEnum, UserRolesEnum, LevelOrderEnum, LevelSystemNamesEnum
from core.exceptions import AlreadyExistsException
from db import SessionLocalAsync
from db.models.language import LanguageModel
from db.models.level import LevelModel
from db.serializers.language import LanguageCreateSerializer
from db.serializers.level import LevelCreateSerializer
from db.serializers.user import UserCreateSerializer
from db.serializers.word import WordCreateSerializer
from services.postgres.repository import SqlAlchemyRepositoryAsync
from services.text_manager.text_manager import TextManager
from services.user_manager.user_manager import UserManager
from services.word_manager.word_manager import WordManager

test_users = [
    {
        'email': 'head_test@mail.ru',
        'name': 'head_test',
        'password': 'test',
        'roles': [UserRolesEnum.head],
    },
    {
        'email': 'adm_test_readstash@mail.ru',
        'name': 'admin_test',
        'password': 'test',
        'roles': [UserRolesEnum.admin],
    },
    {
        'email': 'guest_test_readstash@mail.ru',
        'name': 'guest_test',
        'password': 'test',
        'roles': [UserRolesEnum.guest],
    },
    {
        'email': 'premium_test_readstash@mail.ru',
        'name': 'premium_test',
        'password': 'test',
        'roles': [UserRolesEnum.premium],
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
        for order in LevelOrderEnum:
            cefr_code = LEVEL_ORDERS_CODES[LevelSystemNamesEnum.CEFR].get(order)
            await repo.get_or_create(LevelModel, LevelCreateSerializer(order=order,
                                                                       cefr_code=cefr_code))


test_words = {
    LanguagesISO2NamesEnum.RU: ('мать', 'отец', 'сестра', 'брат'),
    LanguagesISO2NamesEnum.EN: ('mother', 'father', 'sister', 'brother'),
    LanguagesISO2NamesEnum.FR: ('mère', 'père', 'soeur', 'frère'),
    LanguagesISO2NamesEnum.DE: ('mutter', 'vater', 'schwester', 'bruder'),
    LanguagesISO2NamesEnum.IT: ('madre', 'padre', 'sorella', 'fratello'),
    LanguagesISO2NamesEnum.ES: ('madre', 'padre', 'hermana', 'hermano'),
    LanguagesISO2NamesEnum.PT: ('mãe', 'pai', 'irmã', 'irmão')
}


async def recreate_words():
    async with SessionLocalAsync() as session:
        repo_write = SqlAlchemyRepositoryAsync(session)
        word_manager = WordManager(repo_write)
        for lang_iso2, lang_words in test_words.items():
            lang = await repo_write.get(LanguageModel, iso2=lang_iso2)
            for i in range(len(lang_words)):
                try:
                    word_characters = test_words[lang_iso2][i]
                    await word_manager.create_word(WordCreateSerializer(
                        characters=word_characters, language_uuid=lang.uuid))
                except AlreadyExistsException:
                    print(f'while recreate_words: word "{word_characters}" already exists in {lang_iso2}')

test_texts = {
    LanguagesISO2NamesEnum.RU: ('жили были старик со старухой'),
}


# async def recreate_words_from_text():
#     async with SessionLocalAsync() as session:
#         repo_write = SqlAlchemyRepositoryAsync(session)
#         text_manager = TextManager(repo_write)
#         for lang_iso2 in test_words:
#             lang = await repo_write.get(LanguageModel, iso2=lang_iso2)
#
#             for i in range(4):
#                 try:
#                     await word_manager.create_word(WordCreateSerializer(
#                         characters=test_words[lang_iso2][i], language_uuid=lang.uuid))
#                 except AlreadyExistsException:
#                     pass
