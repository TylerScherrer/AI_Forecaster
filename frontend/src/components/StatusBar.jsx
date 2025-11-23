// src/components/StatusBar.jsx
export default function StatusBar({ status }) {
  if (!status) return null;
  return <p className="status-bar">{status}</p>;
}
