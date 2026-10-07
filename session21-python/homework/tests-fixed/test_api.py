# Fixed and extended version of backend/tests/test_api.py.
# FIX: the original creates `client = TestClient(app)` at module level. Without the
# context manager, FastAPI's startup event (Base.metadata.create_all) never runs, so
# the SQLite test database has no `tasks` table -> "no such table: tasks".
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:   # runs startup/shutdown events
        yield c


def test_health(client):
    assert client.get("/health").json() == {"status": "UP"}


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "TaskBoard API"


def test_create_task(client):
    response = client.post("/api/tasks", json={"title": "Deploy application", "priority": "HIGH", "assignee": "Student"})
    assert response.status_code == 201
    assert response.json()["title"] == "Deploy application"


def test_create_task_validation_rejects_empty_title(client):
    assert client.post("/api/tasks", json={"title": ""}).status_code == 422


def test_list_and_get_task(client):
    created = client.post("/api/tasks", json={"title": "Write tests"}).json()
    assert any(t["id"] == created["id"] for t in client.get("/api/tasks").json())
    assert client.get(f"/api/tasks/{created['id']}").json()["title"] == "Write tests"


def test_update_task_status(client):
    created = client.post("/api/tasks", json={"title": "Review PR"}).json()
    response = client.put(f"/api/tasks/{created['id']}", json={"status": "DONE"})
    assert response.status_code == 200
    assert response.json()["status"] == "DONE"


def test_delete_task_then_404(client):
    created = client.post("/api/tasks", json={"title": "Temporary"}).json()
    assert client.delete(f"/api/tasks/{created['id']}").status_code == 204
    assert client.get(f"/api/tasks/{created['id']}").status_code == 404


def test_stats(client):
    stats = client.get("/api/tasks/stats").json()
    assert stats["total"] == stats["todo"] + stats["inProgress"] + stats["done"]
    assert stats["done"] >= 1
