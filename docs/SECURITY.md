# Personalix OS — Security

## Authentication

- **Algorithm**: JWT with configurable secret (`JWT_SECRET` env var)
- **Access tokens**: 30-minute expiry
- **Refresh tokens**: 7-day expiry
- **Token uniqueness**: Every token includes a `jti` (JWT ID) claim as UUID4, ensuring refresh tokens are always unique even if generated within the same second
- **Session storage**: Refresh tokens stored in `user_sessions` table with UNIQUE constraint

## Password Security

- **Algorithm**: PBKDF2-SHA256 with 260,000 iterations + random salt
- **No bcrypt dependency**: Uses Python's built-in `hashlib.pbkdf2_hmac`
- **Verification**: Timing-safe comparison via `hmac.compare_digest`

## API Security

- **All authenticated endpoints** require `Authorization: Bearer <token>` header
- **CORS**: Configured via `CORS_ORIGINS` environment variable
- **Rate limiting**: Redis-backed (pluggable, configurable per-route)
- **Request IDs**: Every request gets a UUID `X-Request-ID` header for audit logging

## Secrets Management

- All secrets are environment variables — never hardcoded
- `.env` files are `.gitignore`d
- `.env.example` contains only placeholder values (no real keys)
- Docker secrets via environment injection in `docker-compose.yml`

## Voice Privacy

- Microphone is **only** activated during the `LISTENING` voice state
- A visible pulsing indicator is shown whenever the mic is active
- `save_transcripts` setting: users can disable persistence of voice text
- No continuous background listening in v1
- No audio data is ever sent to the server — only the text transcript

## Data Isolation

- Every database query includes `WHERE user_id = :current_user_id`
- No cross-user data access is possible through the API
- SQLAlchemy ORM prevents raw SQL injection by default

## Production Checklist

- [ ] Set a strong `JWT_SECRET` (32+ random chars)
- [ ] Set `DEBUG=false`
- [ ] Set `CORS_ORIGINS` to your actual domain
- [ ] Use PostgreSQL (not SQLite) in production
- [ ] Enable HTTPS via nginx/Caddy/Traefik
- [ ] Rotate JWT secrets periodically
- [ ] Enable database connection SSL
- [ ] Set `REDIS_URL` with authentication if exposed

## Reporting Security Issues

Please report security vulnerabilities privately. Do not open public GitHub issues for security concerns.
