# routes/stores_routes.py
from __future__ import annotations

from typing import Any, Dict, List

from flask import Blueprint, jsonify, Response

from services.store_service import get_store_list

stores_bp = Blueprint("stores", __name__)


@stores_bp.get("/stores")
def api_get_stores() -> Response:
    """
    Return the list of stores available for forecasting.

    Response (200):
    {
      "stores": [
        { "value": 2327, "label": "Store 2327 - Milwaukee" },
        ...
      ]
    }

    On error, returns a 500 with a JSON error payload.
    """
    try:
        stores: Any = get_store_list()

        # Normalize / validate shape defensively (Single Responsibility: route handles HTTP + shape).
        if not isinstance(stores, list):
            raise TypeError(
                f"get_store_list() must return a list, got {type(stores).__name__}"
            )

        # Optionally enforce each item having value/label, but keep it light:
        normalized: List[Dict[str, Any]] = []
        for s in stores:
            # If store_service already returns correct dicts, this just passes them through.
            if isinstance(s, dict) and "value" in s and "label" in s:
                normalized.append(
                    {
                        "value": int(s["value"]),
                        "label": str(s["label"]),
                    }
                )
            else:
                # Fall back to something safe; this also helps catch mistakes early.
                raise ValueError(
                    "Each store must be a dict with 'value' and 'label' keys."
                )

        return jsonify({"stores": normalized})

    except Exception as exc:
        # Last-resort handler – log for debugging, return generic 500 to client.
        import traceback

        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Unexpected server error in /stores.",
                    "details": str(exc),
                }
            ),
            500,
        )
