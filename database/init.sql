-- BYF Mühendislik Veritabanı Kurulum Scripti
-- PostgreSQL 12+ uyumlu

-- Veritabanı zaten varsa hata verme
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'byf_muhendislik') THEN
        PERFORM dblink_exec('dbname=' || current_database(), 'CREATE DATABASE byf_muhendislik WITH OWNER = postgres ENCODING = ''UTF8'' TEMPLATE = template0');
    END IF;
END $$;

\c byf_muhendislik;

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Türkçe full-text search configuration
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'turkish') THEN
        CREATE TEXT SEARCH CONFIGURATION turkish (COPY = simple);
        ALTER TEXT SEARCH CONFIGURATION turkish ALTER MAPPING FOR hword, hword_part, word WITH unaccent, simple;
    END IF;
END $$;

-- Yetkileri ayarla
GRANT ALL ON DATABASE byf_muhendislik TO byf_user;
GRANT ALL ON SCHEMA public TO byf_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO byf_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO byf_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO byf_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO byf_user;