-- BYF Mühendislik Veritabanı Kurulum Scripti
-- PostgreSQL 12+ uyumlu

-- Veritabanı oluşturma
CREATE DATABASE byf_muhendislik
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'tr_TR.UTF-8'
    LC_CTYPE = 'tr_TR.UTF-8'
    TEMPLATE = template0;

\c byf_muhendislik;

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Türkçe full-text search configuration
CREATE TEXT SEARCH CONFIGURATION turkish (COPY = simple);
ALTER TEXT SEARCH CONFIGURATION turkish
    ALTER MAPPING FOR hword, hword_part, word
    WITH unaccent, simple;

-- Tabloları oluşturmadan önce yetkileri ayarla
GRANT ALL ON DATABASE byf_muhendislik TO byf_user;