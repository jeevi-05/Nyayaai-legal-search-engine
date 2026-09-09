import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { AlertCircle, UserPlus, User, Briefcase, Gavel } from "lucide-react";
import { getErrorMessage } from "../utils/helpers";

const ROLES = [
  { value: "CIVILIAN", label: "Citizen",  icon: User,      desc: "General public" },
  { value: "LAWYER",   label: "Lawyer",   icon: Briefcase, desc: "Legal practitioner" },
  { value: "JUDGE",    label: "Judge",    icon: Gavel,     desc: "Judicial officer" },
];

export default function RegisterPage() {
  const { user, loading: authLoading, register } = useAuth();
  const navigate = useNavigate();

  // Redirect if already logged in
  useEffect(() => {
    if (user && !authLoading) {
      // Navigate to unified dashboard; it will show role-based features
      navigate('/dashboard', { replace: true });
    }
  }, [user, authLoading, navigate]);

  const [fullName, setFullName] = useState("");
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole]         = useState("CIVILIAN");
  const [error, setError]       = useState("");
  const [loading, setLoading]   = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await register(fullName, email, password, role);
      sessionStorage.setItem("nyayaai_pending_email", email.trim().toLowerCase());
      navigate('/verify-otp', { replace: true, state: { maskedEmail: result.email } });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="mb-8">
        <p className="section-label">Join NyayaAI</p>
        <h2 className="text-3xl font-normal text-navy-800">Create Your Account</h2>
        <p className="text-gray-500 text-sm mt-1">Access AI-powered Indian legal research</p>
      </div>

      {error && (
        <div className="mb-5 flex items-start gap-2.5 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
          <AlertCircle size={16} className="shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Full Name</label>
          <input
            className="input-field"
            placeholder="Your full name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Email Address</label>
          <input
            className="input-field"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
          <input
            className="input-field"
            type="password"
            placeholder="Create a strong password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        {/* Role selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">I am a...</label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            {ROLES.map(({ value, label, icon: Icon, desc }) => (
              <button
                key={value}
                type="button"
                onClick={() => setRole(value)}
                className={`flex items-center gap-2.5 px-3 py-3 rounded-lg border text-left transition-all ${
                  role === value
                    ? "border-gold-500 bg-gold-50 text-navy-800 shadow-sm"
                    : "border-[#ded9ce] text-gray-600 hover:border-gold-300 hover:bg-[#fcfaf4]"
                }`}
              >
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                  role === value ? "bg-navy-600 text-white" : "bg-gray-100 text-gray-500"
                }`}>
                  <Icon size={15} />
                </div>
                <div>
                  <p className="text-xs font-semibold">{label}</p>
                  <p className="text-[10px] text-gray-400">{desc}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full py-3 rounded-xl mt-1"
        >
          {loading ? (
            <><span className="spinner" /> Creating account...</>
          ) : (
            <><UserPlus size={16} /> Create Account</>
          )}
        </button>
      </form>

      <div className="mt-6 pt-5 border-t border-gray-100 text-center">
        <p className="text-sm text-gray-500">
          Already have an account?{" "}
          <Link to="/login" className="text-navy-600 font-semibold hover:text-gold-500 transition-colors">
            Sign in →
          </Link>
        </p>
      </div>
    </>
  );
}
