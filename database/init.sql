-- ===========================================
-- CryptoPulse - Database Initialization
-- ===========================================
-- Este script roda automaticamente quando o container
-- PostgreSQL é criado pela primeira vez

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ===========================================
-- Schema principal
-- ===========================================
-- As tabelas serão criadas pelo Alembic (migrações)
-- Este script apenas prepara o ambiente

-- Criar schema para organização (opcional)
CREATE SCHEMA IF NOT EXISTS cryptopulse;

-- ===========================================
-- Configurações de performance
-- ===========================================

-- Comentário no banco
COMMENT ON DATABASE cryptopulse IS 'CryptoPulse - Crypto Market Early Signal Monitor';

-- ===========================================
-- Usuário read-only para análises (opcional)
-- ===========================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'cryptopulse_readonly') THEN
        CREATE ROLE cryptopulse_readonly WITH LOGIN PASSWORD 'readonly_dev_2024';
    END IF;
END
$$;

-- Permissões básicas serão configuradas após criação das tabelas

-- ===========================================
-- Log de inicialização
-- ===========================================
DO $$
BEGIN
    RAISE NOTICE '✅ CryptoPulse database initialized successfully!';
    RAISE NOTICE '📅 Timestamp: %', NOW();
END
$$;
