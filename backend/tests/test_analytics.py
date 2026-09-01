import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analytics_and_dashboard(client: AsyncClient, auth_headers: dict):
    # 1. Test Productivity Score endpoint
    score_resp = await client.get("/api/v1/analytics/productivity-score", headers=auth_headers)
    assert score_resp.status_code == 200
    score = score_resp.json()
    assert 0.0 <= score["total_score"] <= 100.0
    assert score["grade"] in ["S", "A", "B", "C", "D"]
    assert "breakdown" in score

    # 2. Test Dashboard Summary endpoint
    summary_resp = await client.get("/api/v1/analytics/dashboard-summary", headers=auth_headers)
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert "greeting" in summary
    assert "tasks_summary" in summary
    assert "habits_summary" in summary
    assert "ai_daily_insight" in summary
