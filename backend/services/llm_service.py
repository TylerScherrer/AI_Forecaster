# backend/services/llm_service.py
from __future__ import annotations

from typing import Dict, Any, List, Optional


class ExplanationError(Exception):
    """Raised when a forecast explanation cannot be generated from the given context."""
    pass


def explain_forecast(context: Dict[str, Any]) -> str:
    """
    Create a clear, manager-friendly explanation using numeric context.

    Sections:
    - Summary (with data range)
    - Key numbers (including recent months if available)
    - Suggested actions

    :param context: Dictionary with keys like:
        - "store_id": int
        - "prediction": float
        - "stats": dict with numeric summary fields
        - "history": list of {"date": str, "sales": float}
    :return: Multi-line explanation string.
    :raises ExplanationError: If required fields are missing or invalid.
    """
    # --------- Basic validation ----------
    store_id: Optional[int] = context.get("store_id")
    prediction: Any = context.get("prediction")

    if store_id is None:
        raise ExplanationError("Missing required field 'store_id' in context.")

    if prediction is None:
        raise ExplanationError(
            f"Missing required field 'prediction' in context for store_id={store_id}."
        )

    stats: Dict[str, Any] = context.get("stats", {}) or {}
    history_raw: Any = context.get("history", []) or []

    # Ensure history is a list for downstream logic
    history: List[Dict[str, Any]]
    if isinstance(history_raw, list):
        history = [row for row in history_raw if isinstance(row, dict)]
    else:
        # If it's something weird, treat as no history rather than exploding
        history = []

    last_actual: Optional[float] = stats.get("last_actual")
    avg_3: Optional[float] = stats.get("avg_last_3")
    avg_6: Optional[float] = stats.get("avg_last_6")
    avg_12: Optional[float] = stats.get("avg_last_12")
    trend: Optional[str] = stats.get("trend_direction")
    volatility: Optional[str] = stats.get("volatility")

    # Helper to format dollars safely
    def fmt(value: Any) -> str:
        if value is None:
            return "N/A"
        try:
            return f"${float(value):,.2f}"
        except (TypeError, ValueError):
            return str(value)

    # Helper to get a nice date label (YYYY-MM)
    def fmt_date(raw_date: Any) -> str:
        if not raw_date:
            return "N/A"
        try:
            s = str(raw_date)
        except Exception:
            return "N/A"
        # take just YYYY-MM if it's an ISO-like string
        return s[:7]

    lines: List[str] = []

    # =========================
    # 1) SUMMARY
    # =========================
    neg_forecast = False

    try:
        numeric_prediction: Optional[float] = float(prediction)  # may raise
    except (TypeError, ValueError):
        numeric_prediction = None

    if numeric_prediction is None:
        lines.append(
            f"For store {store_id}, a forecast is available, but the exact value "
            "could not be interpreted as a number."
        )
    else:
        if numeric_prediction < 0:
            neg_forecast = True
            lines.append(
                (
                    f"For store {store_id}, the model produced a negative forecast "
                    f"({fmt(numeric_prediction)}). In practice, this means the model "
                    "expects very low sales and is uncertain. Treat this as roughly "
                    "$0 in sales."
                )
            )
        else:
            lines.append(
                f"For store {store_id}, the forecast for the next period is "
                f"{fmt(numeric_prediction)} in sales."
            )

    # Describe how much history we actually have
    if history:
        n_months = len(history)
        start_date = fmt_date(history[0].get("date"))
        end_date = fmt_date(history[-1].get("date"))
        lines.append(
            f"The model is using {n_months} month(s) of history from "
            f"{start_date} through {end_date}."
        )
    else:
        lines.append(
            "Recent history is limited or unavailable, so it is harder to compare "
            "this forecast to past performance."
        )

    # Compare to 6-month average when possible
    if numeric_prediction is not None and avg_6 not in (None, 0):
        try:
            diff = numeric_prediction - float(avg_6)
            pct = diff / float(avg_6)
        except (TypeError, ValueError, ZeroDivisionError):
            pct = None

        if pct is not None:
            if pct > 0.20:
                lines.append("This is much higher than the store's recent 6-month average.")
            elif pct > 0.05:
                lines.append("This is slightly higher than the store's recent 6-month average.")
            elif pct < -0.20:
                lines.append("This is much lower than the store's recent 6-month average.")
            elif pct < -0.05:
                lines.append("This is slightly lower than the store's recent 6-month average.")
            else:
                lines.append(
                    "This is roughly in line with what the store has done over the last 6 months."
                )
    elif last_actual is not None and numeric_prediction is not None:
        try:
            diff = numeric_prediction - float(last_actual)
            pct = diff / float(last_actual) if float(last_actual) != 0 else None
        except (TypeError, ValueError, ZeroDivisionError):
            pct = None

        if pct is not None:
            if abs(pct) < 0.05:
                lines.append("This forecast is very close to last month's sales.")
            elif pct > 0:
                lines.append("This forecast is higher than last month's sales.")
            else:
                lines.append("This forecast is lower than last month's sales.")

    # Trend descriptor
    if trend and trend != "unknown":
        pretty_trend = trend.replace("_", " ")
        lines.append(f"Overall, the recent trend for this store looks {pretty_trend}.")
    elif trend == "unknown" and history:
        lines.append("There is no strong upward or downward trend in the recent data.")

    # Volatility descriptor
    if volatility:
        lines.append(f"Sales volatility for this store looks {volatility}.")

    # =========================
    # 2) KEY NUMBERS
    # =========================
    lines.append("")
    lines.append("Key numbers:")
    if last_actual is not None:
        lines.append(f"- Last actual month: {fmt(last_actual)}")
    if avg_3 is not None:
        lines.append(f"- Average of last 3 months: {fmt(avg_3)}")
    if avg_6 is not None:
        lines.append(f"- Average of last 6 months: {fmt(avg_6)}")
    if avg_12 is not None:
        lines.append(f"- Average of last 12 months: {fmt(avg_12)}")
    if numeric_prediction is not None:
        lines.append(f"- Forecast for next period: {fmt(numeric_prediction)}")

    # If we have history, show the last few months explicitly
    if history:
        lines.append("")
        lines.append("Recent months:")
        # show up to last 6 months
        for row in history[-6:]:
            d = fmt_date(row.get("date"))
            s = fmt(row.get("sales"))
            lines.append(f"- {d}: {s}")

    # =========================
    # 3) SUGGESTED ACTIONS
    # =========================
    lines.append("")
    lines.append("Suggested actions:")

    if numeric_prediction is None:
        lines.append(
            "- Because the numeric forecast could not be interpreted, rely more on "
            "recent history and local knowledge when planning orders."
        )
    elif neg_forecast:
        lines.append(
            "- Treat this as a near-zero month and investigate why sales might be so weak."
        )
    else:
        if avg_6 not in (None, 0):
            try:
                avg_6_val = float(avg_6)
                if numeric_prediction > avg_6_val * 1.1:
                    lines.append(
                        "- Ensure you have enough inventory to support the higher-than-usual forecast."
                    )
                elif numeric_prediction < avg_6_val * 0.9:
                    lines.append(
                        "- Consider tightening orders if this lower forecast matches what you see locally."
                    )
                else:
                    lines.append(
                        "- Use this forecast as a baseline and adjust for any known events or promotions."
                    )
            except (TypeError, ValueError):
                lines.append(
                    "- Use this forecast together with recent history and your local knowledge."
                )
        elif last_actual is not None:
            lines.append(
                "- Compare this forecast directly to last month's sales to set expectations."
            )

    if volatility == "high":
        lines.append(
            "- Because this store is volatile, avoid over-reacting to a single month's forecast."
        )
    elif volatility == "medium":
        lines.append(
            "- Expect some month-to-month noise when comparing actuals to this forecast."
        )
    else:
        lines.append(
            "- Track actuals against this forecast to see if the store is stabilizing or shifting."
        )

    lines.append(
        "- Cross-check this forecast with any upcoming promotions, holidays, or local events."
    )

    return "\n".join(lines)
