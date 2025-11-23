// src/components/ForecastPanel.jsx
export default function ForecastPanel({
  selectedStore,
  prediction,
  loadingForecast,
}) {
  return (
    <section className="panel">
      <h2 className="panel-title">Forecast</h2>
      {!selectedStore && (
        <p className="panel-subtitle">
          Select a store on the left to view its forecast.
        </p>
      )}

      {selectedStore && (
        <div className="forecast-card">
          <p className="forecast-store">
            <span className="label">Store:</span>{" "}
            <span className="value">
              {selectedStore.label} (#{selectedStore.value})
            </span>
          </p>

          {loadingForecast && (
            <p className="forecast-loading">Loading prediction…</p>
          )}

          {!loadingForecast && prediction != null && (
            <p className="forecast-value">
              <span className="label">Predicted sales:</span>{" "}
              <span className="value">
                {prediction.toFixed ? prediction.toFixed(2) : prediction}
              </span>
            </p>
          )}

          {!loadingForecast && prediction == null && (
            <p className="forecast-empty">No prediction available yet.</p>
          )}
        </div>
      )}
    </section>
  );
}
