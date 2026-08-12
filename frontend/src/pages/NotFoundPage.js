import { Link } from "react-router-dom";
import { Scale, ArrowLeft } from "lucide-react";

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="text-center max-w-md">
        <div className="w-20 h-20 bg-navy-50 rounded-3xl flex items-center justify-center mx-auto mb-6">
          <Scale size={36} className="text-navy-400" strokeWidth={1.5} />
        </div>
        <h1 className="text-7xl font-bold text-navy-600 mb-2">404</h1>
        <p className="text-xl font-semibold text-gray-700 mb-2">Page Not Found</p>
        <p className="text-gray-400 text-sm mb-8 leading-relaxed">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link to="/" className="btn-primary px-8 py-3 rounded-2xl text-base">
          <ArrowLeft size={16} /> Back to Home
        </Link>
      </div>
    </div>
  );
}
