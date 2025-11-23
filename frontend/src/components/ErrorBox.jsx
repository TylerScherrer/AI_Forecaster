// src/components/ErrorBox.jsx
export default function ErrorBox({ error }) {
  if (!error) return null;

  return (
    <div className="error-box">
      <strong>Error:</strong>
      <pre>{error}</pre>
    </div>
  );
}
