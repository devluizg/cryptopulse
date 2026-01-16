# 📚 CryptoPulse - Documentação Completa

## Índice Geral

1. [Guia de Deploy](#guia-de-deploy)
2. [Documentação da API](#documentação-da-api)
3. [Arquitetura do Sistema](#arquitetura-do-sistema)

---

# 🚀 Guia de Deploy

## Sumário
- [Requisitos do Sistema](#requisitos-do-sistema)
- [Deploy Local](#deploy-local)
- [Deploy com Docker](#deploy-com-docker)
- [Deploy em Produção](#deploy-em-produção)
- [CI/CD](#cicd)
- [Monitoramento](#monitoramento)
- [Backup e Restore](#backup-e-restore)
- [Troubleshooting](#troubleshooting)

---

## Requisitos do Sistema

### Software Necessário
- **Docker** ≥ 24.0
- **Docker Compose** ≥ 2.20
- **Node.js** ≥ 20 (desenvolvimento)
- **Python** ≥ 3.12 (desenvolvimento)
- **Git**

### Recursos Mínimos (Produção)

| Componente | CPU | RAM | Disco |
|------------|-----|-----|-------|
| PostgreSQL | 1 core | 512MB | 10GB |
| Redis | 0.5 core | 256MB | 1GB |
| Backend | 1 core | 1GB | 1GB |
| Frontend | 0.5 core | 512MB | 1GB |
| Nginx | 0.5 core | 128MB | 100MB |
| **Total** | **3.5 cores** | **2.4GB** | **13GB** |

---

## Deploy Local

### 1. Clonar Repositório
```bash
git clone https://github.com/seu-usuario/cryptopulse.git
cd cryptopulse
```

### 2. Configurar Variáveis de Ambiente
```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env.local
```

### 3. Iniciar Infraestrutura
```bash
# Subir PostgreSQL e Redis
make up

# Verificar containers
make ps
```

### 4. Setup do Backend
```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar migrações
alembic upgrade head

# Seed inicial
python scripts/seed_assets.py

# Iniciar API
uvicorn src.main:app --reload --port 8000
```

### 5. Setup do Frontend
```bash
cd frontend

# Instalar dependências
npm install

# Iniciar em modo dev
npm run dev
```

### 6. Acessar Aplicação
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Adminer (DB)**: http://localhost:8082
- **Redis Commander**: http://localhost:8083

---

## Deploy com Docker

### Build das Imagens
```bash
# Backend
docker build -t cryptopulse-backend ./backend

# Frontend
docker build -t cryptopulse-frontend ./frontend \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 \
  --build-arg NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Executar com Docker Compose
```bash
cd infrastructure/docker

# Desenvolvimento
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Produção
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Deploy em Produção

### 1. Preparar Servidor
```bash
# Instalar Docker
curl -fsSL https://get.docker.com | sh

# Criar diretório
sudo mkdir -p /opt/cryptopulse
cd /opt/cryptopulse

# Clonar repositório
git clone https://github.com/seu-usuario/cryptopulse.git .
```

### 2. Configurar Variáveis
```bash
cd infrastructure/docker
cp .env.production.example .env.production

# Editar configurações
nano .env.production
```

**Variáveis importantes:**
```env
POSTGRES_PASSWORD=<senha-forte>
REDIS_PASSWORD=<senha-forte>
SECRET_KEY=<gerar-com-openssl-rand-hex-32>
CORS_ORIGINS=https://seudominio.com
NEXT_PUBLIC_API_URL=https://seudominio.com
NEXT_PUBLIC_WS_URL=wss://seudominio.com
```

### 3. Configurar SSL (Let's Encrypt)
```bash
# Instalar Certbot
apt install certbot

# Gerar certificado
certbot certonly --standalone -d seudominio.com

# Copiar para Nginx
mkdir -p infrastructure/nginx/ssl
cp /etc/letsencrypt/live/seudominio.com/fullchain.pem infrastructure/nginx/ssl/
cp /etc/letsencrypt/live/seudominio.com/privkey.pem infrastructure/nginx/ssl/
```

### 4. Executar Deploy
```bash
./infrastructure/scripts/deploy.sh deploy
```

### 5. Verificar Status
```bash
./infrastructure/scripts/healthcheck.sh
```

---

## CI/CD

### Configurar Secrets no GitHub
Vá em **Settings > Secrets and Variables > Actions** e adicione:

| Secret | Descrição |
|--------|-----------|
| `DEPLOY_HOST` | IP ou hostname do servidor |
| `DEPLOY_USER` | Usuário SSH |
| `DEPLOY_SSH_KEY` | Chave SSH privada |
| `NEXT_PUBLIC_API_URL` | URL da API em produção |
| `NEXT_PUBLIC_WS_URL` | URL do WebSocket |

### Fluxo de Deploy Automático
- **Push para `develop`**: Executa testes (CI)
- **Push para `main`**: Executa testes + build de imagens
- **Tag `v*`**: Executa deploy automático em produção

### Deploy Manual
```bash
# Via GitHub Actions
gh workflow run cd.yml -f environment=production
```

---

## Monitoramento

### Logs
```bash
# Todos os logs
./infrastructure/scripts/deploy.sh logs

# Logs específicos
./infrastructure/scripts/deploy.sh logs backend
./infrastructure/scripts/deploy.sh logs frontend
./infrastructure/scripts/deploy.sh logs nginx
```

### Métricas
```bash
# Status dos containers
docker stats

# Health check
./infrastructure/scripts/healthcheck.sh
```

### Alertas (Planejado)
- Configurar Prometheus + Grafana
- Alertas via Slack/Email

---

## Backup e Restore

### Backup Manual
```bash
./infrastructure/scripts/backup.sh
```

### Backup Automático (Cron)
```bash
# Adicionar ao crontab
0 3 * * * /opt/cryptopulse/infrastructure/scripts/backup.sh >> /var/log/cryptopulse-backup.log 2>&1
```

### Restore
```bash
# PostgreSQL
gunzip -c backups/postgres_YYYYMMDD.sql.gz | \
  docker exec -i cryptopulse_postgres psql -U cryptopulse

# Redis
docker cp backups/redis_YYYYMMDD.rdb cryptopulse_redis:/data/dump.rdb
docker restart cryptopulse_redis
```

---

## Troubleshooting

### Container não inicia
```bash
# Ver logs
docker logs cryptopulse_backend

# Verificar recursos
docker stats
df -h
free -m
```

### Erro de conexão com banco
```bash
# Verificar se PostgreSQL está rodando
docker exec cryptopulse_postgres pg_isready

# Testar conexão
docker exec -it cryptopulse_postgres psql -U cryptopulse -d cryptopulse
```

### Erro de permissão
```bash
# Verificar permissões
ls -la /opt/cryptopulse

# Corrigir se necessário
sudo chown -R $USER:$USER /opt/cryptopulse
```

### WebSocket não conecta
- ✅ Verificar se Nginx está configurado para WebSocket
- ✅ Verificar CORS no backend
- ✅ Verificar URL no frontend

### Limpar tudo e começar do zero
```bash
# ⚠️ CUIDADO: Apaga todos os dados!
docker-compose down -v
docker system prune -af
rm -rf postgres_data redis_data
```

---

# 📡 Documentação da API

## Base URL
- **Desenvolvimento**: `http://localhost:8000`
- **Produção**: `https://api.seudominio.com`

## Autenticação
Atualmente a API é pública. Autenticação JWT será implementada em versões futuras.

---

## Endpoints

### Health Check

#### `GET /health`
Verifica se a API está funcionando.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:00:00Z",
  "version": "0.1.0",
  "database": "connected",
  "redis": "connected"
}
```

---

### Assets (Criptomoedas)

#### `GET /api/v1/assets`
Lista todos os ativos monitorados.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `active` | boolean | `true` | Filtrar por ativos ativos |
| `limit` | int | `50` | Limite de resultados |
| `offset` | int | `0` | Offset para paginação |

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "symbol": "BTC",
      "name": "Bitcoin",
      "is_active": true,
      "created_at": "2024-01-15T12:00:00Z"
    }
  ],
  "total": 20,
  "limit": 50,
  "offset": 0
}
```

#### `GET /api/v1/assets/{symbol}`
Retorna detalhes de um ativo específico.

**Response:**
```json
{
  "id": 1,
  "symbol": "BTC",
  "name": "Bitcoin",
  "is_active": true,
  "current_price": 42000.00,
  "price_change_24h": 2.5,
  "volume_24h": 25000000000,
  "market_cap": 820000000000
}
```

---

### Signals (Sinais/Scores)

#### `GET /api/v1/signals`
Lista sinais de todos os ativos.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `min_score` | int | `0` | Score mínimo (0-100) |
| `status` | string | `all` | Filtrar por status (low, attention, high) |

**Response:**
```json
{
  "items": [
    {
      "asset_symbol": "BTC",
      "explosion_score": 75,
      "status": "high",
      "whale_score": 80,
      "volume_score": 70,
      "netflow_score": 65,
      "oi_score": 85,
      "narrative_score": 60,
      "updated_at": "2024-01-15T12:00:00Z"
    }
  ],
  "total": 20
}
```

#### `GET /api/v1/signals/{symbol}`
Retorna o signal de um ativo específico com histórico.

**Response:**
```json
{
  "asset_symbol": "BTC",
  "current": {
    "explosion_score": 75,
    "status": "high",
    "components": {
      "whale_score": 80,
      "volume_score": 70,
      "netflow_score": 65,
      "oi_score": 85,
      "narrative_score": 60
    }
  },
  "history": [
    {
      "score": 72,
      "timestamp": "2024-01-15T11:00:00Z"
    }
  ],
  "reasons": [
    "Alta atividade de whales nas últimas 24h",
    "Volume 150% acima da média",
    "Open Interest crescente"
  ]
}
```

---

### Alerts (Alertas)

#### `GET /api/v1/alerts`
Lista alertas do sistema.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | string | `all` | pending, sent, read |
| `asset_symbol` | string | - | Filtrar por ativo |
| `limit` | int | `50` | Limite de resultados |

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "asset_symbol": "BTC",
      "alert_type": "score_threshold",
      "message": "BTC atingiu score de 80",
      "severity": "high",
      "status": "pending",
      "created_at": "2024-01-15T12:00:00Z"
    }
  ],
  "total": 5
}
```

#### `POST /api/v1/alerts/{id}/read`
Marca um alerta como lido.

**Response:**
```json
{
  "success": true,
  "alert_id": 1,
  "status": "read"
}
```

---

### Jobs (Administração)

#### `GET /api/v1/jobs`
Lista status dos jobs agendados.

**Response:**
```json
{
  "jobs": [
    {
      "name": "price_collection",
      "status": "running",
      "last_run": "2024-01-15T12:00:00Z",
      "next_run": "2024-01-15T12:01:00Z",
      "interval": "1m"
    }
  ]
}
```

#### `POST /api/v1/jobs/{name}/run`
Executa um job manualmente.

**Response:**
```json
{
  "success": true,
  "job": "price_collection",
  "execution_time": "2.5s"
}
```

---

## WebSocket

### Conexão
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected');
  
  // Subscrever a atualizações
  ws.send(JSON.stringify({
    type: 'subscribe',
    channels: ['scores', 'alerts', 'prices']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### Eventos

#### `score_update`
```json
{
  "type": "score_update",
  "data": {
    "symbol": "BTC",
    "score": 75,
    "status": "high",
    "timestamp": "2024-01-15T12:00:00Z"
  }
}
```

#### `alert`
```json
{
  "type": "alert",
  "data": {
    "id": 1,
    "symbol": "BTC",
    "message": "Score atingiu 80",
    "severity": "high"
  }
}
```

#### `price_update`
```json
{
  "type": "price_update",
  "data": {
    "symbol": "BTC",
    "price": 42000.00,
    "change_24h": 2.5
  }
}
```

---

## Códigos de Erro

| Código | Descrição |
|--------|-----------|
| `400` | Bad Request - Parâmetros inválidos |
| `404` | Not Found - Recurso não encontrado |
| `429` | Too Many Requests - Rate limit excedido |
| `500` | Internal Server Error |

**Formato de Erro:**
```json
{
  "detail": "Mensagem de erro",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

---

## Rate Limiting
- **API**: 10 requests/segundo por IP
- **WebSocket**: 100 mensagens/minuto por conexão

---

## Exemplos de Uso

### cURL
```bash
# Listar assets
curl http://localhost:8000/api/v1/assets

# Obter signal do BTC
curl http://localhost:8000/api/v1/signals/BTC

# Listar alertas pendentes
curl "http://localhost:8000/api/v1/alerts?status=pending"
```

### Python
```python
import httpx

async def get_signals():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/signals",
            params={"min_score": 70}
        )
        return response.json()
```

### JavaScript
```javascript
// Fetch API
const response = await fetch('http://localhost:8000/api/v1/signals');
const data = await response.json();

// Axios
import axios from 'axios';
const { data } = await axios.get('/api/v1/signals', {
  params: { min_score: 70 }
});
```

---

# 🏗️ Arquitetura do Sistema

## Visão Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                          USUÁRIOS                                │
│                    (Browser / Mobile)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                           NGINX                                  │
│              (Reverse Proxy / Load Balancer)                     │
│                     SSL Termination                              │
└─────────────────────────────────────────────────────────────────┘
                    │                      │
                    ▼                      ▼
    ┌───────────────────────┐  ┌──────────────────────────┐
    │      FRONTEND         │  │       BACKEND API        │
    │     (Next.js 14)      │  │       (FastAPI)          │
    │                       │  │                          │
    │ • Dashboard           │  │ • REST API               │
    │ • Detalhes de Assets  │  │ • WebSocket              │
    │ • Sistema de Alertas  │  │ • Jobs Agendados         │
    │ • React Query         │  │ • Engine de Scores       │
    │ • Zustand (State)     │  │ • Collectors (Dados)     │
    └───────────────────────┘  └──────────────────────────┘
                                           │
              ┌────────────────────────────┼────────────────┐
              │                            │                │
              ▼                            ▼                ▼
    ┌─────────────────┐        ┌─────────────────┐  ┌──────────────┐
    │   PostgreSQL    │        │      Redis      │  │ APIs Externas│
    │                 │        │                 │  │              │
    │ • Assets        │        │ • Cache         │  │ • Binance    │
    │ • Scores        │        │ • Sessions      │  │ • CoinGecko  │
    │ • Alerts        │        │ • Rate Limit    │  │ • Etherscan  │
    │ • Métricas      │        │ • Pub/Sub       │  │ • CryptoPanic│
    └─────────────────┘        └─────────────────┘  └──────────────┘
```

---

## Estrutura do Backend

```
backend/
├── src/
│   ├── api/                    # Camada de API
│   │   ├── routes/             # Endpoints REST
│   │   │   ├── assets.py       # /api/v1/assets
│   │   │   ├── signals.py      # /api/v1/signals
│   │   │   ├── alerts.py       # /api/v1/alerts
│   │   │   ├── jobs.py         # /api/v1/jobs
│   │   │   └── health.py       # /health
│   │   ├── schemas/            # Pydantic models (request/response)
│   │   ├── middlewares.py      # Logging, CORS, etc
│   │   └── websocket/          # WebSocket handlers
│   │
│   ├── collectors/             # Coletores de dados externos
│   │   ├── market/             # Dados de mercado
│   │   │   ├── price_collector.py
│   │   │   ├── volume_collector.py
│   │   │   └── providers/      # Binance, CoinGecko, etc
│   │   ├── onchain/            # Dados on-chain
│   │   │   ├── whale_collector.py
│   │   │   ├── exchange_flow.py
│   │   │   └── providers/      # Etherscan, Whale Alert
│   │   └── narrative/          # Notícias e eventos
│   │       ├── news_collector.py
│   │       └── providers/      # CryptoPanic, NewsAPI
│   │
│   ├── engine/                 # Motor de cálculo de scores
│   │   ├── score_calculator.py # Orquestrador principal
│   │   └── indicators/         # Indicadores individuais
│   │       ├── base.py
│   │       ├── whale_indicator.py
│   │       ├── volume_indicator.py
│   │       ├── netflow_indicator.py
│   │       ├── oi_indicator.py
│   │       └── narrative_indicator.py
│   │
│   ├── alerts/                 # Sistema de alertas
│   │   ├── alert_manager.py    # Gerenciador principal
│   │   ├── threshold_monitor.py
│   │   └── channels/           # Push, Email, Webhook
│   │
│   ├── jobs/                   # Jobs agendados (APScheduler)
│   │   ├── scheduler.py        # Configuração do scheduler
│   │   └── tasks/              # Tasks individuais
│   │
│   ├── database/               # Camada de dados
│   │   ├── connection.py       # Conexão SQLAlchemy
│   │   ├── models/             # Modelos ORM
│   │   ├── repositories/       # Padrão Repository
│   │   └── migrations/         # Alembic migrations
│   │
│   ├── config/                 # Configurações
│   │   └── settings.py         # Pydantic Settings
│   │
│   ├── utils/                  # Utilitários
│   │   └── logger.py           # Loguru config
│   │
│   └── main.py                 # Entry point FastAPI
│
├── tests/                      # Testes
│   ├── unit/
│   └── integration/
│
├── alembic.ini
├── requirements.txt
└── Dockerfile
```

---

## Estrutura do Frontend

```
frontend/
├── src/
│   ├── app/                    # App Router (Next.js 14)
│   │   ├── layout.tsx          # Layout principal
│   │   ├── page.tsx            # Home (redirect)
│   │   ├── dashboard/          # Dashboard principal
│   │   │   ├── page.tsx
│   │   │   └── loading.tsx
│   │   ├── asset/[symbol]/     # Detalhe do ativo
│   │   │   └── page.tsx
│   │   ├── alerts/             # Página de alertas
│   │   │   └── page.tsx
│   │   └── settings/           # Configurações
│   │       └── page.tsx
│   │
│   ├── components/             # Componentes React
│   │   ├── ui/                 # Componentes base
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Badge.tsx
│   │   │   └── ...
│   │   ├── dashboard/          # Componentes do dashboard
│   │   │   ├── AssetTable.tsx
│   │   │   ├── ScoreCard.tsx
│   │   │   └── ...
│   │   ├── charts/             # Gráficos
│   │   │   ├── ScoreChart.tsx
│   │   │   ├── PriceChart.tsx
│   │   │   └── ...
│   │   └── alerts/             # Componentes de alertas
│   │
│   ├── hooks/                  # Custom hooks
│   │   ├── useAssets.ts
│   │   ├── useSignals.ts
│   │   ├── useAlerts.ts
│   │   └── useWebSocket.ts
│   │
│   ├── lib/                    # Bibliotecas/utils
│   │   ├── api.ts              # Cliente API (axios)
│   │   ├── websocket.ts        # Cliente WebSocket
│   │   └── utils.ts            # Funções utilitárias
│   │
│   ├── store/                  # Estado global (Zustand)
│   │   ├── useAppStore.ts
│   │   └── ...
│   │
│   ├── types/                  # TypeScript types
│   │   ├── asset.ts
│   │   ├── signal.ts
│   │   └── alert.ts
│   │
│   └── styles/                 # Estilos globais
│       └── globals.css
│
├── public/                     # Assets estáticos
├── tests/                      # Testes
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
├── package.json
└── Dockerfile
```

---

## Fluxo de Dados

### 1. Coleta de Dados
```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Binance   │ │  CoinGecko  │ │  Etherscan  │
│  (prices)   │ │  (market)   │ │  (onchain)  │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
                       ▼
            ┌─────────────────┐
            │   Collectors    │
            │  (APScheduler)  │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │   PostgreSQL    │
            │   (Raw Data)    │
            └─────────────────┘
```

### 2. Cálculo de Score
```
┌─────────────────┐
│    Raw Data     │
│  (PostgreSQL)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              Score Calculator                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │  Whale   │ │  Volume  │ │ Netflow  │    ...    │
│  │Indicator │ │Indicator │ │Indicator │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘           │
│       │            │            │                  │
│       └────────────┼────────────┘                  │
│                    │                               │
│                    ▼                               │
│           Weighted Average                         │
│          Explosion Score                           │
└────────────────────┬───────────────────────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │   Asset Score   │
            │  (PostgreSQL)   │
            └─────────────────┘
```

### 3. Distribuição para Usuários
```
┌─────────────────┐
│   Asset Score   │
│  (PostgreSQL)   │
└────────┬────────┘
         │
    ├────┴──────────────────────────┐
    │                                │
    ▼                                ▼
┌─────────────────┐      ┌─────────────────┐
│    REST API     │      │    WebSocket    │
│  (on-demand)    │      │   (real-time)   │
└────────┬────────┘      └────────┬────────┘
         │                        │
         └────────────┬───────────┘
                      │
                      ▼
            ┌─────────────────┐
            │    Frontend     │
            │    (Next.js)    │
            └─────────────────┘
```

---

## Modelo de Dados

### Tabelas Principais

```sql
-- Criptomoedas monitoradas
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Scores calculados
CREATE TABLE asset_scores (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id),
    explosion_score DECIMAL(5,2),
    whale_score DECIMAL(5,2),
    volume_score DECIMAL(5,2),
    netflow_score DECIMAL(5,2),
    oi_score DECIMAL(5,2),
    narrative_score DECIMAL(5,2),
    calculated_at TIMESTAMP DEFAULT NOW()
);

-- Alertas
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id),
    alert_type VARCHAR(50),
    message TEXT,
    severity VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Dados de preço
CREATE TABLE price_data (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id),
    price DECIMAL(20,8),
    volume_24h DECIMAL(30,2),
    market_cap DECIMAL(30,2),
    price_change_24h DECIMAL(10,4),
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- Transações de whales
CREATE TABLE whale_transactions (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id),
    tx_hash VARCHAR(100),
    from_address VARCHAR(100),
    to_address VARCHAR(100),
    amount DECIMAL(30,8),
    amount_usd DECIMAL(20,2),
    tx_type VARCHAR(20),
    recorded_at TIMESTAMP DEFAULT NOW()
);
```

---

## Segurança

### Medidas Implementadas

#### Backend
- ✅ CORS configurado por ambiente
- ✅ Rate limiting por IP
- ✅ Validação de entrada (Pydantic)
- ✅ Logs estruturados

#### Frontend
- ✅ Headers de segurança (X-Frame-Options, CSP)
- ✅ Sanitização de dados
- ✅ HTTPS obrigatório em produção

#### Infraestrutura
- ✅ Containers não-root
- ✅ Rede interna isolada
- ✅ Secrets em variáveis de ambiente
- ✅ SSL/TLS via Let's Encrypt

---

## Escalabilidade

### Atual (MVP)
- Single instance de cada serviço
- Adequado para ~100 usuários simultâneos
- ~50 ativos monitorados

### Futuro

#### Horizontal Scaling
- Múltiplas instâncias do backend
- Load balancer (Nginx)
- Redis para session sharing

#### Database
- Read replicas
- Particionamento de tabelas históricas
- TimescaleDB para séries temporais

#### Cache
- Cache de scores (Redis)
- Cache de API responses
- CDN para assets estáticos

---

## Tecnologias Utilizadas

### Backend
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.12+ | Linguagem principal |
| FastAPI | 0.104+ | Framework web |
| SQLAlchemy | 2.0+ | ORM |
| Alembic | 1.12+ | Migrations |
| Pydantic | 2.5+ | Validação |
| APScheduler | 3.10+ | Jobs agendados |
| Redis | 7.2+ | Cache/Pub-Sub |
| PostgreSQL | 16+ | Database principal |

### Frontend
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Next.js | 14+ | Framework React |
| React | 18+ | UI Library |
| TypeScript | 5+ | Linguagem |
| Tailwind CSS | 3.4+ | Estilos |
| React Query | 5+ | Data fetching |
| Zustand | 4+ | State management |
| Recharts | 2+ | Gráficos |

### DevOps
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Docker | 24+ | Containerização |
| Docker Compose | 2.20+ | Orquestração local |
| Nginx | 1.25+ | Reverse proxy |
| GitHub Actions | - | CI/CD |

---

## Performance

### Métricas de Performance (Esperadas)

#### API Response Times
- **Health Check**: < 50ms
- **GET /assets**: < 100ms
- **GET /signals**: < 200ms
- **GET /signals/{symbol}**: < 150ms
- **POST requests**: < 300ms

#### WebSocket
- **Latência**: < 100ms
- **Throughput**: 1000 msgs/segundo

#### Database
- **Query simples**: < 10ms
- **Query complexa**: < 100ms
- **Índices**: Otimizados para queries frequentes

### Otimizações Implementadas
- ✅ Índices em colunas frequentemente consultadas
- ✅ Cache Redis para dados que mudam pouco
- ✅ Paginação em todas as listagens
- ✅ Connection pooling no banco
- ✅ Lazy loading no frontend

---

## Manutenção

### Tarefas Diárias
- ✅ Verificar logs de erro
- ✅ Monitorar uso de recursos
- ✅ Verificar health checks

### Tarefas Semanais
- ✅ Revisar alertas não lidos
- ✅ Verificar performance das queries
- ✅ Limpar logs antigos

### Tarefas Mensais
- ✅ Atualizar dependências
- ✅ Revisar uso de disco
- ✅ Testar restore de backup
- ✅ Análise de segurança

---

## Roadmap

### Versão 0.2.0 (Próximos 3 meses)
- [ ] Autenticação JWT
- [ ] Sistema de notificações push
- [ ] Mais exchanges (Coinbase, Kraken)
- [ ] Alertas personalizáveis por usuário
- [ ] Dashboard mobile responsivo

### Versão 0.3.0 (6 meses)
- [ ] Machine Learning para predições
- [ ] API GraphQL
- [ ] Multi-tenancy
- [ ] Tema customizável
- [ ] Exportação de relatórios (PDF/CSV)

### Versão 1.0.0 (12 meses)
- [ ] App móvel nativo (React Native)
- [ ] Trading automatizado
- [ ] Análise técnica avançada
- [ ] Integração com exchanges
- [ ] Sistema de assinatura/pagamento

---

## Suporte

### Documentação
- 📖 [README.md](../README.md)
- 🚀 [DEPLOYMENT.md](./DEPLOYMENT.md)
- 📡 [API.md](./API.md)
- 🏗️ [ARCHITECTURE.md](./ARCHITECTURE.md)

### Contato
- **Issues**: [GitHub Issues](https://github.com/seu-usuario/cryptopulse/issues)
- **Discussions**: [GitHub Discussions](https://github.com/seu-usuario/cryptopulse/discussions)
- **Email**: suporte@cryptopulse.com

### Contribuindo
Veja [CONTRIBUTING.md](../CONTRIBUTING.md) para saber como contribuir com o projeto.

---

## Licença

Este projeto está sob a licença MIT. Veja [LICENSE](../LICENSE) para mais detalhes.

---

## Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web incrível
- [Next.js](https://nextjs.org/) - O melhor framework React
- [Binance API](https://binance-docs.github.io/apidocs/) - Dados de mercado
- [CoinGecko](https://www.coingecko.com/api) - Informações de crypto
- Comunidade open source 🙏

---

**📅 Última atualização**: Janeiro 2026  
**📝 Versão da documentação**: 1.0.0