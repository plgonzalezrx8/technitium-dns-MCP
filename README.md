# technitium-dns-MCP

Docker-first FastMCP server for managing Technitium DNS Server over its HTTP API.

## What it does now

This server now exposes a large MCP surface:

- **116 Technitium API-backed tools** plus `dns_health_check`
- Coverage across dashboard, zones, records, DNSSEC, cache, allow/block lists, apps, DNS client, settings, logs, DHCP, admin sessions/users/groups/permissions, and cluster operations
- Read-only and export/download workflows for operational visibility
- Guarded mutation, destructive, and critical-admin workflows for state-changing actions
- Token-first auth via `TECHNITIUM_TOKEN` or `TECHNITIUM_TOKEN_FILE`
- Read-only deployment mode via `TECHNITIUM_READONLY=true`

Detailed endpoint mapping lives in `docs/api-coverage.md`.

## Safety model

The tool surface is intentionally split by risk:

- **Read-only tools** always register.
- **`TECHNITIUM_READONLY=true`** hides all mutation, destructive, and admin tools.
- **Mutating tools** require explicit `confirm=True`.
- **Destructive tools** also require `confirm=True`, but use stronger delete/reset messaging.
- **Critical admin tools** require `confirm=True` plus an explicit acknowledgement string.
- DNS names, IPs, numeric inputs, and upload inputs are validated before requests go upstream.
- Token values stay out of tool output.

For logs specifically:

- `dns_list_logs`, `dns_download_log`, `dns_query_logs`, and `dns_export_query_logs` are always available.
- `dns_delete_log` and `dns_delete_all_logs` only register when write mode is enabled.

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

## Representative tool families

- **Diagnostics:** `dns_health_check`, `dns_get_settings`, `dns_get_top_stats`
- **Zones and records:** `dns_list_zones`, `dns_get_records`, `dns_create_zone`, `dns_delete_record`
- **DNSSEC:** `dns_get_zone_ds_info`, `dns_sign_zone`, `dns_unsign_zone`
- **Policy data:** `dns_list_allowed_zones`, `dns_export_blocked_zones`, `dns_flush_allowed_zones`
- **Apps and DNS client:** `dns_list_apps`, `dns_get_app_config`, `dns_resolve_query`
- **Settings and logs:** `dns_get_tsig_key_names`, `dns_backup_settings`, `dns_list_logs`, `dns_query_logs`
- **DHCP and admin:** `dns_list_dhcp_leases`, `dns_create_admin_user`, `dns_get_cluster_state`

## Example tool usage

Read-only zone listing:

```json
{"tool":"dns_list_zones","arguments":{}}
```

Log inventory:

```json
{"tool":"dns_list_logs","arguments":{}}
```

Query DNS app logs:

```json
{"tool":"dns_query_logs","arguments":{"app_name":"QueryLogs","class_path":"Technitium.Dns.Server.App.QueryLogs"}}
```

Guarded zone creation:

```json
{"tool":"dns_create_primary_zone","arguments":{"zone":"example.com","confirm":true}}
```

When calling from Python or another MCP client, the explicit mutation opt-in is the point. If you omit it, the server rejects the request. If your client exposes literal keyword syntax, that means using `confirm=True`.

## Local development

```bash
uv sync --group dev
uv run pytest -q
uv run ruff check .
uv run mypy src
```

## CI

GitHub Actions runs the same quality gates plus a container build.
