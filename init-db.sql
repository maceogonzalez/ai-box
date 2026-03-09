-- Create LiteLLM database and user
CREATE DATABASE litellm;
CREATE USER litellm WITH PASSWORD 'TttE2J5NstedgCL0ebtV14Mf82C4kTWwwarZE8p1j3TXubN9YPwpDPbqaguZA1Mw';

-- Grant database privileges
GRANT ALL PRIVILEGES ON DATABASE litellm TO litellm;

-- Connect to litellm database
\c litellm

-- Grant schema privileges (PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO litellm;
ALTER SCHEMA public OWNER TO litellm;

-- Grant future privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO litellm;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO litellm;

