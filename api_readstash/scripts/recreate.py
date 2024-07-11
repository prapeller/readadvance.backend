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


async def recreate_texts():
    async with SessionLocalAsync() as session:
        repo_write = SqlAlchemyRepositoryAsync(session)
        text_manager = TextManager(repo_write)

        premium_user_email = test_users[1]['email']
        premium_user = await repo_write.get(UserModel, email=premium_user_email)
        for lang_iso2, content in test_texts.items():
            try:
                await text_manager.create_text(TextCreateSerializer(content=content, user_uuid=premium_user.uuid))
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


async def recreate_words():
    async with SessionLocalAsync() as session:
        repo_write = SqlAlchemyRepositoryAsync(session)
        repo_read = SqlAlchemyRepositoryAsync(session)
        word_manager = WordManager(repo_write, repo_read)
        for language_iso_2, lang_words in test_words.items():
            for characters in lang_words:
                await word_manager.get_or_create_word(WordCreateSerializer(characters=characters,
                                                                           language_iso_2=language_iso_2))


async def recreate_test_data():
    await recreate_test_users()
    await recreate_texts()
    await recreate_words()
