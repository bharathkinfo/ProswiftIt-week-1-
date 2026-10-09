from typing import Any

from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from redis import Redis
from redis.exceptions import RedisError

from app.celery_app import celery_app
from app.config import REDIS_URL
from app.tasks import add_numbers


app = FastAPI(title="Universal Follow-Up Engine", version="0.1.0")


class AddNumbersRequest(BaseModel):
    a: int
    b: int


class QueuedTaskResponse(BaseModel):
    task_id: str
    state: str


class TaskStatusResponse(BaseModel):
    task_id: str
    state: str
    result: Any | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/redis")
def redis_health() -> dict[str, bool | str]:
    client = Redis.from_url(REDIS_URL, decode_responses=True)
    try:
        connected = client.ping()
        return {"service": "redis", "connected": connected}
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis is unavailable") from exc
    finally:
        client.close()


@app.post("/tasks/add", response_model=QueuedTaskResponse, status_code=202)
def queue_addition(payload: AddNumbersRequest) -> QueuedTaskResponse:
    task = add_numbers.delay(payload.a, payload.b)
    return QueuedTaskResponse(task_id=task.id, state="PENDING")


@app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def task_status(task_id: str) -> TaskStatusResponse:
    task = AsyncResult(task_id, app=celery_app)
    result = task.result if task.successful() else None
    return TaskStatusResponse(task_id=task_id, state=task.state, result=result)
