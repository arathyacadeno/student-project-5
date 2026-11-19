import { useState } from "react";
import api from "./api";

function Register({ onSwitchToLogin }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setMessage("");
    setLoading(true);

    try {
      await api.post("/register", {
        name: name.trim(),
        email: email.trim(),
        password: password,
      });

      setSuccess(true);
      setMessage("Registration successful! You can now log in.");
    } catch (error) {
      setSuccess(false);
      setMessage(error.response?.data?.detail || "Registration failed. Try a different email.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-card">
      <div className="auth-brand-head">
        <span className="auth-logo">🎓</span>
        <h1>StudyMatch AI</h1>
        <p className="auth-subtitle">Create your student account</p>
      </div>

      <form onSubmit={handleRegister} className="auth-form">
        <div className="form-field">
          <label>Full Name</label>
          <input
            type="text"
            placeholder="e.g. Alex Morgan"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>

        <div className="form-field">
          <label>Email Address</label>
          <input
            type="email"
            placeholder="alex@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className="form-field">
          <label>Password (min 6 chars)</label>
          <input
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
        </div>

        <button type="submit" className="auth-submit-btn" disabled={loading}>
          {loading ? "Creating Account..." : "Create Account →"}
        </button>
      </form>

      {message && (
        <div className={`auth-msg-banner ${success ? "success" : "error"}`}>
          {message}
          {success && (
            <button className="link-button block-btn" onClick={onSwitchToLogin}>
              Go to Login →
            </button>
          )}
        </div>
      )}

      <div className="auth-switch-footer">
        Already have an account?{" "}
        <button type="button" className="link-button" onClick={onSwitchToLogin}>
          Login here
        </button>
      </div>
    </div>
  );
}

export default Register;