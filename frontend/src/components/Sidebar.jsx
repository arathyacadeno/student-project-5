import { NavLink } from "react-router-dom";

function Sidebar({ user, mobileOpen, onClose }) {
  const isTeacher = user?.role === "teacher";
  const isAdmin = user?.role === "admin";
  const isStaff = isTeacher || isAdmin;

  const studentNavItems = [
    { to: "/dashboard", label: "Dashboard", icon: "📊" },
    { to: "/quiz", label: "Topic Quiz", icon: "🎯" },
    { to: "/groups", label: "Study Groups", icon: "👥" },
    { to: "/materials", label: "Study Materials", icon: "📚" },
    { to: "/videos", label: "Course Videos", icon: "▶️" },
    { to: "/guidance", label: "Course Guidance", icon: "🎓" },
    { to: "/mentor", label: "AI Mentor", icon: "🤖" },
    { to: "/mock-tests", label: "Mock Tests", icon: "📝" },
    { to: "/summaries", label: "Course Summaries", icon: "📖" },
    { to: "/papers", label: "Previous Papers", icon: "📄" },
  ];

  const teacherNavItems = [
    { to: "/teacher", label: "Teacher Dashboard", icon: "👨‍🏫" },
    { to: "/teacher/manage", label: "Manage Content", icon: "🛠️" },
    { to: "/materials", label: "Study Materials", icon: "📚" },
    { to: "/groups", label: "Study Groups", icon: "👥" },
    { to: "/summaries", label: "Course Summaries", icon: "📖" },
    { to: "/papers", label: "Previous Papers", icon: "📄" },
    { to: "/videos", label: "Course Videos", icon: "▶️" },
    { to: "/mentor", label: "AI Mentor", icon: "🤖" },
  ];

  const adminNavItems = [
    { to: "/admin", label: "Admin Dashboard", icon: "🛡️" },
    { to: "/admin/manage/teacher-requests", label: "Teacher Requests", icon: "👨‍🏫" },
    { to: "/admin/manage/accounts", label: "Accounts", icon: "👥" },
    { to: "/admin/manage/classes", label: "Classes", icon: "🏫" },
    { to: "/admin/manage/content", label: "Content Management", icon: "🛠️" },
  ];

  const navItems = isAdmin
    ? adminNavItems
    : isTeacher
    ? teacherNavItems
    : (() => {
        const items = [...studentNavItems];
        items.splice(1, 0, { to: "/profile", label: "My Profile", icon: "👤" });
        return items;
      })();

  return (
    <>
      {!isStaff && mobileOpen && (
        <button
          className="mobile-sidebar-backdrop"
          type="button"
          aria-label="Close navigation menu"
          onClick={onClose}
        />
      )}
      <aside
        id={!isStaff ? "student-mobile-sidebar" : undefined}
        className={`app-sidebar ${!isStaff ? "student-mobile-sidebar" : ""} ${mobileOpen && !isStaff ? "mobile-open" : ""}`}
      >
        <div className="sidebar-top">
          <div className="sidebar-menu-heading">NAVIGATION</div>
          <nav className="sidebar-nav">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/admin" || item.to === "/teacher"}
                onClick={onClose}
                className={({ isActive }) =>
                  `sidebar-link ${isActive ? "active" : ""}`
                }
              >
                <span className="sidebar-icon">{item.icon}</span>
                <span className="sidebar-label">{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="sidebar-footer">
          {isTeacher ? (
            <div className="sidebar-tip">
              <span className="tip-title">💡 Teacher Tip</span>
              <p>Manage curriculum content, track class progress, and review student counselling requests.</p>
            </div>
          ) : isAdmin ? (
            <div className="sidebar-tip">
              <span className="tip-title">🛡️ Admin Tip</span>
              <p>Approve pending teacher requests and oversee platform institutions.</p>
            </div>
          ) : (
            <div className="sidebar-tip">
              <span className="tip-title">💡 Study Tip</span>
              <p>Mock tests update your Skill Profile and recommend targeted materials.</p>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
