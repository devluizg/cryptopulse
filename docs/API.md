# 📡 CryptoPulse - Documentação da API

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
  "version": "0.1.0"
}
Assets
GET /api/v1/assets
Lista todos os ativos monitorados.

Query Parameters:

Param	Type	Default	Description
active	boolean	true	Filtrar ativos ativos
limit	int	50	Limite de resultados
offset	int	0	Offset para paginação
Response:

json
{
  "items": [
    {
      "id": 1,
      "symbol": "BTC",
      "name": "Bitcoin",
      "is_active": true
    }
  ],
  "total": 20
}
GET /api/v1/assets/{symbol}
Retorna detalhes de um ativo.

Signals
GET /api/v1/signals
Lista scores de todos os ativos.

Query Parameters:

Param	Type	Default	Description
min_score	int	0	Score mínimo (0-100)
status	string	all	low, attention, high
Response:

json
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
  ]
}
GET /api/v1/signals/{symbol}
Retorna score detalhado de um ativo com histórico.

Alerts
GET /api/v1/alerts
Lista alertas do sistema.

Query Parameters:

Param	Type	Default	Description
status	string	all	pending, sent, read
asset_symbol	string	-	Filtrar por ativo
Response:

json
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
  ]
}
POST /api/v1/alerts/{id}/read
Marca alerta como lido.

Jobs
GET /api/v1/jobs
Lista jobs agendados.

POST /api/v1/jobs/{name}/run
Executa job manualmente.

WebSocket
Conexão
javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
Eventos
score_update - Atualização de score
alert - Novo alerta
price_update - Atualização de preço
Códigos de Erro
Código	Descrição
400	Bad Request
404	Not Found
429	Rate Limit
500	Internal Error
Rate Limiting
API: 10 req/s por IP
WebSocket: 100 msg/min