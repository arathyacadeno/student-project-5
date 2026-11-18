
import { useState } from "react";
import "./App.css";

import Login from "./Login";
import Register from "./Register";
import Dashboard from "./Dashboard";

function App() {
  const [page, setPage] = useState("login");
  const [student, setStudent] = useState(null);

  const handleLogin = (studentData) => {
    setStudent(studentData);
    setPage("dashboard");
  };

  const handleLogout = () => {
    setStudent(null);
    setPage("login");
  };

  if (page === "dashboard" && student) {
    return (
      <Dashboard
        student={student}
        onLogout={handleLogout}
      />
    );
  }

  return (
    <div className="auth-page">
      {page === "login" ? (
        <>
          <Login onLogin={handleLogin} />
          <p>
            Don't have an account?{" "}
            <button onClick={() => setPage("register")}>
              Register
            </button>
          </p>
        </>
      ) : (
        <>
          <Register />
          <p>
            Already have an account?{" "}
            <button onClick={() => setPage("login")}>
              Login
            </button>
          </p>
        </>
      )}
    </div>
  );
}

export default App;
