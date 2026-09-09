import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function CitizenRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="py-24 text-center text-sm text-gray-500">Checking access…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return user.role === "CIVILIAN" ? children : <Navigate to="/dashboard" replace />;
}
