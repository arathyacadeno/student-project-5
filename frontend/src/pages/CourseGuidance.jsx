import { useState, useEffect } from "react";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import EmptyState from "../components/EmptyState";

function CourseGuidance() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Questionnaire Modal State
  const [showQuizModal, setShowQuizModal] = useState(false);
  const [submittingQuiz, setSubmittingQuiz] = useState(false);
  const [formData, setFormData] = useState({
    preferred_work_style: "Practical / Hands-on",
    favorite_subject: "Computer Science",
    career_interest: "Software & AI",
    higher_study_goal: "Immediate Jobs",
    study_budget: "Medium",
  });

  // Selected course for roadmap deep-dive
  const [selectedCourse, setSelectedCourse] = useState(null);

  const fetchCourses = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get("/guidance/courses");
      setCourses(res.data);
      if (res.data.length > 0 && !selectedCourse) {
        setSelectedCourse(res.data[0]);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to load higher-study course guidance.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  const handleQuizSubmit = async (e) => {
    e.preventDefault();
    setSubmittingQuiz(true);
    try {
      const res = await api.post("/guidance/questionnaire", formData);
      setCourses(res.data.recommended_courses);
      if (res.data.recommended_courses.length > 0) {
        setSelectedCourse(res.data.recommended_courses[0]);
      }
      setShowQuizModal(false);
    } catch (err) {
      console.error(err);
      alert("Failed to submit questionnaire. Please try again.");
    } finally {
      setSubmittingQuiz(false);
    }
  };

  return (
    <div className="course-guidance-page">
      {/* Page Header */}
      <div className="page-header-row">
        <div>
          <h2>🎓 Future Course & Career Guidance</h2>
          <p className="page-subtitle">
            Ranked higher-study paths matched against your academic strengths, skill profile, and interest questionnaire.
          </p>
        </div>
        <button
          className="action-btn-primary"
          onClick={() => setShowQuizModal(true)}
        >
          ✍️ Retake Interest Questionnaire
        </button>
      </div>

      {loading ? (
        <LoadingSpinner message="Calculating course match percentages..." />
      ) : error ? (
        <ErrorMessage error={error} onRetry={fetchCourses} />
      ) : courses.length === 0 ? (
        <EmptyState
          icon="🎓"
          title="No guidance recommendations found"
          message="Take the quick 1-minute questionnaire to receive tailored program matches."
          actionText="Start Questionnaire"
          onAction={() => setShowQuizModal(true)}
        />
      ) : (
        <div className="guidance-layout-grid">
          {/* Left Column: Ranked Recommendations List */}
          <div className="recommendations-sidebar">
            <div className="sidebar-list-header">
              <h3>Ranked Recommendations</h3>
              <span className="results-count">{courses.length} Programs</span>
            </div>

            <div className="course-card-list">
              {courses.map((course) => {
                const isSelected = selectedCourse?.id === course.id;
                const matchClass =
                  course.match_percentage >= 85
                    ? "match-high"
                    : course.match_percentage >= 70
                    ? "match-mid"
                    : "match-normal";

                return (
                  <div
                    key={course.id}
                    className={`course-list-item ${isSelected ? "selected" : ""}`}
                    onClick={() => setSelectedCourse(course)}
                  >
                    <div className="course-item-header">
                      <span className={`match-badge ${matchClass}`}>
                        {course.match_percentage}% Match
                      </span>
                      <span className="degree-tag">{course.degree_level.split(" ")[0]}</span>
                    </div>

                    <h4 className="course-item-title">{course.title}</h4>
                    <span className="stream-text">🔬 {course.stream}</span>

                    <p className="match-reason-preview">{course.recommended_reason}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Column: Deep-Dive Roadmap & Eligibility */}
          {selectedCourse && (
            <div className="course-detail-view">
              <div className="detail-hero-card">
                <div className="detail-hero-top">
                  <div>
                    <span className="stream-badge">{selectedCourse.stream}</span>
                    <h2 className="detail-course-title">{selectedCourse.title}</h2>
                    <span className="degree-level-pill">🎓 {selectedCourse.degree_level}</span>
                  </div>
                  <div className="hero-match-gauge">
                    <span className="gauge-number">{selectedCourse.match_percentage}%</span>
                    <span className="gauge-label">Profile Fit</span>
                  </div>
                </div>

                <p className="detail-description">{selectedCourse.description}</p>
                <div className="fit-reason-callout">
                  <strong>💡 Why this matches you:</strong> {selectedCourse.recommended_reason}
                </div>
              </div>

              {/* Quick Info Grid: Eligibility, Fees, Scope */}
              <div className="info-cards-grid">
                <div className="info-card">
                  <span className="info-icon">📋</span>
                  <h4>Eligibility Criteria</h4>
                  <p>{selectedCourse.eligibility}</p>
                </div>

                <div className="info-card">
                  <span className="info-icon">💰</span>
                  <h4>Estimated Fees</h4>
                  <p>{selectedCourse.fees_range}</p>
                </div>

                <div className="info-card">
                  <span className="info-icon">🚀</span>
                  <h4>Career Scope & Roles</h4>
                  <ul className="careers-list">
                    {selectedCourse.scope_and_careers.map((career, idx) => (
                      <li key={idx}>✓ {career}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Entrance Exams Section */}
              <div className="detail-section-card">
                <h3>📝 Target Entrance Exams & Deadlines</h3>
                <div className="exams-grid">
                  {selectedCourse.entrance_exams.map((exam, idx) => (
                    <div key={idx} className="exam-card">
                      <div className="exam-card-head">
                        <strong>{exam.name}</strong>
                        <span className="importance-pill">{exam.importance}</span>
                      </div>
                      <span className="exam-date">🗓️ Timeline: {exam.date}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Step-by-Step Educational Roadmap */}
              <div className="detail-section-card">
                <h3>🗺️ Step-by-Step Degree & Career Roadmap</h3>
                <div className="roadmap-stepper">
                  {selectedCourse.roadmap_steps.map((step, idx) => (
                    <div key={idx} className="roadmap-step-item">
                      <div className="step-marker">
                        <span className="marker-num">{idx + 1}</span>
                        {idx < selectedCourse.roadmap_steps.length - 1 && (
                          <div className="marker-line"></div>
                        )}
                      </div>
                      <div className="step-content">
                        <div className="step-stage-badge">{step.stage}</div>
                        <h4>{step.title}</h4>
                        <p>{step.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Questionnaire Modal */}
      {showQuizModal && (
        <div className="modal-backdrop" onClick={() => setShowQuizModal(false)}>
          <div className="quiz-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-topbar">
              <div>
                <h3>Future Course Interest Questionnaire</h3>
                <span className="modal-sub">
                  Helps our guidance engine align courses with your personal preferences
                </span>
              </div>
              <button
                className="modal-close-btn"
                onClick={() => setShowQuizModal(false)}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleQuizSubmit} className="quiz-form">
              <div className="quiz-question-block">
                <label>1. What is your preferred learning & work style?</label>
                <select
                  value={formData.preferred_work_style}
                  onChange={(e) =>
                    setFormData({ ...formData, preferred_work_style: e.target.value })
                  }
                >
                  <option value="Practical / Hands-on">Practical / Hands-on & Building Systems</option>
                  <option value="Theoretical / Research">Theoretical / Pure Research & Academic Analysis</option>
                  <option value="Creative / Tech">Creative / Digital Design & Technology</option>
                  <option value="Clinical / Patient Care">Clinical / Direct Human Healthcare</option>
                </select>
              </div>

              <div className="quiz-question-block">
                <label>2. Which subject excites you most?</label>
                <select
                  value={formData.favorite_subject}
                  onChange={(e) =>
                    setFormData({ ...formData, favorite_subject: e.target.value })
                  }
                >
                  <option value="Computer Science">Computer Science & Algorithms</option>
                  <option value="Biology">Biology & Molecular Sciences</option>
                  <option value="Mathematics">Mathematics & Applied Statistics</option>
                </select>
              </div>

              <div className="quiz-question-block">
                <label>3. What is your primary career aspiration?</label>
                <select
                  value={formData.career_interest}
                  onChange={(e) =>
                    setFormData({ ...formData, career_interest: e.target.value })
                  }
                >
                  <option value="Software & AI">Software Engineering & Artificial Intelligence</option>
                  <option value="Medicine & Healthcare">Medicine, Clinical Practice & Biotech</option>
                  <option value="Data & Finance">Data Analytics, Quantitative Finance & Statistics</option>
                  <option value="Genomics & Research">Bioinformatics & Genomic Research</option>
                </select>
              </div>

              <div className="quiz-question-block">
                <label>4. What is your next educational milestone goal?</label>
                <select
                  value={formData.higher_study_goal}
                  onChange={(e) =>
                    setFormData({ ...formData, higher_study_goal: e.target.value })
                  }
                >
                  <option value="Immediate Jobs">Industry Placement immediately after Bachelor's</option>
                  <option value="Master's Degree">Pursue Master's Degree (M.S. / M.Tech)</option>
                  <option value="Research / PhD">Doctoral Studies & Research Lab Career</option>
                </select>
              </div>

              <div className="quiz-question-block">
                <label>5. Planned fee & university preference:</label>
                <select
                  value={formData.study_budget}
                  onChange={(e) =>
                    setFormData({ ...formData, study_budget: e.target.value })
                  }
                >
                  <option value="Low / Public University">Public / Government Merit University (Affordable)</option>
                  <option value="Medium">Reputed Semi-Private / State Institutions</option>
                  <option value="High / Private">Top Private / Global Universities</option>
                </select>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => setShowQuizModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="submit-btn"
                  disabled={submittingQuiz}
                >
                  {submittingQuiz ? "Computing Roadmaps..." : "Calculate My Course Matches 🎯"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default CourseGuidance;
