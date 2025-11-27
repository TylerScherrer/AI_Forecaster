# backend/routes/ai_routes.py
from flask import Blueprint, request, jsonify

from services.forecast_service import forecast_for_store
from services.analytics_service import build_forecast_context
from services.llm_service import explain_forecast

ai_bp = Blueprint("ai", __name__)


@ai_bp.post("/explain_forecast")
def api_explain_forecast():
    """
    Request JSON:
    {
      "store_id": 2327,
      "prediction": 5723.03   # optional; if missing, we compute it
    }
    """
    data = request.get_json(silent=True) or {}
    store_id = data.get("store_id")
    prediction = data.get("prediction")

    if store_id is None:
        return jsonify({"error": "store_id is required"}), 400

    try:
        store_id = int(store_id)

        # Use prediction from body if provided, otherwise compute it
        if prediction is None:
            prediction = forecast_for_store(store_id)
        else:
            prediction = float(prediction)

        # Build stats / history context
        ctx = build_forecast_context(store_id, prediction)

        # Generate explanation text
        explanation = explain_forecast(ctx)

        return jsonify(
            {
                "store_id": store_id,
                "prediction": prediction,
                "context": ctx,
                "explanation": explanation,
            }
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"server error in /explain_forecast: {e}"}), 500
