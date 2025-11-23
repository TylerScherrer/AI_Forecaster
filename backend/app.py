from flask import Flask, jsonify
from flask_cors import CORS
import os
import pandas as pd


from model_utils import (
    get_model,
    build_feature_vector_for_store,
    get_latest_features_df,      # you already had this
    get_store_list_from_features # new helper
)

# ---------------------------------------------------------
# App setup
# ---------------------------------------------------------
app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": os.getenv("CORS_ALLOW_ORIGIN", "*")
        }
    },
)

# ---------------------------------------------------------
# Paths and simple cache for store list
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
IOWA_CSV_PATH = os.path.join(DATA_DIR, "Iowa_Liquor_Sales.csv")

_store_list_cache = None

def get_store_list():
    global _store_list_cache
    if _store_list_cache is not None:
        return _store_list_cache

    df = get_store_list_from_features()
    _store_list_cache = df
    return _store_list_cache




# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------
@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/stores")
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




@app.get("/api/forecast/<int:store_id>")
def api_forecast(store_id: int):
    """
    Return a forecast for a single store.

    Uses:
      - get_model() to load the XGBoost model
      - build_feature_vector_for_store(store_id) to build the
        single-row feature matrix from the latest features per store.
    """
    try:
        model = get_model()
        X = build_feature_vector_for_store(store_id)
        y_pred = float(model.predict(X)[0])

        return jsonify({
            "store_id": store_id,
            "prediction": y_pred,
        })
    except Exception as e:
        return jsonify({
            "store_id": store_id,
            "error": str(e),
        }), 500


# ---------------------------------------------------------
# Entry point for local dev (python app.py)
# ---------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)
