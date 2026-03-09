# User Sync Service - Ollama Stack Edition

Automatically synchronizes OpenWebUI users to LiteLLM for your specific Ollama + n8n + LiteLLM stack.

## 📦 Package Contents

```
user-sync-for-ollama-stack/
├── 📄 sync_users.py              # Main sync service (Python)
├── 🐳 Dockerfile                 # Docker image builder
├── 📋 requirements.txt           # Python dependencies
├── 🚫 .dockerignore              # Build optimization
├── 📝 docker-compose-snippet.yml # Service config (copy to your docker-compose.yml)
├── 📖 INTEGRATION_GUIDE.md       # Complete integration guide
├── ⚡ QUICKSTART.md              # 3-minute setup
└── 📘 README.md                  # This file
```

## 🎯 What This Does

**Automatic User Sync Workflow:**

```
OpenWebUI User Signs Up
         ↓
User-Sync Service Detects (60s)
         ↓
Creates User in LiteLLM
  ├─ Role: internal_user
  ├─ Budget: $100
  └─ Access: All models
         ↓
User Can Use Claude, GPT-4, Gemini Immediately
```

## ⚡ Quick Start

### Option 1: Read QUICKSTART.md (Recommended)

Complete 3-minute setup guide with copy-paste commands.

### Option 2: Read INTEGRATION_GUIDE.md

Detailed integration guide with troubleshooting and advanced configuration.

### Option 3: Fast Track

```bash
# 1. Copy files
cd /your/project
mkdir -p user-sync
cp user-sync-for-ollama-stack/* user-sync/

# 2. Add service to docker-compose.yml
# (Copy from docker-compose-snippet.yml)

# 3. Deploy
docker-compose build user-sync
docker-compose up -d user-sync
docker-compose logs -f user-sync
```

## ✅ Your Stack Compatibility

Specifically configured for:
- ✅ Container: `owui` (OpenWebUI)
- ✅ Container: `litellm` (LiteLLM)
- ✅ Container: `postgres` (PostgreSQL)
- ✅ Network: `ollama_network`
- ✅ Volume: `open_webui_data`
- ✅ Reads from: SQLite database (no API key needed)

## 🔧 Configuration

All configuration via environment variables in `.env`:

```bash
USER_SYNC_INTERVAL=60        # Sync interval (seconds)
DEFAULT_USER_BUDGET=100      # Budget per user ($)
DEFAULT_USER_ROLE=internal_user  # LiteLLM role
```

Plus your existing:
```bash
LITELLM_MASTER_KEY=sk-xxx    # Already in your .env ✅
```

## 📊 Features

- ✅ **Zero-config:** Works out of the box with defaults
- ✅ **No API key needed:** Reads directly from SQLite
- ✅ **Automatic:** Syncs every 60 seconds
- ✅ **Safe:** Read-only access to OpenWebUI data
- ✅ **Logged:** Detailed sync logs for monitoring
- ✅ **Resilient:** Auto-restarts on failure

## 🎓 How It Works

1. **Reads** OpenWebUI users from `/app/backend/data/webui.db`
2. **Compares** with LiteLLM users via API
3. **Creates** missing users in LiteLLM
4. **Assigns** budget and permissions
5. **Logs** all actions

## 🔍 Monitoring

```bash
# Watch sync in real-time
docker-compose logs -f user-sync

# Check service status
docker-compose ps user-sync

# Verify LiteLLM users
curl -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  http://localhost:4000/user/info | jq
```

## 🐛 Troubleshooting

**Service won't start:**
```bash
docker-compose logs user-sync
```

**Users not syncing:**
```bash
docker-compose exec user-sync ls -la /openwebui-data/
# Should show: webui.db
```

**Full reset:**
```bash
docker-compose down user-sync
docker-compose build --no-cache user-sync
docker-compose up -d user-sync
```

See **INTEGRATION_GUIDE.md** for complete troubleshooting.

## 📚 Documentation

1. **QUICKSTART.md** - 3-minute setup (start here!)
2. **INTEGRATION_GUIDE.md** - Complete guide
3. **docker-compose-snippet.yml** - Service config
4. **This README** - Overview

## 🎯 Next Steps

1. ✅ Read **QUICKSTART.md**
2. ✅ Copy files to your project
3. ✅ Add service to docker-compose.yml
4. ✅ Deploy and test
5. ✅ (Optional) Implement team-based sync

## 🚀 Advanced: Team-Based Sync

Want to sync users into teams instead of individual accounts?

See the separate **TEAM_BASED_SYNC_PIPELINE.md** for complete implementation guide.

## 📝 Notes

- Designed specifically for your Ollama stack
- Uses SQLite database reading (no API authentication needed)
- Compatible with your existing services (n8n, nginx, cloudflared, etc.)
- Minimal resource usage (~50MB RAM)

## 🆘 Support

If you encounter issues:
1. Check **INTEGRATION_GUIDE.md** troubleshooting section
2. Review logs: `docker-compose logs user-sync`
3. Verify configuration in docker-compose.yml

---

**Version:** 1.0  
**Last Updated:** 2026-02-16  
**Stack:** Ollama + OpenWebUI + LiteLLM + n8n + PostgreSQL
