// src/components/StoreList.jsx
export default function StoreList({ stores, selectedStore, onSelectStore }) {
  return (
    <section className="panel">
      <h2 className="panel-title">Stores</h2>
      <p className="panel-subtitle">Click a store to see its forecast.</p>

      <ul className="store-list">
        {stores.map((s) => {
          const isActive = selectedStore && selectedStore.value === s.value;
          return (
            <li
              key={s.value}
              className={`store-list-item ${isActive ? "active" : ""}`}
              onClick={() => onSelectStore(s)}
            >
              <span className="store-name">{s.label}</span>
              <span className="store-id">#{s.value}</span>
            </li>
          );
        })}
        {stores.length === 0 && (
          <li className="store-list-empty">No stores loaded.</li>
        )}
      </ul>
    </section>
  );
}
