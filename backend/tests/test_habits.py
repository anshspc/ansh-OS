from datetime import date, timedelta
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_habits_and_streaks(client: AsyncClient, auth_headers: dict):
    # 1. Create Habit
    h_resp = await client.post(
        "/api/v1/habits",
        headers=auth_headers,
        json={
            "title": "Morning Code Review",
            "frequency": "daily",
            "reminder_time": "09:00",
            "color": "#6366f1",
        },
    )
    assert h_resp.status_code == 201
    habit = h_resp.json()
    habit_id = habit["id"]

    # 2. Log completions for today and yesterday to check streak calculation
    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()

    log1 = await client.post(
        f"/api/v1/habits/{habit_id}/log",
        headers=auth_headers,
        json={"logged_date": yesterday_str, "completed": True},
    )
    assert log1.status_code == 200

    log2 = await client.post(
        f"/api/v1/habits/{habit_id}/log",
        headers=auth_headers,
        json={"logged_date": today_str, "completed": True},
    )
    assert log2.status_code == 200
    assert log2.json()["streak_count"] == 2
    assert log2.json()["today_completed"] is True

    # 3. Check Heatmap endpoint
    hm_resp = await client.get("/api/v1/habits/heatmap", headers=auth_headers)
    assert hm_resp.status_code == 200
    heatmap_data = hm_resp.json()
    assert today_str in heatmap_data
