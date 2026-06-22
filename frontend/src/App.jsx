import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import { useAuth } from "./context/AuthContext.jsx";
import Admin from "./pages/Admin.jsx";
import ClauseVerification from "./pages/ClauseVerification.jsx";
import DocumentSummary from "./pages/DocumentSummary.jsx";
import GenerateDocument from "./pages/GenerateDocument.jsx";
import Home from "./pages/Home.jsx";
import LegalAdvisor from "./pages/LegalAdvisor.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";

export default function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/home" replace /> : <Login />}
      />
      <Route
        path="/register"
        element={isAuthenticated ? <Navigate to="/home" replace /> : <Register />}
      />

      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/home" element={<Home />} />
        <Route path="/legal-advisor" element={<LegalAdvisor />} />
        <Route path="/document-summary" element={<DocumentSummary />} />
        <Route path="/generate" element={<GenerateDocument />} />
        <Route path="/clause-verification" element={<ClauseVerification />} />
        <Route path="/admin" element={<Admin />} />
      </Route>

      <Route path="*" element={<Navigate to={isAuthenticated ? "/home" : "/login"} replace />} />
    </Routes>
  );
}
