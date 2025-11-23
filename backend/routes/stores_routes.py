# routes/stores_routes.py
from flask import Blueprint, jsonify

from services.store_service import get_store_list

stores_bp = Blueprint("stores", __name__)


@stores_bp.get("/stores")
def api_get_stores():
    try:
        df = get_store_list()
        stores = [
            {"value": int(row["store_id"]), "label": row["store_label"]}
            for _, row in df.iterrows()
        ]
        return jsonify({"stores": stores})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
