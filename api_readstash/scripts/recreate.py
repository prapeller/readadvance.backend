import asyncio

from core.enums import LanguagesISO2NamesEnum, UserRolesEnum
from core.exceptions import AlreadyExistsException
from db import SessionLocalAsync
from db.models.user import UserModel
from db.serializers.text import TextCreateSerializer
from db.serializers.user import UserCreateSerializer
from db.serializers.word import WordCreateSerializer
from services.postgres.repository import SqlAlchemyRepositoryAsync
from services.text_manager.text_manager import TextManager
from services.user_manager.user_manager import UserManager
from services.word_manager.word_manager import WordManager

test_users = [
    {
        'email': 'readstash_test_head@mail.ru',
        'name': 'test_head',
        'password': 'test',
        'roles': [UserRolesEnum.head],
    },
    {
        'email': 'readstash_test_premium@mail.ru',
        'name': 'test_premium',
        'password': 'test',
        'roles': [UserRolesEnum.premium],
    },
    {
        'email': 'readstash_test_guest@mail.ru',
        'name': 'test_guest',
        'password': 'test',
        'roles': [UserRolesEnum.guest],
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


test_texts = {
    LanguagesISO2NamesEnum.RU: 'Мама мыла раму.',
    LanguagesISO2NamesEnum.EN: 'Mom washed the frame.',
    LanguagesISO2NamesEnum.FR: "Maman a lavé le cadre.",
    LanguagesISO2NamesEnum.DE: 'Mama hat den Rahmen gewaschen.',
    LanguagesISO2NamesEnum.IT: "La mamma ha lavato il telaio.",
    LanguagesISO2NamesEnum.ES: "Mamá lavó el marco.",
    LanguagesISO2NamesEnum.PT: "A mamã lavou a moldura.",
}


async def recreate_test_texts():
    tasks = []
    premium_user_email = test_users[1]['email']
    for language_iso_2, content in test_texts.items():
        tasks.append(create_test_text_task(language_iso_2, content, premium_user_email))
    await asyncio.gather(*tasks)


async def create_test_text_task(language_iso_2: LanguagesISO2NamesEnum, content: str,
                                user_email: str):
    async with SessionLocalAsync() as session:

        repo_write = SqlAlchemyRepositoryAsync(session)
        repo_read = SqlAlchemyRepositoryAsync(session)
        user = await repo_write.get(UserModel, email=user_email)
        text_ser = TextCreateSerializer(content=content, language_iso_2=language_iso_2, user_uuid=user.uuid)
        text_manager = TextManager(repo_write, repo_read)
        try:
            await text_manager.create_text(text_ser)
        except AlreadyExistsException:
            pass


test_words = {
    LanguagesISO2NamesEnum.RU: ('мама', 'мыла', 'раму'),
    LanguagesISO2NamesEnum.EN: ('mom', 'washed', 'frame'),
    LanguagesISO2NamesEnum.FR: ('maman', 'lavé', 'cadre'),
    LanguagesISO2NamesEnum.DE: ('Mama', 'Rahmen', 'gewaschen'),
    LanguagesISO2NamesEnum.IT: ('mamma', 'lavato', 'telaio'),
    LanguagesISO2NamesEnum.ES: ('mamá', 'lavó', 'marco'),
    LanguagesISO2NamesEnum.PT: ('mamã', 'lavou', 'moldura')
}


async def recreate_test_words():
    tasks = []
    for language_iso_2, lang_words in test_words.items():
        for characters in lang_words:
            tasks.append(create_test_word_task(WordCreateSerializer(characters=characters,
                                                                    language_iso_2=language_iso_2)))
    await asyncio.gather(*tasks)


async def create_test_word_task(word_ser: WordCreateSerializer):
    async with SessionLocalAsync() as session:
        repo_write = SqlAlchemyRepositoryAsync(session)
        repo_read = SqlAlchemyRepositoryAsync(session)
        word_manager = WordManager(repo_write, repo_read)
        try:
            await word_manager.create_word(word_ser)
        except AlreadyExistsException:
            pass


async def recreate_test_data():
    await recreate_test_users()
    await recreate_test_words()
    await recreate_test_texts()
