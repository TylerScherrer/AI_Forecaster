// src/App.jsx
import { useEffect, useState } from "react";

import {
  apiHealth,
  apiGetStores,
  apiGetForecast,
  apiExplainForecast,
} from "./api/client";

import StatusBar from "./components/StatusBar";
import ErrorBox from "./components/ErrorBox";
import StoreList from "./components/StoreList";
import ForecastPanel from "./components/ForecastPanel";
import ForecastChart from "./components/ForecastChart";

import "./App.css";

export default function App() {
  const [status, setStatus] = useState("Checking backend…");
  const [error, setError] = useState("");

  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loadingForecast, setLoadingForecast] = useState(false);

  // chart-related state
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [nextPeriodLabel, setNextPeriodLabel] = useState("Next"); // ⭐ NEW

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
    setHistory([]);
    setStats(null);
    setNextPeriodLabel("Next"); // ⭐ reset

    setLoadingForecast(true);
    setLoadingExplanation(false);

    // clear previous errors
    setError("");
    setExplanationError("");

    try {
      // 1) Get forecast + history + stats (+ next_period_label)
      const data = await apiGetForecast(store.value);
      // data should look like:
      // { store_id, prediction, history, stats, next_period_label }

      setPrediction(data.prediction);
      setHistory(data.history || []);
      setStats(data.stats || null);
      setNextPeriodLabel(data.next_period_label || "Next"); // ⭐ NEW

      // 2) Ask LLM to explain (don’t block forecast if this fails)
      setLoadingExplanation(true);
      try {
        const explain = await apiExplainForecast({
          storeId: store.value,
          prediction: data.prediction,
          history: data.history || [],
          stats: data.stats || {},
        });
        setExplanation(explain.explanation);
      } catch (llmErr) {
        setExplanationError(String(llmErr));
      } finally {
        setLoadingExplanation(false);
      }
    } catch (err) {
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
        <ErrorBox error={error} />

        <div className="layout-grid">
          {/* LEFT: store list */}
          <StoreList
            stores={stores}
            selectedStore={selectedStore}
            onSelectStore={handleSelectStore}
          />

          {/* MIDDLE: forecast + AI Insight */}
          <ForecastPanel
            selectedStore={selectedStore}
            prediction={prediction}
            loadingForecast={loadingForecast}
            explanation={explanation}
            loadingExplanation={loadingExplanation}
            explanationError={explanationError}
          />

          {/* RIGHT: forecasting graph */}
          <ForecastChart
            history={history}
            prediction={prediction}
            loading={loadingForecast}
            nextLabel={nextPeriodLabel}    // ⭐ pass label down
          />
        </div>
      </main>
    </div>
  );
}
