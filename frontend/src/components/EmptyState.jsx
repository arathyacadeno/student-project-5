function EmptyState({ icon = "📭", title = "No items found", message, actionText, onAction }) {
  return (
    <div className="empty-state">
      <span className="empty-icon">{icon}</span>
      <h3>{title}</h3>
      {message && <p>{message}</p>}
      {actionText && onAction && (
        <button className="primary-btn" onClick={onAction}>
          {actionText}
        </button>
      )}
    </div>
  );
}

export default EmptyState;
