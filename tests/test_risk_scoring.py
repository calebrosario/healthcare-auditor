# tests/test_risk_scoring.py
import pytest
import sys

sys.path.insert(
    0,
    "/Users/calebrosario/Documents/sandbox/healthcare-auditor/backend",
)

from app.core.risk_scoring import RiskScoringEngine


@pytest.mark.asyncio
async def test_calculate_composite_score():
    engine = RiskScoringEngine()
    scores = {
        "rules_fraud_score": 0.2,
        "ml_fraud_probability": 0.5,
        "network_risk_score": 0.3,
        "nlp_risk_score": 0.1,
        "code_legality_score": 0.9,
    }
    result = await engine.calculate_composite_score(scores)
    assert "final_fraud_score" in result
    assert "risk_level" in result
    assert result["final_fraud_score"] < 1.0


def test_update_weights():
    engine = RiskScoringEngine()
    new_weights = {"rules": 0.3, "ml": 0.3, "network": 0.2, "nlp": 0.2}
    engine.update_weights(new_weights)
    assert engine.weights == new_weights


def test_update_thresholds():
    engine = RiskScoringEngine()
    new_thresholds = {"high": 0.8, "medium": 0.5}
    engine.update_thresholds(new_thresholds)
    assert engine.thresholds == new_thresholds


def test_get_stats():
    engine = RiskScoringEngine()
    stats = engine.get_stats()
    assert "scores_calculated" in stats
    assert "high_risk_count" in stats
