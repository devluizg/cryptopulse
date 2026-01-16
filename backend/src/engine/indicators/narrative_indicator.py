"""
Indicador de Narrativa/Sentiment.

Analisa:
- Sentiment de notícias (bullish/bearish)
- Volume de menções
- Impacto de eventos
- Momentum social
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger
import numpy as np

from .base_indicator import BaseIndicator


class NarrativeIndicator(BaseIndicator):
    """
    Calcula score baseado em narrativa e sentiment do mercado.
    
    Sinais bullish (score alto):
    - Notícias positivas recentes
    - Aumento de menções/hype
    - Eventos importantes (listings, partnerships)
    
    Sinais bearish (score baixo):
    - Notícias negativas (hacks, regulação)
    - FUD generalizado
    - Queda de interesse/menções
    """
    
    # Pesos internos
    WEIGHT_SENTIMENT = 0.40
    WEIGHT_VOLUME = 0.25
    WEIGHT_RECENCY = 0.20
    WEIGHT_IMPACT = 0.15
    
    # Mapeamento de tipos de eventos
    EVENT_IMPACT = {
        "listing": 80,
        "partnership": 75,
        "upgrade": 70,
        "adoption": 70,
        "etf": 85,
        "regulation_positive": 65,
        "regulation_negative": 25,
        "hack": 15,
        "exploit": 20,
        "lawsuit": 25,
        "delisting": 20,
        "bullish": 70,
        "bearish": 30,
        "neutral": 50,
    }
    
    def __init__(self, weight: float = 0.15):
        """
        Inicializa o indicador de narrativa.
        
        Args:
            weight: Peso no score final (padrão 15%)
        """
        super().__init__(name="narrative_momentum", weight=weight)
    
    async def calculate(self, data: Dict[str, Any]) -> float:
        """
        Calcula o score de narrativa/sentiment.
        
        Args:
            data: {
                "news": List[Dict],  # Lista de notícias recentes
                "sentiment_scores": List[float],  # Scores de sentiment (-1 a 1)
                "mention_count": int,  # Número de menções
                "historical_mention_avg": float,  # Média histórica de menções
                "events": List[Dict],  # Eventos significativos
                "asset_symbol": str,
            }
            
        Returns:
            Score de 0 a 100
        """
        result = await self.calculate_with_details(data)
        return result["score"]
    
    async def calculate_with_details(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula score com detalhes completos.
        """
        news = data.get("news", [])
        sentiment_scores = data.get("sentiment_scores", [])
        mention_count = data.get("mention_count", 0)
        historical_mention_avg = data.get("historical_mention_avg", 0)
        events = data.get("events", [])
        asset_symbol = data.get("asset_symbol", "UNKNOWN")
        
        # Se não há dados
        if not news and not events and not sentiment_scores:
            details = {
                "news_count": 0,
                "avg_sentiment": None,
                "mention_ratio": None,
                "significant_events": [],
                "sub_scores": {
                    "sentiment_score": 50,
                    "volume_score": 50,
                    "recency_score": 50,
                    "impact_score": 50,
                },
                "reason": "Sem dados de narrativa disponíveis"
            }
            self._update_state(50.0, data, details)
            return {"score": 50.0, "details": details}
        
        # === SUB-SCORES ===
        
        # 1. Sentiment Score
        sentiment_score = self._calculate_sentiment_score(news, sentiment_scores)
        
        # 2. Volume Score (menções)
        volume_score = self._calculate_volume_score(mention_count, historical_mention_avg)
        
        # 3. Recency Score
        recency_score = self._calculate_recency_score(news)
        
        # 4. Impact Score (eventos)
        impact_score, significant_events = self._calculate_impact_score(events, news)
        
        # === SCORE FINAL ===
        final_score = (
            sentiment_score * self.WEIGHT_SENTIMENT +
            volume_score * self.WEIGHT_VOLUME +
            recency_score * self.WEIGHT_RECENCY +
            impact_score * self.WEIGHT_IMPACT
        )
        final_score = self.clamp_score(final_score)
        
        # Calcular sentiment médio
        if sentiment_scores:
            avg_sentiment = float(np.mean(sentiment_scores))
        elif news:
            avg_sentiment = self._extract_avg_sentiment(news)
        else:
            avg_sentiment = 0.0
        
        # Detalhes
        details = {
            "news_count": len(news),
            "avg_sentiment": round(avg_sentiment, 2) if avg_sentiment else None,
            "mention_count": mention_count,
            "mention_ratio": round(mention_count / historical_mention_avg, 2) if historical_mention_avg > 0 else None,
            "significant_events": significant_events[:5],  # Top 5
            "sub_scores": {
                "sentiment_score": round(sentiment_score, 2),
                "volume_score": round(volume_score, 2),
                "recency_score": round(recency_score, 2),
                "impact_score": round(impact_score, 2),
            },
            "overall_sentiment": self._classify_sentiment(avg_sentiment),
            "reason": self._generate_reason(avg_sentiment, mention_count, significant_events)
        }
        
        self._update_state(final_score, data, details)
        
        logger.debug(
            f"[{self.name}] {asset_symbol}: score={final_score:.1f}, "
            f"sentiment={avg_sentiment:.2f}, news={len(news)}"
        )
        
        return {"score": final_score, "details": details}
    
    def _calculate_sentiment_score(self, news: List[Dict], sentiment_scores: List[float]) -> float:
        """
        Calcula score baseado em sentiment.
        
        Sentiment varia de -1 (bearish) a +1 (bullish)
        """
        # Priorizar sentiment_scores se disponível
        if sentiment_scores:
            sentiments = sentiment_scores
        else:
            # Extrair de news
            sentiments = []
            for n in news:
                sent = n.get("sentiment")
                if sent == "bullish" or sent == "positive":
                    sentiments.append(0.7)
                elif sent == "bearish" or sent == "negative":
                    sentiments.append(-0.7)
                else:
                    sentiments.append(0.0)
        
        if not sentiments:
            return 50.0
        
        # Pesos decrescentes para notícias mais antigas
        weights = self.exponential_decay_weights(len(sentiments), decay=0.85)
        avg_sentiment = self.weighted_average(sentiments, weights)
        
        # Mapear -1..+1 para 0..100
        # -1 -> 15, 0 -> 50, +1 -> 85
        score = 50 + (avg_sentiment * 35)
        
        return self.clamp_score(score)
    
    def _calculate_volume_score(self, mentions: int, historical_avg: float) -> float:
        """
        Calcula score baseado em volume de menções.
        
        Mais menções = mais hype = potencial movimento
        """
        if historical_avg <= 0:
            if mentions > 0:
                return 60.0  # Algum interesse
            return 50.0
        
        ratio = mentions / historical_avg
        
        if ratio >= 3:
            return 90.0  # Viral
        elif ratio >= 2:
            return 75.0 + (ratio - 2) * 15
        elif ratio >= 1.5:
            return 65.0 + (ratio - 1.5) * 20
        elif ratio >= 1:
            return 50.0 + (ratio - 1) * 30
        elif ratio >= 0.5:
            return 35.0 + (ratio - 0.5) * 30
        else:
            return max(20.0, ratio * 70)
    
    def _calculate_recency_score(self, news: List[Dict]) -> float:
        """
        Calcula score baseado em quão recentes são as notícias.
        """
        if not news:
            return 50.0
        
        now = datetime.utcnow()
        scores: List[float] = []
        
        for n in news:
            pub_time = n.get("published_at") or n.get("created_at")
            if not pub_time:
                continue
            
            if isinstance(pub_time, str):
                try:
                    pub_time = datetime.fromisoformat(pub_time.replace("Z", "+00:00"))
                except:
                    continue
            
            age_hours = (now - pub_time.replace(tzinfo=None)).total_seconds() / 3600
            
            # Notícias mais recentes = score maior
            if age_hours <= 1:
                scores.append(95.0)
            elif age_hours <= 4:
                scores.append(80.0)
            elif age_hours <= 12:
                scores.append(65.0)
            elif age_hours <= 24:
                scores.append(50.0)
            else:
                scores.append(max(30.0, 50.0 - (age_hours - 24) / 2))
        
        if not scores:
            return 50.0
        
        return float(np.mean(scores))
    
    def _calculate_impact_score(self, events: List[Dict], news: List[Dict]) -> Tuple[float, List[Dict]]:
        """
        Calcula score baseado em eventos significativos.
        
        Returns:
            Tuple[score, List[eventos significativos]]
        """
        significant: List[Dict] = []
        impact_scores: List[float] = []
        
        # Processar eventos
        for event in events:
            event_type = event.get("type", "").lower()
            impact = float(self.EVENT_IMPACT.get(event_type, 50))
            
            significant.append({
                "type": event_type,
                "title": event.get("title", ""),
                "impact": impact
            })
            impact_scores.append(impact)
        
        # Processar notícias por palavras-chave
        keywords_bullish = ["listing", "partnership", "adoption", "upgrade", "etf", "approved"]
        keywords_bearish = ["hack", "exploit", "lawsuit", "ban", "delisting", "scam"]
        
        for n in news:
            title = (n.get("title", "") + " " + n.get("summary", "")).lower()
            
            for kw in keywords_bullish:
                if kw in title:
                    impact = float(self.EVENT_IMPACT.get(kw, 70))
                    significant.append({
                        "type": kw,
                        "title": n.get("title", "")[:100],
                        "impact": impact
                    })
                    impact_scores.append(impact)
                    break
            
            for kw in keywords_bearish:
                if kw in title:
                    impact = float(self.EVENT_IMPACT.get(kw, 30))
                    significant.append({
                        "type": kw,
                        "title": n.get("title", "")[:100],
                        "impact": impact
                    })
                    impact_scores.append(impact)
                    break
        
        if not impact_scores:
            return 50.0, []
        
        # Ordenar por impacto
        significant.sort(key=lambda x: abs(x["impact"] - 50), reverse=True)
        
        # Score = média ponderada (eventos mais impactantes pesam mais)
        weights = [abs(s["impact"] - 50) + 10 for s in significant]
        scores_list = [s["impact"] for s in significant]
        
        avg_score = self.weighted_average(scores_list, weights)
        
        return avg_score, significant
    
    def _extract_avg_sentiment(self, news: List[Dict]) -> float:
        """Extrai sentiment médio das notícias."""
        sentiments: List[float] = []
        for n in news:
            sent = n.get("sentiment", "neutral")
            if sent in ["bullish", "positive"]:
                sentiments.append(0.7)
            elif sent in ["bearish", "negative"]:
                sentiments.append(-0.7)
            else:
                sentiments.append(0.0)
        
        if sentiments:
            return float(np.mean(sentiments))
        return 0.0
    
    def _classify_sentiment(self, avg_sentiment: Optional[float]) -> str:
        """Classifica o sentiment geral."""
        if avg_sentiment is None:
            return "unknown"
        elif avg_sentiment >= 0.5:
            return "very_bullish"
        elif avg_sentiment >= 0.2:
            return "bullish"
        elif avg_sentiment <= -0.5:
            return "very_bearish"
        elif avg_sentiment <= -0.2:
            return "bearish"
        else:
            return "neutral"
    
    def _generate_reason(self, sentiment: Optional[float], mentions: int, events: List[Dict]) -> str:
        """Gera explicação textual."""
        reasons: List[str] = []
        
        if sentiment is not None:
            if sentiment >= 0.5:
                reasons.append("Sentiment muito positivo")
            elif sentiment >= 0.2:
                reasons.append("Sentiment positivo")
            elif sentiment <= -0.5:
                reasons.append("Sentiment muito negativo")
            elif sentiment <= -0.2:
                reasons.append("Sentiment negativo")
        
        if mentions > 0:
            reasons.append(f"{mentions} menções recentes")
        
        bullish_events = [e for e in events if e.get("impact", 50) > 60]
        bearish_events = [e for e in events if e.get("impact", 50) < 40]
        
        if bullish_events:
            reasons.append(f"{len(bullish_events)} evento(s) positivo(s)")
        if bearish_events:
            reasons.append(f"{len(bearish_events)} evento(s) negativo(s)")
        
        return "; ".join(reasons) if reasons else "Narrativa neutra"
