# backend/services/store_service.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

import pandas as pd

from model_utils import (
    get_latest_features_df,
    get_history_df,
    get_model_config,
)
from store_lookup import get_store_name


class StoreServiceError(Exception):
    """Raised when the store list cannot be built."""
    pass


def _build_store_label(store_id: int, store_name: Optional[str]) -> str:
    if store_name:
        return f"{store_id} - {store_name}"
    return str(store_id)


def _get_stores_with_full_history(
    history_df: pd.DataFrame,
    cfg: Dict[str, Any],
) -> Set[int]:
    """
    Return store_ids that have data for the *last* date in the history table.
    If your dataset ends at 2024-08-01, only stores that have that month
    will be included.
    """
    date_col = cfg["date_col"]      # e.g. "MonthStart"
    store_col = cfg["store_col"]    # e.g. "Store Number"

    if date_col not in history_df.columns or store_col not in history_df.columns:
        raise StoreServiceError(
            f"History DataFrame must contain '{date_col}' and '{store_col}' columns."
        )

    max_date = history_df[date_col].max()   # <- should be 2024-08-01
    latest_rows = history_df[history_df[date_col] == max_date]

    if latest_rows.empty:
        raise StoreServiceError(f"No rows found in history for max date {max_date!r}.")

    store_ids = latest_rows[store_col].dropna().unique()
    return {int(sid) for sid in store_ids}


def get_store_list(
    *,
    features_df: Optional[pd.DataFrame] = None,
) -> List[Dict[str, Any]]:
    """
    Only returns stores that have history up through the latest month
    in the dataset (e.g., August 2024).
    """
    # 1) Load features
    try:
        df: pd.DataFrame = features_df if features_df is not None else get_latest_features_df()
    except Exception as exc:
        raise StoreServiceError("Failed to load latest features DataFrame.") from exc

    if "Store Number" not in df.columns:
        raise StoreServiceError("Missing column 'Store Number' in features DataFrame.")


    # 2) Figure out which stores have full history up to the last month
    try:
        history_df = get_history_df()
        cfg = get_model_config()
        full_history_store_ids = _get_stores_with_full_history(history_df, cfg)
    except Exception as exc:
        raise StoreServiceError(
            "Failed to compute set of stores with full history."
        ) from exc

    # 3) Build filtered store list
    stores: List[Dict[str, Any]] = []
    seen: Set[int] = set()

    for _, row in df.iterrows():
        try:
            store_id_raw = row["Store Number"]
            store_id = int(store_id_raw)
        except (TypeError, ValueError, KeyError):
            continue

        if store_id in seen:
            continue

        # Skip stores not in the history final month
        if store_id not in full_history_store_ids:
            continue

        seen.add(store_id)

        try:
            store_name = get_store_name(store_id)
        except Exception:
            store_name = None

        stores.append({"value": store_id, "label": _build_store_label(store_id, store_name)})

    stores.sort(key=lambda s: int(s["value"]))
    return stores
