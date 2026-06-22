import { ArrowRight, Eye, EyeOff, Gavel, Lock, User } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [remember, setRemember] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (!username || !password) {
      setError("Please enter your username/email and password.");
      return;
    }
    setLoading(true);
    try {
      await login({ username, password });
      navigate("/home");
    } catch (err) {
      setError(err?.response?.data?.error || "Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-bg">
      <div className="auth-center">
        <div className="auth-logo">
          <div className="logo-tile">
            <Gavel size={26} strokeWidth={2.2} />
          </div>
          <div className="auth-title">JurisAI</div>
          <div className="auth-sub">A smart legal advisor and document assistant</div>
        </div>

        <div className="auth-card">
          <h2>Welcome back</h2>
          <p className="sub">Please enter your credentials to access your cases.</p>

          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>Username</label>
              <div className="input-icon">
                <User size={17} />
                <input
                  className="input"
                  placeholder="e.g. j.smith@firm.com"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoComplete="username"
                />
              </div>
            </div>

            <div className="field">
              <div className="auth-row">
                <label style={{ margin: 0 }}>Password</label>
                <span className="link" style={{ fontSize: 13 }}>
                  Forgot Password?
                </span>
              </div>
              <div className="input-icon">
                <Lock size={17} />
                <input
                  className="input"
                  type={showPwd ? "text" : "password"}
                  placeholder="••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  style={{ paddingRight: 42 }}
                />
                <button
                  type="button"
                  onClick={() => setShowPwd((s) => !s)}
                  style={{
                    position: "absolute",
                    right: 12,
                    top: "50%",
                    transform: "translateY(-50%)",
                    background: "none",
                    border: "none",
                    color: "var(--muted-2)",
                  }}
                  aria-label="Toggle password visibility"
                >
                  {showPwd ? <EyeOff size={17} /> : <Eye size={17} />}
                </button>
              </div>
            </div>

            <label className="remember">
              <input
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
              />
              Remember this device
            </label>

            {error && <p className="error-text" style={{ marginBottom: 12 }}>{error}</p>}

            <button className="btn btn-primary btn-block" disabled={loading}>
              {loading ? <span className="spinner" /> : (
                <>
                  Login to Dashboard <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          <div className="auth-foot">
            Don&apos;t have an account? <Link className="link" to="/register">Sign up</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
