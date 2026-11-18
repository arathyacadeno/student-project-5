import { useState, useEffect, useRef } from "react";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";

function AIMentor({ user }) {
  const [messages, setMessages] = useState([]);
  const [weakTopics, setWeakTopics] = useState([]);
  const [suggestedChips, setSuggestedChips] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchHistory = async () => {
    setLoadingHistory(true);
    setError(null);
    try {
      const res = await api.get("/mentor/history");
      setMessages(res.data.messages || []);
      setWeakTopics(res.data.student_weak_topics || []);
      setSuggestedChips(res.data.suggested_chips || []);
    } catch (err) {
      console.error(err);
      setError("Failed to load mentor chat history.");
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, sending]);

  const handleSendMessage = async (msgText) => {
    const textToSend = msgText || inputMessage;
    if (!textToSend.trim() || sending) return;

    const tempUserMsg = {
      id: Date.now(),
      sender: "student",
      message: textToSend,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setInputMessage("");
    setSending(true);

    try {
      const res = await api.post("/mentor/chat", { message: textToSend });
      const mentorMsg = {
        id: Date.now() + 1,
        sender: "mentor",
        message: res.data.response,
        referenced_topics: res.data.referenced_topics,
        created_at: res.data.timestamp || new Date().toISOString(),
      };
      setMessages((prev) => [...prev, mentorMsg]);
      if (res.data.suggested_chips?.length > 0) {
        setSuggestedChips(res.data.suggested_chips);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to receive mentor response. Please try again.");
    } finally {
      setSending(false);
    }
  };

  const handleClearHistory = async () => {
    if (!window.confirm("Are you sure you want to clear your conversation history?")) return;
    try {
      await api.delete("/mentor/history");
      setMessages([]);
    } catch (err) {
      console.error("Failed to clear history", err);
    }
  };

  return (
    <div className="ai-mentor-page">
      {/* Mentor Header */}
      <div className="mentor-header">
        <div className="mentor-header-left">
          <div className="mentor-avatar-badge">🤖</div>
          <div>
            <h2>StudyMatch AI Personal Academic Mentor</h2>
            <p className="mentor-subtitle">
              Your 24/7 dedicated tutor analyzing your test errors, weak topics, and exam preparations.
            </p>
          </div>
        </div>

        <button className="clear-history-btn" onClick={handleClearHistory} title="Clear conversation history">
          🗑️ Clear Chat
        </button>
      </div>

      {/* Weak Topics Context Pill Banner */}
      {weakTopics.length > 0 && (
        <div className="mentor-context-banner">
          <span className="context-indicator">🎯 Mentor Context Active:</span>
          <span>Aware of your focus areas in: </span>
          {weakTopics.map((top, idx) => (
            <span key={idx} className="context-topic-tag">
              {top}
            </span>
          ))}
        </div>
      )}

      {/* Chat Area */}
      <div className="mentor-chat-box">
        {loadingHistory ? (
          <LoadingSpinner message="Loading mentor conversation..." />
        ) : error ? (
          <ErrorMessage error={error} onRetry={fetchHistory} />
        ) : (
          <div className="chat-messages-scroll">
            {messages.length === 0 && (
              <div className="mentor-intro-card">
                <span className="intro-icon">👋</span>
                <h3>Hello {user?.name || "Student"}! I am your AI Mentor.</h3>
                <p>
                  I have synchronized with your latest skill profile and mock test results.
                  Ask me anything from resolving doubts in Calculus to breaking down DNA replication
                  or planning your entrance exam revision roadmap!
                </p>
              </div>
            )}

            {messages.map((msg, index) => {
              const isStudent = msg.sender === "student";
              return (
                <div
                  key={index}
                  className={`chat-message-row ${isStudent ? "student-row" : "mentor-row"}`}
                >
                  <div className="message-avatar">
                    {isStudent ? (user?.name?.charAt(0).toUpperCase() || "S") : "🤖"}
                  </div>

                  <div className={`message-bubble ${isStudent ? "student-bubble" : "mentor-bubble"}`}>
                    <div className="message-sender-name">
                      {isStudent ? (user?.name || "You") : "AI Academic Mentor"}
                    </div>
                    <div className="message-text">
                      <pre className="bubble-pre">{msg.message}</pre>
                    </div>
                    {msg.referenced_topics && msg.referenced_topics.length > 0 && (
                      <div className="bubble-topics-footer">
                        <span>Referenced topics: </span>
                        {msg.referenced_topics.map((t, i) => (
                          <span key={i} className="ref-topic-pill">
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {sending && (
              <div className="chat-message-row mentor-row">
                <div className="message-avatar">🤖</div>
                <div className="message-bubble mentor-bubble typing-bubble">
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span className="typing-text">Analyzing your profile & composing advice...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Suggested Question Chips */}
        {suggestedChips.length > 0 && (
          <div className="suggested-chips-bar">
            <span className="chips-title">💡 Suggested Questions:</span>
            <div className="chips-list">
              {suggestedChips.map((chip, idx) => (
                <button
                  key={idx}
                  className="question-chip-btn"
                  onClick={() => handleSendMessage(chip)}
                  disabled={sending}
                >
                  {chip}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Chat Input Bar */}
        <form
          className="chat-input-bar"
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
        >
          <input
            type="text"
            placeholder="Ask a question, request a concept breakdown, or ask for a revision schedule..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            disabled={sending}
            className="mentor-text-input"
          />
          <button
            type="submit"
            disabled={sending || !inputMessage.trim()}
            className="send-message-btn"
          >
            {sending ? "..." : "Send 📤"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default AIMentor;
