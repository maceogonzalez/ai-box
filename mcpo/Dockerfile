FROM python:3.11-slim

# Install Node.js for Readability.js support
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Install mcpo and uv
RUN pip install mcpo uv --no-cache-dir

EXPOSE 8000

CMD ["uvx", "mcpo", "--host", "0.0.0.0", "--port", "8000", "--", "uvx", "mcp-server-fetch"]