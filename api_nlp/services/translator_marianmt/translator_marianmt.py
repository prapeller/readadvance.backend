import backoff
import os
from core.config import BASE_DIR
from core.enums import LanguagesISO2NamesEnum
from core.shared import singleton_decorator
from db.serializers.translations import TranslInSerializer, TranslOutSerializer
from transformers import MarianMTModel, MarianTokenizer

os.environ['HF_HOME'] = str(BASE_DIR / 'staticfiles/marianmt')


@singleton_decorator
class TranslatorMarianMT:

    @backoff.on_exception(backoff.constant, Exception, max_tries=10)
    def __init__(self):
        self.model_names = {
            (LanguagesISO2NamesEnum.RU, LanguagesISO2NamesEnum.EN): 'Helsinki-NLP/opus-mt-ru-en',
            (LanguagesISO2NamesEnum.EN, LanguagesISO2NamesEnum.RU): 'Helsinki-NLP/opus-mt-en-ru',
            (LanguagesISO2NamesEnum.DE, LanguagesISO2NamesEnum.EN): 'Helsinki-NLP/opus-mt-de-en',
            (LanguagesISO2NamesEnum.EN, LanguagesISO2NamesEnum.DE): 'Helsinki-NLP/opus-mt-en-de',
            (LanguagesISO2NamesEnum.FR, LanguagesISO2NamesEnum.EN): 'Helsinki-NLP/opus-mt-fr-en',
            (LanguagesISO2NamesEnum.EN, LanguagesISO2NamesEnum.FR): 'Helsinki-NLP/opus-mt-en-fr',
            (LanguagesISO2NamesEnum.IT, LanguagesISO2NamesEnum.EN): 'Helsinki-NLP/opus-mt-it-en',
            (LanguagesISO2NamesEnum.EN, LanguagesISO2NamesEnum.IT): 'Helsinki-NLP/opus-mt-en-it',
            (LanguagesISO2NamesEnum.ES, LanguagesISO2NamesEnum.EN): 'Helsinki-NLP/opus-mt-es-en',
            (LanguagesISO2NamesEnum.EN, LanguagesISO2NamesEnum.ES): 'Helsinki-NLP/opus-mt-en-es',
            (LanguagesISO2NamesEnum.PT, LanguagesISO2NamesEnum.EN): 'Helsinki-NLP/opus-mt-tc-big-en-pt',
            (LanguagesISO2NamesEnum.EN, LanguagesISO2NamesEnum.PT): 'Helsinki-NLP/opus-mt-tc-big-en-pt',
        }
        self.models = {k: MarianMTModel.from_pretrained(model_name) for k, model_name in self.model_names.items()}
        self.tokenizers = {k: MarianTokenizer.from_pretrained(model_name) for k, model_name in self.model_names.items()}

    async def translate(
            self,
            tran_ser: TranslInSerializer
    ) -> TranslOutSerializer:

        text_input = tran_ser.text_input
        input_lang_iso2 = tran_ser.input_lang_iso2
        target_lang_iso2 = tran_ser.target_lang_iso2

        # from/to EN
        if input_lang_iso2 == LanguagesISO2NamesEnum.EN or target_lang_iso2 == LanguagesISO2NamesEnum.EN:
            model = self.models.get((input_lang_iso2, target_lang_iso2))
            tokenizer = self.tokenizers.get((input_lang_iso2, target_lang_iso2))

            encoded_input = tokenizer(text_input, return_tensors="pt", padding=True)
            translated_tokens = model.generate(**encoded_input)
            text_output = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

        else:
            # from not EN to not EN - translate to EN first, and then from EN to target
            tran_ser_to_en = TranslInSerializer(text_input=text_input, input_lang_iso2=input_lang_iso2,
                                                target_lang_iso2=LanguagesISO2NamesEnum.EN)
            tran_out_ser_to_en = await self.translate(tran_ser_to_en)
            text_en = tran_out_ser_to_en.text_output
            tran_in_ser_to_target = TranslInSerializer(text_input=text_en,
                                                       input_lang_iso2=LanguagesISO2NamesEnum.EN,
                                                       target_lang_iso2=target_lang_iso2)
            tran_ser_to_target = await self.translate(tran_in_ser_to_target)
            text_output = tran_ser_to_target.text_output

        return TranslOutSerializer(
            text_output=text_output,
            input_lang_iso2=input_lang_iso2,
            target_lang_iso2=target_lang_iso2
        )
