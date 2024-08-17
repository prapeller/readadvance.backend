import backoff
import stanza

from core.config import BASE_DIR
from core.enums import LanguagesISO2NamesEnum
from core.shared import singleton_decorator
from db.serializers.analyses import AnalysesInSerializer, AnalysesOutSerializer

stanza_models_path = BASE_DIR / "staticfiles/stanza"


@singleton_decorator
class AnalyzerStanza:

    @backoff.on_exception(backoff.constant, Exception, max_tries=10)
    def __init__(self):
        stanza.download('ru', str(stanza_models_path))
        stanza.download('en', str(stanza_models_path))
        stanza.download('de', str(stanza_models_path))
        stanza.download('fr', str(stanza_models_path))
        stanza.download('it', str(stanza_models_path))
        stanza.download('es', str(stanza_models_path))
        stanza.download('pt', str(stanza_models_path))
        self.language_models = {
            LanguagesISO2NamesEnum.RU: stanza.Pipeline('ru', dir=str(stanza_models_path)),
            LanguagesISO2NamesEnum.EN: stanza.Pipeline('en', dir=str(stanza_models_path)),
            LanguagesISO2NamesEnum.DE: stanza.Pipeline('de', dir=str(stanza_models_path)),
            LanguagesISO2NamesEnum.FR: stanza.Pipeline('fr', dir=str(stanza_models_path)),
            LanguagesISO2NamesEnum.IT: stanza.Pipeline('it', dir=str(stanza_models_path)),
            LanguagesISO2NamesEnum.ES: stanza.Pipeline('es', dir=str(stanza_models_path)),
            LanguagesISO2NamesEnum.PT: stanza.Pipeline('pt', dir=str(stanza_models_path)),
        }

    async def analyze(self, content_ser: AnalysesInSerializer) -> AnalysesOutSerializer:
        nlp = self.language_models.get(content_ser.iso2)
        doc = nlp(content_ser.content)
        sents = doc.sentences
        words = []
        for sent in sents:
            for word in sent.words:
                word_an_res = {'lemma': word.lemma, 'pos': word.pos}
                words.append(word_an_res)
        return AnalysesOutSerializer(words=words, iso2=content_ser.iso2)
