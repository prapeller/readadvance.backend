import datetime as dt
import re

import pydantic as pd

from core.enums import (
    PeriodEnum,
    QueueTaskPrioritiesEnum,
)


#######################################################################################################################
# celery_interval_schedule, celery_crontab_schedule
#######################################################################################################################

class IntervalScheduleUpdateSerializer(pd.BaseModel):
    every: int | None = None
    period: PeriodEnum | None = None


class IntervalScheduleCreateSerializer(IntervalScheduleUpdateSerializer):
    every: int
    period: PeriodEnum


class IntervalScheduleReadSerializer(IntervalScheduleCreateSerializer):
    id: int
    every: int
    period: PeriodEnum


class CrontabScheduleUpdateSerializer(pd.BaseModel):
    minute: str | None = None
    hour: str | None = None
    day_of_week: str | None = None
    day_of_month: str | None = None
    month_of_year: str | None = None
    timezone: str | None = 'UTC'

    @pd.field_validator('minute')
    @classmethod
    def validate_minute(cls, v: str):
        if v is not None and v != '' and not re.match(
                r'^(\*|([0-5]?\d)([-/][0-5]?\d)*)+(,(\*|([0-5]?\d)([-/][0-5]?\d)*))*$', v):
            raise ValueError("Invalid minute format. Valid formats: '*', '5', '10-20', '5,10,15', '*/5'")
        return v

    @pd.field_validator('hour')
    @classmethod
    def validate_hour(cls, v: str):
        if v is not None and v != '' and not re.match(
                r'^(\*|([01]?\d|2[0-3])([-/][01]?\d|2[0-3])*)+(,(\*|([01]?\d|2[0-3])([-/][01]?\d|2[0-3])*))*$', v):
            raise ValueError("Invalid hour format. Valid formats: '*', '5', '10-20', '5,10,15', '*/5'")
        return v

    @pd.field_validator('day_of_week')
    @classmethod
    def validate_day_of_week(cls, v: str):
        if v is not None and v != '' and not re.match(r'^(\*|([0-6])([-/][0-6])*)+(,(\*|([0-6])([-/][0-6])*))*$', v):
            raise ValueError("Invalid day_of_week format. Valid formats: '*', '1', '1-5', '1,3,5', '*/2'")
        return v

    @pd.field_validator('day_of_month')
    @classmethod
    def validate_day_of_month(cls, v: str):
        if v is not None and v != '' and not re.match(
                r'^(\*|([1-9]|[12]\d|3[01])([-/][1-9]|[12]\d|3[01])*)'
                r'+(,(\*|([1-9]|[12]\d|3[01])([-/][1-9]|[12]\d|3[01])*))*$', v):
            raise ValueError("Invalid day_of_month format. Valid formats: '*', '5', '10-20', '5,10,15', '*/5'")
        return v

    @pd.field_validator('month_of_year')
    @classmethod
    def validate_month_of_year(cls, v: str):
        if v is not None and v != '' and not re.match(
                r'^(\*|([1-9]|1[0-2])([-/][1-9]|1[0-2])*)+(,(\*|([1-9]|1[0-2])([-/][1-9]|1[0-2])*))*$', v):
            raise ValueError("Invalid month_of_year format. Valid formats: '*', '1', '1-12', '1,6,12', '*/3'")
        return v


class CrontabScheduleCreateSerializer(CrontabScheduleUpdateSerializer):
    minute: str | None = None
    hour: str | None = None
    day_of_week: str | None = None
    day_of_month: str | None = None
    month_of_year: str | None = None
    timezone: str | None = None


class CrontabScheduleReadSerializer(CrontabScheduleCreateSerializer):
    id: int


#######################################################################################################################
# celery_periodic_task
#######################################################################################################################


class PeriodicTaskUpdateSerializer(pd.BaseModel):
    name: str | None = None
    task: str | None = None
    interval_id: int | None = None
    crontab_id: int | None = None
    args: str | None = '[]'
    kwargs: str | None = '{}'
    queue: str | None = 'default'
    priority: QueueTaskPrioritiesEnum | None = QueueTaskPrioritiesEnum.q_1
    description: str | None = ''
    enabled: bool | None = True
    start_time: dt.datetime | None = None
    expires: dt.datetime | None = None

    class Config:
        from_attributes = True


class PeriodicTaskUpdateSchedulesSerializer(PeriodicTaskUpdateSerializer):
    interval: IntervalScheduleUpdateSerializer | None = None
    crontab: CrontabScheduleUpdateSerializer | None = None

    class Config:
        from_attributes = True


class PeriodicTaskCreateSerializer(PeriodicTaskUpdateSerializer):
    name: str
    task: str

    class Config:
        from_attributes = True


class PeriodicTaskCreateSchedulesSerializer(PeriodicTaskCreateSerializer):
    interval: IntervalScheduleCreateSerializer | None = None
    crontab: CrontabScheduleUpdateSerializer | None = None

    class Config:
        from_attributes = True


class PeriodicTaskReadSerializer(PeriodicTaskCreateSerializer):
    id: int
    description: str
    date_changed: dt.datetime | None = None
    total_run_count: int
    last_run_at: dt.datetime | None = None
    one_off: bool

    class Config:
        from_attributes = True


class PeriodicTaskReadSchedulesSerializer(PeriodicTaskReadSerializer):
    interval: IntervalScheduleReadSerializer | None = None
    crontab: CrontabScheduleReadSerializer | None = None

    class Config:
        from_attributes = True
