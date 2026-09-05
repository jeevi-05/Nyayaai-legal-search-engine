import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function LawyerRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-navy-600" /></div>;
  if (!user) return <Navigate to="/login" replace />;
  return user.role === "LAWYER" ? children : <Navigate to="/dashboard" replace />;
}
