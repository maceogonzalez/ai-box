---
marp: true
---

# Project Handover Documentation: Bagger Sørensen GenAI Box

> **Instructions for the developer:** This document provides critical context for maintaining and developing the Bagger Sørensen GenAI Box project. Focus on the "why", "where", and "how" of the system architecture and deployment.

## 1. Context: Business Logic

* **Short intro:** This is a **complete GenAI platform** combining multiple LLM providers (OpenAI, Azure, Anthropic, Mistral, local Ollama) with a web interface (Open WebUI), workflow automation (n8n), and user management (LiteLLM proxy). It's a dockerized stack with automatic user synchronization between OpenWebUI and LiteLLM, allowing seamless access to multiple GenAI models through a single unified interface. This is NOT a simple backend-frontend app; it's a **multi-service composition** of specialized tools working together. **Primary Use:** Standalone GenAI platform for Bagger Sørensen. **Optional Integration:** Yap platform can be connected as an external tool/service to OWUI (via shared Docker network), allowing Yap to leverage OWUI's LLM capabilities.

* **Key Stakeholders & Clients:** Bagger Sørensen and team members who need unified access to multiple GenAI models for internal use and potentially customer-facing applications.

* **Core Workflows:**
  1. User signs up/logs in to Open WebUI via Microsoft OAuth
  2. User-Sync service automatically registers user in LiteLLM with budget ($100 default)
  3. User accesses any model through Open WebUI (Claude, GPT-4, local Llama, etc.)
  4. n8n workflows trigger based on user interactions or scheduled events
  5. Admin monitors usage, budgets, and logs through LiteLLM dashboard

* **Business Rules & Quirks:**
  - Users automatically get $100 budget when created in LiteLLM
  - Role-based access: all synced users are `internal_user` by default
  - Microsoft OAuth for authentication (requires Tenant ID, Client ID/Secret)
  - User-Sync uses SQLite database from OpenWebUI volume (not an API call)
  - n8n runs on port 5679, Open WebUI on 3001, Ollama internal on 11434
  - Multiple API keys stored as env variables (.env is NOT tracked in git, security measure)

* **Known Tech Debt:**
  - Nginx + Let's Encrypt SSL setup is commented out (was removed for dev simplicity)
  - Cloudflared tunnel setup is commented out (not currently used)
  - User-Sync is filesystem-dependent (reads OpenWebUI SQLite directly) - fragile if schema changes
  - No comprehensive error handling for failed API calls between services
  - n8n database credentials hardcoded in docker-compose (should use vault/secrets manager)

---

## 2. Context: Developer Workflow

* **Local Setup:**
  ```bash
  # 1. Clone and navigate to project
  git clone <repo-url>
  cd owui
  
  # 2. Create .env file with required variables (see .env template below)
  # Copy all API keys needed (OpenAI, Azure, Anthropic, etc.)
  
  # 3. Start the stack
  docker-compose up -d
  
  # 4. Wait ~30 seconds for containers to initialize, then access:
  # - Open WebUI: http://localhost:3001
  # - n8n: http://localhost:5679
  # - Ollama API: http://localhost:11434
  ```

  **Minimal .env file:**
  ```env
  # Microsoft OAuth
  WEBUI_URL=http://localhost:3001
  WEBUI_SECRET_KEY=your-secret-key-here
  MICROSOFT_CLIENT_ID=xxx
  MICROSOFT_CLIENT_SECRET=xxx
  MICROSOFT_CLIENT_TENANT_ID=xxx
  MICROSOFT_REDIRECT_URI=http://localhost:3001/auth/callback/microsoft
  
  # LLM API Keys
  OPENAI_API_KEY=sk-xxx
  ANTHROPIC_API_KEY=sk-ant-xxx
  AZURE_OPENAI_API_KEY=xxx
  MISTRAL_API_KEY=xxx
  
  # LiteLLM
  LITELLM_MASTER_KEY=your-master-key
  LITELLM_URL=http://litellm:4000
  
  # Database
  POSTGRES_PASSWORD=your-postgres-password
  ```

* **Dev Workflow:**
  1. Start docker-compose (`docker-compose up -d`)
  2. Open http://localhost:3001 in browser → Log in with Microsoft account
  3. Test model access through Open WebUI
  4. If modifying User-Sync service: edit `user-sync/sync_users.py`, then rebuild container:
     ```bash
     docker-compose up -d --build user-sync
     ```
  5. Monitor logs: `docker-compose logs -f open-webui` / `docker-compose logs -f n8n` / etc.
  6. For n8n workflows: Open http://localhost:5679, create/edit workflows in UI

* **Required Tools:**
  - Docker & Docker Compose (5.0+)
  - VS Code or similar editor (Python, YAML syntax highlighting)
  - Postman or curl (for testing LiteLLM API endpoints directly)
  - SQL browser (for debugging OpenWebUI SQLite database at `/var/lib/docker/volumes/open_webui_data/_data/webui.db`)
  - Access to Microsoft Entra ID admin portal (for OAuth configuration)

* **Historical Context:**
  - Originally designed as an internal GenAI stack for Bagger Sørensen
  - Tech stack chosen for: flexibility (multi-provider support), ease of deployment (Docker), user-friendliness (Open WebUI), automation (n8n)
  - User-Sync service was built to solve the "sync problem" - previously users had to be manually created in both systems
  - Removed SSL/Let's Encrypt for local dev simplicity (comment back in when deploying to production)

* **The "weird stuff":**
  - **User-Sync timing:** Syncing happens every 60 seconds (configurable). New users won't appear in LiteLLM instantly—there's a 1-minute lag. This confuses developers initially.
  - **Database volume mounts:** Open WebUI stores data in `open_webui_data` volume. If you delete this volume, all users/chats are lost. Keep backups.
  - **Ollama model downloads:** First run of anything with ollama models takes AGES because it downloads the model (several GB). Don't interrupt.
  - **OAuth requires internet:** Microsoft OAuth won't work on local network without proper redirect URI setup.
  - **LiteLLM sometimes silently fails:** If an API key is wrong or expired, LiteLLM logs show it but Open WebUI won't—check `docker-compose logs litellm`.
  - **n8n port conflict:** Port 5679 is sometimes already in use. If containers won't start, change it in docker-compose.yml: `5680:5679`.

---

## 3. Deployment: Instances

* **Environment Matrix:**

  | Environment | URL | IP/Host | Status |
  |---|---|---|---|
  | Local Dev | http://localhost:3001 | 127.0.0.1 | Active |
  | Staging | [TBD - not currently set up] | [TBD] | N/A |
  | Production | [TBD - not currently set up] | [TBD] | N/A |

* **Hosting Location:**
  - Currently **running locally only** (developer's machine)
  - For production: Recommend AWS EC2, Azure Container Instances, or any Linux VM with Docker support
  - Requires at least **4GB RAM, 2 vCPU** (Ollama can eat memory; plan for 8GB+ if needed)
  - Storage: 20GB+ for model caches (Ollama stores models in volumes)

* **External Dependencies:**
  - **OpenAI API** (for GPT-3.5, GPT-5.2, Whisper, DALL-E, Sora models)
  - **Azure OpenAI** (for GPT-5.1, Mistral models)
  - **Anthropic API** (for Claude models)
  - **Microsoft Entra ID** (for OAuth authentication)
  - **PostgreSQL** (internal to docker-compose, but could be externalized for prod)
  - All of these are **optional**—if you remove API keys, system still works with local Ollama

* **Log Locations:**
  ```bash
  # Access logs from any service
  docker-compose logs -f open-webui
  docker-compose logs -f n8n
  docker-compose logs -f ollama
  docker-compose logs -f user-sync  # WARNING: not currently added to docker-compose
  
  # For persistent logs (production setup), configure log drivers in docker-compose:
  # Each service should write to /var/log/ or use Docker log aggregation (ELK, Datadog, etc.)
  ```

---

## 4. Deployment: Runbook

* **Deployment Process:**
  ```bash
  # 1. SSH into server
  ssh user@server-ip
  
  # 2. Pull latest code
  cd /path/to/owui
  git pull origin main
  
  # 3. Update .env with production secrets (do NOT commit these)
  nano .env  # or your preferred editor
  
  # 4. Rebuild and restart
  docker-compose pull
  docker-compose up -d --build
  
  # 5. Verify all services are running
  docker-compose ps
  docker-compose logs --tail=20 open-webui
  
  # 6. Run health checks
  curl http://localhost:3001  # Should return HTML
  curl http://localhost:5679  # Should return n8n UI
  ```

  **These steps are MANUAL right now.** For production, implement:
  - GitHub Actions CI/CD pipeline to auto-deploy on `main` branch push
  - Automated health checks (every 5 minutes)
  - Slack/email alerts on deployment failure

* **Secrets Configuration:**
  - **Current method:** `.env` file in project root (NOT git-tracked, ignored by .gitignore) ✅ covers local dev
  - **For production:** Move secrets to:
    - AWS Secrets Manager / Parameter Store
    - Azure Key Vault
    - HashiCorp Vault
    - Kubernetes secrets (if using K8s)
  - Each service should read from secure storage on startup
  - **DO NOT store API keys in code, git, or docker images**

* **Rollback Plan:**
  ```bash
  # If deployment fails catastrophically:
  
  # 1. Identify the broken commit
  git log --oneline -5
  
  # 2. Revert to last known good state
  git revert <broken-commit-hash>
  # OR
  git checkout <last-good-commit-hash>
  
  # 3. Rebuild and restart
  docker-compose pull
  docker-compose up -d --build
  
  # 4. Verify services are back online
  docker-compose ps
  docker-compose logs --tail=50 open-webui
  
  # 5. If containers won't start, check:
  # - Disk space: df -h
  # - Memory: free -m
  # - Docker errors: docker-compose logs
  # - Port conflicts: netstat -antp | grep 3001
  ```

* **Common Alarms & Fixes:**

  | Symptom | Likely Cause | Fix |
  |---|---|---|
  | Open WebUI stuck at login page | OAuth not configured or redirect URI wrong | Check MICROSOFT_CLIENT_ID, MICROSOFT_REDIRECT_URI in .env; restart open-webui |
  | "Model not found" error | Missing API key or typo in litellm-config.yaml | Verify API keys in .env; check litellm service logs |
  | n8n won't start | Port 5679 already in use | Change port in docker-compose.yml or kill process: `lsof -i :5679` |
  | User-Sync not syncing users | Database path wrong or permissions issue | Check OPENWEBUI_DB_PATH; verify volume mount; restart user-sync |
  | Ollama taking forever | Downloading model on first run | Don't interrupt; wait 5-10 mins depending on model size |
  | Out of memory | Ollama + other services too much | Reduce num_threads in Ollama or allocate more RAM |

---

## 5. Architecture: System Design

* **Code Repository Links:**
  - Main repo: [This project] `https://github.com/bagger-sorensen/owui` (or your git URL)
  - Open WebUI (upstream): https://github.com/open-webui/open-webui
  - LiteLLM (upstream): https://github.com/BerriAI/litellm
  - n8n (upstream): https://github.com/n8n-io/n8n

* **Core Components:**

  | Component | Tech | Purpose | Port |
  |---|---|---|---|
  | **Open WebUI** | Python + Svelte | Web interface for accessing LLMs | 3001 |
  | **Ollama** | Go + Python | Local LLM inference engine | 11434 (internal) |
  | **LiteLLM** | Python/FastAPI | LLM proxy & cost management | 4000 (internal) |
  | **n8n** | Node.js + TypeScript | Workflow automation | 5679 |
  | **PostgreSQL** | Database | Stores n8n workflows, credentials | 5434 (internal) |
  | **User-Sync** | Python | Syncs users OpenWebUI → LiteLLM | [Background service] |

* **Docker Networking:**
  - **Network Name:** `ollama_network`
  - **Type:** External shared bridge network (`external: true`)
  - **Purpose:** ALL containers in this project connect to the **same Docker network** that is shared with **other projects on the same machine**
  - **Important:** This network must exist before `docker-compose up` is run. Create it with:
    ```bash
    docker network create ollama_network --driver bridge
    ```
  - **Inter-Project Communication:** Because this is an external network, containers from OTHER projects can communicate with containers in this project using the service names (e.g., `http://ollama:11434`, `http://litellm:4000`)
  - **Implications:**
    - ✅ Allows other microservices/projects to call LiteLLM or Ollama without port forwarding
    - ⚠️ Network isolation between projects is relaxed—all projects share the same Docker bridge
    - ⚠️ Port conflicts can occur if multiple projects try to expose the same host port
    - ⚠️ Service discovery works across projects (don't rely on network isolation for security)

* **Connected Projects - Yap:**
  - **Project Name:** Yap (Modular Monorepo Platform)
  - **Connection Type:** Via shared `ollama_network` Docker bridge
  - **Role:** External tool/service that OWUI can optionally integrate
  - **What Yap is:**
    - Frontend: Next.js app (port 3000)
    - Backend: Supabase stack (PostgreSQL, Auth, PostgREST API, Kong Gateway)
    - 9 Reusable packages (@yap-tools/* ) for data management, workspaces, etc.
    - 36 database migrations for progressive schema
  - **How OWUI & Yap Interact:**
    - OWUI can integrate Yap as an external tool/service for managing data, workspaces, and organizational features
    - Yap containers can access OWUI services via shared network for cross-platform integrations
    - Example: OWUI could use Yap's workspace management to organize conversations and knowledge bases
  - **Architecture:**
    - Both stacks are **independent but network-connected** via `ollama_network`
    - OWUI remains the primary GenAI platform
    - Yap provides complementary services that OWUI can optionally leverage
    - No hard dependency between them—either can run standalone
  - **Important Notes:**
    - Requires proper API key exchange between OWUI and Yap services
    - Network latency between services is minimal (same local Docker bridge)
    - If either stack goes down, dependent features fail—plan for graceful degradation

* **API Architecture:**
  - **Protocol/Style:** REST (primary), WebSocket for real-time in Open WebUI
  - **Auth & Security:**
    - OpenWebUI ↔ LiteLLM: Master API key (env var `LITELLM_MASTER_KEY`)
    - Users ↔ OpenWebUI: Microsoft OAuth 2.0 (Entra ID)
    - External APIs: Individual API keys (OpenAI, Azure, Anthropic, etc.)
    - n8n: Basic auth + JWT for API access
  - **API Docs Location:**
    - LiteLLM API: http://localhost:4000/docs (Swagger UI, if running locally)
    - n8n API: http://localhost:5679/api/docs
    - Open WebUI: No formal OpenAPI spec; see https://github.com/open-webui/open-webui/wiki

* **External Integrations:**
  - **Outbound APIs:**
    - OpenAI: Chat, Image, Audio models
    - Microsoft Azure OpenAI: Enterprise GPT models
    - Anthropic: Claude family
    - Mistral: Open-source models via Azure endpoint
    - Microsoft Entra ID: OAuth authentication
  - **All communication:** HTTPS (except local Ollama/LiteLLM which are HTTP internal)

* **High-Level Data Models:**

  ```
  OpenWebUI Database (SQLite / webui.db):
    - users (id, username, email, profile)
    - chats (id, user_id, title, content, timestamp)
    - models (id, name, config)
  
  LiteLLM Database (in-memory or persistent):
    - api_keys (key, team_id, user_id)
    - users (user_id, budget, role, created_at)
    - spend_logs (user_id, model, cost, timestamp)
  
  n8n Database (PostgreSQL):
    - workflows (id, name, definition, active)
    - credentials (id, type, data_encrypted)
    - execution_logs (id, workflow_id, status, timestamp)
  ```

* **Data Flow (Happy Path):**

  ```
  1. User enters prompt in Open WebUI (http://localhost:3001)
  2. Open WebUI sends HTTP POST → LiteLLM (http://litellm:4000/completions)
     - Includes: user_id, model_name, messages, auth_header
  3. LiteLLM validates the request:
     - Checks user budget (from sync with OpenWebUI)
     - Checks if model is in litellm-config.yaml
     - Routes to appropriate provider (OpenAI, Azure, Anthropic, or local Ollama)
  4. Model provider returns response
  5. LiteLLM logs spend, returns response to Open WebUI
  6. Open WebUI displays response to user
  7. Chat is saved to SQLite database
  8. User-Sync service (every 60s): checks for new users in OpenWebUI, creates them in LiteLLM
  ```

* **Cron Jobs / Background Tasks:**

  | Task | Trigger | Frequency | Purpose |
  |---|---|---|---|
  | User Sync | Built-in timer | Every 60 seconds | Sync new OpenWebUI users to LiteLLM |
  | Model Cache Cleanup | Ollama scheduler | Daily | Remove unused model layers |
  | n8n Workflows | User-defined (via UI) | Configurable (hourly, daily, webhook, etc.) | Automation tasks (e.g., send reports, fetch data) |
  | Database Backups | [Need to implement] | Daily | Backup SQLite & PostgreSQL databases |

---

## 🚀 Quick Reference Commands

```bash
# View status
docker-compose ps

# View logs (follow mode)
docker-compose logs -f open-webui

# Rebuild a specific service
docker-compose up -d --build user-sync

# Restart all services
docker-compose restart

# Stop everything
docker-compose down

# Stop and remove volumes (⚠️ deletes all data)
docker-compose down -v

# Access Ollama model list
curl http://localhost:11434/api/tags

# Test LiteLLM with curl
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello"}]}'
```

---

## 📝 Known Issues & Improvements

- [ ] Implement CI/CD pipeline (GitHub Actions)
- [ ] Externalize secrets to cloud vault (AWS/Azure/Vault)
- [ ] Add comprehensive error handling in User-Sync
- [ ] Set up monitoring/alerting (Datadog, New Relic, Prometheus)
- [ ] Add backup/restore automation for databases
- [ ] Implement SSL/TLS for production (comment back in nginx + Let's Encrypt)
- [ ] Set up horizontal scaling for high-volume deployments
- [ ] Add API rate limiting & request logging

---

**Document Updated:** March 3, 2026  
**Maintained By:** Maceo Gonzalez  
**Questions?** Check docker-compose logs first, then refer to upstream project docs for component-specific issues.
