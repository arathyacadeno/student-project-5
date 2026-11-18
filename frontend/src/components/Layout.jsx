import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import BottomNav from "./BottomNav";

function Layout({ user, onLogout, children }) {
  return (
    <div className="app-layout">
      <Navbar user={user} onLogout={onLogout} />
      <div className="layout-body">
        <Sidebar user={user} />
        <main className="layout-main-content">
          {children}
        </main>
      </div>
      <BottomNav user={user} />
    </div>
  );
}

export default Layout;
