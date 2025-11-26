# routes/stores_routes.py
from flask import Blueprint, jsonify

from services.store_service import get_store_list

stores_bp = Blueprint("stores", __name__)


@stores_bp.get("/stores")
def api_get_stores():
    try:
        # Now returns a plain Python list from store_service
        stores = get_store_list()

        # If your store_service already returns [{"value": ..., "label": ...}, ...]
        # you can just return it as-is:
        return jsonify({"stores": stores})

        # If you ever need to force shape, you could do:
        # normalized = [
        #     {"value": int(s["value"]), "label": str(s["label"])}
        #     for s in stores
        # ]
        # return jsonify({"stores": normalized})

    except Exception as e:
        return jsonify({"error": str(e)}), 500