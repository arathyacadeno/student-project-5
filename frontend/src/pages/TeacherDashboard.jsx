import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";

function TeacherDashboard({ user }) {
  const navigate = useNavigate();

  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get("/teacher/dashboard");
      setStats(res.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load teacher analytics. Are you logged in as a teacher?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) return <LoadingSpinner message="Aggregating class analytics & weak topics..." />;
  if (error) return <ErrorMessage error={error} onRetry={fetchStats} />;

  return (
    <div className="teacher-dashboard-page">
      {/* Header */}
      <div className="page-header-row">
        <div>
          <h2>👨‍🏫 Teacher Academic Command Center ({user?.name || "Teacher"})</h2>
          <p className="page-subtitle">
            Monitor class-wide weak topics, identify at-risk students, and publish instructional resources.
          </p>
        </div>
        <div className="teacher-top-actions">
          <button
            className="action-btn-primary"
            onClick={() => navigate("/materials")}
          >
            + Upload Study Material
          </button>
        </div>
      </div>

      {/* KPI Stats */}
      <section className="kpi-grid">
        <div className="kpi-card info">
          <div className="kpi-icon">👥</div>
          <div className="kpi-details">
            <span className="kpi-num">{stats?.total_students || 0}</span>
            <span className="kpi-label">Enrolled Students</span>
            <span className="kpi-subtext">Active skill profiles</span>
          </div>
        </div>

        <div className="kpi-card danger">
          <div className="kpi-icon">🚨</div>
          <div className="kpi-details">
            <span className="kpi-num">{stats?.at_risk_students?.length || 0}</span>
            <span className="kpi-label">Students Needing Support</span>
            <span className="kpi-subtext">Have 1+ weak topics</span>
          </div>
        </div>

        <div className="kpi-card success">
          <div className="kpi-icon">📚</div>
          <div className="kpi-details">
            <span className="kpi-num">{stats?.total_materials || 0}</span>
            <span className="kpi-label">Study Materials</span>
            <span className="kpi-subtext">Published across 3 subjects</span>
          </div>
        </div>

        <div className="kpi-card warning">
          <div className="kpi-icon">📄</div>
          <div className="kpi-details">
            <span className="kpi-num">{stats?.total_papers || 0}</span>
            <span className="kpi-label">Solved Papers</span>
            <span className="kpi-subtext">Previous year exams</span>
          </div>
        </div>
      </section>

      {/* Grid: Class Weak Topics & At-Risk Students */}
      <div className="teacher-split-grid">
        {/* Class Weak Topics Heatmap */}
        <section className="teacher-section-card">
          <div className="card-head-row">
            <div>
              <h3>⚠️ Class-Wide Topic Difficulty Heatmap</h3>
              <p className="subtext">Topics where the highest number of students are struggling</p>
            </div>
          </div>

          <div className="class-topics-table-wrapper">
            <table className="teacher-table">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Topic</th>
                  <th>Struggling Students</th>
                  <th>Class Avg</th>
                  <th>Linked Materials</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {stats?.class_weak_topics?.map((item, idx) => (
                  <tr key={idx}>
                    <td>
                      <span className="subject-pill">{item.subject}</span>
                    </td>
                    <td>
                      <strong>{item.topic}</strong>
                    </td>
                    <td>
                      <span className="weak-count-badge">
                        {item.weak_students_count} Students
                      </span>
                    </td>
                    <td>{item.average_mastery}%</td>
                    <td>
                      <span className="materials-count-pill">
                        {item.linked_materials_count} Resources
                      </span>
                    </td>
                    <td>
                      <button
                        className="table-action-btn"
                        onClick={() =>
                          navigate(`/materials?search=${encodeURIComponent(item.topic)}`)
                        }
                      >
                        View Notes →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* At-Risk Students List */}
        <section className="teacher-section-card">
          <div className="card-head-row">
            <div>
              <h3>🚨 Students Requiring Personal Intervention</h3>
              <p className="subtext">Identified via adaptive mock test marks and skill analytics</p>
            </div>
          </div>

          <div className="at-risk-list">
            {stats?.at_risk_students?.length === 0 ? (
              <p className="all-good-msg">🎉 All students are performing above average!</p>
            ) : (
              stats?.at_risk_students?.map((st) => (
                <div key={st.student_id} className="at-risk-card">
                  <div className="at-risk-top">
                    <div className="at-risk-user">
                      <span className="user-icon-circle">
                        {st.name.charAt(0).toUpperCase()}
                      </span>
                      <div>
                        <strong>{st.name}</strong>
                        <span className="user-email-text">{st.email}</span>
                      </div>
                    </div>
                    <span className="weak-flag">
                      {st.weak_topics_count} Weak Topics
                    </span>
                  </div>

                  <div className="student-weak-pills">
                    {st.weak_topics.map((t, i) => (
                      <span key={i} className="danger-topic-pill">
                        ⚠️ {t}
                      </span>
                    ))}
                  </div>

                  <div className="at-risk-footer">
                    <span>Overall Mastery: <strong>{st.average_mastery}%</strong></span>
                    <button
                      className="contact-btn"
                      onClick={() =>
                        alert(
                          `Intervention memo created for ${st.name}. StudyMatch AI peer group matcher will pair ${st.name} with a strong peer in: ${st.weak_topics.join(", ")}.`
                        )
                      }
                    >
                      🤝 Pair in Peer Study Group
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

export default TeacherDashboard;
