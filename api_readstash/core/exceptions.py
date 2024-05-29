import fastapi as fa

from core.enums import ResponseDetailEnum


class BadRequestException(fa.HTTPException):
    def __init__(self, detail=None):
        super().__init__(
            status_code=fa.status.HTTP_400_BAD_REQUEST,
            detail=ResponseDetailEnum.bad_request if detail is None else detail,
        )


class NotFoundException(fa.HTTPException):
    def __init__(self, detail=None):
        super().__init__(
            status_code=fa.status.HTTP_404_NOT_FOUND,
            detail=ResponseDetailEnum.not_found if detail is None else detail,
        )


class ObjStorageDBException(fa.HTTPException):
    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseDetailEnum.object_storage_db_exception if detail is None else detail,
        )


class NotValidPlaceholdersException(fa.HTTPException):
    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=fa.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ResponseDetailEnum.not_valid_placeholders if detail is None else detail,
        )


class AlreadyExistsException(fa.HTTPException):
    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=fa.status.HTTP_400_BAD_REQUEST,
            detail=ResponseDetailEnum.already_exists if detail is None else detail,
        )


class UnauthorizedException(fa.HTTPException):
    def __init__(self, detail=None):
        super().__init__(
            status_code=fa.status.HTTP_401_UNAUTHORIZED,
            detail=ResponseDetailEnum.unauthorized if detail is None else detail,
        )


class InternalServerError(fa.HTTPException):
    def __init__(self, detail=None):
        super().__init__(
            status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseDetailEnum.server_error if detail is None else detail,
        )


class UnprocessableEntityException(fa.HTTPException):
    def __init__(self, detail=None):
        super().__init__(
            status_code=fa.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ResponseDetailEnum.unprocessable_entity if detail is None else detail,
        )

class KeycloakRequestException(fa.HTTPException):
    def __init__(self, detail=None):
        super().__init__(
            status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='keycloak exception' if detail is None else detail,
        )