import http
import traceback
from pathlib import Path

import httpx
import requests

from core.config import settings
from core.enums import RequestMethodsEnum, UserRolesEnum
from core.exceptions import InternalServerError, UnprocessableEntityException
from core.logger_config import setup_logger
from db.serializers.user import UserUpdateSerializer, KCUserReadSerializer, UserCreateSerializer
from services.keycloak.roles import kc_user_roles

logger = setup_logger(log_name=Path(__file__).resolve().parent.stem)


class KCAdmin():
    def __init__(self):
        self.admin_access_token = None
        self.admin_refresh_token = None
        self._authenticate_sync()
        logger.debug(f'{self} set its access and refresh tokens')
        self.kc_base_url = settings.KEYCLOAK_BASE_URL
        self.kc_realm = settings.KEYCLOAK_REALM

    def _authenticate_sync(self):
        self.admin_access_token, self.admin_refresh_token = self._get_admin_tokens()
        logger.debug(f'{self} set its access and refresh tokens')

    async def _authenticate_async(self):
        self.admin_access_token, self.admin_refresh_token = await self._get_admin_tokens_async()
        logger.debug(f'{self} set its access and refresh tokens')

    def __send_request_sync(self, method: RequestMethodsEnum, url: str, json=None, data=None,
                            params=None, headers: dict | None = None) -> requests.Response:
        try:
            headers = {"Authorization": f"Bearer {self.admin_access_token}"} if headers is None else headers
            if method == RequestMethodsEnum.get:
                resp = requests.get(url, params=params, headers=headers)
            elif method == RequestMethodsEnum.delete:
                resp = requests.delete(url, params=params, headers=headers)
            elif method == RequestMethodsEnum.post:
                resp = requests.post(url, json=json, data=data, headers=headers)
            else:
                resp = requests.put(url, json=json, data=data, headers=headers)
        except Exception:
            logger.error(traceback.format_exc())
            raise
        return resp

    async def __send_request_async(self, method: RequestMethodsEnum, url: str, json=None, data=None,
                                   params=None, headers: dict | None = None) -> requests.Response:
        try:
            headers = {"Authorization": f"Bearer {self.admin_access_token}"} if headers is None else headers

            async with httpx.AsyncClient() as client:
                if method == RequestMethodsEnum.get:
                    resp = await client.get(url, params=params, headers=headers)
                elif method == RequestMethodsEnum.delete:
                    resp = await client.delete(url, params=params, headers=headers)
                elif method == RequestMethodsEnum.post:
                    resp = await client.post(url, json=json, data=data, headers=headers)
                else:
                    resp = await client.put(url, json=json, data=data, headers=headers)
        except Exception:
            logger.error(traceback.format_exc())
            raise
        return resp

    def _send_request_sync(self, method: RequestMethodsEnum, url: str, json=None, data=None,
                           params=None, headers: dict | None = None) -> requests.Response:

        resp = self.__send_request_sync(method, url, json, data, params, headers)
        if resp.status_code >= 400:
            if resp.status_code == 401:
                detail = f'{self} failed with {resp.status_code=:}, re-authenticating...'
                logger.debug(detail)
                self._authenticate_sync()
                resp = self.__send_request_sync(method, url, json, data, params, headers)
            else:
                detail = f'{self} failed with {resp.status_code=:}'
                logger.debug(detail)
                raise InternalServerError(detail=detail)
        return resp

    async def _send_request_async(self, method: RequestMethodsEnum, url: str, json=None, data=None,
                                  params=None, headers: dict | None = None) -> requests.Response:

        resp = await self.__send_request_async(method, url, json, data, params, headers)
        if resp.status_code >= 400:
            if resp.status_code == 401:
                detail = f'{self} failed with {resp.status_code=:}, re-authenticating...'
                logger.debug(detail)
                await self._authenticate_async()
                resp = await self.__send_request_async(method, url, json, data, params, headers)
            else:
                detail = f'{self} failed with {resp.status_code=:}'
                logger.debug(detail)
                raise InternalServerError(detail=detail)
        return resp

    def _get_admin_tokens(self) -> tuple[str, str]:
        try:
            resp = self._send_request_sync(
                RequestMethodsEnum.post,
                url=f'{settings.KEYCLOAK_BASE_URL}/realms/master/protocol/openid-connect/token',
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={
                    "grant_type": "password",
                    "client_secret": f"{settings.KEYCLOAK_CLIENT_SECRET}",
                    "client_id": 'admin-cli',
                    "username": f"{settings.KEYCLOAK_ADMIN}",
                    "password": f"{settings.KEYCLOAK_ADMIN_PASSWORD}",
                })
            resp_json = resp.json()
            return resp_json['access_token'], resp_json['refresh_token']
        except Exception as e:
            logger.error(traceback.format_exc())
            raise InternalServerError(detail=f"cant get admin tokens: {str(e)}")

    async def _get_admin_tokens_async(self) -> tuple[str, str]:
        try:
            resp = await self._send_request_async(
                RequestMethodsEnum.post,
                url=f'{settings.KEYCLOAK_BASE_URL}/realms/master/protocol/openid-connect/token',
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={
                    "grant_type": "password",
                    "client_secret": f"{settings.KEYCLOAK_CLIENT_SECRET}",
                    "client_id": 'admin-cli',
                    "username": f"{settings.KEYCLOAK_ADMIN}",
                    "password": f"{settings.KEYCLOAK_ADMIN_PASSWORD}",
                })
            resp_json = resp.json()
            return resp_json['access_token'], resp_json['refresh_token']
        except Exception as e:
            logger.error(traceback.format_exc())
            raise InternalServerError(detail=f"cant get admin tokens: {str(e)}")

    async def _set_user_role_async(self, user_uuid: str, role: UserRolesEnum) -> requests.Response:
        return await self._send_request_async(
            RequestMethodsEnum.post,
            url=f"{self.kc_base_url}/admin/realms/{self.kc_realm}/users/{user_uuid}/role-mappings/realm",
            json=[kc_user_roles.get(role)])

    async def create_user_async(self, user_ser: UserCreateSerializer) -> KCUserReadSerializer:
        json = {'email': user_ser.email, 'firstName': user_ser.first_name, 'enabled': True}
        if user_ser.last_name is not None:
            json['lastName'] = user_ser.last_name
        resp = await self._send_request_async(
            RequestMethodsEnum.post, url=f"{self.kc_base_url}/admin/realms/{self.kc_realm}/users",
            json=json)
        assert resp.status_code == http.HTTPStatus.CREATED
        user_uuid = await self.get_user_uuid_by_email_async(user_ser.email)
        if user_ser.roles:
            for role in user_ser.roles:
                await self._set_user_role_async(user_uuid, role)
        kc_user = await self.get_user_by_email_async(user_ser.email)
        return kc_user

    async def set_password_async(self, user_uuid: str, password: str) -> requests.Response:
        return await self._send_request_async(
            RequestMethodsEnum.put,
            url=f"{self.kc_base_url}/admin/realms/{self.kc_realm}/users/{user_uuid}/reset-password",
            json={"type": "password", "temporary": "false", "value": password})

    async def verify_async(self, user_uuid: str) -> requests.Response:
        return await self._send_request_async(
            RequestMethodsEnum.put,
            url=f"{self.kc_base_url}/admin/realms/{self.kc_realm}/users/{user_uuid}",
            json={"emailVerified": "true"})

    async def update_user_email_async(self, user_uuid: str, user_ser: UserUpdateSerializer) -> requests.Response:
        assert user_ser.email is not None, 'email is required'
        return await self._send_request_async(
            RequestMethodsEnum.put,
            url=f"{self.kc_base_url}/admin/realms/{self.kc_realm}/users/{user_uuid}",
            json={'email': user_ser.email})

    async def update_user_names_async(self, user_uuid: str, user_ser: UserUpdateSerializer) -> requests.Response:
        assert user_ser.first_name is not None or user_ser.last_name is not None, 'first_name or last_name are required'
        user_ser_credentials = {}
        if user_ser.first_name is not None:
            user_ser_credentials['firstName'] = user_ser.first_name
        if user_ser.last_name is not None:
            user_ser_credentials['lastName'] = user_ser.last_name

        return await self._send_request_async(
            RequestMethodsEnum.put,
            url=f"{self.kc_base_url}/admin/realms/{self.kc_realm}/users/{user_uuid}",
            json=user_ser_credentials)

    async def get_user_uuid_by_email_async(self, email: str) -> str | None:
        try:
            resp = await self._send_request_async(RequestMethodsEnum.get,
                                                  url=f"{self.kc_base_url}/admin/realms/{self.kc_realm}/users?email={email}")
            return resp.json()[0]['id']
        except IndexError:
            return None

    async def _delete_user_roles_all_async(self, user_uuid: str) -> requests.Response:
        return await self._send_request_async(
            RequestMethodsEnum.delete,
            url=f"{self.kc_base_url}/admin/realms/{self.kc_realm}/users/{user_uuid}/role-mappings/realm")

    async def get_user_by_email_async(self, email: str) -> KCUserReadSerializer | None:
        resp = await self._send_request_async(RequestMethodsEnum.get,
                                              url=f"{self.kc_base_url}/admin/realms/{self.kc_realm}/users?email={email}")
        user_dicts = resp.json()
        if not user_dicts:
            return None
        user_dict = user_dicts[0]
        uuid = user_dict.get('id')
        roles = await self.get_user_roles_async(uuid)
        kc_user_ser = KCUserReadSerializer(uuid=uuid,
                                           email=user_dict.get('email'),
                                           first_name=user_dict.get('firstName'),
                                           last_name=user_dict.get('lastName'),
                                           is_active=user_dict.get('enabled'),
                                           roles=roles)
        return kc_user_ser

    async def _get_user_role_mappings_async(self, user_uuid: str) -> list[dict]:
        resp = await self._send_request_async(
            RequestMethodsEnum.get,
            url=f"{self.kc_base_url}/admin/realms/{self.kc_realm}/users/{user_uuid}/role-mappings/realm")
        return resp.json()

    async def get_user_roles_async(self, user_uuid: str) -> list[str]:
        user_role_mappings = await self._get_user_role_mappings_async(user_uuid)
        return [user_role_mapping.get('name') for user_role_mapping in user_role_mappings
                if 'default' not in user_role_mapping.get('name')]

    async def update_user_roles_async(self, user_uuid: str, user_ser: UserUpdateSerializer):
        if user_ser.roles is None:
            raise UnprocessableEntityException(detail='roles were not provided for updating')

        await self._delete_user_roles_all_async(user_uuid)

        for role in user_ser.roles:
            await self._set_user_role_async(user_uuid, role)

    async def deactivate_user_async(self, user_uuid: str) -> None:
        await self._send_request_async(RequestMethodsEnum.put,
                                       url=f"{self.kc_base_url}/admin/realms/{self.kc_realm}/users/{user_uuid}",
                                       json={'enabled': False})

    async def activate_user_async(self, user_uuid: str) -> None:
        await self._send_request_async(RequestMethodsEnum.put,
                                       url=f"{self.kc_base_url}/admin/realms/{self.kc_realm}/users/{user_uuid}",
                                       json={'enabled': True})

    async def remove_user_async(self, user_uuid: str) -> None:
        await self._send_request_async(RequestMethodsEnum.delete,
                                       url=f"{self.kc_base_url}/admin/realms/{self.kc_realm}/users/{user_uuid}")


kc_admin: KCAdmin | None = None


def kc_admin_dependency():
    logger.debug(f'{kc_admin=}')
    return kc_admin


def init_kc_admin():
    global kc_admin
    kc_admin = KCAdmin()
    logger.debug(f'inited {kc_admin=}')
