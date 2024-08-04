from typing import Annotated

from fastapi import HTTPException, APIRouter, Body, Depends
from pydantic import BaseModel
import requests
from datetime import datetime, timedelta


router = APIRouter(
    tags=["Task"]
)
class Task(BaseModel):
    title: str
    description: str
    responsible_id: int


@router.post("/task/add")
def add_task(task: Annotated[Task, Body(..., example={
    "title": "Изучить пример 11 видео-курса",
    "description": "Просмотреть видео, скачать пример. Заменить код вебхука и выложить на сервер для выполнения",
    "responsible_id": 1
})]):
    url = 'https://b24-r7ve9v.bitrix24.ru/rest/1/ljbxv4hh6sizr0f9/tasks.task.add'

    # Устанавливаем DEADLINE на неделю вперед
    deadline = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d') + ' 19:00'

    fields = {
        'TITLE': task.title,
        'DESCRIPTION': task.description,
        'DEADLINE': deadline,
        'RESPONSIBLE_ID': task.responsible_id
    }

    response = requests.post(url, json={'fields': fields})

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()