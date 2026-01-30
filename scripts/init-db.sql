-- Initialize extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create full-text search configuration
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'research_english') THEN
        CREATE TEXT SEARCH CONFIGURATION research_english (COPY = english);
    END IF;
END
$$;
