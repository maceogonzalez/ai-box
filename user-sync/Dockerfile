FROM python:3.11-slim

LABEL maintainer="Maceo"
LABEL description="OpenWebUI to LiteLLM User Sync Service"

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY sync_users.py .

# Make script executable
RUN chmod +x sync_users.py

# Run the service
CMD ["python", "-u", "sync_users.py"]
