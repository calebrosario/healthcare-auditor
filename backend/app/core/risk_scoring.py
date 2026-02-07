"""
Combined risk scoring system integrating all analysis layers.
"""
import logging
from typing import Dict, Any, Optional
from ..config import settings

logger = logging.getLogger(__name__)


class RiskScoringEngine:
    """Orchestrates weighted ensemble scoring from all analysis layers."""

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize risk scoring engine.
        
        Args:
            weights: Optional custom weights (default from config)
        """
        self.weights = weights or settings.SCORING_WEIGHTS
        
        self.thresholds = {
            'high': settings.HIGH_RISK_THRESHOLD,
            'medium': settings.MEDIUM_RISK_THRESHOLD
        }

        self.stats = {
            'scores_calculated': 0,
            'high_risk_count': 0,
            'low_risk_count': 0
        }

    async def calculate_composite_score(
        self,
        layer_scores: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate weighted ensemble fraud score from all analysis layers.

        Args:
            layer_scores: Dictionary with scores from:
                - rules_engine: fraud_score, compliance_score
                - ml: fraud_probability
                - network: network_risk_score
                - nlp: nlp_risk_score
                - code_legality: legality_score

        Returns:
            Dictionary with final fraud score and risk level
        """
        try:
            rules_score = layer_scores.get('rules_fraud_score', 0.5)
            ml_score = layer_scores.get('ml_fraud_probability', 0.5)
            network_score = layer_scores.get('network_risk_score', 0.5)
            nlp_score = layer_scores.get('nlp_risk_score', 0.5)
            legality_score = layer_scores.get('code_legality_score', 1.0)

            legality_fraud_score = 1.0 - legality_score

            final_score = (
                self.weights['rules'] * rules_score +
                self.weights['ml'] * ml_score +
                self.weights['network'] * network_score +
                self.weights['nlp'] * nlp_score +
                0.1 * legality_fraud_score
            )

            if final_score >= self.thresholds['high']:
                risk_level = 'high'
            elif final_score >= self.thresholds['medium']:
                risk_level = 'medium'
            else:
                risk_level = 'low'

            scores_list = [rules_score, ml_score, network_score, nlp_score, legality_fraud_score]
            score_variance = max(scores_list) - min(scores_list)

            self.stats['scores_calculated'] += 1
            if risk_level == 'high':
                self.stats['high_risk_count'] += 1
            else:
                self.stats['low_risk_count'] += 1

            result = {
                'final_fraud_score': round(final_score, 4),
                'risk_level': risk_level,
                'layer_scores': {
                    'rules': rules_score,
                    'ml': ml_score,
                    'network': network_score,
                    'nlp': nlp_score,
                    'code_legality': legality_score
                },
                'score_variance': round(score_variance, 4),
                'weights': self.weights.copy()
            }

            logger.debug(
                f"RiskScoring: final={final_score:.4f}, level={risk_level}, variance={score_variance:.4f}"
            )

            return result

        except Exception as e:
            logger.error(f"Risk scoring calculation failed: {e}")
            return {
                'final_fraud_score': 0.5,
                'risk_level': 'medium',
                'error': str(e)
            }

    def update_weights(self, new_weights: Dict[str, float]) -> None:
        """
        Update scoring weights dynamically.

        Args:
            new_weights: New weights (must sum to 1.0)
        """
        total = sum(new_weights.values())
        if abs(total - 1.0) > 0.01:
            logger.warning(f"Weight update rejected: sum={total:.4f}, expected 1.0")
            return

        self.weights.update(new_weights)
        logger.info(f"RiskScoring weights updated: {self.weights}")

    def update_thresholds(self, new_thresholds: Dict[str, float]) -> None:
        """
        Update risk level thresholds.

        Args:
            new_thresholds: New thresholds (high, medium)
        """
        self.thresholds.update(new_thresholds)
        logger.info(f"RiskScoring thresholds updated: {self.thresholds}")

    def get_stats(self) -> Dict[str, int]:
        """Get scoring statistics."""
        return self.stats.copy()
