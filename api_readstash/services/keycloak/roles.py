from core.config import settings
from core.enums import UserRolesEnum

role_head = {
    "id": '693ea5b2-6f33-4ced-9541-82e0e6e29383',
    "name": UserRolesEnum.head,
    "composite": False,
    "clientRole": False,
    "containerId": settings.KEYCLOAK_REALM,
}

role_admin = {
    "id": 'd17ca287-ea1e-48a3-97b3-77486b522cbf',
    "name": UserRolesEnum.admin,
    "composite": False,
    "clientRole": False,
    "containerId": settings.KEYCLOAK_REALM,
}

role_guest = {
    "id": 'f06fcb2b-a52a-4ed5-a705-a2339875a2de',
    "name": UserRolesEnum.guest,
    "composite": False,
    "clientRole": False,
    "containerId": settings.KEYCLOAK_REALM,
}

role_premium = {
    "id": '87887d86-f16d-4998-808c-47720fc55bd8',
    "name": UserRolesEnum.premium,
    "composite": False,
    "clientRole": False,
    "containerId": settings.KEYCLOAK_REALM,
}

kc_user_roles = {
    UserRolesEnum.head: role_head,
    UserRolesEnum.admin: role_admin,
    UserRolesEnum.guest: role_guest,
    UserRolesEnum.premium: role_premium,
}
