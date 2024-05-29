from pathlib import Path

import fastapi as fa
import pydantic as pd

from core.enums import ResponseDetailEnum
from core.exceptions import AlreadyExistsException, NotFoundException
from core.logger_config import setup_logger
from db.models.user import UserModel
from db.serializers.user import UserCreateSerializer, UserUpdateSerializer, KCUserReadSerializer
from services.keycloak.keycloak import KCAdmin
from services.postgres.repository import SqlAlchemyRepositoryAsync, sqlalchemy_repo_async_dependency, \
    sqlalchemy_repo_async_read_dependency

logger = setup_logger(log_name=Path(__file__).resolve().parent.stem)


class UserManager():
    def __init__(self,
                 repo_write: SqlAlchemyRepositoryAsync,
                 repo_read: SqlAlchemyRepositoryAsync | None = None):
        self.repo_write = repo_write
        self.repo_read = repo_read
        self.kc_admin = KCAdmin()

    async def get_or_create_or_update_user_in_kc(self, user_ser: UserCreateSerializer | UserUpdateSerializer,
                                                 password='test') -> KCUserReadSerializer:
        kc_user = await self.kc_admin.get_user_by_email(user_ser.email)

        if kc_user is None:
            kc_user = await self.kc_admin.create_user(user_ser)
            await self.kc_admin.set_password(kc_user.uuid, password)
            await self.kc_admin.verify(kc_user.uuid)
        else:
            if kc_user.last_name != user_ser.last_name or kc_user.first_name != user_ser.first_name:
                await self.kc_admin.update_user_names(kc_user.uuid, UserUpdateSerializer(first_name=user_ser.first_name,
                                                                                         last_name=user_ser.last_name))
            if kc_user.roles != user_ser.roles:
                await self.kc_admin.update_user_roles(kc_user.uuid, UserUpdateSerializer(roles=user_ser.roles))
        return kc_user

    async def get_or_create_or_update_user_in_local_db(self, user_ser: UserCreateSerializer | UserUpdateSerializer):
        user = await self.repo_write.get(UserModel, raise_if_not_found=False, email=user_ser.email)
        if user is None:
            return await self.repo_write.create(UserModel, user_ser)
        else:
            if (
                    user.first_name != user_ser.first_name or
                    user.last_name != user_ser.last_name or
                    user.roles != user_ser.roles or
                    user.uuid != user_ser.uuid
            ):
                user = await self.repo_write.update(user, user_ser)
        return user

    async def get_or_create_or_update_user(self, user_ser: UserCreateSerializer | UserUpdateSerializer,
                                           password='test'):
        kc_user = await self.get_or_create_or_update_user_in_kc(user_ser, password=password)
        user_ser.uuid = kc_user.uuid
        db_user = await self.get_or_create_or_update_user_in_local_db(user_ser)
        return db_user

    async def _email_exists_in_local_db(self, email: pd.EmailStr) -> None:
        user_with_the_same_email = await self.repo_write.get(UserModel, email=email)
        return user_with_the_same_email is not None

    async def _email_exists_in_kc(self, email: pd.EmailStr) -> None:
        user_with_the_same_email = await self.kc_admin.get_user_by_email(email)
        return user_with_the_same_email is not None

    async def _raise_if_email_exists_in_local_db(self, email: pd.EmailStr) -> None:
        if await self._email_exists_in_local_db(email):
            raise AlreadyExistsException(detail='User with the same email already exists')

    async def _raise_if_email_exists_in_kc(self, email: pd.EmailStr) -> None:
        if await self._email_exists_in_kc(email):
            raise AlreadyExistsException(detail='User with the same email already exists')

    async def _raise_if_email_exists_in_local_db_or_kc(self, email: pd.EmailStr) -> None:
        await self._raise_if_email_exists_in_local_db(email)
        await self._raise_if_email_exists_in_kc(email)

    async def get_user(self, uuid: str) -> UserModel:
        assert self.repo_read is not None, 'repo_read is required'
        user = await self.repo_read.get(UserModel, uuid=uuid)
        if user is None:
            raise NotFoundException(detail='User not found')
        return user

    async def list_filtered(self, **kwargs):
        assert self.repo_read is not None, 'repo_read is required'
        return await self.repo_read.list_filtered(UserModel, **kwargs)

    async def create_user(self, user_ser: UserCreateSerializer):
        await self._raise_if_email_exists_in_local_db_or_kc(user_ser.email)
        await self.kc_admin.create_user(user_ser)
        kc_user_uuid = await self.kc_admin.get_user_uuid_by_email(user_ser.email)
        user_ser.uuid = kc_user_uuid

        user: UserModel = await self.repo_write.create(UserModel, user_ser)
        logger.debug(f'created {user=}')
        return user

    async def clone_locally_from_kc_user(self, user_ser: UserCreateSerializer):
        assert user_ser.uuid is not None, 'uuid is required'
        await self._raise_if_email_exists_in_local_db(user_ser.email)
        user: UserModel = await self.repo_write.create(UserModel, user_ser)
        logger.debug(f'cloned locally from keycloak: {user=}')
        return user

    async def update_user(self, user_uuid: str, user_ser: UserUpdateSerializer, exclude_none=True,
                          exclude_unset=True) -> UserModel:
        user: UserModel = await self.repo_write.get(UserModel, raise_if_not_found=True, uuid=user_uuid)

        if user_ser.email is not None:
            await self._raise_if_email_exists_in_local_db_or_kc(user_ser.email)
            await self.kc_admin.update_user_email(user.uuid, user_ser)

        if user_ser.first_name is not None or user_ser.last_name is not None:
            await self.kc_admin.update_user_names(user.uuid, user_ser)

        if user_ser.roles is not None:
            await self.kc_admin.update_user_roles(user.uuid, user_ser)

        user = await self.repo_write.update(user, user_ser, exclude_none=exclude_none, exclude_unset=exclude_unset)
        logger.debug(f'updated {user=}')
        return user

    async def activate(self, user_uuid) -> dict:
        await self.kc_admin.activate_user(user_uuid)
        user = await self.repo_write.get(UserModel, uuid=user_uuid)
        if not user.is_active:
            await self.repo_write.update(user, UserUpdateSerializer(is_active=True))
        logger.debug(f'activated {user=}')
        return {'detail': ResponseDetailEnum.ok}

    async def deactivate(self, user_uuid) -> dict:
        await self.kc_admin.deactivate_user(user_uuid)
        user = await self.repo_write.get(UserModel, uuid=user_uuid)
        if user.is_active:
            await self.repo_write.update(user, UserUpdateSerializer(is_active=False))
        logger.debug(f'deactivated {user=}')
        return {'detail': ResponseDetailEnum.ok}


async def user_manager_dependency(
        repo_write: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_dependency),
        repo_read: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_read_dependency)) -> UserManager:
    return UserManager(repo_write=repo_write, repo_read=repo_read)
