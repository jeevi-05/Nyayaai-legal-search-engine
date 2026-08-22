import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function JudgeRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  return user.role === "JUDGE" ? children : <Navigate to="/dashboard" replace />;
}
