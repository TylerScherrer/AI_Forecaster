# backend/model_utils.py
import os
import pickle
import json
import pandas as pd
# any other imports you already had...

# --- paths -------------------------------------------------

BASE_DIR = os.path.dirname(__file__)          # .../backend
MODELS_DIR = os.path.join(BASE_DIR, "models") # .../backend/models

MODEL_PATH = os.path.join(MODELS_DIR, "xgb_all_stable_v3.pkl")
FEATURES_LATEST_PATH = os.path.join(MODELS_DIR, "features_latest_per_store_v3.pkl")
FEATURES_ALL_PATH = os.path.join(MODELS_DIR, "features_all_stable_v3.pkl")
CONFIG_PATH = os.path.join(MODELS_DIR, "model_config_v3.json")

_model_cache = None
_features_latest_cache = None
_features_all_cache = None
_model_config_cache = None


def get_model():
    global _model_cache
    if _model_cache is None:
        with open(MODEL_PATH, "rb") as f:
            _model_cache = pickle.load(f)
    return _model_cache


def get_latest_features_df():
    global _features_latest_cache
    if _features_latest_cache is None:
        _features_latest_cache = pd.read_pickle(FEATURES_LATEST_PATH)
    return _features_latest_cache


def get_all_features_df():
    global _features_all_cache
    if _features_all_cache is None:
        _features_all_cache = pd.read_pickle(FEATURES_ALL_PATH)
    return _features_all_cache


def get_model_config():
    global _model_config_cache
    if _model_config_cache is None:
        with open(CONFIG_PATH, "r") as f:
            _model_config_cache = json.load(f)
    return _model_config_cache

def get_store_list_from_features():
    """
    Build a list of stores based on the latest per-store features.

    Returns a list of dicts like:
        {
            "store_id": 1234,
            "label": "1234 - Some Store Name",  # or just "1234" if no name column
            "value": 1234
        }

    This is what /api/stores can send back to the frontend.
    """
    df = get_latest_features_df()

    if "Store Number" not in df.columns:
        # Fail loudly if the features file doesn't look like we expect
        raise KeyError("Column 'Store Number' not found in features_latest_per_store_v3.pkl")

    has_name_col = "Store Name" in df.columns

    stores = []
    # Group by store so we only emit each store once
    for store_id, group in df.groupby("Store Number"):
        # If we have a Store Name column, use it for nicer labels
        if has_name_col:
            store_name = group["Store Name"].iloc[0]
            label = f"{store_id} - {store_name}"
        else:
            label = str(store_id)

        stores.append(
            {
                "store_id": int(store_id),
                "label": label,
                "value": int(store_id),
            }
        )

    # Sort (not required, but nice for UI consistency)
    stores.sort(key=lambda s: s["store_id"])
    return stores
