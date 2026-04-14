# user-sync

Syncs users from OpenWebUI to LiteLLM automatically.

## How it works

Every `USER_SYNC_INTERVAL` seconds (default: 60), the service reads the OpenWebUI SQLite database and creates any missing users in LiteLLM with the configured budget and role.

## Configuration

Set via environment variables in `.env`:

| Variable | Default | Description |
|---|---|---|
| `USER_SYNC_INTERVAL` | `60` | Sync frequency in seconds |
| `DEFAULT_USER_BUDGET` | `100` | Budget assigned to new users ($) |
| `DEFAULT_USER_ROLE` | `internal_user` | LiteLLM role for new users |
| `OPENWEBUI_API_KEY` | — | OpenWebUI API key |
| `LITELLM_MASTER_KEY` | — | LiteLLM master key |

## Logs

```bash
docker compose logs -f user-sync
```
