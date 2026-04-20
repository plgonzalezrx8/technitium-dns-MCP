# technitium-dns-MCP

Docker-first FastMCP server for managing Technitium DNS Server over its HTTP API.

## What it does now

- Health endpoint at `/health`
- MCP endpoint at `/mcp`
- Read-only tools for settings, stats, and zone listing
- Guarded write tool for creating a primary zone
- Token-first auth via `TECHNITIUM_TOKEN` or `TECHNITIUM_TOKEN_FILE`
- Read-only safety mode via `TECHNITIUM_READONLY=true`

## Safety model

- Set `TECHNITIUM_READONLY=true` to hide write tools entirely.
- Mutating tools require explicit `confirm=True`.
- DNS names are validated before requests go upstream.
- Token values stay out of tool output.

## Quick start

1. Copy the sample env file.
2. Add a valid Technitium API token.
3. Start the service.

```bash
cp .env.example .env
$EDITOR .env
docker compose up --build
```

The server listens on `http://localhost:8000`.

## Configuration

```env
TECHNITIUM_URL=http://192.168.1.248:5380
TECHNITIUM_TOKEN=***
TECHNITIUM_READONLY=true
TECHNITIUM_VERIFY_SSL=true
TECHNITIUM_LOG_LEVEL=INFO
MCP_HOST=0.0.0.0
MCP_PORT=8000
```

If Technitium is behind an internal certificate your container does not trust, set:

```env
TECHNITIUM_VERIFY_SSL=false
```

That is less safe than fixing trust properly, but it gets an internal lab deployment unstuck.

If you prefer files over inline secrets:

```env
TECHNITIUM_TOKEN_FILE=/run/secrets/technitium_token
```

## Example tool usage

Read-only zone listing:

```json
{"tool":"dns_list_zones","arguments":{}}
```

Guarded zone creation:

```json
{"tool":"dns_create_primary_zone","arguments":{"zone":"example.com","confirm":true}}
```

When calling this from Python or another MCP client, that explicit mutation opt-in is the point. If you omit it, the server rejects the request. If your client exposes literal keyword syntax, that means using `confirm=True`.

## Local development

```bash
uv sync --group dev
uv run pytest -q
uv run ruff check .
uv run mypy src
```

## CI

GitHub Actions runs the same quality gates plus a container build.
