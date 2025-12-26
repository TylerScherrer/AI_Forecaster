// src/components/ForecastChart.jsx
import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
} from "recharts";

function formatMonthLabel(dateStr) {
  if (!dateStr) return "";
  return String(dateStr).slice(0, 7); // "2023-08-01" -> "2023-08"
}

export default function ForecastChart({
  history,
  prediction,
  loading,
  nextLabel = "Next",   // ⭐ NEW
}) {
  // No data state
  if (loading) {
    return (
      <section className="panel">
        <h2 className="panel-title">Trend &amp; Forecast</h2>
        <p className="panel-subtitle">Loading forecast…</p>
      </section>
    );
  }

  if (!Array.isArray(history) || history.length === 0 || prediction == null) {
    return (
      <section className="panel">
        <h2 className="panel-title">Trend &amp; Forecast</h2>
        <p className="panel-subtitle">
          Select a store to see its trend and forecast.
        </p>
      </section>
    );
  }

  const chartData = [
    ...history.map((row) => ({
      date: formatMonthLabel(row.date),
      actual: row.sales,
      forecast: null,
    })),
    {
      date: nextLabel,   // ⭐ was "Next", now whatever backend sends (e.g. "2024-09")
      actual: null,
      forecast: prediction,
    },
  ];

  return (
    <section className="panel">
      <h2 className="panel-title">Trend &amp; Forecast</h2>
      <p className="panel-subtitle">
        Recent monthly sales vs next-period forecast.
      </p>

      <div style={{ width: "100%", height: 320 }}>
        <ResponsiveContainer>
          <LineChart
            data={chartData}
            margin={{ top: 16, right: 24, left: 0, bottom: 8 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="actual" name="Actual" dot={false} />
            <Line
              type="monotone"
              dataKey="forecast"
              name="Forecast"
              strokeDasharray="4 4"
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
