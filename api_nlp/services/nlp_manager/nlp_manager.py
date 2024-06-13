import backoff
import spacy

from core.enums import LanguagesISO2NamesEnum
from core.shared import singleton_decorator
from db.serializers.text import TextSerializer


@singleton_decorator
class NLPManager:

    @backoff.on_exception(backoff.constant, Exception, max_tries=10)
    def __init__(self):
        self.language_models = {
            LanguagesISO2NamesEnum.RU: spacy.load("ru_core_news_sm"),
            LanguagesISO2NamesEnum.EN: spacy.load("en_core_web_sm"),
            LanguagesISO2NamesEnum.DE: spacy.load("de_core_news_sm"),
            LanguagesISO2NamesEnum.FR: spacy.load("fr_core_news_sm"),
            LanguagesISO2NamesEnum.IT: spacy.load("it_core_news_sm"),
            LanguagesISO2NamesEnum.ES: spacy.load("es_core_news_sm"),
            LanguagesISO2NamesEnum.PT: spacy.load("pt_core_news_sm"),
        }

    async def get_lemm_text_words(self, text: TextSerializer):
        nlp = self.language_models.get(text.iso2)
        doc = nlp(text.content)
        lemmatized_words = [token.lemma_ for token in doc]
        return lemmatized_words
