# 🗄️ CryptoPulse - Schema do Banco de Dados

## Visão Geral

O CryptoPulse utiliza **PostgreSQL 16** como banco de dados principal. Este documento descreve todas as tabelas, relacionamentos, índices e queries úteis.

---

## Índice

1. [Diagrama ER](#diagrama-er)
2. [Tabelas](#tabelas)
3. [Queries Úteis](#queries-úteis)
4. [Manutenção](#manutenção)
5. [Migrações](#migrações)
6. [Performance](#performance)

---

## Diagrama ER

```
┌─────────────────┐         ┌─────────────────┐
│    assets       │         │   price_data    │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │───┐     │ id (PK)         │
│ symbol          │   │     │ asset_id (FK)   │──┐
│ name            │   │     │ price           │  │
│ is_active       │   │     │ volume_24h      │  │
│ created_at      │   │     │ market_cap      │  │
│ updated_at      │   │     │ price_change_24h│  │
└─────────────────┘   │     │ recorded_at     │  │
                      │     └─────────────────┘  │
                      │                          │
                      │     ┌─────────────────┐  │
                      │     │  asset_scores   │  │
                      │     ├─────────────────┤  │
                      ├────▶│ id (PK)         │  │
                      │     │ asset_id (FK)   │──┤
                      │     │ explosion_score │  │
                      │     │ whale_score     │  │
                      │     │ volume_score    │  │
                      │     │ netflow_score   │  │
                      │     │ oi_score        │  │
                      │     │ narrative_score │  │
                      │     │ status          │  │
                      │     │ reasons         │  │
                      │     │ calculated_at   │  │
                      │     └─────────────────┘  │
                      │                          │
                      │     ┌─────────────────┐  │
                      │     │     alerts      │  │
                      │     ├─────────────────┤  │
                      ├────▶│ id (PK)         │  │
                      │     │ asset_id (FK)   │──┤
                      │     │ alert_type      │  │
                      │     │ title           │  │
                      │     │ message         │  │
                      │     │ severity        │  │
                      │     │ status          │  │
                      │     │ metadata        │  │
                      │     │ created_at      │  │
                      │     │ read_at         │  │
                      │     └─────────────────┘  │
                      │                          │
                      │     ┌───────────────────┐│
                      │     │whale_transactions ││
                      │     ├───────────────────┤│
                      ├────▶│ id (PK)           ││
                      │     │ asset_id (FK)     │┘
                      │     │ tx_hash           │
                      │     │ from_address      │
                      │     │ to_address        │
                      │     │ amount            │
                      │     │ amount_usd        │
                      │     │ tx_type           │
                      │     │ blockchain        │
                      │     │ recorded_at       │
                      │     └───────────────────┘
                      │
                      │     ┌─────────────────┐
                      │     │ exchange_flows  │
                      │     ├─────────────────┤
                      ├────▶│ id (PK)         │
                      │     │ asset_id (FK)   │
                      │     │ exchange        │
                      │     │ inflow          │
                      │     │ outflow         │
                      │     │ netflow         │
                      │     │ recorded_at     │
                      │     └─────────────────┘
                      │
                      │     ┌──────────────────┐
                      │     │narrative_events  │
                      │     ├──────────────────┤
                      ├────▶│ id (PK)          │
                      │     │ asset_id (FK)    │
                      │     │ title            │
                      │     │ source           │
                      │     │ url              │
                      │     │ sentiment        │
                      │     │ importance       │
                      │     │ published_at     │
                      │     │ recorded_at      │
                      │     └──────────────────┘
                      │
                      │     ┌──────────────────┐
                      │     │metric_snapshots  │
                      │     ├──────────────────┤
                      └────▶│ id (PK)          │
                            │ asset_id (FK)    │
                            │ metric_type      │
                            │ value            │
                            │ metadata         │
                            │ recorded_at      │
                            └──────────────────┘
```

---

## Tabelas

### 1. assets

**Descrição:** Criptomoedas monitoradas pelo sistema.

```sql
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_assets_symbol ON assets(symbol);
CREATE INDEX idx_assets_active ON assets(is_active);

-- Trigger para updated_at
CREATE TRIGGER update_assets_updated_at
    BEFORE UPDATE ON assets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

#### Colunas

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| `id` | SERIAL | PRIMARY KEY | Identificador único |
| `symbol` | VARCHAR(20) | NOT NULL, UNIQUE | Símbolo do ativo (BTC, ETH) |
| `name` | VARCHAR(100) | NOT NULL | Nome completo do ativo |
| `is_active` | BOOLEAN | DEFAULT true | Se está sendo monitorado |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Data de criação |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Última atualização |

#### Exemplo de Dados

```sql
INSERT INTO assets (symbol, name) VALUES
    ('BTC', 'Bitcoin'),
    ('ETH', 'Ethereum'),
    ('SOL', 'Solana');
```

---

### 2. asset_scores

**Descrição:** Scores calculados para cada ativo pelo engine de análise.

```sql
CREATE TABLE asset_scores (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    explosion_score DECIMAL(5,2) CHECK (explosion_score >= 0 AND explosion_score <= 100),
    whale_score DECIMAL(5,2) CHECK (whale_score >= 0 AND whale_score <= 100),
    volume_score DECIMAL(5,2) CHECK (volume_score >= 0 AND volume_score <= 100),
    netflow_score DECIMAL(5,2) CHECK (netflow_score >= 0 AND netflow_score <= 100),
    oi_score DECIMAL(5,2) CHECK (oi_score >= 0 AND oi_score <= 100),
    narrative_score DECIMAL(5,2) CHECK (narrative_score >= 0 AND narrative_score <= 100),
    status VARCHAR(20) DEFAULT 'low' CHECK (status IN ('low', 'attention', 'high')),
    reasons JSONB DEFAULT '[]',
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_asset_scores_asset_id ON asset_scores(asset_id);
CREATE INDEX idx_asset_scores_calculated_at ON asset_scores(calculated_at DESC);
CREATE INDEX idx_asset_scores_status ON asset_scores(status);
CREATE INDEX idx_asset_scores_explosion_score ON asset_scores(explosion_score DESC);

-- Índice composto para queries frequentes
CREATE INDEX idx_asset_scores_asset_time ON asset_scores(asset_id, calculated_at DESC);
```

#### Colunas

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| `id` | SERIAL | PRIMARY KEY | Identificador único |
| `asset_id` | INTEGER | FK, NOT NULL | Referência ao ativo |
| `explosion_score` | DECIMAL(5,2) | 0-100 | Score final ponderado |
| `whale_score` | DECIMAL(5,2) | 0-100 | Score de atividade de whales |
| `volume_score` | DECIMAL(5,2) | 0-100 | Score de volume |
| `netflow_score` | DECIMAL(5,2) | 0-100 | Score de fluxo de exchanges |
| `oi_score` | DECIMAL(5,2) | 0-100 | Score de Open Interest |
| `narrative_score` | DECIMAL(5,2) | 0-100 | Score de narrativa/notícias |
| `status` | VARCHAR(20) | low/attention/high | Status do score |
| `reasons` | JSONB | Array | Motivos do score |
| `calculated_at` | TIMESTAMP | DEFAULT NOW() | Momento do cálculo |

#### Status

| Status | Range | Descrição |
|--------|-------|-----------|
| `low` | 0-49 | Score baixo, sem alerta |
| `attention` | 50-69 | Score médio, atenção |
| `high` | 70-100 | Score alto, alerta |

#### Exemplo de Reasons (JSONB)

```json
[
  "Alta atividade de whales nas últimas 24h",
  "Volume 150% acima da média",
  "Open Interest crescente",
  "Sentimento positivo em notícias"
]
```

---

### 3. alerts

**Descrição:** Alertas gerados pelo sistema baseados em thresholds e eventos.

```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id) ON DELETE SET NULL,
    alert_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT,
    severity VARCHAR(20) DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'critical')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'read', 'dismissed')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

-- Índices
CREATE INDEX idx_alerts_asset_id ON alerts(asset_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX idx_alerts_type ON alerts(alert_type);

-- Índice para alertas não lidos
CREATE INDEX idx_alerts_unread ON alerts(status) WHERE status = 'pending';
```

#### Colunas

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| `id` | SERIAL | PRIMARY KEY | Identificador único |
| `asset_id` | INTEGER | FK, NULLABLE | Ativo relacionado (pode ser NULL) |
| `alert_type` | VARCHAR(50) | NOT NULL | Tipo do alerta |
| `title` | VARCHAR(200) | NOT NULL | Título do alerta |
| `message` | TEXT | NULLABLE | Mensagem detalhada |
| `severity` | VARCHAR(20) | DEFAULT 'info' | Severidade do alerta |
| `status` | VARCHAR(20) | DEFAULT 'pending' | Status do alerta |
| `metadata` | JSONB | DEFAULT '{}' | Dados adicionais |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Data de criação |
| `read_at` | TIMESTAMP | NULLABLE | Quando foi lido |

#### Alert Types

| Type | Descrição |
|------|-----------|
| `score_threshold` | Score ultrapassou threshold |
| `whale_alert` | Grande transação detectada |
| `volume_spike` | Pico de volume |
| `price_change` | Mudança brusca de preço |
| `netflow_alert` | Fluxo anormal em exchanges |
| `narrative_event` | Evento importante nas notícias |

#### Severity Levels

| Severity | Cor | Uso |
|----------|-----|-----|
| `info` | 🔵 Blue | Informativo |
| `warning` | 🟡 Yellow | Atenção |
| `critical` | 🔴 Red | Crítico |

---

### 4. price_data

**Descrição:** Dados históricos de preço e métricas de mercado.

```sql
CREATE TABLE price_data (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    price DECIMAL(20,8) NOT NULL,
    volume_24h DECIMAL(30,2),
    market_cap DECIMAL(30,2),
    price_change_24h DECIMAL(10,4),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_price_data_asset_id ON price_data(asset_id);
CREATE INDEX idx_price_data_recorded_at ON price_data(recorded_at DESC);
CREATE INDEX idx_price_data_asset_time ON price_data(asset_id, recorded_at DESC);

-- Particionamento (opcional, para grandes volumes)
-- Particionar por mês para melhor performance
```

#### Colunas

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| `id` | SERIAL | PRIMARY KEY | Identificador único |
| `asset_id` | INTEGER | FK, NOT NULL | Referência ao ativo |
| `price` | DECIMAL(20,8) | NOT NULL | Preço atual em USD |
| `volume_24h` | DECIMAL(30,2) | NULLABLE | Volume em 24h |
| `market_cap` | DECIMAL(30,2) | NULLABLE | Capitalização de mercado |
| `price_change_24h` | DECIMAL(10,4) | NULLABLE | Mudança de preço (%) |
| `recorded_at` | TIMESTAMP | DEFAULT NOW() | Momento da coleta |

---

### 5. whale_transactions

**Descrição:** Transações de grandes holders (whales) detectadas on-chain.

```sql
CREATE TABLE whale_transactions (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    tx_hash VARCHAR(100) UNIQUE NOT NULL,
    from_address VARCHAR(100),
    to_address VARCHAR(100),
    amount DECIMAL(30,8) NOT NULL,
    amount_usd DECIMAL(20,2),
    tx_type VARCHAR(20) CHECK (tx_type IN ('transfer', 'exchange_deposit', 'exchange_withdrawal')),
    blockchain VARCHAR(50),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_whale_tx_asset_id ON whale_transactions(asset_id);
CREATE INDEX idx_whale_tx_recorded_at ON whale_transactions(recorded_at DESC);
CREATE INDEX idx_whale_tx_type ON whale_transactions(tx_type);
CREATE INDEX idx_whale_tx_hash ON whale_transactions(tx_hash);
CREATE INDEX idx_whale_tx_amount ON whale_transactions(amount_usd DESC);
```

#### Colunas

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| `id` | SERIAL | PRIMARY KEY | Identificador único |
| `asset_id` | INTEGER | FK, NOT NULL | Referência ao ativo |
| `tx_hash` | VARCHAR(100) | UNIQUE, NOT NULL | Hash da transação |
| `from_address` | VARCHAR(100) | NULLABLE | Endereço de origem |
| `to_address` | VARCHAR(100) | NULLABLE | Endereço de destino |
| `amount` | DECIMAL(30,8) | NOT NULL | Quantidade transferida |
| `amount_usd` | DECIMAL(20,2) | NULLABLE | Valor em USD |
| `tx_type` | VARCHAR(20) | NULLABLE | Tipo da transação |
| `blockchain` | VARCHAR(50) | NULLABLE | Blockchain (ethereum, bitcoin) |
| `recorded_at` | TIMESTAMP | DEFAULT NOW() | Momento da detecção |

#### Transaction Types

| Type | Descrição |
|------|-----------|
| `transfer` | Transferência normal |
| `exchange_deposit` | Depósito em exchange |
| `exchange_withdrawal` | Saque de exchange |

---

### 6. exchange_flows

**Descrição:** Fluxo de entrada/saída de criptomoedas em exchanges.

```sql
CREATE TABLE exchange_flows (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    exchange VARCHAR(50) NOT NULL,
    inflow DECIMAL(30,8) DEFAULT 0,
    outflow DECIMAL(30,8) DEFAULT 0,
    netflow DECIMAL(30,8) DEFAULT 0,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_exchange_flows_asset_id ON exchange_flows(asset_id);
CREATE INDEX idx_exchange_flows_recorded_at ON exchange_flows(recorded_at DESC);
CREATE INDEX idx_exchange_flows_exchange ON exchange_flows(exchange);
CREATE INDEX idx_exchange_flows_asset_exchange ON exchange_flows(asset_id, exchange, recorded_at DESC);
```

#### Colunas

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| `id` | SERIAL | PRIMARY KEY | Identificador único |
| `asset_id` | INTEGER | FK, NOT NULL | Referência ao ativo |
| `exchange` | VARCHAR(50) | NOT NULL | Nome da exchange |
| `inflow` | DECIMAL(30,8) | DEFAULT 0 | Entrada na exchange |
| `outflow` | DECIMAL(30,8) | DEFAULT 0 | Saída da exchange |
| `netflow` | DECIMAL(30,8) | DEFAULT 0 | Fluxo líquido (inflow - outflow) |
| `recorded_at` | TIMESTAMP | DEFAULT NOW() | Momento da coleta |

#### Interpretação do Netflow

| Netflow | Significado |
|---------|-------------|
| Positivo | Mais entrada que saída (bearish) |
| Negativo | Mais saída que entrada (bullish) |
| Próximo de 0 | Equilíbrio |

---

### 7. narrative_events

**Descrição:** Notícias e eventos relevantes que afetam o sentimento do mercado.

```sql
CREATE TABLE narrative_events (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    source VARCHAR(100),
    url VARCHAR(500),
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'negative', 'neutral')),
    importance INTEGER DEFAULT 1 CHECK (importance >= 1 AND importance <= 5),
    published_at TIMESTAMP WITH TIME ZONE,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_narrative_events_asset_id ON narrative_events(asset_id);
CREATE INDEX idx_narrative_events_published_at ON narrative_events(published_at DESC);
CREATE INDEX idx_narrative_events_sentiment ON narrative_events(sentiment);
CREATE INDEX idx_narrative_events_importance ON narrative_events(importance DESC);
```

#### Colunas

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| `id` | SERIAL | PRIMARY KEY | Identificador único |
| `asset_id` | INTEGER | FK, NULLABLE | Ativo relacionado |
| `title` | VARCHAR(500) | NOT NULL | Título da notícia/evento |
| `source` | VARCHAR(100) | NULLABLE | Fonte (CryptoPanic, NewsAPI) |
| `url` | VARCHAR(500) | NULLABLE | URL da notícia |
| `sentiment` | VARCHAR(20) | NULLABLE | Sentimento da notícia |
| `importance` | INTEGER | DEFAULT 1 | Importância (1-5) |
| `published_at` | TIMESTAMP | NULLABLE | Data de publicação |
| `recorded_at` | TIMESTAMP | DEFAULT NOW() | Data de coleta |

#### Sentiment

| Sentiment | Descrição |
|-----------|-----------|
| `positive` | Notícia positiva/bullish |
| `negative` | Notícia negativa/bearish |
| `neutral` | Notícia neutra |

#### Importance Levels

| Level | Descrição | Exemplo |
|-------|-----------|---------|
| 1 | Baixa | Tweet aleatório |
| 2 | Moderada | Notícia menor |
| 3 | Média | Anúncio de projeto |
| 4 | Alta | Partnership grande |
| 5 | Crítica | Fork, hack, regulação |

---

### 8. metric_snapshots

**Descrição:** Snapshots de métricas diversas coletadas ao longo do tempo.

```sql
CREATE TABLE metric_snapshots (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL,
    value DECIMAL(30,8),
    metadata JSONB DEFAULT '{}',
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_metric_snapshots_asset_id ON metric_snapshots(asset_id);
CREATE INDEX idx_metric_snapshots_type ON metric_snapshots(metric_type);
CREATE INDEX idx_metric_snapshots_recorded_at ON metric_snapshots(recorded_at DESC);
CREATE INDEX idx_metric_snapshots_asset_type ON metric_snapshots(asset_id, metric_type, recorded_at DESC);
```

#### Colunas

| Coluna | Tipo | Restrições | Descrição |
|--------|------|------------|-----------|
| `id` | SERIAL | PRIMARY KEY | Identificador único |
| `asset_id` | INTEGER | FK, NULLABLE | Ativo relacionado |
| `metric_type` | VARCHAR(50) | NOT NULL | Tipo da métrica |
| `value` | DECIMAL(30,8) | NULLABLE | Valor da métrica |
| `metadata` | JSONB | DEFAULT '{}' | Metadados adicionais |
| `recorded_at` | TIMESTAMP | DEFAULT NOW() | Momento da coleta |

#### Metric Types

| metric_type | Descrição |
|-------------|-----------|
| `open_interest` | Open Interest de futuros |
| `funding_rate` | Taxa de funding (perpetual) |
| `active_addresses` | Endereços ativos on-chain |
| `hash_rate` | Hash rate (Bitcoin) |
| `tvl` | Total Value Locked (DeFi) |
| `staking_ratio` | % de tokens em staking |
| `circulating_supply` | Supply circulante |

---

## Queries Úteis

### Score mais recente por ativo

```sql
SELECT DISTINCT ON (asset_id)
    a.symbol,
    a.name,
    s.explosion_score,
    s.status,
    s.whale_score,
    s.volume_score,
    s.netflow_score,
    s.oi_score,
    s.narrative_score,
    s.calculated_at
FROM asset_scores s
JOIN assets a ON s.asset_id = a.id
WHERE a.is_active = true
ORDER BY asset_id, calculated_at DESC;
```

### Alertas não lidos

```sql
SELECT 
    al.id,
    a.symbol,
    a.name,
    al.alert_type,
    al.title,
    al.message,
    al.severity,
    al.created_at
FROM alerts al
LEFT JOIN assets a ON al.asset_id = a.id
WHERE al.status = 'pending'
ORDER BY al.severity DESC, al.created_at DESC
LIMIT 50;
```

### Histórico de score (últimas 24h)

```sql
SELECT 
    date_trunc('hour', calculated_at) as hour,
    AVG(explosion_score) as avg_score,
    MAX(explosion_score) as max_score,
    MIN(explosion_score) as min_score
FROM asset_scores
WHERE asset_id = (SELECT id FROM assets WHERE symbol = 'BTC')
  AND calculated_at > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

### Top whales por período

```sql
SELECT 
    a.symbol,
    date_trunc('day', wt.recorded_at) as day,
    COUNT(*) as num_transactions,
    SUM(wt.amount_usd) as total_usd,
    AVG(wt.amount_usd) as avg_usd
FROM whale_transactions wt
JOIN assets a ON wt.asset_id = a.id
WHERE wt.recorded_at > NOW() - INTERVAL '7 days'
GROUP BY a.symbol, day
ORDER BY day DESC, total_usd DESC;
```

### Netflow por exchange

```sql
SELECT 
    a.symbol,
    ef.exchange,
    SUM(ef.netflow) as total_netflow,
    AVG(ef.netflow) as avg_netflow
FROM exchange_flows ef
JOIN assets a ON ef.asset_id = a.id
WHERE ef.recorded_at > NOW() - INTERVAL '24 hours'
GROUP BY a.symbol, ef.exchange
ORDER BY total_netflow DESC;
```

### Assets com maior variação de score

```sql
WITH recent_scores AS (
    SELECT DISTINCT ON (asset_id)
        asset_id,
        explosion_score as current_score,
        calculated_at
    FROM asset_scores
    WHERE calculated_at > NOW() - INTERVAL '1 hour'
    ORDER BY asset_id, calculated_at DESC
),
old_scores AS (
    SELECT DISTINCT ON (asset_id)
        asset_id,
        explosion_score as old_score
    FROM asset_scores
    WHERE calculated_at BETWEEN NOW() - INTERVAL '25 hours' 
                            AND NOW() - INTERVAL '23 hours'
    ORDER BY asset_id, calculated_at DESC
)
SELECT 
    a.symbol,
    a.name,
    rs.current_score,
    os.old_score,
    (rs.current_score - os.old_score) as score_change
FROM recent_scores rs
JOIN old_scores os ON rs.asset_id = os.asset_id
JOIN assets a ON rs.asset_id = a.id
WHERE a.is_active = true
ORDER BY ABS(rs.current_score - os.old_score) DESC
LIMIT 10;
```

### Eventos narrativos recentes com alto impacto

```sql
SELECT 
    a.symbol,
    ne.title,
    ne.source,
    ne.sentiment,
    ne.importance,
    ne.published_at
FROM narrative_events ne
LEFT JOIN assets a ON ne.asset_id = a.id
WHERE ne.importance >= 4
  AND ne.published_at > NOW() - INTERVAL '7 days'
ORDER BY ne.importance DESC, ne.published_at DESC
LIMIT 20;
```

---

## Manutenção

### Limpeza de Dados Antigos

```sql
-- Remover price_data com mais de 90 dias
DELETE FROM price_data 
WHERE recorded_at < NOW() - INTERVAL '90 days';

-- Remover scores com mais de 30 dias
DELETE FROM asset_scores 
WHERE calculated_at < NOW() - INTERVAL '30 days';

-- Remover alertas lidos com mais de 7 dias
DELETE FROM alerts 
WHERE status IN ('read', 'dismissed')
  AND read_at < NOW() - INTERVAL '7 days';

-- Remover whale transactions com mais de 60 dias
DELETE FROM whale_transactions
WHERE recorded_at < NOW() - INTERVAL '60 days';

-- Remover narrative events com mais de 30 dias
DELETE FROM narrative_events
WHERE recorded_at < NOW() - INTERVAL '30 days';
```

### Vacuum e Analyze

```sql
-- Executar periodicamente para manter performance
VACUUM ANALYZE assets;
VACUUM ANALYZE asset_scores;
VACUUM ANALYZE price_data;
VACUUM ANALYZE whale_transactions;
VACUUM ANALYZE alerts;
VACUUM ANALYZE exchange_flows;
VACUUM ANALYZE narrative_events;
VACUUM ANALYZE metric_snapshots;

-- Ou executar em todas as tabelas
VACUUM ANALYZE;
```

### Reindexação

```sql
-- Se índices ficarem fragmentados
REINDEX TABLE asset_scores;
REINDEX TABLE price_data;
REINDEX TABLE whale_transactions;
```

### Estatísticas da Database

```sql
-- Tamanho das tabelas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Número de registros por tabela
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_tuples
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC;
```

---

## Migrações

As migrações são gerenciadas pelo **Alembic**.

### Comandos Básicos

```bash
# Acessar diretório do backend
cd backend

# Criar nova migração (auto-detecta mudanças nos models)
alembic revision --autogenerate -m "descrição da mudança"

# Criar migração vazia (manual)
alembic revision -m "descrição"

# Aplicar todas as migrações pendentes
alembic upgrade head

# Aplicar migração específica
alembic upgrade <revision_id>

# Reverter última migração
alembic downgrade -1

# Reverter todas as migrações
alembic downgrade base

# Ver histórico de migrações
alembic history

# Ver migração atual
alembic current

# Ver SQL que será executado (sem executar)
alembic upgrade head --sql
```

### Estrutura de Migração

```python
"""adiciona_campo_metadata_em_alerts

Revision ID: abc123def456
Revises: prev_revision_id
Create Date: 2024-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'abc123def456'
down_revision = 'prev_revision_id'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar coluna
    op.add_column('alerts', 
        sa.Column('metadata', postgresql.JSONB, nullable=True, server_default='{}')
    )
    
    # Criar índice
    op.create_index('idx_alerts_metadata', 'alerts', ['metadata'], postgresql_using='gin')


def downgrade():
    # Reverter mudanças
    op.drop_index('idx_alerts_metadata', table_name='alerts')
    op.drop_column('alerts', 'metadata')
```

### Boas Práticas de Migração

**✅ Faça:**
- Sempre revisar o código gerado antes de aplicar
- Testar em ambiente de desenvolvimento primeiro
- Fazer backup antes de aplicar em produção
- Incluir `downgrade()` para reverter se necessário
- Usar nomes descritivos para migrações

**❌ Não Faça:**
- Editar migrações já aplicadas
- Deletar arquivos de migração
- Aplicar diretamente em produção sem testar
- Pular migrações no histórico

---

## Performance

### Índices Recomendados

Todos os índices importantes já estão definidos nas tabelas acima, mas aqui está um resumo:

#### Índices Primários
```sql
-- Colunas de chave estrangeira
CREATE INDEX idx_asset_scores_asset_id ON asset_scores(asset_id);
CREATE INDEX idx_price_data_asset_id ON price_data(asset_id);
CREATE INDEX idx_whale_tx_asset_id ON whale_transactions(asset_id);
CREATE INDEX idx_exchange_flows_asset_id ON exchange_flows(asset_id);
CREATE INDEX idx_alerts_asset_id ON alerts(asset_id);
CREATE INDEX idx_narrative_events_asset_id ON narrative_events(asset_id);
CREATE INDEX idx_metric_snapshots_asset_id ON metric_snapshots(asset_id);
```

#### Índices de Timestamp
```sql
-- Para queries temporais
CREATE INDEX idx_asset_scores_calculated_at ON asset_scores(calculated_at DESC);
CREATE INDEX idx_price_data_recorded_at ON price_data(recorded_at DESC);
CREATE INDEX idx_whale_tx_recorded_at ON whale_transactions(recorded_at DESC);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
```

#### Índices Compostos
```sql
-- Para queries que combinam asset + timestamp
CREATE INDEX idx_asset_scores_asset_time ON asset_scores(asset_id, calculated_at DESC);
CREATE INDEX idx_price_data_asset_time ON price_data(asset_id, recorded_at DESC);
CREATE INDEX idx_whale_tx_asset_time ON whale_transactions(asset_id, recorded_at DESC);
```

#### Índices Parciais
```sql
-- Para consultas frequentes com filtros específicos
CREATE INDEX idx_alerts_unread ON alerts(status) WHERE status = 'pending';
CREATE INDEX idx_assets_active ON assets(is_active) WHERE is_active = true;
```

#### Índices GIN (para JSONB)
```sql
-- Para queries em campos JSONB
CREATE INDEX idx_asset_scores_reasons ON asset_scores USING GIN(reasons);
CREATE INDEX idx_alerts_metadata ON alerts USING GIN(metadata);
CREATE INDEX idx_metric_snapshots_metadata ON metric_snapshots USING GIN(metadata);
```

### Análise de Performance

#### Verificar queries lentas
```sql
-- Habilitar log de queries lentas (postgresql.conf)
-- log_min_duration_statement = 1000  # em ms

-- Ver queries mais lentas
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;
```

#### Explicar plano de execução
```sql
-- Ver plano de execução de uma query
EXPLAIN ANALYZE
SELECT 
    a.symbol,
    s.explosion_score,
    s.calculated_at
FROM asset_scores s
JOIN assets a ON s.asset_id = a.id
WHERE a.is_active = true
  AND s.calculated_at > NOW() - INTERVAL '24 hours'
ORDER BY s.explosion_score DESC
LIMIT 10;
```

#### Estatísticas de índices
```sql
-- Ver uso de índices
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Identificar índices não utilizados
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE '%_pkey'
  AND schemaname = 'public';
```

### Particionamento (Futuro)

Para grandes volumes de dados, considere particionar tabelas por tempo:

```sql
-- Exemplo: Particionar price_data por mês
CREATE TABLE price_data (
    id SERIAL,
    asset_id INTEGER NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    volume_24h DECIMAL(30,2),
    market_cap DECIMAL(30,2),
    price_change_24h DECIMAL(10,4),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) PARTITION BY RANGE (recorded_at);

-- Criar partições mensais
CREATE TABLE price_data_2024_01 PARTITION OF price_data
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE price_data_2024_02 PARTITION OF price_data
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- E assim por diante...
```

### Connection Pooling

Configure connection pooling no SQLAlchemy (backend):

```python
# backend/src/database/connection.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,          # Conexões permanentes
    max_overflow=20,       # Conexões extras sob demanda
    pool_timeout=30,       # Timeout para obter conexão
    pool_recycle=3600,     # Reciclar conexões após 1h
    pool_pre_ping=True     # Verificar conexões antes de usar
)
```

### Otimizações de Queries

#### Use EXPLAIN ANALYZE
```sql
-- Sempre use EXPLAIN para entender o plano de execução
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT ...
```

#### Limite resultados
```sql
-- Sempre use LIMIT em consultas de listagem
SELECT * FROM price_data 
ORDER BY recorded_at DESC 
LIMIT 100;
```

#### Use índices apropriados
```sql
-- Ruim: Sem índice
SELECT * FROM asset_scores WHERE calculated_at > '2024-01-01';

-- Bom: Com índice
-- Já existe: idx_asset_scores_calculated_at
```

#### Evite SELECT *
```sql
-- Ruim
SELECT * FROM asset_scores;

-- Bom: Selecione apenas o necessário
SELECT id, asset_id, explosion_score, calculated_at 
FROM asset_scores;
```

---

## Backup e Restore

### Backup Completo

```bash
# Backup completo
pg_dump -U cryptopulse -h localhost cryptopulse > backup.sql

# Backup comprimido
pg_dump -U cryptopulse -h localhost cryptopulse | gzip > backup.sql.gz

# Backup com formato custom (mais flexível)
pg_dump -U cryptopulse -h localhost -Fc cryptopulse > backup.dump
```

### Backup de Tabelas Específicas

```bash
# Apenas tabela de assets
pg_dump -U cryptopulse -h localhost -t assets cryptopulse > assets_backup.sql

# Múltiplas tabelas
pg_dump -U cryptopulse -h localhost -t assets -t asset_scores cryptopulse > tables_backup.sql
```

### Restore

```bash
# Restore completo (SQL)
psql -U cryptopulse -h localhost cryptopulse < backup.sql

# Restore comprimido
gunzip -c backup.sql.gz | psql -U cryptopulse -h localhost cryptopulse

# Restore custom format
pg_restore -U cryptopulse -h localhost -d cryptopulse backup.dump

# Restore de tabela específica
pg_restore -U cryptopulse -h localhost -d cryptopulse -t assets backup.dump
```

### Backup Incremental (WAL)

```bash
# Configurar WAL archiving (postgresql.conf)
# wal_level = replica
# archive_mode = on
# archive_command = 'cp %p /path/to/archive/%f'

# Backup base
pg_basebackup -U cryptopulse -h localhost -D /backup/base -Fp -Xs -P

# Recovery usa WAL archives automaticamente
```

---

## Funções e Triggers Úteis

### Função para atualizar updated_at

```sql
-- Criar função
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$ language 'plpgsql';

-- Aplicar a assets
CREATE TRIGGER update_assets_updated_at
    BEFORE UPDATE ON assets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Função para limpar dados antigos

```sql
-- Função para deletar dados antigos automaticamente
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $
BEGIN
    DELETE FROM price_data WHERE recorded_at < NOW() - INTERVAL '90 days';
    DELETE FROM asset_scores WHERE calculated_at < NOW() - INTERVAL '30 days';
    DELETE FROM alerts WHERE status IN ('read', 'dismissed') AND read_at < NOW() - INTERVAL '7 days';
    DELETE FROM whale_transactions WHERE recorded_at < NOW() - INTERVAL '60 days';
    DELETE FROM narrative_events WHERE recorded_at < NOW() - INTERVAL '30 days';
    
    RAISE NOTICE 'Old data cleaned up successfully';
END;
$ LANGUAGE plpgsql;

-- Executar manualmente
SELECT cleanup_old_data();
```

### Trigger para auditoria

```sql
-- Tabela de auditoria
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50),
    operation VARCHAR(10),
    old_data JSONB,
    new_data JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT NOW()
);

-- Função de auditoria
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_log (table_name, operation, old_data)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD));
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_log (table_name, operation, old_data, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_log (table_name, operation, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(NEW));
        RETURN NEW;
    END IF;
END;
$ LANGUAGE plpgsql;

-- Aplicar trigger em tabelas importantes
CREATE TRIGGER audit_assets
    AFTER INSERT OR UPDATE OR DELETE ON assets
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
```

---

## Segurança

### Roles e Permissões

```sql
-- Criar roles
CREATE ROLE cryptopulse_readonly;
CREATE ROLE cryptopulse_readwrite;
CREATE ROLE cryptopulse_admin;

-- Permissões readonly
GRANT CONNECT ON DATABASE cryptopulse TO cryptopulse_readonly;
GRANT USAGE ON SCHEMA public TO cryptopulse_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO cryptopulse_readonly;

-- Permissões readwrite
GRANT CONNECT ON DATABASE cryptopulse TO cryptopulse_readwrite;
GRANT USAGE ON SCHEMA public TO cryptopulse_readwrite;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO cryptopulse_readwrite;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO cryptopulse_readwrite;

-- Permissões admin
GRANT ALL PRIVILEGES ON DATABASE cryptopulse TO cryptopulse_admin;

-- Criar usuários
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT cryptopulse_readwrite TO app_user;

CREATE USER report_user WITH PASSWORD 'secure_password';
GRANT cryptopulse_readonly TO report_user;
```

### Row Level Security (RLS)

```sql
-- Habilitar RLS em uma tabela
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

-- Criar política (exemplo: usuários só veem seus próprios alertas)
CREATE POLICY alerts_user_policy ON alerts
    FOR SELECT
    USING (created_by = current_user);
```

---

## Monitoramento

### Queries de Monitoramento

```sql
-- Conexões ativas
SELECT 
    datname,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    state_change
FROM pg_stat_activity
WHERE datname = 'cryptopulse';

-- Locks ativos
SELECT 
    locktype,
    relation::regclass,
    mode,
    granted
FROM pg_locks
WHERE NOT granted;

-- Tamanho total do banco
SELECT 
    pg_size_pretty(pg_database_size('cryptopulse')) as database_size;

-- Cache hit ratio (deve ser > 95%)
SELECT 
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 as cache_hit_ratio
FROM pg_statio_user_tables;
```

---

## Referências

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [PostgreSQL Performance](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

📅 **Última atualização**: Janeiro 2024  
📝 **Versão**: 1.0.0