function ErrorMessage({ error, onRetry }) {
  if (!error) return null;
  return (
    <div className="error-banner">
      <div className="error-content">
        <span className="error-icon">⚠️</span>
        <span>{typeof error === "string" ? error : error.message || "An unexpected error occurred."}</span>
      </div>
      {onRetry && (
        <button className="retry-btn" onClick={onRetry}>
          Try Again
        </button>
      )}
    </div>
  );
}

export default ErrorMessage;
