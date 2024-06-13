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


class LanguagesISO2NamesEnum(StrEnumRepr):
    RU = 'RU'  # Russian
    EN = 'EN'  # English
    DE = 'DE'  # German
    FR = 'FR'  # French
    IT = 'IT'  # Italian
    ES = 'ES'  # Spanish, Castilian
    PT = 'PT'  # Portuguese
