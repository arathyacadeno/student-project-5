import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";

function StudentDashboard({ user }) {
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [profile, setProfile] = useState(null);
  const [materials, setMaterials] = useState([]);
  const [recommendedCourses, setRecommendedCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, profRes, matRes] = await Promise.all([
        api.get("/skill-profile/summary"),
        api.get("/profile/me"),
        api.get("/materials?limit=4"),
      ]);
      setSummary(sumRes.data);
      setProfile(profRes.data);
      setMaterials(matRes.data.items || []);

      // Also fetch top 2 course matches
      try {
        const crsRes = await api.get("/api/v1/guidance/courses/recommend");
        setRecommendedCourses((crsRes.data || []).slice(0, 2));
      } catch (cErr) {
        console.warn("Course recommendation preview fetch error:", cErr);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to load dashboard data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner message="Assembling your personalized dashboard..." />;
  if (error) return <ErrorMessage error={error} onRetry={fetchData} />;

  // Prepare chart data from subject breakdown
  const chartData = summary?.subject_breakdown
    ? Object.keys(summary.subject_breakdown).map((subj) => ({
        subject: subj,
        weak: summary.subject_breakdown[subj].weak,
        average: summary.subject_breakdown[subj].average,
        strong: summary.subject_breakdown[subj].strong,
        average_score: summary.subject_breakdown[subj].average_score,
      }))
    : [];

  return (
    <div className="dashboard-page">
      {/* Welcome Banner */}
      <section className="welcome-banner">
        <div className="welcome-text">
          <h2>Welcome back, {user?.name || "Student"}! 👋</h2>
          <p className="welcome-subtitle">
            {profile?.learning_goal ||
              "Your personalized academic pathway is powered by real-time skill tracking."}
          </p>
          <div className="profile-meta-tags">
            {profile?.course && <span className="meta-tag">📘 {profile.course}</span>}
            {profile?.stream && <span className="meta-tag">🔬 {profile.stream}</span>}
            {profile?.academic_level && (
              <span className="meta-tag">🎯 {profile.academic_level}</span>
            )}
          </div>
        </div>
        <div className="welcome-actions">
          <button
            className="action-btn-primary"
            onClick={() => navigate("/mock-tests")}
          >
            🚀 Launch Adaptive Mock Test
          </button>
          <button
            className="action-btn-secondary"
            onClick={() => navigate("/mentor")}
          >
            🤖 Chat with AI Mentor
          </button>
        </div>
      </section>

      {/* KPI Cards */}
      <section className="kpi-grid">
        <div className="kpi-card danger">
          <div className="kpi-icon">⚠️</div>
          <div className="kpi-details">
            <span className="kpi-num">{summary?.weak_count || 0}</span>
            <span className="kpi-label">Weak Topics</span>
            <span className="kpi-subtext">Require focused review</span>
          </div>
        </div>

        <div className="kpi-card warning">
          <div className="kpi-icon">⚖️</div>
          <div className="kpi-details">
            <span className="kpi-num">{summary?.average_count || 0}</span>
            <span className="kpi-label">Developing Topics</span>
            <span className="kpi-subtext">On track for mastery</span>
          </div>
        </div>

        <div className="kpi-card success">
          <div className="kpi-icon">🌟</div>
          <div className="kpi-details">
            <span className="kpi-num">{summary?.strong_count || 0}</span>
            <span className="kpi-label">Strong Topics</span>
            <span className="kpi-subtext">Ready to peer-teach!</span>
          </div>
        </div>

        <div className="kpi-card info">
          <div className="kpi-icon">📈</div>
          <div className="kpi-details">
            <span className="kpi-num">{summary?.average_mastery || 0}%</span>
            <span className="kpi-label">Overall Mastery</span>
            <span className="kpi-subtext">Across all subjects</span>
          </div>
        </div>
      </section>

      {/* Priority Action: Weak Topics Remediation Banner */}
      {summary?.weak_topics && summary.weak_topics.length > 0 && (
        <section className="priority-card">
          <div className="priority-header">
            <div className="priority-title">
              <span className="pulse-dot"></span>
              <h3>Priority Focus: Identified Weak Topics</h3>
            </div>
            <span className="priority-badge">Action Recommended</span>
          </div>
          <p className="priority-desc">
            Your recent assessments indicate lower proficiency in the following topics.
            Study materials and adaptive mock tests have been customized for these:
          </p>
          <div className="weak-topic-pills">
            {summary.weak_topics.map((topic, idx) => (
              <div key={idx} className="weak-topic-pill">
                <span className="pill-topic-name">{topic}</span>
                <div className="pill-actions">
                  <button
                    className="pill-action-notes"
                    onClick={() => navigate(`/materials?search=${encodeURIComponent(topic)}`)}
                  >
                    📖 Read Notes
                  </button>
                  <button
                    className="pill-action-test"
                    onClick={() => navigate("/mock-tests")}
                  >
                    📝 Test Now
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Top Future Course Matches Banner */}
      {recommendedCourses.length > 0 && (
        <section className="teacher-section-card" style={{ marginBottom: "24px" }}>
          <div className="card-head-row">
            <div>
              <h3>🎓 Top Higher-Study Matches (Module 4 Recommender)</h3>
              <p className="subtext">
                Ranked using your skill profile strengths and academic preferences
              </p>
            </div>
            <button
              className="action-btn-secondary btn-sm"
              onClick={() => navigate("/guidance")}
            >
              Explore All Courses →
            </button>
          </div>

          <div className="courses-grid" style={{ marginTop: "12px" }}>
            {recommendedCourses.map((crs) => (
              <div key={crs.id} className="course-card-enhanced">
                <div className="course-card-header">
                  <span className="match-badge match-high">
                    {crs.match_score ?? crs.match_percentage ?? 85}% Match
                  </span>
                  <span className="stream-pill">{crs.stream}</span>
                </div>
                <h4 style={{ margin: "6px 0", fontSize: "15px" }}>{crs.title}</h4>
                <p style={{ fontSize: "12px", color: "#334155", margin: "4px 0 10px" }}>
                  💡 <strong>Reason:</strong> {crs.match_reason || crs.recommended_reason || "Aligned with your strengths"}
                </p>
                <div className="card-bottom-actions">
                  <button
                    className="action-btn-secondary btn-sm"
                    onClick={() => navigate("/guidance")}
                  >
                    View Details & Roadmaps →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Analytics Chart & Next Step Grid */}
      <div className="dashboard-split-grid">
        {/* Recharts Topic Proficiency Chart */}
        <section className="dashboard-chart-card">
          <h3>📊 Subject Skill Profile Distribution</h3>
          <p className="card-subtext">Breakdown of weak, average, and strong topics by subject</p>
          <div className="chart-wrapper">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={chartData} margin={{ top: 15, right: 20, left: -10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="subject" tick={{ fill: "#475569", fontSize: 12 }} />
                  <YAxis allowDecimals={false} tick={{ fill: "#475569", fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#ffffff",
                      borderRadius: "8px",
                      boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                    }}
                  />
                  <Legend />
                  <Bar dataKey="weak" name="Weak Topics" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="average" name="Average Topics" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="strong" name="Strong Topics" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="no-data-msg">Take a mock test to generate skill distribution charts.</p>
            )}
          </div>
        </section>

        {/* Personalized Next Steps */}
        <section className="dashboard-quick-actions-card">
          <h3>🎯 Recommended Next Actions</h3>
          <div className="quick-actions-list">
            <div className="quick-action-item" onClick={() => navigate("/materials")}>
              <span className="qa-icon">📚</span>
              <div className="qa-text">
                <strong>Study Materials Priority Feed</strong>
                <span>Weak topic notes are automatically pinned to the top of your feed.</span>
              </div>
              <span className="qa-arrow">→</span>
            </div>

            <div className="quick-action-item" onClick={() => navigate("/mock-tests")}>
              <span className="qa-icon">📝</span>
              <div className="qa-text">
                <strong>Adaptive Mock Test</strong>
                <span>Difficulty auto-adjusts based on your latest skill levels.</span>
              </div>
              <span className="qa-arrow">→</span>
            </div>

            <div className="quick-action-item" onClick={() => navigate("/guidance")}>
              <span className="qa-icon">🎓</span>
              <div className="qa-text">
                <strong>Future Course Guidance</strong>
                <span>Explore higher studies matching your strengths and questionnaire.</span>
              </div>
              <span className="qa-arrow">→</span>
            </div>

            <div className="quick-action-item" onClick={() => navigate("/papers")}>
              <span className="qa-icon">📄</span>
              <div className="qa-text">
                <strong>Solved Previous Papers</strong>
                <span>Timed practice with verified step-by-step solutions.</span>
              </div>
              <span className="qa-arrow">→</span>
            </div>
          </div>
        </section>
      </div>

      {/* Recommended Materials Section */}
      <section className="dashboard-materials-preview">
        <div className="section-head-row">
          <div>
            <h3>Recommended Study Materials</h3>
            <span className="card-subtext">Curated specifically from your weak and developing topics</span>
          </div>
          <button className="view-all-link" onClick={() => navigate("/materials")}>
            View All Materials →
          </button>
        </div>

        <div className="materials-preview-grid">
          {materials.map((mat) => (
            <div key={mat.id} className="preview-mat-card">
              <div className="card-top-badges">
                <span className="subject-badge">{mat.subject}</span>
                {mat.is_weak_topic && (
                  <span className="weak-priority-badge">⚠️ Weak Topic</span>
                )}
              </div>
              <h4>{mat.title}</h4>
              <p className="mat-summary-preview">{mat.summary}</p>
              <div className="card-footer-action">
                <span className="topic-tag">📌 {mat.topic}</span>
                <button
                  className="read-btn-sm"
                  onClick={() => navigate(`/materials?search=${encodeURIComponent(mat.title)}`)}
                >
                  Read →
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default StudentDashboard;
