# 🏗️ CryptoPulse - Arquitetura

## Visão Geral
┌─────────────────────────────────────────────────────────────┐
│ USUÁRIOS │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ NGINX │
│ (Reverse Proxy / Load Balancer) │
└─────────────────────────────────────────────────────────────┘
│ │
▼ ▼
┌───────────────────┐ ┌───────────────────┐
│ FRONTEND │ │ BACKEND │
│ (Next.js) │ │ (FastAPI) │
└───────────────────┘ └───────────────────┘
│
┌───────────────────┼───────────────────┐
▼ ▼ ▼
┌───────────┐ ┌───────────┐ ┌───────────┐
│ PostgreSQL│ │ Redis │ │APIs Extern│
└───────────┘ └───────────┘ └───────────┘

text

---

## Componentes

### Backend (FastAPI)
backend/src/
├── api/ # REST + WebSocket
│ ├── routes/ # Endpoints
│ ├── schemas/ # Pydantic models
│ └── websocket/ # Real-time
├── collectors/ # Coleta de dados
│ ├── market/ # Binance, CoinGecko
│ ├── onchain/ # Etherscan, Whale Alert
│ └── narrative/ # CryptoPanic, NewsAPI
├── engine/ # Cálculo de scores
│ └── indicators/ # Indicadores individuais
├── alerts/ # Sistema de alertas
├── jobs/ # APScheduler tasks
├── database/ # SQLAlchemy + Alembic
└── config/ # Settings

text

### Frontend (Next.js)
frontend/src/
├── app/ # App Router (páginas)
├── components/ # React components
├── hooks/ # Custom hooks
├── lib/ # API client, utils
├── store/ # Zustand state
└── types/ # TypeScript types

text

---

## Fluxo de Dados

### 1. Coleta (Jobs)
APIs Externas → Collectors → PostgreSQL
│ │
└── Binance └── price_data
└── Etherscan └── whale_transactions
└── CryptoPanic└── narrative_events

text

### 2. Processamento (Engine)
Raw Data → Indicators → Score Calculator → asset_scores
│
├── WhaleIndicator (25%)
├── VolumeIndicator (25%)
├── NetflowIndicator (20%)
├── OIIndicator (15%)
└── NarrativeIndicator (15%)

text

### 3. Distribuição
asset_scores → REST API → Frontend
→ WebSocket → Real-time updates
→ Alerts → Notificações

text

---

## Banco de Dados

### Tabelas Principais

| Tabela | Descrição |
|--------|-----------|
| assets | Criptomoedas monitoradas |
| asset_scores | Scores calculados |
| alerts | Alertas gerados |
| price_data | Histórico de preços |
| whale_transactions | Transações de whales |
| exchange_flows | Fluxo de exchanges |
| narrative_events | Notícias/eventos |

---

## Jobs Agendados

| Job | Intervalo | Função |
|-----|-----------|--------|
| price_collection | 1 min | Coleta preços |
| whale_collection | 5 min | Coleta whales |
| news_collection | 10 min | Coleta notícias |
| score_calculation | 5 min | Calcula scores |
| alert_check | 1 min | Verifica alertas |

---

## Segurança

- CORS configurado por ambiente
- Rate limiting por IP
- Headers de segurança (Nginx)
- Containers não-root
- Rede interna isolada
- SSL/TLS em produção

---

## Escalabilidade

### Atual (MVP)
- Single instance
- ~100 usuários simultâneos
- ~50 ativos

### Futuro
- Múltiplas instâncias + Load Balancer
- Redis para session sharing
- Read replicas do PostgreSQL
- CDN para assets estáticos
