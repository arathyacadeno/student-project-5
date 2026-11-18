import { useState, useEffect, useCallback } from "react";
import api from "../api";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

function MockTests() {
  // Test Lifecycle States: 'setup' | 'running' | 'result'
  const [testState, setTestState] = useState("setup");

  // Config setup state
  const [selectedSubject, setSelectedSubject] = useState("Biology");
  const [difficultyMode, setDifficultyMode] = useState("adaptive");
  const [totalQuestions, setTotalQuestions] = useState(6);
  const [starting, setStarting] = useState(false);

  // Running test state
  const [activeTest, setActiveTest] = useState(null); // { test_id, questions, time_limit_minutes }
  const [userAnswers, setUserAnswers] = useState({}); // { [question_id]: selected_option }
  const [timeLeft, setTimeLeft] = useState(0); // in seconds
  const [submitting, setSubmitting] = useState(false);

  // Result state
  const [testResult, setTestResult] = useState(null);

  // Past History
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  const fetchHistory = async () => {
    try {
      const res = await api.get("/mock-tests/history");
      setHistory(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleSubmitTest = useCallback(async () => {
    if (!activeTest || submitting) return;
    setSubmitting(true);
    try {
      const answersPayload = activeTest.questions.map((q) => ({
        question_id: q.question_id,
        selected_option: userAnswers[q.question_id] !== undefined ? userAnswers[q.question_id] : null,
      }));

      const res = await api.post(`/mock-tests/${activeTest.test_id}/submit`, {
        test_id: activeTest.test_id,
        answers: answersPayload,
      });

      setTestResult(res.data);
      setTestState("result");
      fetchHistory(); // Refresh history
    } catch (err) {
      console.error(err);
      alert("Failed to submit test. Please check connection.");
    } finally {
      setSubmitting(false);
    }
  }, [activeTest, submitting, userAnswers]);

  const handleAutoSubmit = useCallback(() => {
    alert("⏰ Time is up! Submitting your mock test responses automatically.");
    handleSubmitTest();
  }, [handleSubmitTest]);

  // Timer Effect
  useEffect(() => {
    if (testState !== "running" || timeLeft <= 0) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleAutoSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [testState, timeLeft, handleAutoSubmit]);

  const handleStartTest = async () => {
    setStarting(true);
    try {
      const res = await api.post("/mock-tests/generate", {
        subject: selectedSubject,
        difficulty_mode: difficultyMode,
        total_questions: Number(totalQuestions),
      });
      setActiveTest(res.data);
      setTimeLeft(res.data.time_limit_minutes * 60);
      setUserAnswers({});
      setTestState("running");
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to start mock test");
    } finally {
      setStarting(false);
    }
  };

  const handleSelectOption = (questionId, optionIndex) => {
    setUserAnswers((prev) => ({
      ...prev,
      [questionId]: optionIndex,
    }));
  };

  const formatTimer = (secs) => {
    const mins = Math.floor(secs / 60);
    const remainder = secs % 60;
    return `${mins.toString().padStart(2, "0")}:${remainder.toString().padStart(2, "0")}`;
  };

  // Convert topic breakdown into chart-friendly array
  const topicChartData = testResult?.topic_breakdown
    ? Object.keys(testResult.topic_breakdown).map((topic) => ({
        topic,
        correct: testResult.topic_breakdown[topic].correct,
        total: testResult.topic_breakdown[topic].total,
        accuracy: Math.round(
          (testResult.topic_breakdown[topic].correct / testResult.topic_breakdown[topic].total) * 100
        ),
      }))
    : [];

  return (
    <div className="mock-tests-page">
      {/* ==================== VIEW 1: SETUP SCREEN ==================== */}
      {testState === "setup" && (
        <>
          <div className="page-header-row">
            <div>
              <h2>📝 Adaptive Mock Tests</h2>
              <p className="page-subtitle">
                Practice tests tailored to your current topic proficiency. Results automatically update your Skill Profile.
              </p>
            </div>
          </div>

          <div className="test-config-card">
            <div className="config-header">
              <h3>🎯 Configure Your Assessment</h3>
              <span className="adaptive-badge">✨ Adaptive AI Enabled</span>
            </div>

            <div className="config-form-grid">
              <div className="config-group">
                <label>Target Subject</label>
                <div className="subject-button-group">
                  {["Biology", "Mathematics", "Computer Science"].map((subj) => (
                    <button
                      key={subj}
                      type="button"
                      className={`subj-btn ${selectedSubject === subj ? "active" : ""}`}
                      onClick={() => setSelectedSubject(subj)}
                    >
                      {subj}
                    </button>
                  ))}
                </div>
              </div>

              <div className="config-group">
                <label>Difficulty Selection</label>
                <div className="difficulty-options-grid">
                  <div
                    className={`diff-choice-card ${difficultyMode === "adaptive" ? "selected" : ""}`}
                    onClick={() => setDifficultyMode("adaptive")}
                  >
                    <span className="diff-icon">🧠</span>
                    <strong>Adaptive (Recommended)</strong>
                    <p>Selects questions based on your weak and developing topics in your skill profile.</p>
                  </div>

                  <div
                    className={`diff-choice-card ${difficultyMode === "easy" ? "selected" : ""}`}
                    onClick={() => setDifficultyMode("easy")}
                  >
                    <span className="diff-icon">🌱</span>
                    <strong>Easy Level</strong>
                    <p>Foundational concepts and direct definitions.</p>
                  </div>

                  <div
                    className={`diff-choice-card ${difficultyMode === "medium" ? "selected" : ""}`}
                    onClick={() => setDifficultyMode("medium")}
                  >
                    <span className="diff-icon">⚡</span>
                    <strong>Medium Level</strong>
                    <p>Standard exam application problems.</p>
                  </div>

                  <div
                    className={`diff-choice-card ${difficultyMode === "difficult" ? "selected" : ""}`}
                    onClick={() => setDifficultyMode("difficult")}
                  >
                    <span className="diff-icon">🔥</span>
                    <strong>Difficult Level</strong>
                    <p>Advanced multi-step and entrance-level challenges.</p>
                  </div>
                </div>
              </div>

              <div className="config-group">
                <label>Number of Questions</label>
                <select
                  value={totalQuestions}
                  onChange={(e) => setTotalQuestions(e.target.value)}
                  className="questions-select"
                >
                  <option value={4}>4 Questions (~8 Minutes)</option>
                  <option value={6}>6 Questions (~12 Minutes)</option>
                  <option value={8}>8 Questions (~16 Minutes)</option>
                </select>
              </div>
            </div>

            <button
              className="start-test-action-btn"
              onClick={handleStartTest}
              disabled={starting}
            >
              {starting ? "Generating Custom Test..." : "🚀 Begin Timed Mock Test"}
            </button>
          </div>

          {/* Past Mock Test History */}
          <div className="history-section-card">
            <h3>📜 Past Assessment Performance History</h3>
            {loadingHistory ? (
              <p>Loading history...</p>
            ) : history.length === 0 ? (
              <p className="no-history-text">No completed mock tests yet. Take your first test above!</p>
            ) : (
              <div className="history-table-wrapper">
                <table className="history-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Subject</th>
                      <th>Mode</th>
                      <th>Score</th>
                      <th>Percentage</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((t) => (
                      <tr key={t.id}>
                        <td>{new Date(t.created_at).toLocaleDateString()}</td>
                        <td>
                          <strong>{t.subject}</strong>
                        </td>
                        <td>
                          <span className="history-mode-pill">{t.difficulty_mode}</span>
                        </td>
                        <td>
                          {t.score} / {t.total_marks}
                        </td>
                        <td>
                          <span
                            className={`pct-badge ${
                              t.percentage >= 75
                                ? "high"
                                : t.percentage >= 50
                                ? "mid"
                                : "low"
                            }`}
                          >
                            {t.percentage}%
                          </span>
                        </td>
                        <td>
                          <span className="completed-tag">✓ Completed</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {/* ==================== VIEW 2: RUNNING TEST SCREEN ==================== */}
      {testState === "running" && activeTest && (
        <div className="test-running-container">
          {/* Fixed Sticky Header */}
          <div className="test-header-bar">
            <div>
              <h3>{activeTest.subject} Mock Examination</h3>
              <span className="test-meta-info">
                Mode: {activeTest.difficulty_mode.toUpperCase()} | Total Questions: {activeTest.total_questions}
              </span>
            </div>
            <div className={`countdown-clock ${timeLeft < 120 ? "urgent" : ""}`}>
              <span className="clock-icon">⏳</span>
              <span className="clock-digits">{formatTimer(timeLeft)}</span>
            </div>
          </div>

          {/* Question Palette & Questions */}
          <div className="test-questions-list">
            {activeTest.questions.map((q, idx) => (
              <div key={q.question_id} className="test-question-card">
                <div className="q-card-header">
                  <span className="q-number-pill">Question {idx + 1}</span>
                  <div className="q-badges">
                    <span className="q-topic-badge">📌 {q.topic}</span>
                    <span className={`q-diff-badge ${q.difficulty}`}>{q.difficulty}</span>
                  </div>
                </div>

                <p className="q-text">{q.question_text}</p>

                <div className="q-options-container">
                  {q.options.map((option, optIdx) => {
                    const isSelected = userAnswers[q.question_id] === optIdx;
                    return (
                      <div
                        key={optIdx}
                        className={`q-option-choice ${isSelected ? "selected" : ""}`}
                        onClick={() => handleSelectOption(q.question_id, optIdx)}
                      >
                        <span className="opt-letter">
                          {String.fromCharCode(65 + optIdx)}
                        </span>
                        <span className="opt-label">{option}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* Test Submit Footer */}
          <div className="test-submit-bar">
            <span className="answered-count-text">
              Answered: {Object.keys(userAnswers).length} of {activeTest.total_questions} questions
            </span>
            <button
              className="submit-test-btn"
              onClick={handleSubmitTest}
              disabled={submitting}
            >
              {submitting ? "Grading & Updating Profile..." : "Submit Examination ✓"}
            </button>
          </div>
        </div>
      )}

      {/* ==================== VIEW 3: RESULTS SCREEN ==================== */}
      {testState === "result" && testResult && (
        <div className="test-results-view">
          <div className="results-hero-card">
            <div className="score-summary-left">
              <h2>Test Results & Skill Evaluation</h2>
              <span className="result-subject-tag">{testResult.subject}</span>
              <div className="hero-percentage">
                <span className="pct-number">{testResult.percentage}%</span>
                <span className="pct-caption">
                  {testResult.score} of {testResult.total_marks} Marks Scored
                </span>
              </div>
              <p className="profile-update-notice">
                ✅ <strong>Skill Profile Auto-Updated:</strong> Your topic proficiencies have been recalculated based on this attempt!
              </p>
            </div>

            {/* Recharts Topic Accuracy Chart */}
            <div className="result-chart-box">
              <h4>Topic Accuracy Breakdown</h4>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={topicChartData} margin={{ top: 10, right: 10, left: -20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="topic" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Bar dataKey="accuracy" name="Accuracy %" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Detailed Question Review */}
          <div className="review-section">
            <h3>🔍 Detailed Answer Explanations</h3>
            <div className="review-cards-list">
              {testResult.questions_review.map((item, idx) => (
                <div
                  key={idx}
                  className={`review-card ${item.is_correct ? "correct" : "incorrect"}`}
                >
                  <div className="review-card-head">
                    <span className="review-qnum">Question {idx + 1}</span>
                    <span className={`review-status-pill ${item.is_correct ? "correct" : "incorrect"}`}>
                      {item.is_correct ? "✓ Correct (+1)" : "✗ Incorrect (0)"}
                    </span>
                  </div>

                  <p className="review-qtext">{item.question_text}</p>

                  <div className="review-options">
                    {item.options.map((opt, optIdx) => {
                      const isUserChoice = item.selected_option === optIdx;
                      const isCorrectChoice = item.correct_option === optIdx;

                      let optClass = "neutral";
                      if (isCorrectChoice) optClass = "correct-choice";
                      else if (isUserChoice && !item.is_correct) optClass = "wrong-choice";

                      return (
                        <div key={optIdx} className={`review-opt-item ${optClass}`}>
                          <span className="review-opt-letter">{String.fromCharCode(65 + optIdx)}</span>
                          <span className="review-opt-text">{opt}</span>
                          {isCorrectChoice && <span className="verified-badge">✓ Correct Answer</span>}
                          {isUserChoice && !item.is_correct && <span className="your-badge">Your Answer</span>}
                        </div>
                      );
                    })}
                  </div>

                  {item.explanation && (
                    <div className="explanation-box">
                      <strong>💡 Step-by-Step Explanation:</strong>
                      <p>{item.explanation}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="results-footer-actions">
            <button
              className="action-btn-primary"
              onClick={() => {
                setTestState("setup");
                setTestResult(null);
                setActiveTest(null);
              }}
            >
              Take Another Mock Test 📝
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default MockTests;
