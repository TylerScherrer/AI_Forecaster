from flask import Flask, jsonify
from flask_cors import CORS
import os
import pandas as pd

from model_utils import (
    get_model,
    build_feature_vector_for_store,
    get_latest_features_df,
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


def get_store_list() -> pd.DataFrame:
    """
    Build and cache the store list as a DataFrame with:
      - store_id
      - store_name

    Steps:
    1) Read Store Number + Store Name from the raw CSV.
    2) Drop duplicates.
    3) Filter to stores that actually have a latest feature row
       in features_latest_per_store_v3.pkl.
    """

    global _store_list_cache
    if _store_list_cache is not None:
        return _store_list_cache

    # 1) Load base store info from CSV
    df = pd.read_csv(
        IOWA_CSV_PATH,
        usecols=["Store Number", "Store Name"],
    ).dropna()

    df = df.drop_duplicates(subset="Store Number")

    df = df.rename(
        columns={
            "Store Number": "store_id",
            "Store Name": "store_name",
        }
    )

    # 2) Only keep stores that have a feature row
    latest_df = get_latest_features_df()
    valid_ids = set(latest_df["Store Number"].unique())
    df = df[df["store_id"].isin(valid_ids)]

    # 3) Sort for nicer UI ordering
    df = df.sort_values("store_name").reset_index(drop=True)

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
    """
    Return all available stores as:
      { value: store_id, label: store_name }
    """
    try:
        df = get_store_list()
        stores = [
            {"value": int(row["store_id"]), "label": row["store_name"]}
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
