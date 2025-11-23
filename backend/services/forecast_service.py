# services/forecast_service.py
from model_utils import (
    get_model,
    build_feature_vector_for_store,
)


def forecast_for_store(store_id: int) -> float:
    """
    Build features for a single store and return a numeric prediction.
    """
    model = get_model()
    X = build_feature_vector_for_store(store_id)
    y_pred = float(model.predict(X)[0])
    return y_pred
