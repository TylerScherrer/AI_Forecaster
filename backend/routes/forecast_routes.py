# routes/forecast_routes.py
from flask import Blueprint, jsonify

from services.forecast_service import forecast_for_store

forecast_bp = Blueprint("forecast", __name__)


@forecast_bp.get("/forecast/<int:store_id>")
def api_forecast(store_id: int):
    """
    Return a forecast for a single store.
    """
    try:
        prediction = forecast_for_store(store_id)
        return jsonify({
            "store_id": store_id,
            "prediction": prediction,
        })
    except Exception as e:
        return jsonify({
            "store_id": store_id,
            "error": str(e),
        }), 500
