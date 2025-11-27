# backend/services/llm_service.py
from typing import Dict, Any


def explain_forecast(context: Dict[str, Any]) -> str:
    """
    Create a clear, manager-friendly explanation using numeric context.
    Sections:
    - Summary (with data range)
    - Key numbers (including recent months if available)
    - Suggested actions
    """
    store_id = context.get("store_id")
    prediction = context.get("prediction")
    stats = context.get("stats", {})
    history = context.get("history", []) or []

    last_actual = stats.get("last_actual")
    avg_3 = stats.get("avg_last_3")
    avg_6 = stats.get("avg_last_6")
    avg_12 = stats.get("avg_last_12")
    trend = stats.get("trend_direction")
    volatility = stats.get("volatility")

    # Helper to format dollars safely
    def fmt(v):
        if v is None:
            return "N/A"
        try:
            return f"${float(v):,.2f}"
        except Exception:
            return str(v)

    # Helper to get a nice date label (YYYY-MM)
    def fmt_date(d: str) -> str:
        if not d:
            return "N/A"
        # take just YYYY-MM if it's an ISO string
        return d[:7]

    lines: list[str] = []

    # =========================
    # 1) SUMMARY
    # =========================
    neg_forecast = False
    if isinstance(prediction, (int, float)):
        if prediction < 0:
            neg_forecast = True
            lines.append(
                f"For store {store_id}, the model produced a negative forecast "
                f"({fmt(prediction)}). In practice, this means the model expects "
                "very low sales and is uncertain. Treat this as roughly $0 in sales."
            )
        else:
            lines.append(
                f"For store {store_id}, the forecast for the next period is {fmt(prediction)} in sales."
            )
    else:
        lines.append(
            f"For store {store_id}, a forecast is available, but the exact value could not be formatted."
        )

    # Describe how much history we actually have
    if history:
        n_months = len(history)
        start_date = fmt_date(history[0].get("date"))
        end_date = fmt_date(history[-1].get("date"))
        lines.append(
            f"The model is using {n_months} month(s) of history from {start_date} through {end_date}."
        )
    else:
        lines.append(
            "Recent history is limited or unavailable, so it is harder to compare this forecast to past performance."
        )

    # Compare to 6-month average when possible
    if isinstance(prediction, (int, float)) and avg_6 not in (None, 0):
        diff = prediction - avg_6
        pct = diff / avg_6

        if pct > 0.20:
            lines.append("This is much higher than the store's recent 6-month average.")
        elif pct > 0.05:
            lines.append("This is slightly higher than the store's recent 6-month average.")
        elif pct < -0.20:
            lines.append("This is much lower than the store's recent 6-month average.")
        elif pct < -0.05:
            lines.append("This is slightly lower than the store's recent 6-month average.")
        else:
            lines.append("This is roughly in line with what the store has done over the last 6 months.")
    elif last_actual is not None:
        # If we don't have a 6-month avg but we DO have a last month, relate to that
        if isinstance(prediction, (int, float)) and last_actual != 0:
            diff = prediction - last_actual
            pct = diff / last_actual
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
    if isinstance(prediction, (int, float)):
        lines.append(f"- Forecast for next period: {fmt(prediction)}")

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

    if neg_forecast:
        lines.append("- Treat this as a near-zero month and investigate why sales might be so weak.")
    else:
        if isinstance(prediction, (int, float)) and avg_6 not in (None, 0):
            if prediction > avg_6 * 1.1:
                lines.append("- Ensure you have enough inventory to support the higher-than-usual forecast.")
            elif prediction < avg_6 * 0.9:
                lines.append("- Consider tightening orders if this lower forecast matches what you see locally.")
            else:
                lines.append("- Use this forecast as a baseline and adjust for any known events or promotions.")
        elif last_actual is not None:
            lines.append("- Compare this forecast directly to last month's sales to set expectations.")

    if volatility == "high":
        lines.append("- Because this store is volatile, avoid over-reacting to a single month's forecast.")
    elif volatility == "medium":
        lines.append("- Expect some month-to-month noise when comparing actuals to this forecast.")
    else:
        lines.append("- Track actuals against this forecast to see if the store is stabilizing or shifting.")

    lines.append("- Cross-check this forecast with any upcoming promotions, holidays, or local events.")

    return "\n".join(lines)
