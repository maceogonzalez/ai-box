# AI Box — Self-Hosted AI Infrastructure

Internal AI platform built for the [Center for Hybrid Intelligence (CHI)](https://chi.au.dk) at Aarhus University. Powers Tech Circle workshops and internal AI experimentation.

## Stack Overview

```
┌─────────────────────────────────────────────────────────┐
│                      Users / Workshops                  │
└───────────────────────────┬─────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   OpenWebUI    │  Chat interface (port 3001)
                    │  Microsoft SSO │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │    LiteLLM     │  Model gateway (port 4000)
                    │   + Langfuse   │  Observability & cost tracking
                    └───────┬────────┘
                            │
          ┌─────────────────┼──────────────────┐
          │                 │                  │
    ┌─────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
    │   OpenAI   │  │  Anthropic   │  │  Azure/Mistral│
    │  GPT / DALL│  │    Claude    │  │  + Ollama     │
    └────────────┘  └──────────────┘  └──────────────┘

    ┌────────────┐  ┌──────────────┐  ┌──────────────┐
    │    n8n     │  │     mcpo     │  │  user-sync   │
    │ Automation │  │  MCP servers │  │ OWUI↔LiteLLM │
    └────────────┘  └──────────────┘  └──────────────┘
```

## Services

| Service | Description | Port |
|---|---|---|
| `open-webui` | Chat interface with Microsoft SSO | 3001 |
| `litellm` | Unified LLM gateway (100+ providers) | 4000 |
| `langfuse` | LLM observability & cost tracing | 3002 |
| `n8n` | Workflow automation | 5679 |
| `mcpo` | MCP server proxy for OpenWebUI tools | 8000 |
| `user-sync` | Syncs users between OpenWebUI and LiteLLM | — |
| `postgres` | Database backend (n8n + LiteLLM) | 5434 |
| `ollama` | Local LLM hosting | — |

## Supported Models

**Text**
- OpenAI: GPT-3.5, GPT-5.2, GPT-5.1 (Azure)
- Anthropic: Claude Haiku 4.5, Opus 4.5, Sonnet 4.6 (with extended thinking)
- Mistral Small (Azure)
- Ollama: Llama 3.2 and any locally hosted model

**Image generation**
- DALL-E 2, DALL-E 3, GPT Image 1

**Audio**
- Whisper-1 (STT), TTS-1 (TTS)

## Quick Start

### 1. Clone

```bash
git clone https://github.com/maceogonzalez/ai-box.git
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AZURE_OPENAI_API_KEY=...
MISTRAL_API_KEY=...
GEMINI_API_KEY=...

# LiteLLM
LITELLM_MASTER_KEY=sk-...
LITELLM_SALT_KEY=...
LITELLM_DB_PASSWORD=...
LITELLM_UI_PASSWORD=...

# OpenWebUI
WEBUI_URL=http://localhost:3001
WEBUI_SECRET_KEY=...

# Microsoft SSO (Azure AD)
MICROSOFT_CLIENT_ID=...
MICROSOFT_CLIENT_SECRET=...
MICROSOFT_CLIENT_TENANT_ID=...
MICROSOFT_REDIRECT_URI=...
OPENID_PROVIDER_URL=...

# PostgreSQL
POSTGRES_PASSWORD=...

# Langfuse (set after first launch — see Langfuse Setup below)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...

# user-sync
OPENWEBUI_API_KEY=...
DEFAULT_USER_BUDGET=100
DEFAULT_USER_ROLE=internal_user
USER_SYNC_INTERVAL=3600

# LiteLLM UI
LITELLM_UI_USERNAME=admin
```

### 3. Create the external Docker network

```bash
docker network create ollama_network
```

> **Note:** This network is declared as `external` in `docker-compose.yml` because it was originally used to connect this project to a separate Docker project (`yap`) running on the same machine via a shared bridge network.

### 4. Create the Langfuse database

The `litellm` database and user are created automatically via `init-db.sh` on first boot. You only need to create the `langfuse` database manually:

```bash
docker compose up -d postgres
docker exec -it postgres psql -U n8n -c "CREATE DATABASE langfuse;"
```

### 5. Start all services

```bash
docker compose up -d
```

### 6. Langfuse setup

1. Go to `http://localhost:3002`
2. Create an admin account
3. Create a project named `ai-box`
4. Go to **Settings → API Keys** → generate a key pair
5. Add the keys to your `.env` (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`)
6. Restart LiteLLM: `docker compose restart litellm`

## Accessing the Platform

| Interface | URL |
|---|---|
| OpenWebUI | http://localhost:3001 |
| LiteLLM Dashboard | http://localhost:4000/ui |
| Langfuse | http://localhost:3002 |
| n8n | http://localhost:5679 |

## Key Configuration Files

- `docker-compose.yml` — service definitions
- `litellm-config.yaml` — model list, routing, callbacks
- `init-db.sh` — auto-creates the `litellm` database and user on first postgres boot (reads `LITELLM_DB_PASSWORD` from env)
- `mcpo/` — MCP server proxy config
- `user-sync/` — user sync service between OpenWebUI and LiteLLM

## Observability

Langfuse traces every LLM call through LiteLLM. Each trace includes:
- Exact prompt and response
- Token counts (input / output)
- Estimated cost per call
- Latency
- User identity (passed from OpenWebUI via `X-OpenWebUI-User-Email` header)

## Troubleshooting

**LiteLLM loads a stale API key**
Your shell session may have an env var overriding the `.env`. Fix:
```bash
unset OPENAI_API_KEY  # or whichever key
docker compose down
docker compose up -d --force-recreate
```

**Langfuse not receiving traces**
Check that `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST=http://langfuse:3000` are set in the `litellm` service env, and that `success_callback: ["langfuse"]` is in `litellm-config.yaml`.

**Database connection issues**
```bash
docker logs postgres
docker exec -it postgres psql -U n8n -d n8n
```

## Contributing

1. Clone the repo
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes
4. Open a pull request on `main`

Never commit `.env` — it is gitignored.

## Built With

- [OpenWebUI](https://github.com/open-webui/open-webui)
- [LiteLLM](https://github.com/BerriAI/litellm)
- [Langfuse](https://langfuse.com)
- [n8n](https://n8n.io)
- [Ollama](https://ollama.ai)
- [PostgreSQL](https://postgresql.org)
