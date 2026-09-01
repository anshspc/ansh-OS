# Personalix OS — AI Architecture

## AI System Overview

The AI engine of Personalix OS is a multi-provider, tool-calling agent that has full access to the user's personal data through a structured tool dispatcher.

## Provider Abstraction

```python
# app/ai/llm_provider.py
class BaseLLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages, tools) -> LLMResponse: ...

# Concrete providers:
# OpenAIProvider    → gpt-4o-mini with function calling
# AnthropicProvider → claude-3-5-sonnet with tool use
# GeminiProvider    → gemini-1.5-flash with function declarations
# FallbackHeuristicProvider → deterministic intent parser (no API key needed)
```

The active provider is selected via:
1. Per-request `provider` field in the chat payload
2. `DEFAULT_AI_PROVIDER` environment variable
3. Automatic fallback to `FallbackHeuristicProvider` if no API key is configured

## Tool Calling System

### Available Tools (11 total)

| Tool | Description |
|---|---|
| `create_task` | Create a task with title, due date, priority |
| `update_task` | Update task status, priority, or due date |
| `get_tasks` | Retrieve tasks with optional status filter |
| `create_goal` | Create a strategic goal with category |
| `update_goal` | Update goal progress or status |
| `log_habit` | Log a habit completion for today |
| `get_habits` | Retrieve habit list with streak data |
| `search_knowledge` | Semantic vector search across documents |
| `get_calendar_events` | Retrieve upcoming calendar events |
| `create_calendar_event` | Create a new event |
| `get_analytics` | Retrieve productivity score breakdown |

### Tool Execution Flow

```
User Message
     │
     ▼
AIOrchestrator.process_chat()
     │
     ├── 1. Build system context
     │      ├── User preferences
     │      ├── Long-term AI memories (top-5 by relevance)
     │      ├── Upcoming calendar events
     │      ├── Active tasks (top-10)
     │      └── Dynamic productivity state
     │
     ├── 2. LLM call with tool definitions
     │
     ├── 3. Tool execution loop (max 3 rounds)
     │      ├── Parse tool_calls from LLM response
     │      ├── ToolDispatcher.execute(name, args)
     │      ├── Append tool results to messages
     │      └── LLM call again with results
     │
     └── 4. Return final AIChatResponse
            ├── reply (natural language)
            ├── tool_calls (list of executed tools + results)
            ├── conversation_id
            └── tokens_used
```

## AI Memory System

### Memory Categories

| Category | Example |
|---|---|
| `preference` | "User prefers TypeScript over JavaScript" |
| `goal` | "User wants to switch to AI engineering by end of year" |
| `project` | "User is building Personalix OS as portfolio project" |
| `fact` | "User works best in 2-hour deep work blocks" |
| `behavioral_pattern` | "User's productivity peaks between 10am and 2pm" |

### Memory Extraction

Memories are extracted from conversations when:
- The user states a preference explicitly
- The user describes a goal or aspiration
- The AI infers a behavioral pattern from repeated requests

### Memory Retrieval in Context

At the start of every conversation turn, the top-5 most relevant memories are fetched and injected into the system context:

```python
memories = await AIMemoryService.get_memories(db, user_id, limit=5)
memory_context = "\n".join([f"- [{m.category}] {m.content}" for m in memories])
system_prompt += f"\n\nUser Long-Term Memory:\n{memory_context}"
```

## Vector RAG System

### Embedding Pipeline

```
Document text
      │
      ▼
Chunking (500 tokens, 50 token overlap)
      │
      ▼
Embedding (OpenAI text-embedding-3-small → 1536 dims)
OR
Offline SHA-256 hash encoder → 1536-dim float array
      │
      ▼
Store in document_chunks table (embedding as JSON array)
```

### Retrieval Pipeline

```
Query string
      │
      ▼
Embed query (same encoder as ingestion)
      │
      ▼
SELECT all chunks for user
      │
      ▼
Cosine similarity (Python, in-memory)
      │
      ▼
Top-K results sorted by similarity score
      │
      ▼
Return chunks + scores to caller
```

### Offline Mode

When no OpenAI key is present, the system uses a deterministic hash encoder:

```python
def _offline_embed(text: str) -> list[float]:
    # SHA-256 of text → 32 bytes → repeat to 1536 floats
    # Deterministic: same text always produces same vector
    # Cosine similarity still works for relative ranking
```

This means the knowledge base works completely offline — useful for development and demos.

## Voice AI Pipeline

```
Browser SpeechRecognition
      │ transcript string
      ▼
POST /api/v1/voice/chat
      │
      ▼
voice_router.py
      ├── Destructive command detection (regex gate)
      ├── Screen context injection (current page + entity)
      ├── Language/Hinglish flag
      └── Build voice-mode system addendum
      │
      ▼
AIOrchestrator.process_chat()
      │ (identical pipeline to text chat)
      ▼
_strip_markdown_for_tts(reply)
      │ (removes code blocks, bullets, markdown syntax)
      ▼
VoiceChatResponse { reply, requires_confirmation, tool_calls }
      │
      ▼
Browser SpeechSynthesis.speak(reply)
```

## Fallback Heuristic Engine

The `FallbackHeuristicProvider` operates without any external API key. It:

1. Parses the user message for intent keywords (`create`, `add`, `update`, `delete`, `show`, `search`)
2. Identifies entity type from keywords (`task`, `goal`, `habit`, `note`, `meeting`)
3. Extracts arguments from the message (title, date, priority)
4. Returns a structured tool call + a friendly natural language reply

This provides a complete demonstration experience even without OpenAI/Anthropic/Gemini credentials.

## Conversation Persistence

All AI conversations are stored in the database:

```
ai_conversations (id, user_id, title, pinned, created_at)
        │
        └── ai_messages (id, conversation_id, role, content, 
                         tool_calls JSON, created_at)
```

Voice messages are stored with the same schema, with the `content` field containing the transcript/reply.
