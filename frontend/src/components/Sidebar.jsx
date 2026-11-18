import { NavLink } from "react-router-dom";

function Sidebar({ user }) {
  const isTeacher = user?.role === "teacher";

  const navItems = [
    { to: "/dashboard", label: "Dashboard", icon: "📊" },
    { to: "/materials", label: "Study Materials", icon: "📚" },
    { to: "/guidance", label: "Course Guidance", icon: "🎓" },
    { to: "/mentor", label: "AI Mentor", icon: "🤖" },
    { to: "/mock-tests", label: "Mock Tests", icon: "📝" },
    { to: "/summaries", label: "Course Summaries", icon: "📖" },
    { to: "/papers", label: "Previous Papers", icon: "📄" },
  ];

  if (isTeacher) {
    navItems.push({ to: "/teacher", label: "Teacher Dashboard", icon: "👨‍🏫" });
  }

  return (
    <aside className="app-sidebar">
      <div className="sidebar-menu-heading">NAVIGATION</div>
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? "active" : ""}`
            }
          >
            <span className="sidebar-icon">{item.icon}</span>
            <span className="sidebar-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-tip">
          <span className="tip-title">💡 Study Tip</span>
          <p>Mock tests update your Skill Profile and recommend targeted materials.</p>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
