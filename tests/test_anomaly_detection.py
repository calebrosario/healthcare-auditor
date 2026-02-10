# tests/test_anomaly_detection.py
import pytest
import sys

sys.path.insert(
    0,
    "/Users/calebrosario/Documents/sandbox/healthcare-auditor/backend",
)

from app.core.anomaly_detection import AnomalyDetection


@pytest.mark.asyncio
async def test_z_score_anomaly():
    detector = AnomalyDetection()
    amounts = [100.0, 110.0, 105.0, 115.0, 108.0, 10000.0]
    z_scores = await detector.z_score_anomaly(amounts)
    assert z_scores[-1] > 0.0
    assert z_scores[0] < 1.0


@pytest.mark.asyncio
async def test_benfords_law():
    detector = AnomalyDetection()
    amounts = [123.0, 254.0, 89.0, 412.0, 156.0, 789.0, 321.0, 654.0, 987.0, 123.0]
    result = await detector.benfords_law_analysis(amounts)
    assert "p_value" in result
    assert "chi2" in result
    assert result["p_value"] > 0.05


@pytest.mark.asyncio
async def test_frequency_spike_detection():
    detector = AnomalyDetection()
    timestamps = [
        "2026-02-01 10:00",
        "2026-02-01 10:01",
        "2026-02-01 10:02",
        "2026-02-01 10:03",
        "2026-02-01 10:04",
        "2026-02-01 10:05",
        "2026-02-01 10:10",
    ]
    spikes = await detector.frequency_spike_detection(timestamps, window_minutes=10)
    assert len(spikes) == 0
