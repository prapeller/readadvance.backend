import pydantic as pd


class TaskReadSerializer(pd.BaseModel):
    task_id: str
