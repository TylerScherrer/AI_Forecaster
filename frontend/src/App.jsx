// src/App.jsx
import { useEffect, useState } from "react";

import { apiHealth, apiGetStores, apiGetForecast } from "./api/client";
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

  // Health check
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

  // Load store list
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

  // Handle store click
  async function handleSelectStore(store) {
    setSelectedStore(store);
    setPrediction(null);
    setLoadingForecast(true);
    setError("");

    try {
      const data = await apiGetForecast(store.value);
      setPrediction(data.prediction);
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
          <StoreList
            stores={stores}
            selectedStore={selectedStore}
            onSelectStore={handleSelectStore}
          />

          <ForecastPanel
            selectedStore={selectedStore}
            prediction={prediction}
            loadingForecast={loadingForecast}
          />
        </div>
      </main>
    </div>
  );
}
