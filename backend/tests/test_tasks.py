import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_task_lifecycle(client: AsyncClient, auth_headers: dict):
    # 1. Create a task with subtasks
    create_resp = await client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Build Architecture Specs",
            "description": "Write system design markdown",
            "priority": "high",
            "estimated_duration": 45,
            "tags": ["architecture", "spec"],
            "subtasks": [
                {"title": "Draft DB ERD", "is_completed": False, "position": 0},
                {"title": "Draft API routes", "is_completed": False, "position": 1},
            ],
        },
    )
    assert create_resp.status_code == 201
    task = create_resp.json()
    task_id = task["id"]
    assert task["title"] == "Build Architecture Specs"
    assert task["priority"] == "high"
    assert len(task["subtasks"]) == 2

    # 2. Get tasks list
    list_resp = await client.get("/api/v1/tasks", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # 3. Update task status to completed
    update_resp = await client.put(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
        json={"status": "completed"},
    )
    assert update_resp.status_code == 200
    updated_task = update_resp.json()
    assert updated_task["status"] == "completed"
    assert updated_task["completed_at"] is not None

    # 4. Toggle subtask
    subtask_id = task["subtasks"][0]["id"]
    st_resp = await client.put(
        f"/api/v1/tasks/{task_id}/subtasks/{subtask_id}",
        headers=auth_headers,
        json={"is_completed": True},
    )
    assert st_resp.status_code == 200
    assert st_resp.json()["is_completed"] is True

    # 5. Delete task
    del_resp = await client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert del_resp.status_code == 204
