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
HISTORY_PATH = os.path.join(MODELS_DIR, "store_month_history_v1.pkl")

_model_cache = None
_features_latest_cache = None
_features_all_cache = None
_model_config_cache = None

STORE_METADATA_PATH = os.path.join(MODELS_DIR, "store_metadata.json")
_store_metadata_cache = None

def get_store_metadata():
    global _store_metadata_cache
    if _store_metadata_cache is None:
        try:
            with open(STORE_METADATA_PATH, "r") as f:
                _store_metadata_cache = json.load(f)
        except FileNotFoundError:
            _store_metadata_cache = {}
    return _store_metadata_cache


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
            "label": "Some Store Name (#1234)" or "Store #1234",
            "value": 1234
        }
    """
    df = get_latest_features_df()

    if "Store Number" not in df.columns:
        raise KeyError("Column 'Store Number' not found in features_latest_per_store_v3.pkl")

    # Try to find any reasonable store-name column in the features dataframe
    possible_name_cols = [
        "Store Name",
        "store_name",
        "Store_Name",
        "STORE_NAME",
    ]
    name_col = None
    for cand in possible_name_cols:
        if cand in df.columns:
            name_col = cand
            break

    stores = []

    # Group by store number so we only emit each store once
    for store_id, group in df.groupby("Store Number"):
        sid = int(store_id)

        if name_col is not None:
            store_name = str(group[name_col].iloc[0])
            label = f"{store_name} (#${sid})".replace("#$", "#")  # little safety hack
        else:
            label = f"Store #{sid}"

        stores.append(
            {
                "store_id": sid,
                "label": label,
                "value": sid,
            }
        )

    stores.sort(key=lambda s: s["store_id"])
    return stores


def build_feature_vector_for_store(store_id: int):
    """
    Given a store_id, build a single-row feature DataFrame for the model.

    Returns:
        X : pandas.DataFrame with shape (1, n_features)
    """
    # Use the "latest per store" features table
    df = get_latest_features_df()

    if "Store Number" not in df.columns:
        raise KeyError("Column 'Store Number' not found in latest features dataframe")

    row = df[df["Store Number"] == store_id]

    if row.empty:
        raise ValueError(f"No feature row found for store_id={store_id}")

    # Figure out which columns are features
    config = get_model_config()

    # Try to read an explicit list of feature columns from config, if present
    feature_cols = (
        config.get("feature_columns")
        or config.get("X_columns")
        or None
    )

    if feature_cols is None:
        # Fallback: use all numeric columns except obvious ID / target / date columns
        exclude_cols = {
            "Store Number",
            "Store Name",
            "Sale (Dollars)",
            "MonthStart",
        }
        feature_cols = [
            c for c in row.columns
            if c not in exclude_cols and pd.api.types.is_numeric_dtype(row[c])
        ]

    # Ensure the columns exist
    missing = [c for c in feature_cols if c not in row.columns]
    if missing:
        raise KeyError(f"Feature columns missing from dataframe: {missing}")

    # Slice to just feature columns; keep as DataFrame with 1 row
    X = row[feature_cols].astype(float)

    return X

# Cached store–month history dataframe
_history_df_cache = None

def get_history_df() -> pd.DataFrame:
    """
    Load the full store-month history table.

    Supports either:
      - InvoiceMonth
      - MonthStart

    Normalizes whichever exists into the config's date_col.
    """
    global _history_df_cache
    if _history_df_cache is None:
        df = pd.read_pickle(HISTORY_PATH)

        cfg = get_model_config()
        desired_date_col = cfg.get("date_col", "MonthStart")
        store_col = cfg.get("store_col", "Store Number")

        # Detect available date column in the history pickle
        if desired_date_col not in df.columns:
            # Fallback candidates
            candidates = ["InvoiceMonth", "MonthStart"]
            found = next((c for c in candidates if c in df.columns), None)
            if found is None:
                raise KeyError(
                    f"History file missing date column. Expected '{desired_date_col}' "
                    f"or one of {candidates}. Found columns: {list(df.columns)}"
                )
            # Use the found column as the working date column
            working_date_col = found
        else:
            working_date_col = desired_date_col

        # Normalize to monthly timestamp (YYYY-MM-01)
        df[working_date_col] = pd.to_datetime(df[working_date_col]).dt.to_period("M").dt.to_timestamp()

        # If config expects a different name, copy into that name
        if working_date_col != desired_date_col:
            df[desired_date_col] = df[working_date_col]

        df[store_col] = df[store_col].astype(int)

        _history_df_cache = df

    return _history_df_cache

