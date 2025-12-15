# OpenWebUI AI Platform with LiteLLM Gateway

A comprehensive Docker-based AI platform integrating OpenWebUI, LiteLLM proxy gateway, Ollama, n8n automation, and support for multiple AI providers including OpenAI Sora-2 video generation.

## Features

- **OpenWebUI**: Modern web interface for AI interactions
- **LiteLLM Proxy**: Unified gateway for 100+ LLM providers with cost tracking
- **Ollama**: Local LLM deployment support
- **Sora-2 Adapter**: Custom adapter for OpenAI Sora-2 video generation
- **n8n**: Workflow automation platform
- **MCP YouTube Transcript**: Extract transcripts from YouTube videos
- **Nginx**: Reverse proxy with security headers
- **Cloudflare Tunnel**: Secure external access
- **PostgreSQL**: Database backend for n8n and LiteLLM

## Supported AI Models

### Text Generation
- OpenAI: GPT-3.5, GPT-4, GPT-5, GPT-5.1 (Azure)
- Anthropic: Claude 4.5 Sonnet
- Google: Gemini 2.5 Pro
- Mistral: Mistral Small (Azure)
- Ollama: Llama 3.2 and any locally hosted models

### Video Generation
- OpenAI Sora-2 (with custom adapter for OpenWebUI integration)

### Image Generation
- DALL-E 2
- DALL-E 3
- GPT Image 1

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  OpenWebUI  │────▶│ Sora Adapter │────▶│  LiteLLM    │
│  (Port 3000)│     │ (Port 8001)  │     │ (Port 4000) │
└─────────────┘     └──────────────┘     └─────────────┘
       │                                         │
       │                                         ▼
       │                                  ┌─────────────┐
       └─────────────────────────────────▶│   AI APIs   │
                                          │ OpenAI, etc │
                                          └─────────────┘
```

## Prerequisites

- Docker and Docker Compose
- API keys for your desired AI providers (OpenAI, Anthropic, Google, etc.)
- At least 4GB RAM available for containers
- Port availability: 80, 443, 3000, 4000, 5432, 5678, 8001

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
LITELLM_MASTER_KEY=sk-your-generated-master-key
LITELLM_SALT_KEY=your-generated-salt-key
POSTGRES_PASSWORD=your-secure-postgres-password
LITELLM_DB_PASSWORD=your-secure-db-password
LITELLM_UI_PASSWORD=your-admin-password

# Optional
GEMINI_API_KEY=your-gemini-key
MISTRAL_API_KEY=your-mistral-key
AZURE_OPENAI_API_KEY=your-azure-key
LITELLM_UI_USERNAME=admin
```

### 3. Build Custom OpenWebUI Image

```bash
docker build -t owui-sora:latest .
```

### 4. Start Services

```bash
docker-compose up -d
```

### 5. Access the Platform

- **OpenWebUI**: http://localhost:3000
- **LiteLLM Dashboard**: http://localhost:4000/ui
- **n8n Automation**: http://localhost:5678

## Using Sora-2 Video Generation

### Setup in OpenWebUI

1. Navigate to **Settings** → **Connections**
2. Add a new OpenAI API connection:
   - **Name**: Sora-2 (LiteLLM)
   - **Base URL**: `http://localhost:8001/v1`
   - **API Key**: Any value (not validated)
3. Select the `sora-2` model

### Generate Videos

Simply send a prompt in OpenWebUI:
```
a dog running in a park at sunset
```

The adapter will return:
- Video ID
- Generation status
- Download instructions
- Cost tracking link

### Download Generated Videos

Once the video is ready:

```bash
python download_video.py video_<ID>
```

Example:
```bash
python download_video.py video_690e148dbfb08190930a1e369ce6fc18
```

### Video Parameters

- **Durations**: 4s, 8s, or 12s
- **Sizes**:
  - `720x1280` (portrait, default)
  - `1280x720` (landscape)

Modify defaults in `litellm-config.yaml`:
```yaml
- model_name: sora-2
  litellm_params:
    model: openai/sora-2
    api_key: os.environ/OPENAI_API_KEY
    seconds: "4"
    size: "720x1280"
```

## Cost Tracking

LiteLLM provides comprehensive cost tracking for all API calls:

1. Open the dashboard: http://localhost:4000/ui
2. View:
   - Per-request costs
   - Usage graphs
   - Model statistics
   - Detailed logs

### Sora-2 Pricing
- Standard: $0.10 per second
  - 4s = $0.40
  - 8s = $0.80
  - 12s = $1.20
- Pro: $0.30 per second (higher quality)

## Service Details

### OpenWebUI
Custom-built image with:
- OpenAI SDK upgraded to support Sora
- UTF-8 encoding fixes
- Middleware bug fixes

### LiteLLM Proxy
Centralized gateway providing:
- Cost tracking and budgets
- Rate limiting
- Load balancing
- Unified API interface
- Database-backed logging

### Sora Adapter
Flask-based proxy that:
- Converts chat completions to video requests
- Maintains LiteLLM tracking
- Returns OpenWebUI-compatible responses

### n8n
Workflow automation with:
- PostgreSQL database backend
- YouTube transcript integration (via MCP)
- Custom node support

## Configuration Files

### `docker-compose.yml`
Main service orchestration file defining all containers and their relationships.

### `litellm-config.yaml`
LiteLLM proxy configuration:
- Model definitions
- API key mappings
- Default parameters
- MCP server connections

### `nginx.conf`
Reverse proxy configuration:
- Security headers
- Exploit blocking
- Routing rules

### `Dockerfile`
Custom OpenWebUI image build instructions.

## Security Features

- Environment-based secrets management
- No hardcoded credentials
- SSL/TLS support via Certbot
- Security headers (X-Frame-Options, CSP, etc.)
- Exploit pattern blocking
- Cloudflare Tunnel for secure external access

## Networking

All services communicate on the `ollama_network` Docker bridge network:
- Internal service discovery
- Isolated from host network
- Controlled port exposure

## Data Persistence

Volumes for persistent data:
- `ollama_data`: Ollama models
- `open_webui_data`: OpenWebUI user data
- `n8n_data`: n8n workflows and credentials
- `postgres_data`: Database storage

## Troubleshooting

### Adapter Won't Start
```bash
# Check if port 8001 is available
netstat -ano | findstr :8001

# Restart the adapter
python sora_litellm_adapter.py
```

### LiteLLM Not Responding
```bash
# Check Docker status
docker ps | grep litellm

# View logs
docker logs litellm

# Restart service
docker restart litellm
```

### Database Connection Issues
```bash
# Check PostgreSQL status
docker logs postgres

# Verify connection
docker exec -it postgres psql -U n8n -d n8n
```

### Video Download Fails
- Ensure `OPENAI_API_KEY` is set in environment
- Check video status is "completed"
- Verify video ID format

## Development

### Running Locally (Without Docker)

1. Install dependencies:
```bash
pip install flask flask-cors requests openai
```

2. Set environment variables:
```bash
export OPENAI_API_KEY=your-key
export LITELLM_MASTER_KEY=your-key
```

3. Start the adapter:
```bash
python sora_litellm_adapter.py
```

### Modifying the Adapter

The Sora adapter (`sora_litellm_adapter.py`) intercepts chat completion requests and converts them to video generation requests. Key functions:
- `/v1/chat/completions`: Main endpoint for OpenWebUI integration
- `/v1/models`: Lists available models
- `/health`: Health check endpoint
- `/<path:path>`: Transparent proxy for other requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project integrates several open-source components, each with their own licenses:
- OpenWebUI: MIT License
- LiteLLM: MIT License
- Ollama: MIT License
- n8n: Sustainable Use License

## Support

For issues and questions:
- OpenWebUI: https://github.com/open-webui/open-webui
- LiteLLM: https://docs.litellm.ai
- n8n: https://docs.n8n.io

## Acknowledgments

Built with:
- [OpenWebUI](https://github.com/open-webui/open-webui)
- [LiteLLM](https://github.com/BerriAI/litellm)
- [Ollama](https://ollama.ai)
- [n8n](https://n8n.io)
- [Nginx](https://nginx.org)
- [PostgreSQL](https://postgresql.org)
