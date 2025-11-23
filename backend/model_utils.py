import os
import joblib
import pandas as pd

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
MODELS_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATH = os.path.join(MODELS_DIR, "xgb_all_stable_v3.pkl")
FEATURE_NAMES_PATH = os.path.join(MODELS_DIR, "features_all_stable_v3.pkl")
LATEST_FEATURES_PATH = os.path.join(MODELS_DIR, "features_latest_per_store_v3.pkl")
CONFIG_PATH = os.path.join(MODELS_DIR, "model_config_v3.json")

STORE_COL = "Store Number"

# -------------------------------------------------------------------
# In-memory caches
# -------------------------------------------------------------------
_model = None
_feature_names = None
_latest_features_df = None


def get_model():
    """Load and cache the trained XGBoost model."""
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def get_feature_names():
    """
    Load and cache the ordered list of feature names.

    In v3 we saved this directly as a Python list via joblib, so
    we just load it and return.
    """
    global _feature_names
    if _feature_names is None:
        obj = joblib.load(FEATURE_NAMES_PATH)
        # If it's a DataFrame for some reason, convert; otherwise assume list-like
        if isinstance(obj, pd.DataFrame) and obj.shape[1] == 1:
            _feature_names = obj.iloc[:, 0].tolist()
        else:
            _feature_names = list(obj)
    return _feature_names


def get_latest_features_df() -> pd.DataFrame:
    """
    Load and cache the precomputed 'latest features per store' DataFrame.

    This is the features_latest_per_store_v3.pkl file we created in the
    notebook: one row per store, with all model feature columns.
    """
    global _latest_features_df
    if _latest_features_df is None:
        _latest_features_df = pd.read_pickle(LATEST_FEATURES_PATH)
    return _latest_features_df


def build_feature_vector_for_store(store_id: int) -> pd.DataFrame:
    """
    Build the single-row feature matrix X for a given store_id.

    We:
      - look up that store in features_latest_per_store_v3.pkl
      - select columns in the exact feature order the model expects
      - return a DataFrame with shape (1, n_features)
    """
    features_df = get_latest_features_df()
    feature_names = get_feature_names()

    # Ensure store_id types match (store_id in CSV is usually int)
    row = features_df[features_df[STORE_COL] == int(store_id)]

    if row.empty:
        raise ValueError(f"No latest feature row found for store_id={store_id}")

    # Keep only the columns the model was trained on, in the right order
    X = row[feature_names].copy()
    return X

def get_store_list_from_features():
    """
    Build a store list from features_latest_per_store_v3.pkl
    and attach real store_name when we have it.
    """
    latest = get_latest_features_df()

    stores = (
        latest[["Store Number"]]
        .drop_duplicates()
        .rename(columns={"Store Number": "store_id"})
        .sort_values("store_id")
        .reset_index(drop=True)
    )

    # join with lookup to get store_name
    lookup = get_store_lookup()  # has store_id, store_name
    stores = stores.merge(lookup, on="store_id", how="left")

    # Fallback label if name missing
    stores["store_label"] = stores["store_name"].fillna(
        stores["store_id"].apply(lambda s: f"Store #{int(s)}")
    )

    return stores


DATA_DIR = os.path.join(BASE_DIR, "data")
STORE_LOOKUP_PATH = os.path.join(DATA_DIR, "store_lookup.csv")

_store_lookup_cache = None

def get_store_lookup():
    """
    Load and cache store_lookup.csv:
      columns: store_id, store_name
    """
    global _store_lookup_cache
    if _store_lookup_cache is not None:
        return _store_lookup_cache

    df = pd.read_csv(STORE_LOOKUP_PATH)
    _store_lookup_cache = df
    return _store_lookup_cache