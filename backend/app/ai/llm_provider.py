import json
import re
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings
from app.core.logging import logger


class BaseLLMProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Returns a dictionary with:
        {
            "reply": str,
            "tool_calls": List[{"id": str, "name": str, "arguments": dict}],
            "provider": str,
            "model": str,
            "tokens_used": int
        }
        """
        pass


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.base_url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise Exception(f"OpenAI API Error ({resp.status_code}): {resp.text}")
            
            data = resp.json()
            choice = data["choices"][0]
            msg = choice["message"]
            
            tool_calls = []
            if "tool_calls" in msg and msg["tool_calls"]:
                for tc in msg["tool_calls"]:
                    try:
                        args = json.loads(tc["function"]["arguments"])
                    except Exception:
                        args = {}
                    tool_calls.append({
                        "id": tc["id"],
                        "name": tc["function"]["name"],
                        "arguments": args,
                    })

            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            return {
                "reply": msg.get("content") or "",
                "tool_calls": tool_calls,
                "provider": "openai",
                "model": self.model,
                "tokens_used": tokens_used,
            }


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        # Extract system prompt if present
        system_prompt = ""
        user_messages = []
        for m in messages:
            if m.get("role") == "system":
                system_prompt += m.get("content", "") + "\n"
            else:
                user_messages.append({"role": m["role"], "content": m["content"]})

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": user_messages,
            "max_tokens": 1500,
            "temperature": temperature,
        }
        if system_prompt:
            payload["system"] = system_prompt.strip()

        if tools:
            # Convert OpenAI tool format to Anthropic format
            anthropic_tools = []
            for t in tools:
                fn = t["function"]
                anthropic_tools.append({
                    "name": fn["name"],
                    "description": fn.get("description", ""),
                    "input_schema": fn.get("parameters", {"type": "object", "properties": {}}),
                })
            payload["tools"] = anthropic_tools

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.base_url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise Exception(f"Anthropic API Error ({resp.status_code}): {resp.text}")

            data = resp.json()
            reply_text = ""
            tool_calls = []

            for content_block in data.get("content", []):
                if content_block.get("type") == "text":
                    reply_text += content_block.get("text", "")
                elif content_block.get("type") == "tool_use":
                    tool_calls.append({
                        "id": content_block.get("id", str(uuid.uuid4())[:8]),
                        "name": content_block.get("name"),
                        "arguments": content_block.get("input", {}),
                    })

            tokens_used = (data.get("usage", {}).get("input_tokens", 0) +
                           data.get("usage", {}).get("output_tokens", 0))

            return {
                "reply": reply_text,
                "tool_calls": tool_calls,
                "provider": "anthropic",
                "model": self.model,
                "tokens_used": tokens_used,
            }


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        
        contents = []
        system_instruction = None

        for m in messages:
            role = m.get("role")
            content = m.get("content", "")
            if role == "system":
                system_instruction = {"parts": [{"text": content}]}
            else:
                gemini_role = "user" if role == "user" else "model"
                contents.append({"role": gemini_role, "parts": [{"text": content}]})

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"temperature": temperature},
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.base_url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise Exception(f"Gemini API Error ({resp.status_code}): {resp.text}")

            data = resp.json()
            candidates = data.get("candidates", [])
            reply_text = ""
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                for p in parts:
                    if "text" in p:
                        reply_text += p["text"]

            return {
                "reply": reply_text,
                "tool_calls": [],
                "provider": "gemini",
                "model": self.model,
                "tokens_used": 200,
            }


class OfflineHeuristicProvider(BaseLLMProvider):
    """
    Production-grade heuristic NLP assistant engine that interprets user intents,
    triggers real tool calls (tasks, plans, reviews, notes, knowledge search),
    and formats intelligent markdown replies without requiring third-party API keys.
    """
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        user_message = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_message = m.get("content", "")
                break

        msg_lower = user_message.lower().strip()
        tool_calls: List[Dict[str, Any]] = []
        reply: str = ""

        # Intent 1: "Plan my day" / "daily plan" / "what should I do today"
        if any(k in msg_lower for k in ["plan my day", "daily plan", "schedule my day", "what should i focus on today"]):
            tool_calls.append({
                "id": str(uuid.uuid4())[:8],
                "name": "generate_daily_plan",
                "arguments": {},
            })
            reply = "I've structured an optimized daily plan for you based on your pending high-priority tasks and calendar schedule."

        # Intent 2: "Weekly review" / "summarize my week" / "how did i do this week"
        elif any(k in msg_lower for k in ["weekly review", "summarize my week", "how was my week", "prepare weekly review"]):
            tool_calls.append({
                "id": str(uuid.uuid4())[:8],
                "name": "generate_weekly_review",
                "arguments": {},
            })
            reply = "I've compiled your comprehensive weekly performance review, analyzing task completion rates, habit consistency, and key bottlenecks."

        # Intent 3: Create a task -> "create a task...", "add task...", "remind me to..."
        elif any(msg_lower.startswith(k) for k in ["create task", "create a task", "add task", "add a task", "new task", "remind me to"]):
            # Extract title and priority
            raw_title = re.sub(r'^(create\s+(a\s+)?task|add\s+(a\s+)?task|new\s+task|remind\s+me\s+to)\s*:?\s*', '', user_message, flags=re.IGNORECASE).strip()
            priority = "medium"
            if "urgent" in msg_lower or "critical" in msg_lower or "asap" in msg_lower:
                priority = "critical"
            elif "high priority" in msg_lower or "important" in msg_lower:
                priority = "high"

            tool_calls.append({
                "id": str(uuid.uuid4())[:8],
                "name": "create_task",
                "arguments": {
                    "title": raw_title or "New Task",
                    "priority": priority,
                },
            })
            reply = f"I've created the task: **{raw_title or 'New Task'}** (Priority: `{priority}`)."

        # Intent 4: Knowledge / Notes search -> "find...", "search for...", "what do I know about..."
        elif any(msg_lower.startswith(k) for k in ["find ", "search ", "what do i have on ", "lookup "]):
            query = re.sub(r'^(find|search(\s+for)?|what\s+do\s+i\s+have\s+on|lookup)\s+', '', user_message, flags=re.IGNORECASE).strip()
            tool_calls.append({
                "id": str(uuid.uuid4())[:8],
                "name": "search_knowledge",
                "arguments": {"query": query},
            })
            reply = f"Searching your documents, notes, and tasks for '{query}'..."

        # Intent 5: Create a note -> "create note...", "take a note..."
        elif any(msg_lower.startswith(k) for k in ["create note", "take note", "add note", "new note"]):
            content = re.sub(r'^(create\s+note|take\s+note|add\s+note|new\s+note)\s*:?\s*', '', user_message, flags=re.IGNORECASE).strip()
            title = content.split("\n")[0][:40] or "Quick Note"
            tool_calls.append({
                "id": str(uuid.uuid4())[:8],
                "name": "create_note",
                "arguments": {"title": title, "content": content},
            })
            reply = f"I've created a new note: **{title}**."

        # Intent 6: Productivity Stats / Status check
        elif any(k in msg_lower for k in ["productivity score", "my stats", "how productive am i", "dashboard summary"]):
            tool_calls.append({
                "id": str(uuid.uuid4())[:8],
                "name": "get_productivity_stats",
                "arguments": {},
            })
            reply = "Fetching your real-time productivity breakdown and performance metrics."

        # Default Intelligent Assistant Response
        else:
            reply = (
                f"Hello! I am your **Personalix OS Assistant**.\n\n"
                f"I can help you coordinate your workflow across tasks, projects, goals, habits, and knowledge. Try asking me:\n"
                f"- `\"Plan my day\"` — Auto-generates time blocks for your focus tasks.\n"
                f"- `\"Create a task: Refactor authentication service\"` — Adds prioritized tasks.\n"
                f"- `\"Prepare my weekly review\"` — Computes wins, streaks, and bottlenecks.\n"
                f"- `\"Search for backend architecture notes\"` — Semantic search across your knowledge base.\n"
                f"- `\"What should I prioritize today?\"` — Identifies urgent deadlines and high leverage items."
            )

        return {
            "reply": reply,
            "tool_calls": tool_calls,
            "provider": "offline_heuristic",
            "model": "personalix-heuristic-v1",
            "tokens_used": 50,
        }


def get_llm_provider(preferred_provider: str = "auto") -> BaseLLMProvider:
    """Factory selecting the best available LLM provider with graceful fallbacks."""
    provider_choice = preferred_provider or settings.DEFAULT_AI_PROVIDER

    if provider_choice in ("auto", "openai") and settings.OPENAI_API_KEY:
        return OpenAIProvider(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)

    if provider_choice in ("auto", "anthropic") and settings.ANTHROPIC_API_KEY:
        return AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY, model=settings.ANTHROPIC_MODEL)

    if provider_choice in ("auto", "gemini") and settings.GOOGLE_API_KEY:
        return GeminiProvider(api_key=settings.GOOGLE_API_KEY, model=settings.GEMINI_MODEL)

    # Fallback to local heuristic provider (zero external dependency required)
    return OfflineHeuristicProvider()
