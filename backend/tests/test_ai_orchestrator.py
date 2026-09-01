import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ai_chat_and_tools(client: AsyncClient, auth_headers: dict):
    # 1. Test AI Chat with Task Creation Intent
    chat_resp = await client.post(
        "/api/v1/ai/chat",
        headers=auth_headers,
        json={"message": "create task: Review security audit findings", "provider": "fallback"},
    )
    assert chat_resp.status_code == 200
    data = chat_resp.json()
    assert "conversation_id" in data
    assert len(data["tool_calls"]) >= 1
    assert data["tool_calls"][0]["name"] == "create_task"

    # 2. Test AI Memory Extraction & Storage
    mem_chat_resp = await client.post(
        "/api/v1/ai/chat",
        headers=auth_headers,
        json={"message": "Remember that I prefer morning deep work sessions from 8am to 11am", "provider": "fallback"},
    )
    assert mem_chat_resp.status_code == 200

    # Verify memory persisted
    mems_resp = await client.get("/api/v1/ai/memories", headers=auth_headers)
    assert mems_resp.status_code == 200
    memories = mems_resp.json()
    assert len(memories) >= 1
