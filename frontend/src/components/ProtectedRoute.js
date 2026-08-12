import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { hasModeAccess } from "../config/roles";

export default function ProtectedRoute({ children }) {
  const { user, loading, mode } = useAuth();

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-navy-600"></div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Check if user has access to current mode
  if (mode && !hasModeAccess(user.role, mode.id)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="max-w-md text-center px-6">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-navy-600 mb-3">Access Denied</h2>
          <p className="text-gray-600 mb-6">
            This feature is available only for authorized users. Your role does not permit access to this section.
          </p>
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-left mb-6">
            <p className="text-sm text-red-700">
              <strong>Permission Required:</strong> {mode?.name || "This mode"}
            </p>
            <p className="text-sm text-red-700">
              <strong>Your Role:</strong> {user.role}
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <a href="/" className="btn-primary px-6 py-2.5 rounded-xl">
              Go to Dashboard
            </a>
          </div>
        </div>
      </div>
    );
  }

  return children;
}
