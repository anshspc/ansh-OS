# Personalix OS — API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs`

All endpoints except `/health`, `/auth/login`, `/auth/register`, and `/auth/demo-login` require:
```
Authorization: Bearer <access_token>
```

---

## Authentication

### POST /auth/register
```json
Request:  { "email": "you@example.com", "password": "...", "full_name": "..." }
Response: { "access_token": "...", "refresh_token": "...", "token_type": "bearer" }
```

### POST /auth/login
```json
Request:  { "email": "...", "password": "..." }
Response: { "access_token": "...", "refresh_token": "...", "token_type": "bearer" }
```

### POST /auth/demo-login
```json
Response: { "access_token": "...", "refresh_token": "..." }
# Demo credentials: demo@personalix.os / Demo@personalix2024
```

### GET /auth/me
```json
Response: { "id": "uuid", "email": "...", "full_name": "...", "preferences": {} }
```

---

## Tasks

### GET /tasks?status=todo&priority=high&limit=50
### POST /tasks
```json
{ "title": "...", "status": "todo", "priority": "high", "due_date": "2024-12-31", "tags": [] }
```
### PATCH /tasks/{id}
### DELETE /tasks/{id}

### GET /tasks/{id}/subtasks
### POST /tasks/{id}/subtasks

---

## Projects

### GET /projects
### POST /projects
```json
{ "title": "...", "description": "...", "color": "#6366f1", "emoji": "🚀", "target_date": "..." }
```
### GET /projects/{id}
### PATCH /projects/{id}
### DELETE /projects/{id}

### GET /projects/{id}/milestones
### POST /projects/{id}/milestones
### PATCH /projects/{id}/milestones/{milestone_id}

---

## Goals

### GET /goals?category=career&status=active
### POST /goals
```json
{ "title": "...", "category": "career", "target_date": "...", "progress": 0 }
```
### PATCH /goals/{id}
### GET /goals/{id}/milestones
### POST /goals/{id}/milestones

---

## Habits

### GET /habits
### POST /habits
```json
{ "name": "Morning workout", "frequency": "daily", "color": "#10b981", "icon": "💪" }
```
### POST /habits/{id}/log
```json
{ "logged_date": "2024-01-15", "note": "Felt great" }
```
### GET /habits/{id}/heatmap?days=365
```json
Response: [{ "date": "2024-01-15", "count": 1 }]
```

---

## Notes

### GET /notes?tag=python&pinned=true
### POST /notes
```json
{ "title": "...", "content": "## Markdown content", "tags": ["python", "backend"] }
```
### PATCH /notes/{id}
### DELETE /notes/{id}

---

## Documents (Vector RAG)

### GET /documents
### POST /documents
```json
{ "title": "...", "content": "Full text...", "source_type": "manual" }
```
### POST /documents/upload  (multipart/form-data)
### GET /documents/search?q=fastapi+async&limit=5
```json
Response: [{ "chunk": "...", "document_title": "...", "similarity": 0.87, "document_id": "..." }]
```

---

## Calendar

### GET /calendar?start=2024-01-01&end=2024-01-31
### POST /calendar
```json
{ "title": "Team sync", "start_time": "2024-01-15T10:00:00Z", "end_time": "...", "event_type": "meeting" }
```
### PATCH /calendar/{id}
### DELETE /calendar/{id}

---

## Daily Plans

### GET /daily-plans?date=2024-01-15
### POST /daily-plans/generate
```json
{ "date": "2024-01-15" }  → AI generates time blocks
```
### PATCH /daily-plans/{id}/blocks/{block_id}
```json
{ "is_completed": true }
```

---

## Weekly Reviews

### GET /weekly-reviews
### POST /weekly-reviews/generate
```json
{ "week_start": "2024-01-08" }  → AI generates review
```

---

## AI Assistant

### POST /ai/chat
```json
Request:  { "message": "...", "conversation_id": null, "provider": "fallback" }
Response: { "conversation_id": "...", "reply": "...", "tool_calls": [...], "tokens_used": 42 }
```

### GET /ai/conversations
### GET /ai/conversations/{id}/messages
### DELETE /ai/conversations/{id}
### PATCH /ai/conversations/{id}  (pin/title)

### GET /ai/memories
### POST /ai/memories
```json
{ "category": "preference", "content": "...", "source": "manual" }
```
### DELETE /ai/memories/{id}

---

## Personalix Voice

### POST /voice/chat
```json
Request: {
  "transcript": "What tasks do I have today?",
  "conversation_id": null,
  "screen_context": { "page": "dashboard" },
  "language": "en-US",
  "input_type": "voice"
}
Response: {
  "reply": "You have 5 tasks today. Your highest priority is...",
  "requires_confirmation": false,
  "tool_calls": [...],
  "conversation_id": "..."
}
```

### GET /voice/settings
### PUT /voice/settings
```json
{ "voice_speed": 1.1, "voice_pitch": 1.0, "language": "en-IN", "auto_speak": true }
```
### GET /voice/history?limit=50
### GET /voice/capabilities

---

## Analytics

### GET /analytics/productivity-score
```json
Response: {
  "total_score": 78,
  "components": {
    "task_completion": { "score": 22, "max": 25, "details": "..." },
    "goal_progress":   { "score": 16, "max": 20, "details": "..." },
    "focus_time":      { "score": 15, "max": 20, "details": "..." },
    "habit_consistency":{ "score": 18, "max": 20, "details": "..." },
    "deadline_adherence":{ "score": 7, "max": 15, "details": "..." }
  }
}
```

### GET /analytics/dashboard-summary
### GET /analytics/activity-feed?limit=20

---

## Health

### GET /health
```json
{ "status": "healthy", "database": "connected", "version": "1.0.0" }
```
