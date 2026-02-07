backend/app/core/anomaly_detection.py
"""
Statistical anomaly detection for healthcare billing fraud.
"""
import logging
import numpy as np
from scipy import stats
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)

Z_SCORE_THRESHOLD = 3.0
BENFORDS_P_VALUE_THRESHOLD = 0.05
FREQ_SPIKE_WINDOW_MINUTES = 10
FREQ_SPIKE_THRESHOLD_MULTIPLIER = 3.0
MIN_BENFORDS_SAMPLE_SIZE = 10


class AnomalyDetection:
    """Statistical anomaly detection using Z-score, Benford's Law, frequency spikes."""

    async def z_score_anomaly(self, values: List[float], threshold: float = Z_SCORE_THRESHOLD) -> List[float]:
        """
        Calculate Z-scores for values to detect outliers.

        Z-score = (value - mean) / std_dev

        Args:
            values: List of numeric values (e.g., billed amounts)
            threshold: Z-score threshold for anomaly (default: Z_SCORE_THRESHOLD)

        Returns:
            List of Z-scores, one per input value
        """
        if len(values) < 2:
            logger.warning("z_score_anomaly: Not enough values")
            return [0.0] * len(values)

        values_array = np.array(values)
        mean = np.mean(values_array)
        std_dev = np.std(values_array)

        if std_dev == 0:
            return [0.0] * len(values)

        z_scores = (values_array - mean) / std_dev

        logger.debug(f"z_score_anomaly: mean={mean}, std={std_dev}, max_z={max(abs(z_scores))}")
        return z_scores.tolist()

    async def benfords_law_analysis(self, amounts: List[float]) -> Dict[str, Any]:
        """
        Analyze if amounts follow Benford's Law (first digit distribution).

        Benford's Law: First digit d appears with probability log10(1 + 1/d)

        Args:
            amounts: List of billed amounts

        Returns:
            Dictionary with chi2, p_value, observed frequencies, expected frequencies
        """
        if len(amounts) < 10:
            logger.warning("benfords_law: Not enough values for reliable test")
            return {'chi2': 0.0, 'p_value': 1.0, 'observed': [], 'expected': []}

        # Extract first digits
        first_digits = [int(str(abs(x)).lstrip('0')[0]) for x in amounts if x != 0]

        if not first_digits:
            return {'chi2': 0.0, 'p_value': 1.0, 'observed': [], 'expected': []}

        # Expected frequencies per Benford's Law
        expected_freqs = [np.log10(1 + 1/d) for d in range(1, 10)]

        # Observed frequencies
        observed_counts = [first_digits.count(d) for d in range(1, 10)]
        observed_freqs = [count / len(first_digits) for count in observed_counts]

        # Chi-square test
        try:
            chi2, p_value = stats.chisquare(observed_freqs, f_exp=expected_freqs)
        except Exception as e:
            logger.error(f"benfords_law: Chi-square test failed: {e}")
            return {'chi2': 0.0, 'p_value': 1.0, 'observed': [], 'expected': []}

        result = {
            'chi2': float(chi2),
            'p_value': float(p_value),
            'observed': observed_freqs,
            'expected': expected_freqs,
            'is_anomaly': p_value < BENFORDS_P_VALUE_THRESHOLD
        }

        logger.debug(f"benfords_law: chi2={chi2:.2f}, p={p_value:.4f}, is_anomaly={result['is_anomaly']}")
        return result

    async def frequency_spike_detection(
        self,
        timestamps: List[str],
        window_minutes: int = 10,
        threshold_multiplier: float = 3.0
    ) -> List[Dict[str, Any]]:
        """
        Detect unusual frequency spikes in timestamps.

        Args:
            timestamps: List of ISO 8601 timestamp strings
            window_minutes: Rolling window size in minutes
            threshold_multiplier: Multiplier for spike detection (mean * multiplier)

        Returns:
            List of spike records with timestamp, count, expected_count, anomaly_score
        """
        if len(timestamps) < 3:
            logger.warning("frequency_spike_detection: Not enough timestamps")
            return []

        # Parse timestamps
        dt_objects = [datetime.fromisoformat(ts) for ts in timestamps]
        dt_objects.sort()

        # Count events in rolling windows using sliding window (O(n) instead of O(n²))
        spikes = []
        window_delta = timedelta(minutes=window_minutes)
        window = deque()
        all_window_counts = []

        # Single pass: maintain sliding window of events within window_minutes
        for dt in dt_objects:
            # Add current timestamp to window
            window.append(dt)

            # Remove events that fell outside the window
            while window and dt - window[0] > window_delta:
                window.popleft()

            count = len(window)
            all_window_counts.append(count)

        # Calculate statistics from all window counts
        if len(all_window_counts) < 2:
            logger.debug("frequency_spike_detection: Not enough data for statistical analysis")
            return []

        expected = np.mean(all_window_counts)
        std = np.std(all_window_counts)

        # Detect spikes
        for i, dt in enumerate(dt_objects):
            count = all_window_counts[i]

            if std > 0:
                z_score = (count - expected) / std
                if z_score > threshold_multiplier:
                    spikes.append({
                        'timestamp': dt.isoformat(),
                        'count': count,
                        'expected_count': expected,
                        'z_score': z_score,
                        'anomaly_score': min(z_score / threshold_multiplier, 1.0)
                    })

        logger.debug(f"frequency_spike_detection: Found {len(spikes)} spikes")
        return spikes

    async def analyze_bill(
        self,
        bill: Any,
        historical_bills: List[Any] = None
    ) -> Dict[str, Any]:
        """
        Run all statistical anomaly checks on a bill.

        Args:
            bill: Bill object with billed_amount, bill_date
            historical_bills: List of historical bills for comparison

        Returns:
            Dictionary with anomaly results
        """
        amount = getattr(bill, 'billed_amount', 0.0)
        bill_date = getattr(bill, 'bill_date', None)

        # Get historical amounts for comparison
        historical_amounts = []
        if historical_bills:
            historical_amounts = [
                hb.billed_amount for hb in historical_bills if hasattr(hb, 'billed_amount')
            ]

        all_amounts = historical_amounts + [amount]

        # Run anomaly detection
        z_scores = await self.z_score_anomaly(all_amounts)
        benford_result = await self.benfords_law_analysis(historical_amounts + [amount] if historical_amounts else [amount])

        return {
            'z_score': z_scores[-1] if z_scores else 0.0,
            'is_zscore_anomaly': abs(z_scores[-1]) > 3.0 if z_scores else False,
            'benfords_p_value': benford_result.get('p_value', 1.0),
            'is_benfords_anomaly': benford_result.get('is_anomaly', False),
            'anomaly_score': self._calculate_anomaly_score(z_scores, benford_result)
        }

    def _calculate_anomaly_score(self, z_scores: List[float], benford_result: Dict[str, Any]) -> float:
        """Calculate composite anomaly score (0-1)."""
        score = 0.0

        if z_scores:
            max_z = max(abs(z) for z in z_scores)
            if max_z > 3.0:
                score += 0.5
            elif max_z > 2.0:
                score += 0.3

        if benford_result.get('is_anomaly', False):
            score += 0.5

        return min(score, 1.0)
