# backend/services/forecast_service.py
from __future__ import annotations

from typing import Any

from model_utils import (
    get_model,
    build_feature_vector_for_store,
)


class ForecastError(Exception):
    """Raised when a forecast cannot be generated for a store."""
    pass


def forecast_for_store(store_id: int) -> float:
    """
    Build features for a single store and return a numeric prediction.

    :param store_id: Unique identifier for the store to forecast.
    :return: Predicted sales value as a float.
    :raises ForecastError: If the model or features cannot be built,
                           or if the prediction fails/returns invalid data.
    """
    # 1) Load model
    try:
        model: Any = get_model()
    except Exception as exc:
        raise ForecastError(f"Failed to load model for store_id={store_id}") from exc

    # 2) Build feature vector
    try:
        X = build_feature_vector_for_store(store_id)
    except Exception as exc:
        raise ForecastError(
            f"Failed to build feature vector for store_id={store_id}"
        ) from exc

    if X is None:
        raise ForecastError(
            f"Feature vector is None for store_id={store_id}"
        )

    # 3) Run prediction
    try:
        y_pred = model.predict(X)
    except Exception as exc:
        raise ForecastError(
            f"Model prediction failed for store_id={store_id}"
        ) from exc

    # Basic shape / value validation
    if y_pred is None:
        raise ForecastError(
            f"Model returned None for store_id={store_id}"
        )

    # Most sklearn-style models return an array-like
    try:
        value = float(y_pred[0])
    except (TypeError, IndexError, ValueError) as exc:
        raise ForecastError(
            f"Unexpected prediction format ({y_pred!r}) for store_id={store_id}"
        ) from exc

    return value
