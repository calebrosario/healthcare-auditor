# tests/test_ml_models.py
import pytest
import numpy as np
import sys

sys.path.insert(0, "/Users/calebrosario/Documents/sandbox/healthcare-auditor/.worktrees/fraud-detection-ml/backend")

from app.core.ml_models import MLModelEngine, RandomForestModel, IsolationForestModel


@pytest.mark.asyncio
async def test_random_forest_prediction():
    model = RandomForestModel()
    X_train = np.array([[100, 1], [150, 2], [200, 3]])
    y_train = np.array([0, 0, 1])
    await model.fit(X_train, y_train)
    prediction = await model.predict(np.array([[250, 4]]))
    assert prediction["fraud_probability"] > 0.5


@pytest.mark.asyncio
async def test_isolation_forest_anomaly():
    model = IsolationForestModel()
    X = np.array([[100, 1], [150, 2], [200, 3], [10000, 1]])
    await model.fit(X)
    anomaly = await model.predict(np.array([[10000, 1]]))
    assert anomaly["is_anomaly"] == True
