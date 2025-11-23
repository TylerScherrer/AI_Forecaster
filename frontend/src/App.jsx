import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL;

export default function App() {
  const [status, setStatus] = useState("Loading...");
  const [error, setError] = useState("");
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loadingForecast, setLoadingForecast] = useState(false);

  // Health check
  useEffect(() => {
    async function checkBackend() {
      try {
        const res = await fetch(`${API_BASE}/health`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setStatus(data.ok ? "Backend is connected" : "Unexpected response");
      } catch (err) {
        setError(String(err));
        setStatus("Backend unreachable");
      }
    }
    checkBackend();
  }, []);

  // Load store list
  useEffect(() => {
    async function loadStores() {
      try {
        const res = await fetch(`${API_BASE}/stores`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setStores(Array.isArray(data.stores) ? data.stores : []);
      } catch (err) {
        setError(String(err));
      }
    }
    loadStores();
  }, []);

  // When user clicks a store
  async function handleSelectStore(store) {
    setSelectedStore(store);
    setPrediction(null);
    setLoadingForecast(true);
    setError("");

    try {
      const res = await fetch(`${API_BASE}/forecast/${store.value}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setPrediction(data.prediction);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoadingForecast(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-start",
        fontFamily: "system-ui, sans-serif",
        padding: 24,
      }}
    >
      <h1>AI Forecaster</h1>
      <p>{status}</p>

      {error && (
        <pre
          style={{
            color: "crimson",
            background: "#111",
            padding: 12,
            borderRadius: 8,
            maxWidth: 600,
            whiteSpace: "pre-wrap",
          }}
        >
          {error}
        </pre>
      )}

      <div
        style={{
          display: "flex",
          gap: 24,
          marginTop: 24,
          width: "100%",
          maxWidth: 900,
        }}
      >
        {/* Store list */}
        <div style={{ flex: 1 }}>
          <h3>Stores (click one)</h3>
          <ul
            style={{
              listStyle: "none",
              padding: 0,
              margin: 0,
              maxHeight: 400,
              overflowY: "auto",
              border: "1px solid #ccc",
              borderRadius: 8,
            }}
          >
            {stores.map((s) => (
              <li
                key={s.value}
                onClick={() => handleSelectStore(s)}
                style={{
                  padding: "8px 12px",
                  cursor: "pointer",
                  background:
                    selectedStore && selectedStore.value === s.value
                      ? "#eef"
                      : "white",
                  borderBottom: "1px solid #eee",
                }}
              >
                {s.label} (#{s.value})
              </li>
            ))}
            {stores.length === 0 && <li style={{ padding: 8 }}>No stores loaded.</li>}
          </ul>
        </div>

        {/* Prediction panel */}
        <div style={{ flexBasis: 280 }}>
          <h3>Forecast</h3>
          {!selectedStore && <p>Select a store to see a prediction.</p>}

          {selectedStore && (
            <div
              style={{
                border: "1px solid #ccc",
                borderRadius: 8,
                padding: 16,
              }}
            >
              <p>
                <strong>Store:</strong> {selectedStore.label} (#{selectedStore.value})
              </p>
              {loadingForecast && <p>Loading prediction...</p>}
              {!loadingForecast && prediction != null && (
                <p>
                  <strong>Predicted value:</strong>{" "}
                  {prediction.toFixed ? prediction.toFixed(2) : prediction}
                </p>
              )}
              {!loadingForecast && prediction == null && (
                <p>No prediction available yet.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
