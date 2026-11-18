
import { useState } from "react";
import axios from "axios";

function Login({ onLogin }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const [student, setStudent] = useState(null);

    const handleLogin = async (e) => {
        e.preventDefault();
        setMessage("Logging in...");

        try {
            const response = await axios.post(
                "http://127.0.0.1:8000/login",
                {
                    email: email,
                    password: password
                }
            );

            setStudent(response.data);
            setMessage("Login successful!");
            onLogin(response.data);

        } catch (error) {
            setStudent(null);
            setMessage(
                error.response?.data?.detail || "Login failed"
            );
        }
    };

    return (
        <div className="register-container">
            <h1>StudyMatch AI</h1>
            <h2>Student Login</h2>

            <form onSubmit={handleLogin}>
                <input
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />

                <input
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />

                <button type="submit">Login</button>
            </form>

            <p>{message}</p>

            {student && (
                <div>
                    <h3>Welcome, {student.name}!</h3>
                    <p>Email: {student.email}</p>
                    <p>Student ID: {student.student_id}</p>
                </div>
            )}
        </div>
    );
}

export default Login;
