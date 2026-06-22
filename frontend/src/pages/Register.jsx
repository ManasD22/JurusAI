import { ArrowRight, Gavel } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (!fullName || !email || !password) {
      setError("Please fill in all fields.");
      return;
    }
    setLoading(true);
    try {
      await register({ full_name: fullName, email, password });
      navigate("/home");
    } catch (err) {
      const data = err?.response?.data;
      const msg =
        data?.email?.[0] ||
        data?.password?.[0] ||
        data?.username?.[0] ||
        "Could not create the account. Please try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="split">
      <div className="split-left">
        <div className="logo-tile">
          <Gavel size={30} strokeWidth={2.2} />
        </div>
        <h1>JurisAI</h1>
        <p>A smart legal advisor and document assistant</p>
      </div>

      <div className="split-right">
        <form className="split-form" onSubmit={handleSubmit}>
          <h2>Create Account</h2>

          <div className="field">
            <label>Full Name</label>
            <input
              className="input"
              placeholder="Johnathan Doe"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          </div>

          <div className="field">
            <label>Email Address</label>
            <input
              className="input"
              type="email"
              placeholder="j.doe@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="field">
            <label>Password</label>
            <input
              className="input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error && <p className="error-text" style={{ marginBottom: 12 }}>{error}</p>}

          <button className="btn btn-primary btn-block" disabled={loading} style={{ marginTop: 6 }}>
            {loading ? <span className="spinner" /> : (
              <>
                Create Account <ArrowRight size={18} />
              </>
            )}
          </button>

          <div className="auth-foot">
            Already have an account? <Link className="link" to="/login">Log in</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
