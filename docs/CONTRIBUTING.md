# 🤝 CryptoPulse - Guia de Contribuição

Obrigado por considerar contribuir com o CryptoPulse! Este documento fornece diretrizes para contribuir com o projeto.

---

## Índice

1. [Código de Conduta](#código-de-conduta)
2. [Como Contribuir](#como-contribuir)
3. [Configuração do Ambiente](#configuração-do-ambiente)
4. [Padrões de Código](#padrões-de-código)
5. [Commits e Pull Requests](#commits-e-pull-requests)
6. [Reportando Bugs](#reportando-bugs)
7. [Sugerindo Melhorias](#sugerindo-melhorias)

---

## Código de Conduta

Este projeto adota um Código de Conduta que esperamos que todos os participantes sigam. Por favor, leia o documento completo para entender quais ações serão ou não toleradas.

### Nossos Compromissos

- ✅ Seja respeitoso e inclusivo
- ✅ Aceite críticas construtivas
- ✅ Foque no que é melhor para a comunidade
- ✅ Mostre empatia com outros membros
- ❌ Não tolere assédio ou discriminação
- ❌ Não compartilhe informações privadas de outros

---

## Como Contribuir

### Tipos de Contribuição

| Tipo | Descrição | Label |
|------|-----------|-------|
| 🐛 **Bug Fixes** | Correções de bugs | `bug` |
| ✨ **Features** | Novas funcionalidades | `enhancement` |
| 📝 **Documentação** | Melhorias na documentação | `documentation` |
| 🧪 **Testes** | Adição de testes | `tests` |
| 🎨 **UI/UX** | Melhorias de interface | `ui/ux` |
| ⚡ **Performance** | Otimizações | `performance` |
| 🔒 **Segurança** | Melhorias de segurança | `security` |

### Processo de Contribuição

#### 1. Fork o Repositório
```bash
# Via GitHub UI ou
gh repo fork seu-usuario/cryptopulse
```

#### 2. Clone Seu Fork
```bash
git clone https://github.com/SEU-USUARIO/cryptopulse.git
cd cryptopulse
```

#### 3. Configure o Upstream
```bash
git remote add upstream https://github.com/seu-usuario/cryptopulse.git
```

#### 4. Crie uma Branch
```bash
# Para features
git checkout -b feature/nome-da-feature

# Para bug fixes
git checkout -b fix/nome-do-bug

# Para documentação
git checkout -b docs/nome-da-doc
```

#### 5. Faça Suas Alterações
- Escreva código limpo e bem documentado
- Siga os padrões de código do projeto
- Adicione/atualize testes conforme necessário

#### 6. Teste Suas Mudanças
```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm run test
npm run lint
```

#### 7. Commit Suas Mudanças
```bash
git add .
git commit -m "feat: adiciona nova funcionalidade X"
```

#### 8. Push para Seu Fork
```bash
git push origin feature/nome-da-feature
```

#### 9. Abra um Pull Request
- Vá para o GitHub
- Clique em "Compare & pull request"
- Preencha o template de PR
- Aguarde review

---

## Configuração do Ambiente

### Pré-requisitos

| Software | Versão Mínima | Verificar |
|----------|---------------|-----------|
| Python | 3.12+ | `python --version` |
| Node.js | 20+ | `node --version` |
| Docker | 24+ | `docker --version` |
| Docker Compose | 2.20+ | `docker-compose --version` |
| Git | 2.40+ | `git --version` |

### Setup Completo

#### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/cryptopulse.git
cd cryptopulse
```

#### 2. Configurar Backend
```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configurar variáveis de ambiente
cp .env.example .env

# Executar migrações
alembic upgrade head

# Seed inicial
python scripts/seed_assets.py
```

#### 3. Configurar Frontend
```bash
cd ../frontend

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local
```

#### 4. Iniciar Infraestrutura
```bash
cd ..

# Subir PostgreSQL e Redis
make up

# Verificar status
make ps
```

### Executando o Projeto

#### Backend
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm run dev
```

### Executando Testes

#### Backend
```bash
cd backend

# Todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/unit/ -v
pytest tests/integration/ -v

# Com coverage
pytest tests/ --cov=src --cov-report=html
```

#### Frontend
```bash
cd frontend

# Testes unitários
npm run test

# Testes com watch mode
npm run test:watch

# Coverage
npm run test:coverage

# E2E (se configurado)
npm run test:e2e
```

#### Linting
```bash
# Backend
cd backend
ruff check src/
black src/ --check

# Frontend
cd frontend
npm run lint
npm run type-check
```

---

## Padrões de Código

### Python (Backend)

#### Style Guide
- **PEP 8**: Padrão oficial do Python
- **Linter**: Ruff
- **Formatter**: Black (opcional)
- **Type Hints**: Obrigatório para funções públicas

#### Boas Práticas

**✅ Bom:**
```python
from typing import Optional

async def get_asset_by_symbol(symbol: str) -> Optional[Asset]:
    """
    Busca um ativo pelo símbolo.
    
    Args:
        symbol: Símbolo do ativo (ex: BTC, ETH)
        
    Returns:
        Asset se encontrado, None caso contrário
        
    Raises:
        ValueError: Se o símbolo for inválido
    """
    if not symbol or len(symbol) > 10:
        raise ValueError("Símbolo inválido")
    
    return await AssetRepository.find_by_symbol(symbol.upper())
```

**❌ Ruim:**
```python
async def get_asset(s):
    return await db.query(Asset).filter(Asset.symbol == s).first()
```

#### Estrutura de Módulos
```python
# Imports padrão
import os
from datetime import datetime

# Imports de terceiros
from fastapi import APIRouter, Depends
from sqlalchemy import select

# Imports locais
from src.database.models import Asset
from src.api.schemas import AssetResponse
```

#### Convenções de Nomenclatura
| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Variáveis | `snake_case` | `asset_symbol` |
| Funções | `snake_case` | `calculate_score()` |
| Classes | `PascalCase` | `AssetRepository` |
| Constantes | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Privado | `_prefixo` | `_internal_method()` |

---

### TypeScript (Frontend)

#### Style Guide
- **ESLint**: Linter configurado
- **Prettier**: Formatação automática
- **Types**: Sempre usar tipos explícitos

#### Boas Práticas

**✅ Bom:**
```typescript
// Interfaces bem definidas
interface Asset {
  id: number;
  symbol: string;
  name: string;
  isActive: boolean;
}

interface AssetCardProps {
  asset: Asset;
  onSelect?: (asset: Asset) => void;
}

// Componente funcional com tipos
const AssetCard: React.FC<AssetCardProps> = ({ asset, onSelect }) => {
  const handleClick = () => {
    onSelect?.(asset);
  };

  return (
    <div onClick={handleClick} className="asset-card">
      <h3>{asset.name}</h3>
      <span>{asset.symbol}</span>
    </div>
  );
};

// Hook customizado com tipos
function useAssets() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  
  // ...
  
  return { assets, loading };
}
```

**❌ Ruim:**
```typescript
const AssetCard = ({ asset, onSelect }: any) => {
  return <div>{asset.name}</div>;
};

function useAssets() {
  const [assets, setAssets] = useState([]);
  return { assets };
}
```

#### Convenções de Nomenclatura
| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Variáveis | `camelCase` | `assetSymbol` |
| Funções | `camelCase` | `calculateScore()` |
| Componentes | `PascalCase` | `AssetCard` |
| Interfaces | `PascalCase` | `AssetProps` |
| Types | `PascalCase` | `ScoreStatus` |
| Hooks | `use + PascalCase` | `useAssets()` |
| Constantes | `UPPER_SNAKE_CASE` | `API_BASE_URL` |

#### Estrutura de Componentes
```typescript
// 1. Imports
import React, { useState, useEffect } from 'react';
import { Asset } from '@/types/asset';
import { Button } from '@/components/ui/Button';

// 2. Tipos/Interfaces
interface AssetListProps {
  assets: Asset[];
  onSelectAsset: (asset: Asset) => void;
}

// 3. Componente
export const AssetList: React.FC<AssetListProps> = ({ 
  assets, 
  onSelectAsset 
}) => {
  // 3a. Hooks
  const [selectedId, setSelectedId] = useState<number | null>(null);
  
  // 3b. Handlers
  const handleSelect = (asset: Asset) => {
    setSelectedId(asset.id);
    onSelectAsset(asset);
  };
  
  // 3c. Effects
  useEffect(() => {
    // ...
  }, [assets]);
  
  // 3d. Render
  return (
    <div className="asset-list">
      {assets.map(asset => (
        <AssetCard 
          key={asset.id}
          asset={asset}
          selected={asset.id === selectedId}
          onSelect={handleSelect}
        />
      ))}
    </div>
  );
};
```

---

### Estrutura de Arquivos

#### Princípios
1. **Um componente por arquivo**
2. **Nomes descritivos e claros**
3. **Agrupar por feature, não por tipo**
4. **Manter arquivos pequenos (< 300 linhas)**

#### Exemplo de Organização
```
src/
├── features/
│   ├── assets/
│   │   ├── components/
│   │   │   ├── AssetCard.tsx
│   │   │   ├── AssetList.tsx
│   │   │   └── AssetDetail.tsx
│   │   ├── hooks/
│   │   │   ├── useAssets.ts
│   │   │   └── useAssetDetail.ts
│   │   ├── api/
│   │   │   └── assetApi.ts
│   │   └── types/
│   │       └── asset.types.ts
│   └── signals/
│       └── ...
└── shared/
    ├── components/
    ├── hooks/
    └── utils/
```

---

## Commits e Pull Requests

### Conventional Commits

Usamos o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé opcional]
```

### Tipos de Commit

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `feat` | Nova feature | `feat(api): adiciona endpoint de alertas` |
| `fix` | Correção de bug | `fix(websocket): corrige desconexão aleatória` |
| `docs` | Documentação | `docs: atualiza guia de instalação` |
| `style` | Formatação | `style: aplica prettier no código` |
| `refactor` | Refatoração | `refactor(database): melhora estrutura de queries` |
| `test` | Testes | `test(api): adiciona testes para signals` |
| `chore` | Manutenção | `chore: atualiza dependências` |
| `perf` | Performance | `perf(engine): otimiza cálculo de scores` |
| `ci` | CI/CD | `ci: adiciona workflow de deploy` |
| `build` | Build | `build: atualiza configuração do Docker` |
| `revert` | Reverter | `revert: desfaz commit abc123` |

### Escopo (Opcional)

Especifica a área afetada:
- `api` - Backend API
- `frontend` - Frontend
- `database` - Database
- `docker` - Docker/Infraestrutura
- `collectors` - Data collectors
- `engine` - Score engine
- `websocket` - WebSocket
- `alerts` - Sistema de alertas

### Exemplos de Commits

**Features:**
```bash
feat(collectors): adiciona suporte ao CoinMarketCap API
feat(frontend): implementa dark mode
feat(alerts): adiciona notificações por email
```

**Bug Fixes:**
```bash
fix(api): corrige erro 500 no endpoint /signals
fix(websocket): resolve memory leak na conexão
fix(database): corrige migration duplicada
```

**Documentação:**
```bash
docs: atualiza README com instruções de deploy
docs(api): adiciona exemplos de uso no Swagger
docs: corrige typos no guia de contribuição
```

**Breaking Changes:**
```bash
feat(api)!: altera estrutura de resposta do /signals

BREAKING CHANGE: O campo `score` agora retorna um objeto
ao invés de um número. Atualize seu código:

Antes: { score: 75 }
Depois: { score: { value: 75, status: "high" } }
```

**Múltiplas mudanças:**
```bash
feat(api): adiciona paginação em todos os endpoints

- Adiciona parâmetros limit e offset
- Retorna total de itens no response
- Atualiza documentação da API

Closes #123
```

### Pull Request

#### Template de PR

```markdown
## 📝 Descrição
Breve descrição das mudanças realizadas.

## 🎯 Tipo de Mudança
- [ ] 🐛 Bug fix (correção de bug)
- [ ] ✨ Nova feature (nova funcionalidade)
- [ ] 💥 Breaking change (mudança que quebra compatibilidade)
- [ ] 📝 Documentação
- [ ] 🎨 Melhoria de UI/UX
- [ ] ⚡ Performance
- [ ] 🧪 Testes

## 🧪 Como Testar
1. Faça checkout da branch
2. Execute `npm install` (ou `pip install -r requirements.txt`)
3. Execute os testes com `npm test`
4. Navegue para `/dashboard`
5. Verifique se...

## 📸 Screenshots (se aplicável)
Cole screenshots ou GIFs demonstrando as mudanças visuais.

## 📋 Checklist
- [ ] Meu código segue os padrões do projeto
- [ ] Eu revisei meu próprio código
- [ ] Eu comentei código complexo quando necessário
- [ ] Eu atualizei a documentação relevante
- [ ] Meus testes passam localmente
- [ ] Eu adicionei testes que provam que minha correção é efetiva ou que minha feature funciona
- [ ] Testes novos e existentes passam localmente
- [ ] Não há warnings no console
- [ ] Build passa sem erros

## 🔗 Issues Relacionadas
Closes #123
Relates to #456

## 💭 Contexto Adicional
Qualquer informação adicional sobre o PR.
```

#### Boas Práticas para PRs

**✅ Faça:**
- Mantenha PRs pequenos e focados
- Escreva descrição clara e detalhada
- Adicione screenshots para mudanças visuais
- Responda comentários prontamente
- Mantenha o PR atualizado com a branch principal

**❌ Não Faça:**
- PRs gigantes com múltiplas features
- Commits de merge desnecessários
- Ignorar feedback dos reviewers
- Fazer force push após reviews
- Deixar conflitos sem resolver

#### Review Process

1. **Auto-review**: Revise seu próprio código antes de abrir o PR
2. **CI Checks**: Aguarde os checks automáticos passarem
3. **Code Review**: Responda aos comentários dos reviewers
4. **Aprovação**: Aguarde aprovação de pelo menos 1 maintainer
5. **Merge**: O PR será merged pelo maintainer

---

## Reportando Bugs

### Antes de Reportar

**Checklist:**
- [ ] Verifique se o bug já foi reportado nas [Issues](https://github.com/seu-usuario/cryptopulse/issues)
- [ ] Verifique se está usando a versão mais recente
- [ ] Tente reproduzir o bug em ambiente limpo
- [ ] Colete logs e informações relevantes

### Template de Bug Report

```markdown
## 🐛 Descrição do Bug
Uma descrição clara e concisa do bug.

## 📋 Passos para Reproduzir
1. Vá para '...'
2. Clique em '...'
3. Role até '...'
4. Veja o erro

## ✅ Comportamento Esperado
O que deveria acontecer.

## ❌ Comportamento Atual
O que está acontecendo.

## 📸 Screenshots
Se aplicável, adicione screenshots para ajudar a explicar o problema.

## 🖥️ Ambiente
- **OS**: [ex: Ubuntu 22.04, Windows 11, macOS 14]
- **Browser**: [ex: Chrome 120, Firefox 121]
- **Node**: [ex: 20.10.0]
- **Python**: [ex: 3.12.1]
- **Versão do CryptoPulse**: [ex: 0.1.0]

## 📝 Logs
```
Cole logs relevantes aqui
```

## 🔍 Contexto Adicional
Qualquer informação adicional sobre o problema.

## 🤔 Possível Solução
Se você tem uma ideia de como corrigir (opcional).
```

### Severidade do Bug

| Severidade | Descrição | Label |
|------------|-----------|-------|
| 🔴 **Critical** | Sistema não funciona | `severity: critical` |
| 🟠 **High** | Feature importante quebrada | `severity: high` |
| 🟡 **Medium** | Bug que afeta UX | `severity: medium` |
| 🟢 **Low** | Problema cosmético | `severity: low` |

---

## Sugerindo Melhorias

### Template de Feature Request

```markdown
## 💡 Problema/Motivação
Qual problema isso resolve? Por que essa feature é necessária?

## 🎯 Solução Proposta
Como você imagina a solução? Descreva em detalhes.

## 🔄 Alternativas Consideradas
Outras soluções que você considerou. Por que escolheu esta?

## 📸 Mockups/Exemplos
Adicione mockups, wireframes, ou exemplos de implementações similares.

## ⚙️ Complexidade Estimada
- [ ] Baixa (poucas horas)
- [ ] Média (alguns dias)
- [ ] Alta (semanas)

## 🎁 Benefícios
Quais são os benefícios dessa feature?

## ⚠️ Riscos/Desafios
Quais desafios técnicos podem surgir?

## 📋 Tarefas
- [ ] Tarefa 1
- [ ] Tarefa 2
- [ ] Tarefa 3

## 💭 Contexto Adicional
Qualquer informação adicional.
```

### Tipos de Melhorias

| Tipo | Descrição | Label |
|------|-----------|-------|
| 🚀 **Enhancement** | Melhoria de feature existente | `enhancement` |
| ✨ **New Feature** | Nova funcionalidade | `feature request` |
| 🎨 **UI/UX** | Melhorias de interface | `ui/ux` |
| ⚡ **Performance** | Otimizações | `performance` |
| 📱 **Mobile** | Melhorias mobile | `mobile` |
| ♿ **Accessibility** | Acessibilidade | `a11y` |

---

## Dúvidas e Suporte

### Como Obter Ajuda

1. **Documentação**: Consulte a [documentação](../README.md)
2. **Discussions**: Abra uma [discussão](https://github.com/seu-usuario/cryptopulse/discussions)
3. **Discord**: Entre no nosso servidor Discord
4. **Email**: suporte@cryptopulse.com

### FAQ

**P: Posso trabalhar em uma issue sem ela estar atribuída a mim?**
R: Sim, mas comente na issue dizendo que está trabalhando nela para evitar duplicação.

**P: Quanto tempo leva para meu PR ser revisado?**
R: Geralmente 2-5 dias úteis. PRs críticos podem ser revisados mais rapidamente.

**P: Meu PR foi recusado, e agora?**
R: Não desanime! Leia os comentários, faça as alterações sugeridas e tente novamente.

**P: Posso contribuir se sou iniciante?**
R: Sim! Procure issues com a label `good first issue`.

---

## Reconhecimento

Todos os contribuidores serão reconhecidos no [Contributors](https://github.com/seu-usuario/cryptopulse/graphs/contributors).

**Top Contributors:**
- 🥇 Contribuidor 1 - X commits
- 🥈 Contribuidor 2 - Y commits
- 🥉 Contribuidor 3 - Z commits

---

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma [Licença MIT](../LICENSE) do projeto.

---

**Obrigado por contribuir com o CryptoPulse! 🚀💙**

Juntos estamos construindo algo incrível!

---

📅 **Última atualização**: Janeiro 2024  
📝 **Versão**: 1.0.0