FROM ghcr.io/open-webui/open-webui:main

# Mettre à jour OpenAI vers une version qui supporte Sora
RUN pip install --upgrade openai>=1.55.0

# Fix middleware.py bug with JSONResponse handling
COPY fix_middleware.py /tmp/fix_middleware.py
RUN python /tmp/fix_middleware.py && rm /tmp/fix_middleware.py

# Fixer l'encodage pour éviter les erreurs ASCII
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV PYTHONIOENCODING=utf-8