import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import EmptyState from "../components/EmptyState";

function PreviousPapers({ user }) {
  const navigate = useNavigate();
  const isTeacher = user?.role === "teacher";

  // Views: 'list' | 'study' | 'timed_exam' | 'exam_result'
  const [viewMode, setViewMode] = useState("list");

  // Filters
  const [selectedSubject, setSelectedSubject] = useState("All");
  const [selectedExam, setSelectedExam] = useState("All");
  const [selectedYear, setSelectedYear] = useState("All");
  const [topicSearch, setTopicSearch] = useState("");

  // Papers Data
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Active Paper for Study or Timed Exam
  const [activePaper, setActivePaper] = useState(null);
  const [loadingPaper, setLoadingPaper] = useState(false);

  // Timed exam attempt state
  const [examAnswers, setExamAnswers] = useState({});
  const [examTimeLeft, setExamTimeLeft] = useState(0);
  const [submittingExam, setSubmittingExam] = useState(false);
  const [attemptResult, setAttemptResult] = useState(null);

  // Teacher Upload Modal
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadExamName, setUploadExamName] = useState("JEE Main");
  const [uploadSubject, setUploadSubject] = useState("Mathematics");
  const [uploadYear, setUploadYear] = useState(2024);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadTopicTags, setUploadTopicTags] = useState("");
  const [uploadFilePath, setUploadFilePath] = useState("");
  const [uploadAnswerKey, setUploadAnswerKey] = useState("");
  const [uploading, setUploading] = useState(false);

  // PDF Preview Modal
  const [previewPaper, setPreviewPaper] = useState(null);

  const fetchPapers = async () => {
    setLoading(true);
    setError(null);
    try {
      // First try extended endpoint /api/v1/papers
      const params = {};
      if (selectedSubject !== "All") params.subject = selectedSubject;
      if (selectedExam !== "All") params.exam = selectedExam;
      if (selectedYear !== "All") params.year = Number(selectedYear);
      if (topicSearch.trim()) params.topic = topicSearch.trim();

      const res = await api.get("/api/v1/papers", { params });
      setPapers(res.data.items || []);
    } catch (err) {
      console.warn("Extended papers endpoint error, falling back to /papers:", err);
      try {
        const fallback = await api.get("/papers");
        setPapers(fallback.data || []);
      } catch (e2) {
        setError("Failed to load question papers library.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, [selectedSubject, selectedExam, selectedYear]);

  const handleSubmitExam = useCallback(async () => {
    if (!activePaper || submittingExam) return;
    setSubmittingExam(true);
    try {
      const answersPayload = activePaper.questions.map((q) => ({
        question_id: q.id,
        selected_option: examAnswers[q.id] !== undefined ? examAnswers[q.id] : null,
      }));

      const timeSpent = (activePaper.time_limit_minutes || 60) * 60 - examTimeLeft;

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
  }, [activePaper, submittingExam, examAnswers, examTimeLeft]);

  // Exam Countdown Timer
  useEffect(() => {
    if (viewMode !== "timed_exam" || examTimeLeft <= 0) return;

    const timer = setInterval(() => {
      setExamTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          alert("⏰ Time is up! Submitting your examination answers.");
          handleSubmitExam();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [viewMode, examTimeLeft, handleSubmitExam]);

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
      setExamTimeLeft((res.data.time_limit_minutes || 60) * 60);
      setViewMode("timed_exam");
    } catch (err) {
      console.error(err);
      alert("Failed to start timed paper attempt.");
    } finally {
      setLoadingPaper(false);
    }
  };

  const formatTimer = (secs) => {
    const mins = Math.floor(secs / 60);
    const rem = secs % 60;
    return `${mins.toString().padStart(2, "0")}:${rem.toString().padStart(2, "0")}`;
  };

  // Teacher: Upload Paper
  const handleUploadPaper = async (e) => {
    e.preventDefault();
    setUploading(true);
    try {
      const tagsList = uploadTopicTags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);

      await api.post("/api/v1/papers", {
        exam_name: uploadExamName,
        subject: uploadSubject,
        year: Number(uploadYear),
        title: uploadTitle,
        topic_tags: tagsList,
        file_path: uploadFilePath || `/papers/${uploadExamName.toLowerCase().replace(" ", "_")}_${uploadYear}.pdf`,
        answer_key_file: uploadAnswerKey || null,
      });

      setShowUploadModal(false);
      setUploadTitle("");
      setUploadTopicTags("");
      fetchPapers();
      alert("Paper submitted successfully for class library!");
    } catch (err) {
      console.error("Upload paper error:", err);
      alert("Failed to upload paper metadata.");
    } finally {
      setUploading(false);
    }
  };

  // Teacher: Approve Paper
  const handleApprovePaper = async (paperId) => {
    try {
      await api.patch(`/api/v1/papers/${paperId}/approve`, { approval_status: "approved" });
      fetchPapers();
      alert("Paper approved and published.");
    } catch (err) {
      console.error("Approve paper error:", err);
      alert("Failed to approve paper.");
    }
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
                Official past examinations with step-by-step solutions, timed simulation mode, and automated remediation links back to study materials.
              </p>
            </div>
            {isTeacher && (
              <button
                className="action-btn-primary"
                onClick={() => setShowUploadModal(true)}
              >
                + Upload Question Paper
              </button>
            )}
          </div>

          {/* Filters Bar */}
          <div className="papers-filters-bar">
            {/* Subject Tabs */}
            <div className="stream-filter-pills">
              {["All", "Biology", "Mathematics", "Computer Science", "Physics"].map((subj) => (
                <button
                  key={subj}
                  className={`filter-pill ${selectedSubject === subj ? "active" : ""}`}
                  onClick={() => setSelectedSubject(subj)}
                >
                  {subj}
                </button>
              ))}
            </div>

            {/* Exam Filter Dropdown */}
            <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
              <select
                value={selectedExam}
                onChange={(e) => setSelectedExam(e.target.value)}
                className="search-input"
                style={{ padding: "6px 12px", fontSize: "13px" }}
              >
                <option value="All">All Exams</option>
                <option value="JEE Main">JEE Main</option>
                <option value="NEET-UG">NEET-UG</option>
                <option value="GATE">GATE</option>
                <option value="KEAM">KEAM</option>
                <option value="Board">State Board / CBSE</option>
              </select>

              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(e.target.value)}
                className="search-input"
                style={{ padding: "6px 12px", fontSize: "13px" }}
              >
                <option value="All">All Years</option>
                <option value="2024">2024</option>
                <option value="2023">2023</option>
                <option value="2022">2022</option>
              </select>

              <input
                type="text"
                placeholder="🔍 Search topic..."
                value={topicSearch}
                onChange={(e) => setTopicSearch(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && fetchPapers()}
                className="search-input"
                style={{ padding: "6px 12px", fontSize: "13px", width: "160px" }}
              />
            </div>
          </div>

          {loading ? (
            <LoadingSpinner message="Loading previous year question papers..." />
          ) : error ? (
            <ErrorMessage error={error} onRetry={fetchPapers} />
          ) : papers.length === 0 ? (
            <EmptyState
              icon="📄"
              title="No papers found matching criteria"
              message="Try clearing filters or search term."
              actionText="Reset Filters"
              onAction={() => {
                setSelectedSubject("All");
                setSelectedExam("All");
                setSelectedYear("All");
                setTopicSearch("");
              }}
            />
          ) : (
            <div className="courses-grid">
              {papers.map((paper) => (
                <div key={paper.id} className="course-card-enhanced">
                  <div className="course-card-header">
                    <span className="exam-code-badge">{paper.exam_name || "Official"}</span>
                    <span className="degree-tag">{paper.year}</span>
                    <span className="stream-pill">{paper.subject}</span>
                  </div>

                  <h3 className="course-card-title">{paper.title}</h3>

                  {paper.topic_tags && (
                    <div className="card-exams-tags" style={{ marginTop: "8px" }}>
                      {paper.topic_tags.map((tag, i) => (
                        <span key={i} className="exam-tag-mini">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="card-key-details" style={{ marginTop: "12px" }}>
                    <div>📄 <strong>Format:</strong> Solved PDF</div>
                    <div>⏱️ <strong>Limit:</strong> {paper.time_limit_minutes || 60} mins</div>
                    <div>🎯 <strong>Marks:</strong> {paper.total_marks || 50}</div>
                  </div>

                  <div className="card-bottom-actions">
                    <button
                      className="action-btn-secondary btn-sm"
                      onClick={() => setPreviewPaper(paper)}
                    >
                      📄 View PDF
                    </button>
                    {paper.answer_key_file && (
                      <button
                        className="action-btn-secondary btn-sm"
                        onClick={() =>
                          alert(`Answer Key & Solutions available for ${paper.title} at ${paper.answer_key_file}`)
                        }
                      >
                        🔑 Key
                      </button>
                    )}
                    <button
                      className="action-btn-primary btn-sm"
                      onClick={() => handleStartTimedExam(paper.id)}
                    >
                      ⏱️ Timed Attempt
                    </button>
                  </div>

                  {isTeacher && paper.approval_status === "pending" && (
                    <div style={{ marginTop: "10px", borderTop: "1px dashed #cbd5e1", paddingTop: "8px" }}>
                      <span className="status-badge status-pending" style={{ marginRight: "8px" }}>
                        PENDING APPROVAL
                      </span>
                      <button
                        className="table-action-btn"
                        onClick={() => handleApprovePaper(paper.id)}
                      >
                        Approve Paper ✓
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ================= VIEW 2: TIMED EXAM MODE ================= */}
      {viewMode === "timed_exam" && activePaper && (
        <div className="running-test-container">
          <div className="test-running-header">
            <div>
              <h3>⏱️ Timed Paper Simulation: {activePaper.title}</h3>
              <span className="stream-pill">{activePaper.subject}</span>
              <span className="degree-tag" style={{ marginLeft: "8px" }}>Year {activePaper.year}</span>
            </div>

            <div className="timer-box">
              <span className={`timer-display ${examTimeLeft < 300 ? "timer-danger" : ""}`}>
                ⏳ {formatTimer(examTimeLeft)}
              </span>
              <button
                className="action-btn-primary"
                onClick={handleSubmitExam}
                disabled={submittingExam}
              >
                {submittingExam ? "Submitting..." : "Submit Examination 🚀"}
              </button>
            </div>
          </div>

          <div style={{ maxWidth: "800px", margin: "0 auto", padding: "20px 0" }}>
            {activePaper.questions && activePaper.questions.map((q, idx) => (
              <div
                key={q.id}
                className="quiz-question-group"
                style={{ background: "white", padding: "20px", borderRadius: "10px", marginBottom: "20px", border: "1px solid var(--border-color)" }}
              >
                <div className="review-top-row">
                  <span className="q-badge">Question {idx + 1}</span>
                  <span className="topic-badge">🏷️ {q.topic}</span>
                </div>

                <p className="question-text" style={{ fontSize: "16px", margin: "14px 0" }}>
                  {q.question_text}
                </p>

                <div className="mcq-options-grid">
                  {q.options && q.options.map((opt, optIdx) => {
                    const isSelected = examAnswers[q.id] === optIdx;
                    return (
                      <div
                        key={optIdx}
                        className={`mcq-option-row ${isSelected ? "selected" : ""}`}
                        onClick={() => setExamAnswers({ ...examAnswers, [q.id]: optIdx })}
                      >
                        <span className="option-letter">{String.fromCharCode(65 + optIdx)}</span>
                        <span className="option-text">{opt}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}

            <div style={{ textAlign: "center", marginTop: "20px" }}>
              <button
                className="action-btn-primary"
                style={{ padding: "12px 32px", fontSize: "16px" }}
                onClick={handleSubmitExam}
                disabled={submittingExam}
              >
                {submittingExam ? "Grading..." : "Submit Answers & View Detailed Solutions"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= VIEW 3: EXAM RESULTS & REMEDIATION ================= */}
      {viewMode === "exam_result" && attemptResult && (
        <div className="test-result-page">
          <div className="result-hero-banner">
            <div>
              <h2>📊 Previous Paper Performance Report</h2>
              <p>Step-by-step solutions revealed. Wrong answers are mapped directly to study materials.</p>
            </div>
            <button
              className="action-btn-primary"
              onClick={() => {
                setViewMode("list");
                fetchPapers();
              }}
            >
              ← Back to Papers Library
            </button>
          </div>

          <div className="kpi-grid">
            <div className="kpi-card success">
              <div className="kpi-icon">🎯</div>
              <div className="kpi-details">
                <span className="kpi-num">{attemptResult.percentage}%</span>
                <span className="kpi-label">Accuracy Score</span>
                <span className="kpi-subtext">{attemptResult.score} / {attemptResult.total_marks} Marks</span>
              </div>
            </div>

            <div className="kpi-card info">
              <div className="kpi-icon">⏱️</div>
              <div className="kpi-details">
                <span className="kpi-num">
                  {Math.floor(attemptResult.time_spent_seconds / 60)}m {attemptResult.time_spent_seconds % 60}s
                </span>
                <span className="kpi-label">Time Spent</span>
                <span className="kpi-subtext">Exam pace analysis</span>
              </div>
            </div>

            <div className="kpi-card danger">
              <div className="kpi-icon">⚠️</div>
              <div className="kpi-details">
                <span className="kpi-num">{attemptResult.remediation_materials?.length || 0}</span>
                <span className="kpi-label">Remediation Topics</span>
                <span className="kpi-subtext">Linked study materials</span>
              </div>
            </div>
          </div>

          {/* Remediation Study Materials Box */}
          {attemptResult.remediation_materials && attemptResult.remediation_materials.length > 0 && (
            <div className="teacher-section-card" style={{ marginBottom: "24px" }}>
              <h3>📚 Targeted Remediation Study Materials</h3>
              <p className="subtext">
                Directly study the notes and theory for the questions you got wrong on this paper.
              </p>

              <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "14px" }}>
                {attemptResult.remediation_materials.map((item, idx) => (
                  <div key={idx} className="remediation-row">
                    <div>
                      <span className="danger-topic-pill" style={{ marginRight: "8px" }}>
                        ⚠️ Q{item.question_number}: {item.topic}
                      </span>
                      <strong>{item.material_title}</strong>
                    </div>
                    <button
                      className="table-action-btn"
                      onClick={() => navigate(`/materials?search=${encodeURIComponent(item.topic)}`)}
                    >
                      Study Notes →
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Step-by-Step Question Review */}
          <div className="teacher-section-card">
            <h3>📝 Step-by-Step Solved Question Review</h3>
            <div className="question-review-list" style={{ marginTop: "16px" }}>
              {attemptResult.question_breakdown && attemptResult.question_breakdown.map((q, idx) => (
                <div
                  key={idx}
                  className={`review-question-card ${q.is_correct ? "correct" : "incorrect"}`}
                >
                  <div className="review-top-row">
                    <span className="q-badge">Question {q.question_number}</span>
                    <span className={`status-pill ${q.is_correct ? "status-success" : "status-danger"}`}>
                      {q.is_correct ? "✓ Correct" : "✗ Incorrect"}
                    </span>
                    <span className="topic-badge">🏷️ {q.topic}</span>
                  </div>

                  <p className="review-q-text">{q.question_text}</p>

                  <div className="review-answers-box">
                    <div>
                      <strong>Your Answer:</strong>{" "}
                      <span className={q.is_correct ? "correct-text" : "incorrect-text"}>
                        {q.options && q.selected_option !== null && q.selected_option !== undefined
                          ? q.options[q.selected_option]
                          : "(Unanswered)"}
                      </span>
                    </div>
                    <div>
                      <strong>Correct Solved Answer:</strong>{" "}
                      <span className="correct-text">
                        {q.options ? q.options[q.correct_option] : q.correct_option}
                      </span>
                    </div>
                  </div>

                  {q.step_by_step_solution && (
                    <div className="review-explanation-box">
                      <strong>💡 Step-by-Step Official Solution:</strong>
                      <p>{q.step_by_step_solution}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ================= MODAL: TEACHER UPLOAD QUESTION PAPER ================= */}
      {showUploadModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-md">
            <div className="modal-header">
              <h3>+ Upload & Tag Question Paper</h3>
              <button className="modal-close" onClick={() => setShowUploadModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleUploadPaper} className="modal-body">
              <div className="info-grid-2col" style={{ marginBottom: "12px" }}>
                <div>
                  <label>Exam Name:</label>
                  <select
                    value={uploadExamName}
                    onChange={(e) => setUploadExamName(e.target.value)}
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  >
                    <option value="JEE Main">JEE Main</option>
                    <option value="NEET-UG">NEET-UG</option>
                    <option value="GATE">GATE</option>
                    <option value="KEAM">KEAM</option>
                    <option value="Board">State Board / CBSE</option>
                  </select>
                </div>

                <div>
                  <label>Subject:</label>
                  <select
                    value={uploadSubject}
                    onChange={(e) => setUploadSubject(e.target.value)}
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  >
                    <option value="Mathematics">Mathematics</option>
                    <option value="Biology">Biology</option>
                    <option value="Computer Science">Computer Science</option>
                    <option value="Physics">Physics</option>
                  </select>
                </div>
              </div>

              <div className="info-grid-2col" style={{ marginBottom: "12px" }}>
                <div>
                  <label>Year:</label>
                  <input
                    type="number"
                    min="2000"
                    max="2030"
                    value={uploadYear}
                    onChange={(e) => setUploadYear(e.target.value)}
                    required
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>

                <div>
                  <label>Paper Title:</label>
                  <input
                    type="text"
                    placeholder="e.g. JEE Main 2024 Shift 1 Mathematics"
                    value={uploadTitle}
                    onChange={(e) => setUploadTitle(e.target.value)}
                    required
                    className="search-input"
                    style={{ width: "100%", marginTop: "4px" }}
                  />
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: "12px" }}>
                <label>Topic Tags (comma-separated):</label>
                <input
                  type="text"
                  placeholder="e.g. Calculus, Algebra, Matrices, Coordinate Geometry"
                  value={uploadTopicTags}
                  onChange={(e) => setUploadTopicTags(e.target.value)}
                  className="search-input"
                  style={{ width: "100%", marginTop: "4px" }}
                />
              </div>

              <div className="form-group" style={{ marginBottom: "12px" }}>
                <label>Paper Document Path / URL (PDF):</label>
                <input
                  type="text"
                  placeholder="/papers/jee_main_2024_maths.pdf"
                  value={uploadFilePath}
                  onChange={(e) => setUploadFilePath(e.target.value)}
                  className="search-input"
                  style={{ width: "100%", marginTop: "4px" }}
                />
              </div>

              <div className="form-group" style={{ marginBottom: "16px" }}>
                <label>Answer Key / Solution Path (Optional):</label>
                <input
                  type="text"
                  placeholder="/papers/jee_main_2024_maths_ans.pdf"
                  value={uploadAnswerKey}
                  onChange={(e) => setUploadAnswerKey(e.target.value)}
                  className="search-input"
                  style={{ width: "100%", marginTop: "4px" }}
                />
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="action-btn-secondary"
                  onClick={() => setShowUploadModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="action-btn-primary"
                  disabled={uploading}
                >
                  {uploading ? "Uploading..." : "Save to Library"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ================= MODAL: PDF PREVIEW ================= */}
      {previewPaper && (
        <div className="modal-backdrop">
          <div className="modal-dialog modal-md">
            <div className="modal-header">
              <h3>📄 {previewPaper.title}</h3>
              <button className="modal-close" onClick={() => setPreviewPaper(null)}>
                &times;
              </button>
            </div>
            <div className="modal-body" style={{ textAlign: "center", padding: "30px 20px" }}>
              <div style={{ fontSize: "48px", marginBottom: "12px" }}>📑</div>
              <h4>{previewPaper.exam_name} {previewPaper.year} — {previewPaper.subject}</h4>
              <p style={{ color: "var(--text-muted)", marginTop: "6px" }}>
                File Path: <code>{previewPaper.file_path}</code>
              </p>

              {previewPaper.topic_tags && (
                <div className="pills-wrap" style={{ justifyContent: "center", margin: "16px 0" }}>
                  {previewPaper.topic_tags.map((t, i) => (
                    <span key={i} className="exam-tag-mini">
                      {t}
                    </span>
                  ))}
                </div>
              )}

              <div style={{ display: "flex", gap: "12px", justifyContent: "center", marginTop: "20px" }}>
                <button
                  className="action-btn-primary"
                  onClick={() => {
                    alert(`Opening download link for: ${previewPaper.file_path}`);
                  }}
                >
                  ⬇️ Download PDF Paper
                </button>
                <button
                  className="action-btn-secondary"
                  onClick={() => {
                    setPreviewPaper(null);
                    handleStartTimedExam(previewPaper.id);
                  }}
                >
                  ⏱️ Attempt in Timed Mode
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PreviousPapers;
