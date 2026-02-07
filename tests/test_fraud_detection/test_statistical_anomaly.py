"""
Test file for statistical anomaly detection components.
Following TDD approach - tests written before implementation.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from backend.app.fraud_detection.statistical_anomaly import (
    ZScoreDetector, 
    StatisticalAnomalyDetector,
    AnomalyResult
)

class TestZScoreDetector:
    """Test cases for Z-score based anomaly detection."""
    
    def test_zscore_detector_init_default(self):
        """Test ZScoreDetector initialization with default parameters."""
        detector = ZScoreDetector()
        assert detector.threshold == 3.0
        assert detector.mean is None
        assert detector.std is None
        assert not detector.fitted
    
    def test_zscore_detector_init_custom_threshold(self):
        """Test ZScoreDetector initialization with custom threshold."""
        detector = ZScoreDetector(threshold=2.5)
        assert detector.threshold == 2.5
    
    def test_fit_calculates_mean_and_std(self):
        """Test that fit method calculates mean and standard deviation."""
        detector = ZScoreDetector()
        data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        
        result = detector.fit(data)
        
        # Should return self for method chaining
        assert result is detector
        
        # Should calculate statistics
        assert detector.mean is not None
        assert detector.std is not None
        assert detector.fitted
        
        # Verify calculations
        expected_mean = np.mean(data)
        expected_std = np.std(data)
        assert abs(detector.mean - expected_mean) < 1e-10
        assert abs(detector.std - expected_std) < 1e-10
    
    def test_predict_without_fit_raises_error(self):
        """Test that predict raises error when detector not fitted."""
        detector = ZScoreDetector()
        data = np.array([1, 2, 3])
        
        with pytest.raises(ValueError, match="must be fitted before prediction"):
            detector.predict(data)
    
    def test_predict_detects_outliers(self):
        """Test that predict correctly detects outliers."""
        detector = ZScoreDetector(threshold=2.0)
        normal_data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        outlier_data = np.array([100])  # Clear outlier
        
        # Fit on normal data
        detector.fit(normal_data)
        
        # Normal data should not be outliers
        normal_predictions = detector.predict(normal_data)
        assert not any(normal_predictions)
        
        # Outlier should be detected
        outlier_predictions = detector.predict(outlier_data)
        assert all(outlier_predictions)
    
    def test_anomaly_scores_return_continuous_values(self):
        """Test that anomaly_scores returns continuous Z-score values."""
        detector = ZScoreDetector()
        data = np.array([1, 2, 3, 4, 5])
        
        detector.fit(data)
        scores = detector.anomaly_scores(data)
        
        # Should return numpy array
        assert isinstance(scores, np.ndarray)
        
        # All scores should be non-negative
        assert all(score >= 0 for score in scores)
        
        # Extreme values should have higher scores
        extreme_data = np.array([1000])
        extreme_score = detector.anomaly_scores(extreme_data)[0]
        assert extreme_score > scores.mean()
    
    def test_single_value_data_handling(self):
        """Test handling of single value dataset."""
        detector = ZScoreDetector()
        single_data = np.array([5])
        
        detector.fit(single_data)
        assert detector.mean == 5
        assert detector.std == 0  # Std dev of single value is 0
        
        # Prediction with same value should not be outlier
        prediction = detector.predict(single_data)
        assert not prediction[0]
    
    def test_constant_dataset_handling(self):
        """Test handling of dataset with all identical values."""
        detector = ZScoreDetector()
        constant_data = np.array([5, 5, 5, 5, 5])
        
        detector.fit(constant_data)
        assert detector.mean == 5
        assert detector.std == 0
        
        # Any prediction should not be outlier for same value
        predictions = detector.predict(np.array([5]))
        assert not predictions[0]


class TestStatisticalAnomalyDetector:
    """Test cases for comprehensive statistical anomaly detection."""
    
    def test_statistical_detector_init(self):
        """Test StatisticalAnomalyDetector initialization."""
        detector = StatisticalAnomalyDetector()
        assert detector.zscore_threshold == 3.0
        assert detector.iqr_factor == 1.5
        assert detector.methods == ['zscore', 'iqr', 'modified_zscore']
    
    def test_detect_anomalies_with_multiple_methods(self):
        """Test anomaly detection using multiple statistical methods."""
        detector = StatisticalAnomalyDetector()
        normal_data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        outlier_data = np.array([1, 2, 100, 4, 5, 6, 7, 8, 9, 10])
        
        # Normal data should have no anomalies
        normal_result = detector.detect_anomalies(normal_data)
        assert not normal_result.is_anomalous
        
        # Data with outlier should be detected
        outlier_result = detector.detect_anomalies(outlier_data)
        assert outlier_result.is_anomalous
        
        # Check result structure
        assert hasattr(outlier_result, 'zscore')
        assert hasattr(outlier_result, 'iqr')
        assert hasattr(outlier_result, 'modified_zscore')
        assert hasattr(outlier_result, 'combined_score')
    
    def test_custom_methods_configuration(self):
        """Test detector with custom methods configuration."""
        detector = StatisticalAnomalyDetector(methods=['zscore', 'iqr'])
        
        data = np.array([1, 2, 3, 4, 5, 100])
        result = detector.detect_anomalies(data)
        
        # Should only have configured methods
        assert hasattr(result, 'zscore')
        assert hasattr(result, 'iqr')
        assert not hasattr(result, 'modified_zscore')


class TestAnomalyResult:
    """Test cases for AnomalyResult data structure."""
    
    def test_anomaly_result_creation(self):
        """Test AnomalyResult creation with all fields."""
        result = AnomalyResult(
            is_anomalous=True,
            zscore={'score': 3.5, 'is_outlier': True},
            iqr={'score': 0.8, 'is_outlier': False},
            modified_zscore={'score': 2.8, 'is_outlier': True},
            combined_score=0.7
        )
        
        assert result.is_anomalous is True
        assert result.zscore['is_outlier'] is True
        assert result.iqr['is_outlier'] is False
        assert result.modified_zscore['is_outlier'] is True
        assert result.combined_score == 0.7
    
    def test_anomaly_result_str_representation(self):
        """Test string representation of AnomalyResult."""
        result = AnomalyResult(
            is_anomalous=False,
            zscore={'score': 1.2, 'is_outlier': False},
            combined_score=0.3
        )
        
        str_repr = str(result)
        assert 'AnomalyResult' in str_repr
        assert 'is_anomalous=False' in str_repr


@pytest.mark.asyncio
async def test_statistical_detector_async_interface():
    """Test that statistical detector works in async context."""
    detector = StatisticalAnomalyDetector()
    
    # Simulate async operation
    import asyncio
    async def detect_with_delay():
        await asyncio.sleep(0.01)  # Simulate async work
        data = np.array([1, 2, 3, 4, 5, 100])
        return detector.detect_anomalies(data)
    
    result = await detect_with_delay()
    assert result.is_anomalous
    assert result.combined_score > 0.5
