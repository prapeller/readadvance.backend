from enum import Enum


class StrEnumRepr(str, Enum):
    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class IntEnumRepr(int, Enum):
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


class EnvEnum(StrEnumRepr):
    local = 'local'
    docker_compose_local = 'docker-compose-local'
    docker_compose_prod = 'docker-compose-prod'


class RequestMethodsEnum(StrEnumRepr):
    get = 'GET'
    post = 'POST'
    put = 'PUT'
    delete = 'DELETE'


class UserRolesEnum(str, Enum):
    head = 'head'
    admin = 'admin'
    guest = 'guest'
    premium = 'premium'
    anonymous = 'anonymous'


class ContentTypesEnum(StrEnumRepr):
    # application
    zip = 'application/zip'
    xml = 'application/xml'
    pdf = 'application/pdf'
    octet_stream = 'application/octet-stream'
    form_urlencoded = 'application/x-www-form-urlencoded'
    form_data = 'multipart/form-data'
    json = 'application/json'
    # text
    html = 'text/html'
    txt = 'text/plain'
    # image
    gif = 'image/gif'
    webp = 'image/webp'
    jpeg = 'image/jpeg'
    svg = 'image/svg+xml'
    png = 'image/png'
    #     video
    avi = 'video/x-msvideo'
    mpeg = 'video/mpeg'
    video_ogg = 'video/ogg'
    video_webm = 'video/webm'
    mp4 = 'video/mp4'
    #     audio
    wav = 'audio/wav'
    mp3 = 'audio/mpeg'
    audio_ogg = 'audio/ogg'
    audio_webm = 'audio/webm'
    aac = 'audio/aac'
    flac = 'audio/flac'


class ImageContentTypesEnum(StrEnumRepr):
    jpeg = ContentTypesEnum.jpeg
    svg = ContentTypesEnum.svg
    png = ContentTypesEnum.png
    gif = ContentTypesEnum.gif
    webp = ContentTypesEnum.webp


class AudioContentTypesEnum(StrEnumRepr):
    mp3 = ContentTypesEnum.mp3


class VideoContentTypesEnum(StrEnumRepr):
    avi = ContentTypesEnum.avi
    mpeg = ContentTypesEnum.mpeg
    video_ogg = ContentTypesEnum.video_ogg
    video_webm = ContentTypesEnum.video_webm
    mp4 = ContentTypesEnum.mp4


class TextContentTypesEnum(StrEnumRepr):
    html = ContentTypesEnum.html
    txt = ContentTypesEnum.txt


class WordFileContentTypesEnum(StrEnumRepr):
    image = 'image'
    audio = 'audio'


class DBEnum(StrEnumRepr):
    postgres_readstash = 'postgres_readstash'
    postgres_obj_storage = 'postgres_obj_storage'


class DBSessionModeEnum(StrEnumRepr):
    r = 'read'
    rw = 'read_or_write'


class UserDataRenderPlaceholdersEnum(StrEnumRepr):
    user_name = '%user_name%'


class ResponseDetailEnum(StrEnumRepr):
    ok = 'Ok'
    unauthorized = 'Unauthorized for this action'
    bad_request = 'Bad reqeust'
    unprocessable_entity = 'Unprocessable entity'
    not_found = 'Not found'
    already_exists = 'Already exists'
    already_active_user = 'This user is already active'
    already_inactive_user = 'This user is inactive already'
    already_registered_email = 'This email is already registered'
    server_error = 'Server error'
    object_storage_db_exception = 'Object Storage Exception: '
    not_valid_placeholders = 'Not valid placeholders found: '


class OrderEnum(StrEnumRepr):
    asc = 'asc'
    desc = 'desc'


class PeriodEnum(StrEnumRepr):
    days = 'days'
    hours = 'hours'
    minutes = 'minutes'
    seconds = 'seconds'
    microseconds = 'microseconds'


class QueueTaskPrioritiesEnum(IntEnumRepr):
    q_1 = 1
    q_2 = 2
    q_3 = 3
    q_4 = 4
    q_5 = 5


class LevelOrderEnum(IntEnumRepr):
    o_1 = 1
    o_2 = 2
    o_3 = 3
    o_4 = 4
    o_5 = 5
    o_6 = 6


class LevelSystemNamesEnum(StrEnumRepr):
    CEFR = 'CEFR'
    HSK = 'HSK'
    TRKI = 'ТРКИ'


class LevelCEFRCodesEnum(StrEnumRepr):
    A1 = 'A1'
    A2 = 'A2'
    B1 = 'B1'
    B2 = 'B2'
    C1 = 'C1'
    C2 = 'C2'

    NOT_IDENTIFIED = 'not identified'


class UTCTimeZonesEnum(StrEnumRepr):
    utc_p14 = 'UTC+14'
    utc_p13 = 'UTC+13'
    utc_p12 = 'UTC+12'
    utc_p11 = 'UTC+11'
    utc_p10 = 'UTC+10'
    utc_p09 = 'UTC+9'
    utc_p08 = 'UTC+8'
    utc_p07 = 'UTC+7'
    utc_p06 = 'UTC+6'
    utc_p05 = 'UTC+5'
    utc_p04 = 'UTC+4'
    utc_p03 = 'UTC+3'
    utc_p02 = 'UTC+2'
    utc_p01 = 'UTC+1'
    utc_p00 = 'UTC+0'
    utc_m01 = 'UTC−1'
    utc_m02 = 'UTC−2'
    utc_m03 = 'UTC−3'
    utc_m04 = 'UTC−4'
    utc_m05 = 'UTC−5'
    utc_m06 = 'UTC−6'
    utc_m07 = 'UTC−7'
    utc_m08 = 'UTC−8'
    utc_m09 = 'UTC−9'
    utc_m10 = 'UTC−10'
    utc_m11 = 'UTC−11'
    utc_m12 = 'UTC−12'


class ChatGPTModelsEnum(StrEnumRepr):
    gpt_4 = 'gpt-4'  # OpenAI's GPT-4 model
    gpt_3_5 = 'gpt-3.5-turbo'  # OpenAI's GPT-3.5-turbo model


class TranslationMethodsEnum(StrEnumRepr):
    manual = 'manual'
    gpt_4 = ChatGPTModelsEnum.gpt_4
    gpt_3_5 = ChatGPTModelsEnum.gpt_3_5


class LanguagesISO2NamesEnum(StrEnumRepr):
    RU = 'RU'  # Russian
    EN = 'EN'  # English
    DE = 'DE'  # German
    FR = 'FR'  # French
    IT = 'IT'  # Italian
    ES = 'ES'  # Spanish, Castilian
    PT = 'PT'  # Portuguese


class UserWordStatusEnum(StrEnumRepr):
    to_learn = 'to_learn'
    known = 'known'
