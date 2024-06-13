import datetime as dt

import pydantic as pd

from core.enums import UTCTimeZonesEnum, UserRolesEnum


class UserUpdateSerializer(pd.BaseModel):
    uuid: str | None = None
    external_uuid: str | None = None
    email: pd.EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    timezone: UTCTimeZonesEnum | None = None
    telegram_id: str | None = None
    is_accepting_emails: bool | None = None
    is_accepting_interface_messages: bool | None = None
    is_accepting_telegram: bool | None = None
    roles: list[UserRolesEnum] | None = None
    is_active: bool | None = None

    @pd.field_validator('email')
    @classmethod
    def lower_email(cls, v):
        return v.lower()


class UserCreateSerializer(UserUpdateSerializer):
    email: pd.EmailStr
    uuid: str | None = None
    external_uuid: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    timezone: UTCTimeZonesEnum | None = UTCTimeZonesEnum.utc_p03
    is_accepting_emails: bool | None = True
    is_accepting_interface_messages: bool | None = True
    is_accepting_telegram: bool | None = False
    is_active: bool | None = True
    roles: list[UserRolesEnum] | None = [UserRolesEnum.head]


class UserReadSerializer(UserCreateSerializer):
    id: int
    uuid: str | None = None
    created_at: dt.datetime
    updated_at: dt.datetime | None = None

    class Config:
        from_attributes = True


class KCUserReadSerializer(pd.BaseModel):
    uuid: str
    external_uuid: str | None = None
    email: pd.EmailStr
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool
    roles: list[UserRolesEnum] = []


UserReadSerializer.model_rebuild()
