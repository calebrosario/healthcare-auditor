"""
Machine learning models for fraud detection.
"""
import logging
import numpy as np
import joblib
from pathlib import Path
from typing import List, Dict, Any, Optional
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import NotFittedError

logger = logging.getLogger(__name__)


class RandomForestModel:
    """Random Forest classifier for supervised fraud detection."""

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize Random Forest model.

        Args:
            model_path: Path to saved model (for loading)
        """
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path
        self.is_trained = False

        if model_path and Path(model_path).exists():
            self.load_model(model_path)

    async def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train Random Forest model.

        Args:
            X: Feature matrix
            y: Target labels (0=legitimate, 1=fraud)
        """
        X_scaled = self.scaler.fit_transform(X)
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_scaled, y)
        self.is_trained = True
        logger.info(f"RandomForestModel trained on {len(X)} samples")

    async def predict(self, X: np.ndarray) -> Dict[str, Any]:
        """
        Predict fraud probability.

        Args:
            X: Feature matrix

        Returns:
            Dictionary with fraud_probability and prediction
        """
        if not self.is_trained or self.model is None:
            logger.warning("RandomForestModel not trained, returning neutral")
            return {'fraud_probability': 0.5, 'prediction': 0}

        X_scaled = self.scaler.transform(X)
        proba = self.model.predict_proba(X_scaled)
        prediction = self.model.predict(X_scaled)

        return {
            'fraud_probability': float(proba[0][1]),
            'prediction': int(prediction[0])
        }

    async def partial_fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Incremental training (requires warm_start)."""
        if not self.is_trained:
            await self.fit(X, y)
        else:
            X_scaled = self.scaler.transform(X)
            self.model.fit(X_scaled, y)
            logger.info("RandomForestModel incrementally updated")

    def save_model(self, path: str) -> None:
        """Save model to disk."""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")

        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, path)
        logger.info(f"RandomForestModel saved to {path}")

    def load_model(self, path: str) -> None:
        import os
        import hashlib
        from pathlib import Path

        model_path = Path(path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        data = joblib.load(path)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid model file format: expected dict, got {type(data)}")

        if 'model' not in data or 'scaler' not in data:
            raise ValueError("Invalid model file: missing 'model' or 'scaler' keys")

        self.model = data['model']
        self.scaler = data['scaler']
        self.is_trained = True
        logger.info(f"RandomForestModel loaded from {path}")


class IsolationForestModel:
    """Isolation Forest for unsupervised anomaly detection."""

    def __init__(self, contamination: float = 0.1, model_path: Optional[str] = None):
        """
        Initialize Isolation Forest model.

        Args:
            contamination: Expected proportion of outliers
            model_path: Path to saved model
        """
        self.model = None
        self.contamination = contamination
        self.model_path = model_path
        self.is_trained = False

        if model_path and Path(model_path).exists():
            self.load_model(model_path)

    async def fit(self, X: np.ndarray) -> None:
        """
        Train Isolation Forest model.

        Args:
            X: Feature matrix
        """
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X)
        self.is_trained = True
        logger.info(f"IsolationForestModel trained on {len(X)} samples")

    async def predict(self, X: np.ndarray) -> Dict[str, Any]:
        """
        Predict if sample is anomaly.

        Args:
            X: Feature matrix

        Returns:
            Dictionary with is_anomaly and anomaly_score
        """
        if not self.is_trained or self.model is None:
            logger.warning("IsolationForestModel not trained, returning neutral")
            return {'is_anomaly': False, 'anomaly_score': 0.5}

        prediction = self.model.predict(X)
        score = self.model.score_samples(X)

        is_anomaly = prediction[0] == -1
        anomaly_score = min(-score, 1.0) if score < 0 else 0.0

        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': float(anomaly_score[0])
        }

    def save_model(self, path: str) -> None:
        """Save model to disk."""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")

        joblib.dump(self.model, path)
        logger.info(f"IsolationForestModel saved to {path}")

    def load_model(self, path: str) -> None:
        from pathlib import Path
        from sklearn.ensemble import IsolationForest

        model_path = Path(path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        self.model = joblib.load(path)

        if not isinstance(self.model, IsolationForest):
            raise ValueError(f"Invalid model type: expected IsolationForest, got {type(self.model)}")

        self.is_trained = True
        logger.info(f"IsolationForestModel loaded from {path}")


class MLModelEngine:
    """Orchestrator for ML models."""

    def __init__(
        self,
        rf_model_path: Optional[str] = None,
        iso_model_path: Optional[str] = None
    ):
        """
        Initialize ML model engine.

        Args:
            rf_model_path: Path to Random Forest model
            iso_model_path: Path to Isolation Forest model
        """
        self.rf_model = RandomForestModel(rf_model_path)
        self.iso_model = IsolationForestModel(contamination=0.1, model_path=iso_model_path)
        self.stats = {
            'predictions_made': 0,
            'errors': 0
        }

    async def predict_fraud(
        self,
        features: np.ndarray,
        use_supervised: bool = True,
        use_unsupervised: bool = True
    ) -> Dict[str, Any]:
        """
        Generate fraud prediction using ensemble of models.

        Args:
            features: Feature matrix
            use_supervised: Use Random Forest model
            use_unsupervised: Use Isolation Forest model

        Returns:
            Dictionary with ensemble fraud score and individual model scores
        """
        scores = {}

        try:
            if use_supervised and self.rf_model.is_trained:
                rf_result = await self.rf_model.predict(features)
                scores['random_forest'] = rf_result['fraud_probability']
            else:
                scores['random_forest'] = 0.5

            if use_unsupervised and self.iso_model.is_trained:
                iso_result = await self.iso_model.predict(features)
                scores['isolation_forest'] = iso_result['anomaly_score']
            else:
                scores['isolation_forest'] = 0.0

            ensemble_score = (
                0.7 * scores['random_forest'] +
                0.3 * scores['isolation_forest']
            )

            self.stats['predictions_made'] += 1

            return {
                'fraud_probability': float(ensemble_score),
                'individual_scores': scores
            }

        except (ValueError, TypeError, KeyError, NotFittedError) as e:
            logger.error(f"MLModelEngine.predict_fraud: {type(e).__name__}: {e}")
            self.stats['errors'] += 1
            return {
                'fraud_probability': 0.5,
                'individual_scores': {'random_forest': 0.5, 'isolation_forest': 0.0}
            }
        except Exception as e:
            logger.error(f"MLModelEngine.predict_fraud: Unexpected error: {type(e).__name__}: {e}")
            self.stats['errors'] += 1
            raise

    def get_stats(self) -> Dict[str, int]:
        """Get prediction statistics."""
        return self.stats.copy()
