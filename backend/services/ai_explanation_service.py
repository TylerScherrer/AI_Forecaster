# backend/services/ai_explanation_service.py
from __future__ import annotations

from typing import Any, Dict, Optional

from services.forecast_service import forecast_for_store
from services.analytics_service import build_forecast_context
from services.llm_service import explain_forecast


# --------
# Domain-level exceptions
# --------

class StoreNotFoundError(Exception):
    """Raised when we cannot build a forecast for a given store_id."""
    pass


class ForecastComputationError(Exception):
    """Raised when the numeric forecast cannot be computed."""
    pass


class ExplanationGenerationError(Exception):
    """Raised when the LLM explanation cannot be generated."""
    pass


# --------
# Use case / application service
# --------

def generate_forecast_explanation(
    store_id: int,
    prediction_override: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Orchestrate the full 'explain forecast' use case:

    1) Compute or use the given prediction.
    2) Build analytics context (history, stats, category mix, etc.).
    3) Ask the LLM to generate a manager-friendly explanation.

    Returns a dict ready to jsonify in the route.
    """
    # 1) Get numeric forecast
    try:
        if prediction_override is None:
            prediction: float = float(forecast_for_store(store_id))
        else:
            prediction = float(prediction_override)
    except KeyError as exc:
        # e.g. store_id not present in features
        raise StoreNotFoundError(f"Store {store_id} was not found") from exc
    except Exception as exc:
        raise ForecastComputationError(
            f"Failed to compute forecast for store {store_id}"
        ) from exc

    # 2) Build analytics context
    try:
        context: Dict[str, Any] = build_forecast_context(store_id, prediction)
    except Exception as exc:
        # keep this generic for now; you could add an AnalyticsError later
        raise ForecastComputationError(
            f"Failed to build analytics context for store {store_id}"
        ) from exc

    # 3) Generate LLM explanation
    try:
        explanation: str = explain_forecast(context)
    except Exception as exc:
        raise ExplanationGenerationError(
            f"Failed to generate explanation for store {store_id}"
        ) from exc

    return {
        "store_id": store_id,
        "prediction": prediction,
        "context": context,
        "explanation": explanation,
    }
