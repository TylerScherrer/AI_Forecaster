# backend/services/analytics_service.py
from typing import Dict, Any, List, Optional
import pandas as pd

from model_utils import get_history_df, get_model_config


def _safe_mean(series: pd.Series) -> Optional[float]:
    return float(series.mean()) if len(series) > 0 else None


def _compute_trend_direction(last_actual: Optional[float],
                             avg_6: Optional[float]) -> str:
    if last_actual is None or avg_6 is None or avg_6 == 0:
        return "unknown"

    diff = last_actual - avg_6
    pct = diff / avg_6

    if pct > 0.15:
        return "strong_up"
    elif pct > 0.05:
        return "slight_up"
    elif pct < -0.15:
        return "strong_down"
    elif pct < -0.05:
        return "slight_down"
    else:
        return "flat"


def _compute_volatility(recent: pd.DataFrame, target_col: str) -> Optional[str]:
    if len(recent) <= 1:
        return None

    std = float(recent[target_col].std())
    mean = float(recent[target_col].mean())
    if mean <= 0:
        return None

    ratio = std / mean
    if ratio > 0.35:
        return "high"
    elif ratio > 0.20:
        return "medium"
    else:
        return "low"


def build_forecast_context(
    store_id: int,
    prediction: float,
    history_months: int = 12,
    *,
    history_df: Optional[pd.DataFrame] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a compact context object for a store's forecast using the
    full monthly history table (one row per store + month).

    Dependencies (history + config) can be provided explicitly to improve
    testability and reduce coupling, but default to model_utils helpers.
    """

    # -------------------------
    # Dependencies (DIP-friendly)
    # -------------------------
    cfg = config or get_model_config()
    df = history_df if history_df is not None else get_history_df()

    target_col = cfg["target_col"]   # e.g. "Sale (Dollars)"
    date_col   = cfg["date_col"]     # e.g. "MonthStart"
    store_col  = cfg["store_col"]    # e.g. "Store Number"

    # -------------------------
    # Store filtering
    # -------------------------
    df_store = df[df[store_col] == store_id].copy().sort_values(date_col)

    if df_store.empty:
        return {
            "store_id": store_id,
            "prediction": prediction,
            "history": [],
            "stats": {
                "months_active": 0,
                "last_actual": None,
                "avg_last_3": None,
                "avg_last_6": None,
                "avg_last_12": None,
                "trend_direction": "unknown",
                "volatility": None,
                "forecast_vs_6": None,
                "yoy_growth_12v12": None,
                "is_limited_history": True,
            },
        }

    # -------------------------
    # Recent window & history list
    # -------------------------
    recent = df_store.tail(history_months)

    history: List[Dict[str, Any]] = []
    for _, row in recent.iterrows():
        dt = row[date_col]
        date_str = dt.isoformat() if hasattr(dt, "isoformat") else str(dt)
        history.append(
            {"date": date_str, "sales": float(row[target_col])}
        )

    # -------------------------
    # Averages & last actual
    # -------------------------
    last_3  = recent.tail(3)[target_col]
    last_6  = recent.tail(6)[target_col]
    last_12 = recent.tail(12)[target_col]

    avg_3  = _safe_mean(last_3)
    avg_6  = _safe_mean(last_6)
    avg_12 = _safe_mean(last_12)

    last_actual: Optional[float] = (
        float(recent[target_col].iloc[-1]) if len(recent) > 0 else None
    )

    # -------------------------
    # Forecast vs 6-month average
    # -------------------------
    forecast_vs_6: Optional[float] = None
    try:
        pred_val = float(prediction)
        if avg_6 and avg_6 > 0:
            forecast_vs_6 = (pred_val - avg_6) / avg_6
    except Exception:
        # If prediction can't be cast or avg_6 is weird, just leave None
        forecast_vs_6 = None

    # -------------------------
    # Trend & volatility
    # -------------------------
    trend = _compute_trend_direction(last_actual, avg_6)
    volatility = _compute_volatility(recent, target_col)

    # -------------------------
    # YoY growth (last 12 vs previous 12)
    # -------------------------
    months_active = len(df_store)
    yoy_growth: Optional[float] = None

    if months_active >= 24:
        last12 = df_store.tail(12)[target_col].sum()
        prev12 = df_store.iloc[-24:-12][target_col].sum()
        if prev12 > 0:
            yoy_growth = (last12 - prev12) / prev12

    is_limited_history = months_active < 6

    # -------------------------
    # Final context
    # -------------------------
    return {
        "store_id": store_id,
        "prediction": prediction,
        "history": history,
        "stats": {
            "months_active": months_active,
            "last_actual": last_actual,
            "avg_last_3": avg_3,
            "avg_last_6": avg_6,
            "avg_last_12": avg_12,
            "trend_direction": trend,
            "volatility": volatility,
            "forecast_vs_6": forecast_vs_6,
            "yoy_growth_12v12": yoy_growth,
            "is_limited_history": is_limited_history,
        },
    }
