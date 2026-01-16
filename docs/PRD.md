# 📄 CryptoPulse  
## Product Requirements Document (PRD)

---

## 1. Informações Gerais

### 1.1 Nome do Produto
**CryptoPulse** (nome interno)

### 1.2 Tipo de Produto
Plataforma Web de Monitoramento e Alertas de Mercado Cripto

### 1.3 Status do Documento
Versão: 1.0  
Data: 2026-01  
Autor: Equipe CryptoPulse

---

## 2. Visão do Produto

### 2.1 Descrição
CryptoPulse é uma plataforma visual de inteligência de mercado cripto que identifica **condições estatisticamente raras** e **sinais antecipados** associados a grandes movimentos de preço.

O sistema combina:
- Dados on-chain  
- Dados de mercado  
- Eventos externos e narrativas relevantes  

O produto **não prevê preços**, nem fornece recomendações financeiras diretas. Ele gera **alertas explicáveis**, baseados em múltiplas camadas de dados, que indicam **alta probabilidade de movimentos anormais**.

### 2.2 Proposta de Valor
> **“Veja o que o mercado ainda não precificou.”**

Principais diferenciais:
- Alertas baseados em múltiplas fontes de dados
- Explicação clara do *porquê* de cada sinal
- Visual limpo, sem excesso de indicadores técnicos
- Foco exclusivo em eventos fora do padrão histórico

---

## 3. Problema a Ser Resolvido

### 3.1 Contexto
Movimentos extremos de preço (100%+, 500%, 1000%) **raramente começam no gráfico**.  
A maioria das ferramentas atuais analisa apenas:
- Preço
- Indicadores técnicos tradicionais (RSI, MACD, médias móveis)

### 3.2 Dores do Usuário
Investidores e traders não conseguem:
- Monitorar movimentações de baleias em tempo hábil
- Cruzar dados on-chain com fluxo para exchanges
- Relacionar dados técnicos com narrativa institucional ou política
- Identificar acúmulo silencioso antes de grandes movimentos

---

## 4. Objetivos do Produto

### 4.1 Objetivo Principal
Detectar **zonas de pressão explosiva** no mercado cripto antes de grandes variações de preço, com **transparência total dos critérios utilizados**.

### 4.2 Objetivos Secundários
- Reduzir ruído, hype e decisões emocionais
- Incentivar decisões baseadas em probabilidade e contexto
- Criar base histórica para análise e aprendizado contínuo
- Servir como ferramenta de apoio, não de decisão automática

---

## 5. Público-Alvo

### 5.1 Usuários Primários
- Traders swing e position
- Investidores cripto de médio e longo prazo
- Usuários avançados com entendimento de risco

### 5.2 Usuários Secundários
- Criadores de conteúdo financeiro
- Analistas independentes
- Estudantes e pesquisadores de dados financeiros

---

## 6. Escopo Funcional (MVP)

### 6.1 Monitoramento de Ativos
- Lista configurável de criptomoedas
- Atualização contínua dos dados
- Histórico diário de sinais por ativo

---

### 6.2 Coleta de Dados

#### 6.2.1 Dados On-Chain
- Transferências acima de um valor mínimo configurável (whales)
- Fluxo líquido para exchanges (inflow / outflow)
- Número de endereços ativos
- Variações anormais em padrões de movimentação

#### 6.2.2 Dados de Mercado
- Volume diário
- Volume comparado à média histórica
- Variação percentual de preço (24h, 7d)
- Open Interest (quando disponível)

#### 6.2.3 Dados de Narrativa
- Notícias relevantes categorizadas
- Eventos institucionais e regulatórios
- Marcação manual ou via feeds externos

---

### 6.3 Engine de Sinais

#### 6.3.1 Explosion Score
Cada ativo recebe um **Explosion Score (0–100)**, calculado a partir de indicadores compostos:

- Whale Accumulation Score  
- Exchange Netflow Score  
- Volume Anomaly Score  
- Open Interest Pressure Score  
- Narrative Momentum Score  

Os pesos são definidos inicialmente de forma heurística e ajustáveis futuramente.

#### 6.3.2 Classificação Visual
- 🔴 **Baixo potencial** (0–39)
- 🟡 **Atenção** (40–69)
- 🟢 **Zona de possível explosão** (70–100)

---

### 6.4 Alertas

Alertas são disparados quando:
- O Explosion Score ultrapassa um limiar configurável
- Há mudança brusca em um componente crítico

Tipos de alerta:
- Dashboard em tempo real (MVP)
- Push / Email (fase futura)

---

## 7. Experiência do Usuário (UX)

### 7.1 Dashboard Principal
Tabela com:
- Criptomoeda
- Explosion Score
- Status visual (badge colorido)
- Variação de preço (24h)
- Principais fatores que compõem o score

### 7.2 Tela de Detalhe do Ativo
- Breakdown completo do score
- Gráficos temporais dos indicadores
- Linha do tempo de eventos relevantes
- Explicação textual dos sinais

---

## 8. Fora de Escopo (Não-Escopo)

❌ Recomendações financeiras diretas  
❌ Botões “Comprar” ou “Vender”  
❌ Previsões determinísticas de preço  
❌ Trading automático ou bots  
❌ Copy trading  

---

## 9. Requisitos Técnicos (Alto Nível)

### 9.1 Backend
- Coleta contínua de dados via APIs externas
- Normalização e validação de dados
- Armazenamento histórico
- Cálculo periódico dos scores
- WebSocket para atualizações em tempo real

### 9.2 Frontend
- Dashboard web responsivo
- Visualização clara e objetiva
- Ênfase em explicabilidade dos dados

### 9.3 Armazenamento
- Banco relacional para dados agregados
- Banco de séries temporais para histórico
- Cache para dados em tempo real

---

## 10. Métricas de Sucesso

### 10.1 Métricas de Produto
- Percentual de grandes movimentos precedidos por alertas
- Tempo médio entre alerta e movimento relevante
- Retenção diária e semanal de usuários

### 10.2 Métricas de Qualidade
- Taxa de falsos positivos
- Feedback de clareza e confiança nos alertas
- Uso recorrente da tela de detalhamento

---

## 11. Riscos e Limitações

- Dados incompletos ou atrasados
- Eventos políticos imprevisíveis
- Mudanças abruptas de mercado
- Dependência de APIs externas
- Possibilidade de overfitting em fases futuras

---

## 12. Considerações Éticas e Legais

- Disclaimer explícito: **não é aconselhamento financeiro**
- Transparência total dos critérios de cálculo
- Nenhuma promessa de retorno financeiro
- Uso responsável dos dados coletados

---

## 13. Roadmap

### Fase 1 – MVP ✅
- Dashboard com Explosion Score
- Coleta de dados essencial
- Alertas em tempo real
- WebSocket

### Fase 2 – Evolução
- Ajuste dinâmico de pesos
- Análise histórica automática
- Alertas personalizados por usuário

### Fase 3 – Expansão
- Sentimento em redes sociais
- Atividade de desenvolvedores (GitHub)
- Comparação entre ciclos históricos

### Fase 4 – Produto
- Plataforma SaaS
- Perfis de usuário
- API pública

---

## 14. Premissas e Dependências

### Premissas
- Usuário entende risco de mercado
- Alertas são ferramentas de apoio
- Mercado cripto é altamente volátil

### Dependências
- APIs on-chain
- APIs de mercado
- Fontes de notícias confiáveis

---

## 15. Glossário

- **Whale**: Endereço com grande quantidade de capital
- **Netflow**: Fluxo líquido para exchanges
- **Explosion Score**: Indicador composto de pressão de mercado
- **Narrativa**: Contexto externo que influencia comportamento do mercado

---

## 16. Resumo Executivo

> **CryptoPulse não tenta prever o futuro.**  
> Ele mede a **pressão invisível** que normalmente antecede grandes movimentos no mercado cripto.  
>
> **Menos hype. Mais sinal.**
