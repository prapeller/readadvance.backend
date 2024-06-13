from pathlib import Path

import fastapi as fa

from core.logger_config import setup_logger
from db.models.periodic_task import (
    PeriodicTaskModel,
    IntervalScheduleModel,
    CrontabScheduleModel,
)
from db.serializers.periodic_task import (
    PeriodicTaskCreateSchedulesSerializer,
    PeriodicTaskCreateSerializer,
    PeriodicTaskUpdateSchedulesSerializer,
    PeriodicTaskUpdateSerializer,
)
from services.postgres.repository import SqlAlchemyRepositorySync, sqlalchemy_repo_sync_dependency

logger = setup_logger(log_name=Path(__file__).resolve().parent.stem)


class PeriodicTaskManager:
    def __init__(self, repo: SqlAlchemyRepositorySync):
        self.repo = repo

    def create_periodic_task_with_schedule(
            self,
            periodic_task_ser: PeriodicTaskCreateSchedulesSerializer) -> PeriodicTaskModel:
        if periodic_task_ser.interval is not None:
            is_created, interval = self.repo.get_or_create(IntervalScheduleModel, periodic_task_ser.interval)
            periodic_task_ser.interval_id = interval.id

        if periodic_task_ser.crontab is not None:
            is_created, crontab = self.repo.get_or_create(CrontabScheduleModel, periodic_task_ser.crontab)
            periodic_task_ser.crontab_id = crontab.id

        periodic_task = self.repo.create(PeriodicTaskModel,
                                         PeriodicTaskCreateSerializer(**periodic_task_ser.model_dump()))
        return periodic_task

    def update_periodic_task_with_schedule(
            self,
            task_id,
            periodic_task_ser: PeriodicTaskUpdateSchedulesSerializer) -> PeriodicTaskModel:
        periodic_task = self.repo.get(PeriodicTaskModel, id=task_id)
        if periodic_task_ser.interval is not None:
            periodic_task_ser.crontab_id = None
            is_created, interval = self.repo.get_or_create(
                IntervalScheduleModel, periodic_task_ser.interval)
            periodic_task_ser.interval_id = interval.id

        if periodic_task_ser.crontab is not None:
            periodic_task_ser.interval_id = None
            is_created, crontab = self.repo.get_or_create(
                CrontabScheduleModel, periodic_task_ser.crontab)
            periodic_task_ser.crontab_id = crontab.id

        periodic_task = self.repo.update(periodic_task, PeriodicTaskUpdateSerializer(**periodic_task_ser.model_dump()))
        return periodic_task


async def periodic_task_manager_sync_dependency(
        repo: SqlAlchemyRepositorySync = fa.Depends(sqlalchemy_repo_sync_dependency),
) -> PeriodicTaskManager:
    return PeriodicTaskManager(repo)
