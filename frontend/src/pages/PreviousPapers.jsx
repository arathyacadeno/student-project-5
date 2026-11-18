import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import EmptyState from "../components/EmptyState";

function PreviousPapers() {
  const navigate = useNavigate();

  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [selectedSubject, setSelectedSubject] = useState("All");
  const [selectedYear, setSelectedYear] = useState("All");

  // Selected Paper State & View Mode ('list' | 'study' | 'timed_exam' | 'exam_result')
  const [viewMode, setViewMode] = useState("list");
  const [activePaper, setActivePaper] = useState(null);
  const [loadingPaper, setLoadingPaper] = useState(false);

  // Timed exam attempt state
  const [examAnswers, setExamAnswers] = useState({});
  const [examTimeLeft, setExamTimeLeft] = useState(0);
  const [submittingExam, setSubmittingExam] = useState(false);
  const [attemptResult, setAttemptResult] = useState(null);

  const fetchPapers = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (selectedSubject !== "All") params.subject = selectedSubject;
      if (selectedYear !== "All") params.year = Number(selectedYear);

      const res = await api.get("/papers", { params });
      setPapers(res.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load previous question papers.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, [selectedSubject, selectedYear]);

  // Exam Countdown Timer
  useEffect(() => {
    if (viewMode !== "timed_exam" || examTimeLeft <= 0) return;

    const timer = setInterval(() => {
      setExamTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleAutoSubmitExam();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [viewMode, examTimeLeft]);

  const handleOpenStudyMode = async (paperId) => {
    setLoadingPaper(true);
    try {
      const res = await api.get(`/papers/${paperId}`);
      setActivePaper(res.data);
      setViewMode("study");
    } catch (err) {
      console.error(err);
      alert("Failed to load solved question paper.");
    } finally {
      setLoadingPaper(false);
    }
  };

  const handleStartTimedExam = async (paperId) => {
    setLoadingPaper(true);
    try {
      const res = await api.get(`/papers/${paperId}`);
      setActivePaper(res.data);
      setExamAnswers({});
      setExamTimeLeft(res.data.time_limit_minutes * 60);
      setViewMode("timed_exam");
    } catch (err) {
      console.error(err);
      alert("Failed to start timed paper attempt.");
    } finally {
      setLoadingPaper(false);
    }
  };

  const handleAutoSubmitExam = () => {
    alert("⏰ Time is up! Submitting your examination answers.");
    handleSubmitExam();
  };

  const handleSubmitExam = async () => {
    if (!activePaper || submittingExam) return;
    setSubmittingExam(true);
    try {
      const answersPayload = activePaper.questions.map((q) => ({
        question_id: q.id,
        selected_option: examAnswers[q.id] !== undefined ? examAnswers[q.id] : null,
      }));

      const timeSpent = activePaper.time_limit_minutes * 60 - examTimeLeft;

      const res = await api.post(`/papers/${activePaper.id}/attempt`, {
        paper_id: activePaper.id,
        time_spent_seconds: Math.max(1, timeSpent),
        answers: answersPayload,
      });

      setAttemptResult(res.data);
      setViewMode("exam_result");
    } catch (err) {
      console.error(err);
      alert("Failed to submit exam attempt.");
    } finally {
      setSubmittingExam(false);
    }
  };

  const formatTimer = (secs) => {
    const mins = Math.floor(secs / 60);
    const rem = secs % 60;
    return `${mins.toString().padStart(2, "0")}:${rem.toString().padStart(2, "0")}`;
  };

  return (
    <div className="previous-papers-page">
      {/* ================= VIEW 1: PAPERS LIST ================= */}
      {viewMode === "list" && (
        <>
          <div className="page-header-row">
            <div>
              <h2>📄 Solved Previous-Year Question Papers</h2>
              <p className="page-subtitle">
                Official past examinations with step-by-step solutions. Attempt in Timed Mode to diagnose weak points and access direct study material links.
              </p>
            </div>
          </div>

          {/* Filters Bar */}
          <div className="papers-filters-bar">
            <div className="subject-tabs-bar">
              {["All", "Biology", "Mathematics", "Computer Science"].map((subj) => (
                <button
                  key={subj}
                  className={`subj-tab ${selectedSubject === subj ? "active" : ""}`}
                  onClick={() => setSelectedSubject(subj)}
                >
                  {subj}
                </button>
              ))}
            </div>

            <div className="year-filter-wrapper">
              <label>Exam Year:</label>
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(e.target.value)}
                className="year-select"
              >
                <option value="All">All Years</option>
                <option value="2024">2024</option>
                <option value="2023">2023</option>
                <option value="2022">2022</option>
              </select>
            </div>
          </div>

          {loading ? (
            <LoadingSpinner message="Loading previous question papers..." />
          ) : error ? (
            <ErrorMessage error={error} onRetry={fetchPapers} />
          ) : papers.length === 0 ? (
            <EmptyState
              icon="📄"
              title="No past papers found"
              message="Try changing the subject or year filter."
            />
          ) : (
            <div className="papers-grid">
              {papers.map((p) => (
                <div key={p.id} className="paper-card">
                  <div className="paper-card-top">
                    <span className="paper-subj-badge">{p.subject}</span>
                    <span className="paper-year-pill">Year {p.year}</span>
                  </div>

                  <h3 className="paper-title">{p.title}</h3>

                  <div className="paper-meta-details">
                    <span>⏱️ Duration: {p.time_limit_minutes} Mins</span>
                    <span>📊 Total Marks: {p.total_marks}</span>
                    <span>❓ Questions: {p.questions_count}</span>
                  </div>

                  <div className="paper-card-actions">
                    <button
                      className="study-mode-btn"
                      onClick={() => handleOpenStudyMode(p.id)}
                      disabled={loadingPaper}
                    >
                      📖 Study Solved Answers
                    </button>
                    <button
                      className="timed-exam-btn"
                      onClick={() => handleStartTimedExam(p.id)}
                      disabled={loadingPaper}
                    >
                      ⏱️ Attempt Timed Exam
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ================= VIEW 2: STUDY SOLVED MODE ================= */}
      {viewMode === "study" && activePaper && (
        <div className="study-paper-view">
          <div className="paper-view-header">
            <button
              className="back-btn"
              onClick={() => {
                setViewMode("list");
                setActivePaper(null);
              }}
            >
              ← Back to Papers List
            </button>
            <div className="paper-view-titles">
              <h2>{activePaper.title}</h2>
              <span className="paper-tag-line">
                {activePaper.subject} • {activePaper.year} • Verified Step-by-Step Solutions
              </span>
            </div>
            <button
              className="timed-exam-btn"
              onClick={() => handleStartTimedExam(activePaper.id)}
            >
              ⏱️ Switch to Timed Exam Mode
            </button>
          </div>

          <div className="solved-questions-container">
            {activePaper.questions.map((q) => (
              <div key={q.id} className="solved-q-card">
                <div className="solved-q-head">
                  <span className="solved-qnum">Question {q.question_number}</span>
                  <span className="solved-topic-badge">📌 {q.topic}</span>
                  {q.related_material_id && (
                    <button
                      className="link-material-pill"
                      onClick={() =>
                        navigate(`/materials?search=${encodeURIComponent(q.topic)}`)
                      }
                    >
                      📚 Review Material: {q.related_material_title || q.topic} →
                    </button>
                  )}
                </div>

                <p className="solved-qtext">{q.question_text}</p>

                <div className="solved-options-grid">
                  {q.options.map((opt, optIdx) => {
                    const isCorrect = q.correct_option === optIdx;
                    return (
                      <div
                        key={optIdx}
                        className={`solved-opt-item ${isCorrect ? "correct-answer" : ""}`}
                      >
                        <span className="opt-letter">{String.fromCharCode(65 + optIdx)}</span>
                        <span className="opt-text">{opt}</span>
                        {isCorrect && <span className="correct-tag">✓ Correct Answer</span>}
                      </div>
                    );
                  })}
                </div>

                {/* Step-by-Step Solution Block */}
                <div className="solution-deepdive-box">
                  <div className="solution-title">
                    <span className="sol-icon">💡</span>
                    <strong>Verified Step-by-Step Solution & Method:</strong>
                  </div>
                  <pre className="solution-pre">{q.step_by_step_solution}</pre>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ================= VIEW 3: TIMED EXAM MODE ================= */}
      {viewMode === "timed_exam" && activePaper && (
        <div className="exam-mode-view">
          <div className="exam-sticky-bar">
            <div>
              <h3>{activePaper.title}</h3>
              <span className="exam-subtext">Real Exam Simulation Mode</span>
            </div>
            <div className={`countdown-clock ${examTimeLeft < 300 ? "urgent" : ""}`}>
              <span>⏳ {formatTimer(examTimeLeft)}</span>
            </div>
          </div>

          <div className="exam-questions-list">
            {activePaper.questions.map((q, idx) => (
              <div key={q.id} className="exam-q-card">
                <div className="exam-q-header">
                  <span className="q-number-pill">Question {idx + 1}</span>
                  <span className="q-topic-badge">📌 {q.topic}</span>
                </div>

                <p className="exam-qtext">{q.question_text}</p>

                <div className="exam-options-list">
                  {q.options.map((opt, optIdx) => {
                    const isSelected = examAnswers[q.id] === optIdx;
                    return (
                      <div
                        key={optIdx}
                        className={`exam-opt-choice ${isSelected ? "selected" : ""}`}
                        onClick={() =>
                          setExamAnswers((prev) => ({
                            ...prev,
                            [q.id]: optIdx,
                          }))
                        }
                      >
                        <span className="opt-letter">{String.fromCharCode(65 + optIdx)}</span>
                        <span className="opt-label">{opt}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="exam-submit-footer">
            <span>
              Answered: {Object.keys(examAnswers).length} of {activePaper.questions.length} questions
            </span>
            <button
              className="submit-exam-btn"
              onClick={handleSubmitExam}
              disabled={submittingExam}
            >
              {submittingExam ? "Grading & Linking Materials..." : "Submit Examination ✓"}
            </button>
          </div>
        </div>
      )}

      {/* ================= VIEW 4: EXAM RESULT & REMEDIATION ================= */}
      {viewMode === "exam_result" && attemptResult && (
        <div className="exam-result-view">
          <div className="result-hero-banner">
            <div>
              <h2>Examination Attempt Completed!</h2>
              <span className="paper-title-tag">{attemptResult.paper_title}</span>
            </div>
            <div className="hero-score-stat">
              <span className="hero-pct">{attemptResult.percentage}%</span>
              <span className="hero-raw">
                {attemptResult.score} / {attemptResult.total_marks} Marks
              </span>
            </div>
          </div>

          {/* Remediation List with Direct Material Links */}
          <div className="remediation-section">
            <div className="remediation-head">
              <h3>🔍 Question Analysis & Remediation Links</h3>
              <p>
                Every incorrect answer is linked directly to the corresponding study notes and concept resources:
              </p>
            </div>

            <div className="remediation-cards">
              {attemptResult.remediations.map((item) => (
                <div
                  key={item.question_id}
                  className={`remediation-card ${item.is_correct ? "correct" : "incorrect"}`}
                >
                  <div className="remed-head">
                    <span className="remed-qnum">Question {item.question_number}</span>
                    <span className="remed-topic">📌 {item.topic}</span>
                    <span className={`remed-status ${item.is_correct ? "pass" : "fail"}`}>
                      {item.is_correct ? "✓ Correct" : "✗ Incorrect"}
                    </span>
                  </div>

                  <p className="remed-qtext">{item.question_text}</p>

                  {/* Wrong Answer Remediation Link to Study Material */}
                  {!item.is_correct && (
                    <div className="remediation-alert-box">
                      <div className="remed-alert-icon">⚠️</div>
                      <div className="remed-alert-content">
                        <strong>Identified Weak Point: {item.topic}</strong>
                        <p>You missed this question. Strengthen this concept using the connected study material:</p>
                        {item.related_material_id ? (
                          <button
                            className="remed-study-link-btn"
                            onClick={() =>
                              navigate(`/materials?search=${encodeURIComponent(item.topic)}`)
                            }
                          >
                            📖 Open Study Material: {item.related_material_title || item.topic} →
                          </button>
                        ) : (
                          <button
                            className="remed-study-link-btn"
                            onClick={() =>
                              navigate(`/materials?search=${encodeURIComponent(item.topic)}`)
                            }
                          >
                            📖 Search Notes for {item.topic} →
                          </button>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Step by Step Solution */}
                  <div className="solution-deepdive-box">
                    <strong>Step-by-Step Verified Solution:</strong>
                    <pre className="solution-pre">{item.step_by_step_solution}</pre>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="results-bottom-actions">
            <button
              className="action-btn-primary"
              onClick={() => {
                setViewMode("list");
                setActivePaper(null);
                setAttemptResult(null);
              }}
            >
              ← Back to All Question Papers
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default PreviousPapers;
