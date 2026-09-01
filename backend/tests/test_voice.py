"""Tests for Personalix Voice endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_voice_capabilities(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/voice/capabilities", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "stt_providers" in data
    assert "supported_languages" in data
    assert isinstance(data["supported_languages"], list)
    assert len(data["supported_languages"]) > 0


@pytest.mark.asyncio
async def test_voice_settings_get_default(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/voice/settings", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["auto_speak"] is True
    assert data["voice_speed"] == 1.0
    assert data["voice_pitch"] == 1.0
    assert data["save_transcripts"] is True
    assert data["language"] == "en-US"


@pytest.mark.asyncio
async def test_voice_settings_update(client: AsyncClient, auth_headers: dict):
    payload = {
        "voice_name": "Google UK English Female",
        "voice_speed": 1.2,
        "voice_pitch": 0.9,
        "auto_speak": True,
        "language": "en-GB",
        "proactive_mode": False,
        "proactive_interval_minutes": 15,
        "save_transcripts": True,
        "voice_history_enabled": True,
        "wake_word_enabled": False,
        "confirm_destructive_actions": True,
    }
    resp = await client.put("/api/v1/voice/settings", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["voice_name"] == "Google UK English Female"
    assert data["voice_speed"] == 1.2
    assert data["language"] == "en-GB"

    # Verify persisted
    resp2 = await client.get("/api/v1/voice/settings", headers=auth_headers)
    assert resp2.json()["voice_name"] == "Google UK English Female"


@pytest.mark.asyncio
async def test_voice_chat_basic(client: AsyncClient, auth_headers: dict):
    payload = {
        "transcript": "What tasks do I have today?",
        "screen_context": {"page": "dashboard"},
        "language": "en-US",
        "input_type": "voice",
    }
    resp = await client.post("/api/v1/voice/chat", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 0
    assert data["input_type"] == "voice"
    assert "conversation_id" in data
    assert data["requires_confirmation"] is False


@pytest.mark.asyncio
async def test_voice_chat_empty_transcript(client: AsyncClient, auth_headers: dict):
    payload = {"transcript": "   ", "language": "en-US", "input_type": "voice"}
    resp = await client.post("/api/v1/voice/chat", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "catch" in data["reply"].lower() or "repeat" in data["reply"].lower()


@pytest.mark.asyncio
async def test_voice_chat_destructive_triggers_confirmation(
    client: AsyncClient, auth_headers: dict
):
    payload = {
        "transcript": "Delete all my completed tasks",
        "language": "en-US",
        "input_type": "voice",
    }
    resp = await client.post("/api/v1/voice/chat", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["requires_confirmation"] is True
    assert data["confirmation_prompt"] is not None
    assert "?" in data["reply"] or "confirm" in data["reply"].lower()


@pytest.mark.asyncio
async def test_voice_chat_screen_context_injected(client: AsyncClient, auth_headers: dict):
    payload = {
        "transcript": "Give me a quick update.",
        "screen_context": {
            "page": "projects",
            "entity_type": "project",
            "entity_title": "Personalix OS",
            "entity_id": "proj-001",
        },
        "language": "en-US",
        "input_type": "voice",
    }
    resp = await client.post("/api/v1/voice/chat", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 5


@pytest.mark.asyncio
async def test_voice_chat_hinglish(client: AsyncClient, auth_headers: dict):
    payload = {
        "transcript": "Mujhe aaj ke tasks dikhao.",
        "language": "hi-IN",
        "input_type": "voice",
    }
    resp = await client.post("/api/v1/voice/chat", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 0


@pytest.mark.asyncio
async def test_voice_history(client: AsyncClient, auth_headers: dict):
    payload = {
        "transcript": "How productive was I this week?",
        "language": "en-US",
        "input_type": "voice",
    }
    await client.post("/api/v1/voice/chat", json=payload, headers=auth_headers)

    resp = await client.get("/api/v1/voice/history?limit=10", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
