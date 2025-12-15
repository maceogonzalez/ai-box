FROM ghcr.io/open-webui/open-webui:main

# Upgrade OpenAI to a version that supports Sora
RUN pip install --upgrade openai>=1.55.0

# Fix middleware.py bug with JSONResponse handling
COPY fix_middleware.py /tmp/fix_middleware.py
RUN python /tmp/fix_middleware.py && rm /tmp/fix_middleware.py

# Fix encoding to avoid ASCII errors
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV PYTHONIOENCODING=utf-8