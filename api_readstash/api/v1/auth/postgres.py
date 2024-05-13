import os
import subprocess

import fastapi as fa

from core.config import BASE_DIR
from core.enums import EnvEnum
from core.exceptions import NotFoundException
from core.security import auth_head, current_user_dependency
from db.models.user import UserModel

router = fa.APIRouter()


@router.post("/dump", status_code=fa.status.HTTP_201_CREATED)
@auth_head
def postgres_dump(
        env: EnvEnum = EnvEnum.local,
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    script_path = BASE_DIR / 'scripts/postgres/dump.sh'
    if not os.path.isfile(script_path):
        raise NotFoundException(f'{script_path} not found')

    result = subprocess.run(script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={'ENV': env})
    return {
        'stderr': f'{result.stderr.decode("utf-8", "ignore")}',
        'stdout': f'{result.stdout.decode("utf-8", "ignore")}',
    }


@router.get("/check-dumps")
@auth_head
def postgres_check_dumps(
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    script_path = BASE_DIR / 'scripts/postgres/check_dumps.sh'
    if not os.path.isfile(script_path):
        raise NotFoundException(f'{script_path} not found')

    result = subprocess.run(script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {
        'stderr': f'{result.stderr.decode("utf-8", "ignore")}',
        'stdout': f'{result.stdout.decode("utf-8", "ignore")}',
    }


@router.get("/download-last-dump")
@auth_head
def postgres_download_last_dump(
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    file_path = BASE_DIR / 'staticfiles/backups/dump_last'
    if not os.path.isfile(file_path):
        raise NotFoundException(f'{file_path} not found')

    headers = {'Content-Disposition': 'attachment',
               'Content-Type': 'application/octet-stream'}
    return fa.responses.FileResponse(path=file_path, headers=headers, filename='dump_last')


@router.post("/restore-from-dump", status_code=fa.status.HTTP_201_CREATED)
@auth_head
async def postgres_restore(
        dump_file: fa.UploadFile,
        env: EnvEnum = EnvEnum.local,
        current_user: UserModel = fa.Depends(current_user_dependency),
):
    script_path = BASE_DIR / 'scripts/postgres/restore_from_dump.sh'
    if not os.path.isfile(script_path):
        raise NotFoundException(f'{script_path} not found')

    contents = await dump_file.read()
    uploaded_file_path = BASE_DIR / 'staticfiles/backups/uploaded_dump'
    with open(uploaded_file_path, 'wb') as uploaded:
        uploaded.write(contents)

    subprocess.Popen(script_path, env={'ENV': env})
    return {'message': 'ok'}
