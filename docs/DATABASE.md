# Personalix OS — Database Schema

## Overview

- **Development/Test**: SQLite (aiosqlite) — zero config, auto-used
- **Production**: PostgreSQL 16 + pgvector extension
- **ORM**: SQLAlchemy 2.0 with `async_sessionmaker`

## Tables (13 total)

### users
```sql
id          UUID PRIMARY KEY
email       VARCHAR UNIQUE NOT NULL
full_name   VARCHAR
hashed_password VARCHAR NOT NULL
is_active   BOOLEAN DEFAULT TRUE
preferences JSONB         -- { working_hours_start, working_hours_end, productivity_style }
created_at  TIMESTAMPTZ DEFAULT now()
updated_at  TIMESTAMPTZ
```

### user_sessions
```sql
id              UUID PRIMARY KEY
user_id         UUID REFERENCES users(id)
refresh_token   VARCHAR UNIQUE NOT NULL  -- includes UUID jti to prevent collisions
expires_at      TIMESTAMPTZ NOT NULL
created_at      TIMESTAMPTZ DEFAULT now()
```

### tasks
```sql
id          UUID PRIMARY KEY
user_id     UUID REFERENCES users(id)
parent_id   UUID REFERENCES tasks(id)   -- self-referential for subtasks
title       VARCHAR NOT NULL
description TEXT
status      ENUM(inbox, todo, in_progress, completed, archived)
priority    ENUM(low, medium, high, urgent)
due_date    DATE
position    INTEGER DEFAULT 0           -- for kanban ordering
tags        JSONB
created_at  TIMESTAMPTZ
updated_at  TIMESTAMPTZ
```

### projects
```sql
id          UUID PRIMARY KEY
user_id     UUID REFERENCES users(id)
title       VARCHAR NOT NULL
description TEXT
status      ENUM(planning, active, on_hold, completed, archived)
color       VARCHAR DEFAULT '#6366f1'
emoji       VARCHAR DEFAULT '🚀'
target_date DATE
created_at  TIMESTAMPTZ
updated_at  TIMESTAMPTZ
```

### project_milestones
```sql
id          UUID PRIMARY KEY
project_id  UUID REFERENCES projects(id)
title       VARCHAR NOT NULL
is_completed BOOLEAN DEFAULT FALSE
due_date    DATE
created_at  TIMESTAMPTZ
```

### goals
```sql
id          UUID PRIMARY KEY
user_id     UUID REFERENCES users(id)
title       VARCHAR NOT NULL
description TEXT
category    ENUM(career, health, finance, learning, personal, creative, relationships)
status      ENUM(active, achieved, paused, abandoned)
target_date DATE
progress    INTEGER DEFAULT 0     -- 0-100
created_at  TIMESTAMPTZ
updated_at  TIMESTAMPTZ
```

### goal_milestones
```sql
id          UUID PRIMARY KEY
goal_id     UUID REFERENCES goals(id)
title       VARCHAR NOT NULL
is_completed BOOLEAN DEFAULT FALSE
created_at  TIMESTAMPTZ
```

### habits
```sql
id          UUID PRIMARY KEY
user_id     UUID REFERENCES users(id)
name        VARCHAR NOT NULL
description TEXT
frequency   ENUM(daily, weekly)
color       VARCHAR DEFAULT '#6366f1'
icon        VARCHAR DEFAULT '⭐'
is_active   BOOLEAN DEFAULT TRUE
created_at  TIMESTAMPTZ
```

### habit_logs
```sql
id          UUID PRIMARY KEY
habit_id    UUID REFERENCES habits(id)
logged_date DATE NOT NULL
note        TEXT
created_at  TIMESTAMPTZ
UNIQUE(habit_id, logged_date)
```

### notes
```sql
id          UUID PRIMARY KEY
user_id     UUID REFERENCES users(id)
title       VARCHAR NOT NULL
content     TEXT                  -- Markdown
tags        JSONB                 -- string array
is_pinned   BOOLEAN DEFAULT FALSE
word_count  INTEGER DEFAULT 0
created_at  TIMESTAMPTZ
updated_at  TIMESTAMPTZ
```

### documents
```sql
id          UUID PRIMARY KEY
user_id     UUID REFERENCES users(id)
title       VARCHAR NOT NULL
content     TEXT                  -- full text
source_type ENUM(upload, url, manual)
source_url  VARCHAR
file_type   VARCHAR
created_at  TIMESTAMPTZ
```

### document_chunks
```sql
id          UUID PRIMARY KEY
document_id UUID REFERENCES documents(id)
chunk_index INTEGER
content     TEXT
embedding   JSONB                 -- float[1536] stored as JSON array
                                  -- (pgvector column in production)
tokens      INTEGER
created_at  TIMESTAMPTZ
```

### calendar_events
```sql
id          UUID PRIMARY KEY
user_id     UUID REFERENCES users(id)
title       VARCHAR NOT NULL
description TEXT
start_time  TIMESTAMPTZ NOT NULL
end_time    TIMESTAMPTZ
event_type  ENUM(meeting, focus, personal, deadline, reminder)
location    VARCHAR
is_all_day  BOOLEAN DEFAULT FALSE
created_at  TIMESTAMPTZ
updated_at  TIMESTAMPTZ
```

### ai_conversations
```sql
id          UUID PRIMARY KEY
user_id     UUID REFERENCES users(id)
title       VARCHAR NOT NULL
pinned      BOOLEAN DEFAULT FALSE
created_at  TIMESTAMPTZ
updated_at  TIMESTAMPTZ
```

### ai_messages
```sql
id              UUID PRIMARY KEY
conversation_id UUID REFERENCES ai_conversations(id)
role            ENUM(user, assistant, system)
content         TEXT NOT NULL
tool_calls      JSONB         -- [{name, arguments, result, status}]
tokens_used     INTEGER DEFAULT 0
created_at      TIMESTAMPTZ
```

### ai_memories
```sql
id          UUID PRIMARY KEY
user_id     UUID REFERENCES users(id)
category    ENUM(preference, goal, project, fact, behavioral_pattern)
content     TEXT NOT NULL
confidence  FLOAT DEFAULT 0.8   -- 0.0-1.0
source      VARCHAR             -- 'conversation' or 'manual'
created_at  TIMESTAMPTZ
updated_at  TIMESTAMPTZ
```

### activity_logs
```sql
id          UUID PRIMARY KEY
user_id     UUID REFERENCES users(id)
action      VARCHAR NOT NULL     -- e.g. 'task.created', 'habit.logged'
entity_type VARCHAR
entity_id   UUID
metadata    JSONB
created_at  TIMESTAMPTZ
```

## Connection Configuration

```python
# Development (auto-detected, no config needed)
DATABASE_URL = "sqlite+aiosqlite:///./personalix.db"

# Production
DATABASE_URL = "postgresql+asyncpg://user:password@host:5432/personalix"
```

## pgvector Setup (Production)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- In production, document_chunks.embedding uses the vector type:
ALTER TABLE document_chunks 
  ADD COLUMN embedding_vec vector(1536);

-- Create an IVFFlat index for fast ANN search:
CREATE INDEX ON document_chunks 
  USING ivfflat (embedding_vec vector_cosine_ops) 
  WITH (lists = 100);
```
