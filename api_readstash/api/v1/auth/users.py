import fastapi as fa
import pydantic as pd

from core.security import auth_head, current_user_dependency
from db.models.user import UserModel
from db.serializers.user import UserReadSerializer, UserUpdateSerializer, UserCreateSerializer
from services.keycloak.keycloak import KCAdmin
from services.user_manager.user_manager import UserManager, user_manager_dependency
router = fa.APIRouter()


@router.get("/all",
            response_model=list[UserReadSerializer])
@auth_head
async def users_list(
        current_user: UserModel = fa.Depends(current_user_dependency),
        user_manager: UserManager = fa.Depends(user_manager_dependency),
):
    """list all users"""
    return await user_manager.list_filtered()


@router.get("/active",
            response_model=list[UserReadSerializer])
@auth_head
async def users_list(
        current_user: UserModel = fa.Depends(current_user_dependency),
        user_manager: UserManager = fa.Depends(user_manager_dependency),
):
    """list all active users"""
    return await user_manager.list_filtered(is_active=True)


@router.get("/inactive",
            response_model=list[UserReadSerializer])
@auth_head
async def users_list(
        current_user: UserModel = fa.Depends(current_user_dependency),
        user_manager: UserManager = fa.Depends(user_manager_dependency),
):
    """list all inactive users"""
    return await user_manager.list_filtered(is_active=False)


@router.get("/me",
            response_model=UserReadSerializer)
async def users_read_me(
        current_user: UserModel = fa.Depends(current_user_dependency)
):
    return current_user


@router.get("/{user_uuid}",
            response_model=UserReadSerializer)
@auth_head
async def users_read(
        user_uuid: pd.UUID4,
        user_manager: UserManager = fa.Depends(user_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """read user by uuid"""
    return await user_manager.get_user(uuid=str(user_uuid))


@router.get("/fetch-from-keycloack/my-roles")
@auth_head
async def users_fetch_from_keycloak_my_roles(
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """fetches from keycloack realm-level role-mappings of current user"""
    return await KCAdmin().get_user_roles(current_user.uuid)


@router.post("/", response_model=UserReadSerializer)
@auth_head
async def users_create(
        user_ser: UserCreateSerializer,
        user_manager: UserManager = fa.Depends(user_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """create user"""
    return await user_manager.create_user(user_ser)


@router.put("/me", response_model=UserReadSerializer)
async def users_update_me(
        user_ser: UserUpdateSerializer,
        user_manager: UserManager = fa.Depends(user_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """update current user"""
    return await user_manager.update_user(current_user.uuid, user_ser)


@router.put("/{user_uuid}",
            response_model=UserReadSerializer)
@auth_head
async def users_update(
        user_uuid: pd.UUID4,
        user_ser: UserUpdateSerializer,
        user_manager: UserManager = fa.Depends(user_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    return await user_manager.update_user(str(user_uuid), user_ser)


@router.post("/activate/{user_uuid}")
@auth_head
async def users_activate(
        user_uuid: pd.UUID4,
        user_manager: UserManager = fa.Depends(user_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """activate user"""
    return await user_manager.activate(str(user_uuid))


@router.delete("/deactivate/{user_uuid}")
@auth_head
async def users_deactivate(
        user_uuid: pd.UUID4,
        user_manager: UserManager = fa.Depends(user_manager_dependency),
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    """deactivate user"""
    return await user_manager.deactivate(str(user_uuid))
