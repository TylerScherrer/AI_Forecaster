# backend/routes/ai_routes.py
from __future__ import annotations

from typing import Any, Dict, Tuple

from flask import Blueprint, request, jsonify, Response

from services.ai_explanation_service import (
    generate_forecast_explanation,
    StoreNotFoundError,
    ForecastComputationError,
    ExplanationGenerationError,
)

ai_bp = Blueprint("ai", __name__)


@ai_bp.post("/explain_forecast")
def api_explain_forecast() -> Response:
    """
    Explain a store-level forecast in plain language.

    Request JSON:
    {
      "store_id": 2327,          # required
      "prediction": 5723.03      # optional; if missing, we compute it
    }

    Response JSON (200):
    {
      "store_id": 2327,
      "prediction": 5723.03,
      "context": { ... },
      "explanation": "..."
    }
    """
    data: Dict[str, Any] = request.get_json(silent=True) or {}

    store_id_raw: Any = data.get("store_id")
    prediction_raw: Any = data.get("prediction")

    if store_id_raw is None:
        return jsonify({"error": "store_id is required"}), 400

    # Validate store_id type up front
    try:
        store_id: int = int(store_id_raw)
    except (TypeError, ValueError):
        return jsonify({"error": "store_id must be an integer"}), 400

    # Let prediction remain optional; we only coerce to float in the use-case layer.
    prediction_override: Any = prediction_raw

    try:
        result: Dict[str, Any] = generate_forecast_explanation(
            store_id=store_id,
            prediction_override=prediction_override,
        )
        return jsonify(result)

    except StoreNotFoundError as exc:
        # Domain-level 404 when we can't build features/forecast for this store
        return jsonify({"error": str(exc)}), 404

    except ExplanationGenerationError as exc:
        # LLM / explanation-specific failures.
        # 502 is reasonable here (bad gateway / upstream error), but 500 is okay too.
        return (
            jsonify(
                {
                    "error": "Could not generate AI explanation for this forecast.",
                    "details": str(exc),
                }
            ),
            502,
        )

    except ForecastComputationError as exc:
        # Problems computing numeric forecast or analytics context.
        return (
            jsonify(
                {
                    "error": "Could not compute forecast details for this store.",
                    "details": str(exc),
                }
            ),
            500,
        )

    except Exception as exc:
        # Last-resort handler for truly unexpected errors.
        import traceback

        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Unexpected server error in /explain_forecast.",
                    "details": str(exc),
                }
            ),
            500,
        )
