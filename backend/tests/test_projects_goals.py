import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_project_and_goal_lifecycle(client: AsyncClient, auth_headers: dict):
    # 1. Create a Goal
    goal_resp = await client.post(
        "/api/v1/goals",
        headers=auth_headers,
        json={
            "title": "Ship Personalix OS",
            "category": "career",
            "description": "Production release",
            "milestones": [
                {"title": "Backend Complete", "position": 0},
                {"title": "Frontend Complete", "position": 1},
            ],
        },
    )
    assert goal_resp.status_code == 201
    goal = goal_resp.json()
    goal_id = goal["id"]
    assert goal["title"] == "Ship Personalix OS"

    # 2. Create a Project linked to Goal
    proj_resp = await client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={
            "title": "Personalix OS Web Client",
            "description": "Next.js frontend",
            "goal_id": goal_id,
            "color": "#3b82f6",
            "icon": "layout",
        },
    )
    assert proj_resp.status_code == 201
    proj = proj_resp.json()
    proj_id = proj["id"]
    assert proj["goal_id"] == goal_id

    # 3. Add task linked to Project
    task_resp = await client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Design Kanban Component",
            "project_id": proj_id,
            "goal_id": goal_id,
            "priority": "high",
        },
    )
    assert task_resp.status_code == 201

    # 4. Verify Project list and task counts
    projs_resp = await client.get("/api/v1/projects", headers=auth_headers)
    assert projs_resp.status_code == 200
    assert len(projs_resp.json()) >= 1
