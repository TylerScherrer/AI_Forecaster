// src/App.jsx
import { useEffect, useState } from "react";

import {
  apiHealth,
  apiGetStores,
  apiGetForecast,
  apiExplainForecast, // ✅ NEW
} from "./api/client";

import StatusBar from "./components/StatusBar";
import ErrorBox from "./components/ErrorBox";
import StoreList from "./components/StoreList";
import ForecastPanel from "./components/ForecastPanel";

import "./App.css";

export default function App() {
  const [status, setStatus] = useState("Checking backend…");
  const [error, setError] = useState("");

  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loadingForecast, setLoadingForecast] = useState(false);

  // LLM-related state
  const [explanation, setExplanation] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);
  const [explanationError, setExplanationError] = useState("");

  // -------------------------------
  // Health check
  // -------------------------------
  useEffect(() => {
    async function checkBackend() {
      try {
        const data = await apiHealth();
        setStatus(data.ok ? "Backend is connected" : "Unexpected response");
      } catch (err) {
        setError(String(err));
        setStatus("Backend unreachable");
      }
    }
    checkBackend();
  }, []);

  // -------------------------------
  // Load store list
  // -------------------------------
  useEffect(() => {
    async function loadStores() {
      try {
        const storesData = await apiGetStores();
        setStores(storesData);
      } catch (err) {
        setError(String(err));
      }
    }
    loadStores();
  }, []);

  // -------------------------------
  // When a store is selected
  // -------------------------------
  async function handleSelectStore(store) {
    setSelectedStore(store);

    // reset previous results
    setPrediction(null);
    setExplanation(null);

    setLoadingForecast(true);
    setLoadingExplanation(false);

    // clear previous errors
    setError("");
    setExplanationError("");

    try {
      // 1) Get numeric forecast
      const data = await apiGetForecast(store.value);
      setPrediction(data.prediction);

      // 2) Ask LLM to explain (don’t block forecast if this fails)
      setLoadingExplanation(true);
      try {
        const explain = await apiExplainForecast({
          storeId: store.value,
          prediction: data.prediction,
        });
        setExplanation(explain.explanation);
      } catch (llmErr) {
        // Only mark LLM-specific error here
        setExplanationError(String(llmErr));
      } finally {
        setLoadingExplanation(false);
      }
    } catch (err) {
      // Hard failure getting prediction
      setError(String(err));
    } finally {
      setLoadingForecast(false);
    }
  }

  return (
    <div className="app-root">
      <header className="app-header">
        <div>
          <h1 className="app-title">AI Forecaster</h1>
          <p className="app-subtitle">
            Simple store-level forecasts for busy managers.
          </p>
        </div>
        <StatusBar status={status} />
      </header>

      <main className="app-main">
        {/* Global error for hard failures */}
        <ErrorBox error={error} />

        <div className="layout-grid">
          <StoreList
            stores={stores}
            selectedStore={selectedStore}
            onSelectStore={handleSelectStore}
          />

          <ForecastPanel
            selectedStore={selectedStore}
            prediction={prediction}
            loadingForecast={loadingForecast}
            explanation={explanation}
            loadingExplanation={loadingExplanation}
            explanationError={explanationError}
          />
        </div>
      </main>
    </div>
  );
}
