from unittest.mock import Mock

from app.main import AddNumbersRequest, health, queue_addition, redis_health
from app.tasks import add_numbers


def test_health() -> None:
    response = health()
    assert response == {"status": "ok"}


def test_add_numbers_task() -> None:
    assert add_numbers.run(10, 20) == 30


def test_queue_addition(monkeypatch) -> None:
    queued_task = Mock(id="test-task-id")
    delay = Mock(return_value=queued_task)
    monkeypatch.setattr("app.main.add_numbers.delay", delay)

    response = queue_addition(AddNumbersRequest(a=10, b=20))

    delay.assert_called_once_with(10, 20)
    assert response.model_dump() == {
        "task_id": "test-task-id",
        "state": "PENDING",
    }


def test_redis_health(monkeypatch) -> None:
    redis_client = Mock()
    redis_client.ping = Mock(return_value=True)
    redis_client.close = Mock()
    monkeypatch.setattr("app.main.Redis.from_url", Mock(return_value=redis_client))

    response = redis_health()

    assert response == {"service": "redis", "connected": True}
    redis_client.close.assert_called_once()
