# backend/routes/forecast_routes.py
from __future__ import annotations

from typing import Any, Dict, Tuple
from datetime import datetime

from flask import Blueprint, jsonify, Response

from services.forecast_service import forecast_for_store, ForecastError
from services.analytics_service import build_forecast_context

forecast_bp = Blueprint("forecast", __name__)


def _next_month_label(last_date_str: str) -> str:
    """
    Given an ISO-ish date string like '2024-08-01', return '2024-09'.
    """
    if not last_date_str:
        return "Next"

    # we only care about year + month, so slice then parse
    try:
        dt = datetime.fromisoformat(str(last_date_str)[:10])
    except Exception:
        return "Next"

    year = dt.year
    month = dt.month

    if month == 12:
        return f"{year + 1}-01"
    else:
        return f"{year}-{month + 1:02d}"


@forecast_bp.get("/forecast/<int:store_id>")
def api_forecast(store_id: int) -> Tuple[Response, int]:
    try:
        prediction: float = float(forecast_for_store(store_id))

        context: Dict[str, Any] = build_forecast_context(
            store_id=store_id,
            prediction=prediction,
            history_months=12,
        )

        history = context.get("history", []) or []
        stats = context.get("stats", {}) or {}

        # last history date -> next month label (e.g. '2024-09')
        if history:
            last_date_str = history[-1].get("date")
            next_period_label = _next_month_label(last_date_str)
        else:
            next_period_label = "Next"

        payload: Dict[str, Any] = {
            "store_id": store_id,
            "prediction": prediction,
            "history": history,
            "stats": stats,
            "next_period_label": next_period_label,  # ⭐ NEW
        }

        return jsonify(payload), 200

    except ForecastError as exc:
        return jsonify({"store_id": store_id, "error": str(exc)}), 500

    except KeyError:
        return jsonify({"error": f"Store {store_id} was not found."}), 404

    except Exception as exc:
        import traceback

        traceback.print_exc()
        return (
            jsonify(
                {
                    "store_id": store_id,
                    "error": "Unexpected server error in /forecast.",
                    "details": str(exc),
                }
            ),
            500,
        )
