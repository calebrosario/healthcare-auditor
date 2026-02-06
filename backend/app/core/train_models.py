scripts / train_models.py
#!/usr/bin/env python3
"""
ML model training script for healthcare fraud detection.

Usage:
    python scripts/train_models.py --bootstrap
    python scripts/train_models.py --retrain --data-path /path/to/training.csv
"""
import asyncio
import argparse
import logging
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from backend.app.core.ml_models import RandomForestModel, IsolationForestModel


async def load_training_data(db, limit: int = 10000) -> pd.DataFrame:
    """
    Load labeled training data from PostgreSQL.

    Args:
        db: Async database session
        limit: Maximum number of records to load

    Returns:
        DataFrame with features and labels
    """
    from sqlalchemy import select, text

    query = text("""
        SELECT
            b.billed_amount,
            b.provider_id,
            b.insurer_id,
            b.procedure_code,
            b.status,
            b.fraud_score,
            COUNT(*) OVER (PARTITION BY b.provider_id) AS provider_claim_count,
            AVG(b.billed_amount) OVER (PARTITION BY b.provider_id) AS provider_avg_amount
        FROM bills b
        WHERE b.status IN ('paid', 'rejected', 'flagged')
          AND b.fraud_score IS NOT NULL
        LIMIT :limit
    """)

    result = await db.execute(query, {"limit": limit})
    rows = result.fetchall()

    df = pd.DataFrame([dict(row) for row in rows])

    df["label"] = (df["fraud_score"] > 0.5).astype(int)

    logger.info(f"Loaded {len(df)} training samples")
    logger.info(
        f"Fraud samples: {df['label'].sum()}, Legitimate: {len(df) - df['label'].sum()}"
    )

    return df


def engineer_features(df: pd.DataFrame) -> np.ndarray:
    """
    Engineer features for ML training.

    Args:
        df: Raw DataFrame

    Returns:
        Feature matrix
    """
    features = pd.DataFrame()

    features["billed_amount"] = df["billed_amount"]
    features["amount_zscore"] = (df["billed_amount"] - df["billed_amount"].mean()) / df[
        "billed_amount"
    ].std()

    features["provider_claim_count"] = df["provider_claim_count"]
    features["provider_avg_ratio"] = df["billed_amount"] / df["provider_avg_amount"]

    return features.fillna(0).values


async def train_models(
    db, bootstrap: bool = False, output_dir: str = "/tmp/ml_models"
) -> Dict[str, Any]:
    """
    Train ML models and save to disk.

    Args:
        db: Async database session
        bootstrap: Create synthetic data if no training data available
        output_dir: Directory to save models

    Returns:
        Training statistics
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if bootstrap:
        logger.info("Bootstrap mode: Generating synthetic training data")
        df = pd.DataFrame(
            {
                "billed_amount": np.random.normal(150, 50, 1000),
                "provider_id": np.random.randint(1, 100, 1000),
                "insurer_id": np.random.randint(1, 10, 1000),
                "procedure_code": np.random.choice(["99213", "99214", "99215"], 1000),
                "status": np.random.choice(["paid"] * 950 + ["rejected"] * 50),
                "fraud_score": [0.1] * 950 + [0.9] * 50,
                "provider_claim_count": np.random.randint(1, 100, 1000),
                "provider_avg_amount": np.random.normal(150, 30, 1000),
            }
        )
    else:
        df = await load_training_data(db)
        if df.empty:
            logger.warning("No training data found, using bootstrap mode")
            return await train_models(db, bootstrap=True, output_dir=output_dir)

    X = engineer_features(df)
    y = df["label"].values

    logger.info("Training Random Forest model...")
    rf_model = RandomForestModel()
    await rf_model.fit(X, y)

    rf_path = output_path / "random_forest_model.joblib"
    rf_model.save_model(str(rf_path))
    logger.info(f"Random Forest model saved to {rf_path}")

    logger.info("Training Isolation Forest model...")
    iso_model = IsolationForestModel(contamination=0.1)
    await iso_model.fit(X)

    iso_path = output_path / "isolation_forest_model.joblib"
    iso_model.save_model(str(iso_path))
    logger.info(f"Isolation Forest model saved to {iso_path}")

    metadata = {
        "trained_at": datetime.utcnow().isoformat(),
        "model_version": "1.0",
        "n_samples": len(df),
        "n_features": X.shape[1],
        "n_fraud": int(y.sum()),
        "random_forest_path": str(rf_path),
        "isolation_forest_path": str(iso_path),
    }

    metadata_path = output_path / "model_metadata.json"
    import json

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Model metadata saved to {metadata_path}")

    return metadata


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Train ML models for fraud detection")
    parser.add_argument(
        "--bootstrap", action="store_true", help="Generate synthetic training data"
    )
    parser.add_argument(
        "--retrain", action="store_true", help="Retrain existing models"
    )
    parser.add_argument("--data-path", type=str, help="Path to training data CSV")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="/tmp/ml_models",
        help="Output directory for models",
    )

    args = parser.parse_args()

    from backend.app.core.database import async_sessionmaker, create_async_engine
    from backend.app.config import settings

    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as db:
        await train_models(db, bootstrap=args.bootstrap, output_dir=args.output_dir)

    await engine.dispose()
    logger.info("ML model training complete")


if __name__ == "__main__":
    asyncio.run(main())
