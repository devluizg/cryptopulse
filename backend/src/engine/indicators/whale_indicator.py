"""
Indicador de atividade de Whales (grandes carteiras).

Analisa:
- Volume de transações grandes (> $1M)
- Frequência de movimentações
- Direção (acumulação vs distribuição)
- Comparação com média histórica
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import numpy as np

from .base_indicator import BaseIndicator


class WhaleIndicator(BaseIndicator):
    """
    Calcula score baseado em atividade de whales.
    
    Sinais bullish (score alto):
    - Whales acumulando (comprando)
    - Volume de whale acima da média
    - Múltiplas transações grandes em curto período
    
    Sinais bearish (score baixo):
    - Whales distribuindo (vendendo)
    - Volume abaixo da média
    - Movimentos para exchanges (potencial venda)
    """
    
    # Configurações
    MIN_TRANSACTION_USD = 1_000_000  # $1M mínimo para considerar whale
    LOOKBACK_HOURS = 24  # Janela de análise
    
    # Pesos internos
    WEIGHT_VOLUME = 0.35
    WEIGHT_COUNT = 0.25
    WEIGHT_DIRECTION = 0.25
    WEIGHT_RECENCY = 0.15
    
    def __init__(self, weight: float = 0.25):
        """
        Inicializa o indicador de whales.
        
        Args:
            weight: Peso no score final (padrão 25%)
        """
        super().__init__(name="whale_accumulation", weight=weight)
    
    async def calculate(self, data: Dict[str, Any]) -> float:
        """
        Calcula o score de atividade de whales.
        
        Args:
            data: {
                "transactions": List[Dict],  # Transações recentes
                "historical_avg_volume": float,  # Volume médio histórico
                "historical_avg_count": float,  # Contagem média histórica
                "asset_symbol": str,  # Símbolo do ativo
            }
            
        Returns:
            Score de 0 a 100
        """
        result = await self.calculate_with_details(data)
        return result["score"]
    
    async def calculate_with_details(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula score com detalhes completos.
        
        Args:
            data: Dados para cálculo
            
        Returns:
            Dict com score e detalhes
        """
        transactions = data.get("transactions", [])
        historical_avg_volume = data.get("historical_avg_volume", 0)
        historical_avg_count = data.get("historical_avg_count", 0)
        asset_symbol = data.get("asset_symbol", "UNKNOWN")
        
        # Se não há transações, score neutro
        if not transactions:
            details = {
                "transaction_count": 0,
                "total_volume_usd": 0,
                "avg_transaction_size": 0,
                "inflow_volume": 0,
                "outflow_volume": 0,
                "net_direction": "neutral",
                "volume_vs_avg": 0,
                "count_vs_avg": 0,
                "recency_score": 0,
                "sub_scores": {
                    "volume_score": 50,
                    "count_score": 50,
                    "direction_score": 50,
                    "recency_score": 50,
                },
                "reason": "Sem transações de whale no período"
            }
            self._update_state(50.0, data, details)
            return {"score": 50.0, "details": details}
        
        # Calcular métricas
        total_volume = sum(tx.get("amount_usd", 0) for tx in transactions)
        tx_count = len(transactions)
        avg_size = total_volume / tx_count if tx_count > 0 else 0
        
        # Separar inflow (para exchanges) e outflow (de exchanges)
        inflow_volume = sum(
            tx.get("amount_usd", 0) 
            for tx in transactions 
            if tx.get("transaction_type") == "inflow" or tx.get("to_exchange", False)
        )
        outflow_volume = sum(
            tx.get("amount_usd", 0) 
            for tx in transactions 
            if tx.get("transaction_type") == "outflow" or tx.get("from_exchange", False)
        )
        
        # Determinar direção líquida
        net_flow = outflow_volume - inflow_volume  # Positivo = acumulação
        if net_flow > total_volume * 0.1:
            net_direction = "accumulation"
        elif net_flow < -total_volume * 0.1:
            net_direction = "distribution"
        else:
            net_direction = "neutral"
        
        # === SUB-SCORES ===
        
        # 1. Volume Score (comparação com média)
        if historical_avg_volume > 0:
            volume_ratio = total_volume / historical_avg_volume
            volume_score = self._ratio_to_score(volume_ratio)
        else:
            volume_score = 60.0 if total_volume > 0 else 50.0
        
        # 2. Count Score (frequência de transações)
        if historical_avg_count > 0:
            count_ratio = tx_count / historical_avg_count
            count_score = self._ratio_to_score(count_ratio)
        else:
            count_score = 60.0 if tx_count > 0 else 50.0
        
        # 3. Direction Score (acumulação vs distribuição)
        if total_volume > 0:
            direction_ratio = net_flow / total_volume  # -1 a +1
            # Mapear -1..+1 para 20..80 (acumulação é bullish)
            direction_score = 50 + (direction_ratio * 30)
        else:
            direction_score = 50.0
        
        # 4. Recency Score (transações mais recentes = mais relevante)
        recency_score = self._calculate_recency_score(transactions)
        
        # === SCORE FINAL ===
        final_score = (
            volume_score * self.WEIGHT_VOLUME +
            count_score * self.WEIGHT_COUNT +
            direction_score * self.WEIGHT_DIRECTION +
            recency_score * self.WEIGHT_RECENCY
        )
        final_score = self.clamp_score(final_score)
        
        # Detalhes
        details = {
            "transaction_count": tx_count,
            "total_volume_usd": total_volume,
            "avg_transaction_size": avg_size,
            "inflow_volume": inflow_volume,
            "outflow_volume": outflow_volume,
            "net_flow": net_flow,
            "net_direction": net_direction,
            "volume_vs_avg": total_volume / historical_avg_volume if historical_avg_volume > 0 else None,
            "count_vs_avg": tx_count / historical_avg_count if historical_avg_count > 0 else None,
            "sub_scores": {
                "volume_score": round(volume_score, 2),
                "count_score": round(count_score, 2),
                "direction_score": round(direction_score, 2),
                "recency_score": round(recency_score, 2),
            },
            "weights": {
                "volume": self.WEIGHT_VOLUME,
                "count": self.WEIGHT_COUNT,
                "direction": self.WEIGHT_DIRECTION,
                "recency": self.WEIGHT_RECENCY,
            },
            "reason": self._generate_reason(net_direction, volume_score, tx_count)
        }
        
        self._update_state(final_score, data, details)
        
        logger.debug(
            f"[{self.name}] {asset_symbol}: score={final_score:.1f}, "
            f"txs={tx_count}, volume=${total_volume:,.0f}, direction={net_direction}"
        )
        
        return {"score": final_score, "details": details}
    
    def _ratio_to_score(self, ratio: float) -> float:
        """
        Converte um ratio (atual/média) para score 0-100.
        
        ratio = 1.0 -> score = 50 (na média)
        ratio = 2.0 -> score = 75 (2x a média)
        ratio = 0.5 -> score = 35 (metade da média)
        ratio = 3.0+ -> score = 90+ (muito acima)
        """
        if ratio <= 0:
            return 30.0
        
        # Usar log para suavizar extremos
        # log2(1) = 0 -> 50
        # log2(2) = 1 -> 65
        # log2(4) = 2 -> 80
        # log2(0.5) = -1 -> 35
        log_ratio = np.log2(ratio)
        score = 50 + (log_ratio * 15)
        
        return self.clamp_score(score)
    
    def _calculate_recency_score(self, transactions: List[Dict]) -> float:
        """
        Calcula score baseado em quão recentes são as transações.
        
        Transações nas últimas 2 horas = score alto
        Transações há mais de 12 horas = score baixo
        """
        if not transactions:
            return 50.0
        
        now = datetime.utcnow()
        scores = []
        
        for tx in transactions:
            tx_time = tx.get("timestamp")
            if isinstance(tx_time, str):
                try:
                    tx_time = datetime.fromisoformat(tx_time.replace("Z", "+00:00"))
                except:
                    continue
            elif not isinstance(tx_time, datetime):
                continue
            
            # Calcular idade em horas
            age_hours = (now - tx_time.replace(tzinfo=None)).total_seconds() / 3600
            
            # Score decai com o tempo
            # 0-2h: 80-100
            # 2-6h: 60-80
            # 6-12h: 40-60
            # 12-24h: 20-40
            if age_hours <= 2:
                score = 100 - (age_hours * 10)
            elif age_hours <= 6:
                score = 80 - ((age_hours - 2) * 5)
            elif age_hours <= 12:
                score = 60 - ((age_hours - 6) * 3.33)
            else:
                score = max(20, 40 - ((age_hours - 12) * 1.67))
            
            # Ponderar pelo valor da transação
            tx_value = tx.get("amount_usd", 0)
            weight = min(tx_value / 10_000_000, 2.0)  # Cap em 2x para tx de $10M+
            scores.append((score, weight))
        
        if not scores:
            return 50.0
        
        # Média ponderada
        total_weight = sum(w for _, w in scores)
        if total_weight == 0:
            return 50.0
        
        weighted_score = sum(s * w for s, w in scores) / total_weight
        return self.clamp_score(weighted_score)
    
    def _generate_reason(self, direction: str, volume_score: float, tx_count: int) -> str:
        """Gera explicação textual do score."""
        reasons = []
        
        if direction == "accumulation":
            reasons.append("Whales acumulando")
        elif direction == "distribution":
            reasons.append("Whales distribuindo")
        
        if volume_score >= 70:
            reasons.append("volume muito acima da média")
        elif volume_score >= 60:
            reasons.append("volume acima da média")
        elif volume_score <= 40:
            reasons.append("volume abaixo da média")
        
        if tx_count >= 10:
            reasons.append(f"{tx_count} transações grandes detectadas")
        elif tx_count >= 5:
            reasons.append(f"{tx_count} transações significativas")
        elif tx_count > 0:
            reasons.append(f"{tx_count} transação(ões) detectada(s)")
        
        return "; ".join(reasons) if reasons else "Atividade normal de whales"
