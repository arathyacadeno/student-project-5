<<<<<<< HEAD
import { useState } from "react";
=======
>>>>>>> c5b52f8b434c693f78a0a874b4f4b7f77bd0c366
import { useLocation } from "react-router-dom";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import BottomNav from "./BottomNav";
import ChatWidget from "./ChatWidget";

function Layout({ user, onLogout, children }) {
  const location = useLocation();
  const isMentorPage = location.pathname === "/mentor";
<<<<<<< HEAD
  const isStaff = ["teacher", "admin"].includes(user?.role);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className={`app-layout ${isStaff ? "teacher-layout" : "student-layout"}`}>
      <Navbar
        user={user}
        onLogout={onLogout}
        mobileMenuOpen={mobileMenuOpen}
        onMenuToggle={() => setMobileMenuOpen((open) => !open)}
      />
      <div className="layout-body">
        <Sidebar
          user={user}
          mobileOpen={mobileMenuOpen}
          onClose={() => setMobileMenuOpen(false)}
        />
=======
  const isTeacher = user?.role === "teacher";

  return (
    <div className="app-layout">
      <Navbar user={user} onLogout={onLogout} />
      <div className="layout-body">
        <Sidebar user={user} />
>>>>>>> c5b52f8b434c693f78a0a874b4f4b7f77bd0c366
        <main className="layout-main-content">
          {children}
        </main>
      </div>
      <BottomNav user={user} />
      {/* Floating AI Mentor Chatbot accessible everywhere for students except full mentor page */}
<<<<<<< HEAD
      {!isMentorPage && !isStaff && <ChatWidget user={user} />}
=======
      {!isMentorPage && !isTeacher && <ChatWidget user={user} />}
>>>>>>> c5b52f8b434c693f78a0a874b4f4b7f77bd0c366
    </div>
  );
}

export default Layout;
