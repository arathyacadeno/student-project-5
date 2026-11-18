
import { useState } from "react";
import axios from "axios";

function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();
    setMessage("Registering...");

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/register",
        {
          name: name,
          email: email,
          password: password
        }
      );

      setMessage("Registration successful!");
      setName("");
      setEmail("");
      setPassword("");

    } catch (error) {
      setMessage(
        error.response?.data?.detail || "Registration failed"
      );
    }
  };

  return (
    <div className="register-container">
      <h1>StudyMatch AI</h1>
      <h2>Student Registration</h2>

      <form onSubmit={handleRegister}>
        <input
          type="text"
          placeholder="Enter your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

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

        <button type="submit">Register</button>
      </form>

      <p>{message}</p>
    </div>
  );
}

export default Register;
