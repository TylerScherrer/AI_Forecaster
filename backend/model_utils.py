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
