import hashlib
import hmac
import time
from functools import wraps

import fastapi as fa
from fastapi_resource_server import OidcResourceServer, JwtDecodeOptions
from sqlalchemy.exc import ProgrammingError
from starlette.middleware.base import BaseHTTPMiddleware

from core import config
from core.config import settings
from core.enums import UserRolesEnum, DBEnum
from core.exceptions import UnauthorizedException, BadRequestException, NotFoundException
from core.logger_config import setup_logger
from db.models.user import UserModel
from db.serializers.user import UserUpdateSerializer, UserCreateSerializer
from scripts.migrate import migrate
from services.user_manager.user_manager import user_manager_dependency, UserManager

logger = setup_logger('security')

issuer = f"{settings.KEYCLOAK_BASE_URL}/realms/{settings.KEYCLOAK_REALM}"
logger.debug(f'{issuer=}')

oauth2_scheme = OidcResourceServer(
    issuer=issuer,
    jwt_decode_options=JwtDecodeOptions(verify_aud=False, verify_signature=None, verify_iat=None, verify_exp=None,
                                        verify_nbf=None, verify_iss=None, verify_sub=None, verify_jti=None,
                                        verify_at_hash=None, require_aud=None, require_iat=None, require_exp=None,
                                        require_nbf=None, require_iss=None, require_sub=None, require_jti=None,
                                        require_at_hash=None, leeway=None),
)


def auth_required(roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user: UserModel = kwargs.get('current_user')
            if current_user and not any(role in current_user.roles for role in roles):
                detail = f'{current_user=:} is not authorized to {func.__name__}'
                logger.error(detail)
                raise UnauthorizedException
            return await func(*args, **kwargs)

        return wrapper

    return decorator


auth_head = auth_required([UserRolesEnum.head])
auth_head_or_admin = auth_required([UserRolesEnum.head, UserRolesEnum.admin])


async def current_user_dependency(
        user_manager: UserManager = fa.Depends(user_manager_dependency),
        keycloak_data: dict = fa.Security(oauth2_scheme)) -> UserModel | None:
    keycloak_uuid = keycloak_data.get('sub')
    keycloak_email = keycloak_data.get('email')
    keycloak_first_name = keycloak_data.get('given_name')
    keycloak_last_name = keycloak_data.get('family_name')
    keycloak_roles = keycloak_data.get('realm_access').get('roles')
    keycloak_roles = [r for r in keycloak_roles if r in (ur for ur in UserRolesEnum)]
    if not keycloak_roles:
        raise UnauthorizedException(detail='User has no roles')
    try:
        user = await user_manager.get_user(uuid=keycloak_uuid)
        user_is_the_same = (keycloak_email == user.email and
                            keycloak_first_name == user.first_name and
                            keycloak_last_name == user.last_name and
                            set(keycloak_roles) == set(user.roles))
        if not user_is_the_same:
            user = await user_manager.update_user(user.uuid, UserUpdateSerializer(
                email=keycloak_email,
                first_name=keycloak_first_name,
                last_name=keycloak_last_name,
                roles=keycloak_roles,
            ))
            detail = f'updated {user=}'
            logger.debug(detail)
        return user
    except NotFoundException:
        user = await user_manager.clone_locally_from_kc_user(UserCreateSerializer(
                uuid=keycloak_uuid,
                email=keycloak_email,
                first_name=keycloak_first_name,
                last_name=keycloak_last_name,
                roles=keycloak_roles,
            ))
        detail = f'created {user=}'
        logger.debug(detail)
        return user
    except ProgrammingError:
        migrate(db=DBEnum.postgres_readstash)
        detail = 'Database was migrated. Please, try again.'
        logger.error(detail)
        raise BadRequestException(detail=detail)


async def generate_timestamp_hmac() -> tuple[int, str]:
    timestamp = int(time.time())  # Current Unix timestamp
    signature = hmac.new(settings.INTER_SERVICE_SECRET.encode(), str(timestamp).encode(), hashlib.sha256).hexdigest()
    return timestamp, signature


class VerifyHMACMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: fa.Request, call_next):
        if 'api/v1/internal' in request.url.path:
            logger.debug(f'{request.client.host=}, {request.url.path=}, {request.method=}, {request.headers=}')
            try:
                received_signature = request.headers.get('X-HMAC-Signature')
                received_timestamp_str = request.headers.get('X-Timestamp')
                if received_timestamp_str is None or received_signature is None:
                    detail = f'necessary headers not provided: {received_timestamp_str=}, {received_signature=}'
                    logger.error(f'from {request.client=} {detail}')
                    return fa.responses.JSONResponse(status_code=fa.status.HTTP_401_UNAUTHORIZED,
                                                     content={'detail': detail})
                received_timestamp = int(received_timestamp_str)
                current_timestamp = int(time.time())
                if abs(current_timestamp - received_timestamp) > config.ACCEPTABLE_HMAC_TIME_SECONDS:
                    detail = f'{received_timestamp=:} doesnt feet timeframe'
                    logger.error(f'from {request.client=} {detail}')
                    return fa.responses.JSONResponse(status_code=fa.status.HTTP_401_UNAUTHORIZED,
                                                     content={'detail': detail})

                expected_signature = hmac.new(settings.INTER_SERVICE_SECRET.encode(), str(received_timestamp).encode(),
                                              hashlib.sha256).hexdigest()
                if not hmac.compare_digest(expected_signature, received_signature):
                    detail = f'{received_signature=:} doesnt match {expected_signature=:}'
                    logger.error(f'from {request.client=} {detail}')
                    return fa.responses.JSONResponse(status_code=fa.status.HTTP_401_UNAUTHORIZED,
                                                     content={'detail': detail})
            except Exception as e:
                return fa.responses.JSONResponse(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                 content={'detail': str(e)})

        response = await call_next(request)
        return response
