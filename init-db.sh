#!/bin/bash
set -e

# Create LiteLLM database and user
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE litellm;
    CREATE USER litellm WITH PASSWORD '$LITELLM_DB_PASSWORD';
    GRANT ALL PRIVILEGES ON DATABASE litellm TO litellm;
EOSQL

# Grant schema privileges (PostgreSQL 15+)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "litellm" <<-EOSQL
    GRANT ALL ON SCHEMA public TO litellm;
    ALTER SCHEMA public OWNER TO litellm;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO litellm;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO litellm;
EOSQL
