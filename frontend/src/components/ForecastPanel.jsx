// src/components/ForecastPanel.jsx
export default function ForecastPanel({
  selectedStore,
  prediction,
  loadingForecast,
  explanation,
  loadingExplanation,
  explanationError,
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

          {prediction != null && (
            <div className="ai-explanation">
              <h3 className="ai-title">AI Insight</h3>

              {loadingExplanation && (
                <p className="forecast-loading">
                  Analyzing this store’s recent performance…
                </p>
              )}

              {explanationError && (
                <p className="error-text">
                  Couldn’t load explanation: {explanationError}
                </p>
              )}

              {!loadingExplanation && !explanationError && explanation && (
                <div className="ai-body">
                  {explanation.split("\n").map((line, idx) => (
                    <p key={idx}>{line}</p>
                  ))}
                </div>
              )}


              {!loadingExplanation &&
                !explanationError &&
                !explanation && (
                  <p className="forecast-empty">
                    No explanation available yet.
                  </p>
                )}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
