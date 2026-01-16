<div align="center">

# 🚀 CryptoPulse

### Crypto Market Early Signal Monitor

**Veja o que o mercado ainda não precificou.**

[![CI](https://github.com/seu-usuario/cryptopulse/workflows/CI/badge.svg)](https://github.com/seu-usuario/cryptopulse/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)

[Demo](#-demo) • [Instalação](#-instalação) • [Como Funciona](#-como-funciona) • [Documentação](#-documentação) • [Contribuir](#-contribuir)

</div>

---

## 📌 Sobre o Projeto

**CryptoPulse** é uma plataforma de inteligência de mercado cripto que identifica **sinais antecipados de grandes movimentos de preço**, combinando múltiplas camadas de dados:

- 🐋 **Dados On-Chain** — movimentação de whales, inflow/outflow de exchanges  
- 📊 **Dados de Mercado** — volume, open interest, variação de preço  
- 📰 **Narrativa** — notícias, eventos institucionais e regulatórios  

Cada ativo recebe um **Explosion Score (0–100)** que indica **probabilidade de comportamento anormal**, com explicações claras dos fatores envolvidos.

> ⚠️ **Disclaimer**  
> CryptoPulse **não é aconselhamento financeiro**.  
> Não prevê preços, não recomenda compra ou venda e não garante retornos.

---

## ✨ Principais Features

| Feature | Descrição |
|------|-----------|
| 📈 **Dashboard em Tempo Real** | Visualização centralizada dos scores |
| 🔔 **Sistema de Alertas** | Notificações por mudança crítica |
| 📊 **Gráficos Interativos** | Histórico de indicadores e scores |
| 🔌 **WebSocket** | Atualizações em tempo real |
| 📱 **Responsivo** | Desktop e mobile |
| 🎯 **Explicabilidade** | Justificativa clara para cada score |

---

## 🖼️ Screenshots

<div align="center">

### Dashboard Principal
![Dashboard](docs/diagrams/dashboard-preview.png)

### Detalhe do Ativo
![Asset Detail](docs/diagrams/asset-detail-preview.png)

</div>

---

## 🧱 Tech Stack

### Backend
- **Python 3.12**
- **FastAPI** (async)
- **SQLAlchemy 2.0**
- **PostgreSQL 16**
- **Redis 7**
- **APScheduler**
- **Loguru**

### Frontend
- **Next.js 14**
- **TypeScript**
- **Tailwind CSS**
- **React Query**
- **Zustand**
- **Recharts**

### Infraestrutura
- **Docker / Docker Compose**
- **Nginx**
- **GitHub Actions (CI/CD)**

---

## 🚀 Instalação

### Pré-requisitos
- Docker ≥ 24
- Docker Compose ≥ 2.20
- Git

---

### 🔥 Quick Start

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/cryptopulse.git
cd cryptopulse

# 2. Variáveis de ambiente
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 3. Subir infraestrutura
make up

# 4. Migrações
cd backend && alembic upgrade head && cd ..

# 5. Dados iniciais
cd backend && python scripts/seed_assets.py && cd ..

# 6. Backend
make api

# 7. Frontend
cd frontend
npm install
npm run dev

🌐 Acessos Locais
Serviço	URL
Frontend	http://localhost:3000

API Docs	http://localhost:8000/docs

ReDoc	http://localhost:8000/redoc

Adminer	http://localhost:8082

Redis Commander	http://localhost:8083
📁 Estrutura do Projeto
cryptopulse/
├── backend/                 # API FastAPI
│   ├── src/
│   │   ├── api/             # Endpoints + WebSocket
│   │   ├── collectors/      # Coleta de dados externos
│   │   ├── engine/          # Cálculo do Explosion Score
│   │   ├── alerts/          # Sistema de alertas
│   │   ├── jobs/            # Jobs agendados
│   │   ├── database/        # Models e repositórios
│   │   └── config/          # Configurações
│   ├── tests/
│   └── Dockerfile
│
├── frontend/                # Next.js App
│   ├── src/
│   │   ├── app/             # Rotas
│   │   ├── components/      # Componentes UI
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── types/
│   └── Dockerfile
│
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   └── scripts/
│
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   ├── DATABASE_SCHEMA.md
│   └── PRD.md
│
├── .github/
│   └── workflows/
│
├── Makefile
└── README.md

🧠 Como Funciona
Explosion Score

O score é composto por 5 indicadores principais:

Indicador	Peso	Fonte
🐋 Whale Score	25%	Transações on-chain
📊 Volume Score	25%	Volume vs média
💹 Netflow Score	20%	Inflow / Outflow
📈 Open Interest	15%	Mercado futuro
📰 Narrative Score	15%	Notícias
Classificação
Score	Status	Significado
0–39	🔴 Low	Mercado estável
40–69	🟡 Attention	Aumento de atividade
70–100	🟢 High	Alta pressão
📖 Documentação
Documento	Descrição
API.md	Documentação da API
ARCHITECTURE.md	Arquitetura do sistema
DEPLOYMENT.md	Deploy e CI/CD
DATABASE_SCHEMA.md	Modelo de dados
PRD.md	Product Requirements
CONTRIBUTING.md	Guia de contribuição
🧪 Testes
# Backend
cd backend && pytest tests/ -v

# Backend com coverage
pytest --cov=src --cov-report=html

# Frontend
cd frontend && npm run test
npm run test:coverage

🔧 Comandos Úteis
# Infra
make up
make down
make logs
make ps

# Backend
make api
make test
make migrate-up
make seed

# Database
make shell-db
make shell-redis

# Geral
make status
make clean

🚀 Deploy em Produção
Docker Compose
cd infrastructure/docker
cp .env.production.example .env.production
nano .env.production
./infrastructure/scripts/deploy.sh deploy

CI/CD

develop: testes automáticos

main: build + testes

v*: deploy automático

Veja DEPLOYMENT.md para detalhes.

🗺️ Roadmap

✅ MVP — Dashboard, Scores, Alertas

🔜 v0.2 — Ajuste de pesos (ML)

🔜 v0.3 — Sentimento em redes sociais

🔜 v0.4 — App mobile

🎯 v1.0 — SaaS + API pública

🤝 Contribuir

Contribuições são bem-vindas!

Fork o projeto

Crie sua branch (git checkout -b feature/nova-feature)

Commit (git commit -m 'feat: nova feature')

Push (git push origin feature/nova-feature)

Abra um Pull Request

Veja CONTRIBUTING.md.

📄 Licença

Licenciado sob a MIT License.
Veja o arquivo LICENSE.

🙏 Agradecimentos

CoinGecko — dados de mercado

Etherscan — dados on-chain

CryptoPanic — notícias

Feito com ❤️ para a comunidade cripto.

⬆️ Voltar ao topo


---

Se quiser, no próximo passo eu posso:
- 🔹 Ajustar o README para **open-source público**
- 🔹 Criar versão **enxuta para investidores**
- 🔹 Padronizar badges reais (CI, Coverage, Release)
- 🔹 Criar `CONTRIBUTING.md` no mesmo nível de qualidade

Só mandar 👍# cryptopulse
