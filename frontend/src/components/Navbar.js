import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useMode } from "../context/ModeContext";
import { getRoleFeatures, ROLE_NAMES } from "../config/roles";
import {
  Scale, Search, LogOut, Menu, X, ChevronDown, Gavel, GitCompare,
  Brain, TrendingUp, FileText, Upload, LayoutDashboard
} from "lucide-react";

export default function Navbar() {
  const { user, logout, loading } = useAuth();
  const { mode } = useMode();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
    setMobileOpen(false);
    setProfileOpen(false);
  };

  const isActive = (path) => location.pathname === path;

  // Get role-specific features for navigation
  const navFeatures = user ? getRoleFeatures(user.role) : [];

  // Get role display name
  const roleName = user ? ROLE_NAMES[user.role] || user.role : null;

  return (
    <nav className="bg-navy-600 shadow-nav sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">

          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 shrink-0" onClick={() => setMobileOpen(false)}>
            <div className="w-9 h-9 bg-gold-400 rounded-lg flex items-center justify-center shadow-sm">
              <Scale size={20} className="text-navy-700" strokeWidth={2.5} />
            </div>
            <div className="leading-none">
              <span className="text-white font-bold text-lg tracking-tight">NyayaAI</span>
              <span className="block text-gold-400 text-[10px] font-semibold tracking-widest uppercase">Legal Intelligence</span>
            </div>
          </Link>

          {/* Role Badge - Desktop */}
          {user && !loading && (
            <div className="hidden md:flex items-center gap-2">
              <span className="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold text-white">
                {roleName}
              </span>
            </div>
          )}

          {/* Desktop nav - Role specific features */}
          {user && !loading && mode && (
            <div className="hidden md:flex items-center gap-1">
              <Link
                to="/dashboard"
                className={`flex items-center gap-1.5 text-sm px-3 py-2 rounded-lg font-medium transition-all duration-150 ${
                  isActive("/dashboard") ? `${mode.activeColor}` : `${mode.navColor}`
                }`}
              >
                <LayoutDashboard size={15} />
                Dashboard
              </Link>
              {user.role === "JUDGE" && <span className="text-gold-400 text-[10px] font-bold uppercase tracking-wider px-1">Judicial Intelligence</span>}
              {navFeatures.map(({ id, name, path }) => {
                const Icon = getNavIcon(id);
                return (
                  <Link
                    key={id}
                    to={path}
                    className={`flex items-center gap-1.5 text-sm px-3 py-2 rounded-lg font-medium transition-all duration-150 ${
                      isActive(path)
                        ? `${mode.activeColor}`
                        : `${mode.navColor}`
                    }`}
                  >
                    <Icon size={15} />
                    {name}
                  </Link>
                );
              })}
              {user.role === "ADMIN" && (
                <Link
                  to="/upload"
                  className={`flex items-center gap-1.5 text-sm px-3 py-2 rounded-lg font-medium transition-all duration-150 ${
                    isActive("/upload")
                      ? "bg-gold-400 text-navy-700"
                      : "text-navy-100 hover:text-white hover:bg-white/10"
                  }`}
                >
                  <Upload size={15} />
                  Upload
                </Link>
              )}
            </div>
          )}

          {/* Right side */}
          <div className="flex items-center gap-2">
            {user ? (
              <>
                {/* Profile dropdown */}
                <div className="relative hidden md:block">
                  <button
                    onClick={() => setProfileOpen((v) => !v)}
                    className="flex items-center gap-2 bg-white/10 hover:bg-white/20 rounded-xl pl-1.5 pr-3 py-1.5 transition-all"
                  >
                    <div className="w-7 h-7 rounded-lg bg-gold-400 flex items-center justify-center">
                      <span className="text-navy-700 font-bold text-xs">
                        {user.fullName?.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <span className="text-white text-sm font-medium max-w-[100px] truncate">{user.fullName}</span>
                    <ChevronDown size={14} className={`text-navy-200 transition-transform ${profileOpen ? "rotate-180" : ""}`} />
                  </button>

                  {profileOpen && (
                    <div className="absolute right-0 mt-2 w-52 bg-white rounded-2xl shadow-card-hover border border-gray-100 py-2 z-50">
                      <div className="px-4 py-2 border-b border-gray-100 mb-1">
                        <p className="text-xs font-semibold text-navy-600 truncate">{user.fullName}</p>
                        <p className="text-xs text-gray-400 truncate">{user.email}</p>
                        <span className="badge bg-navy-50 text-navy-600 mt-1">{user.role}</span>
                      </div>
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                      >
                        <LogOut size={14} />
                        Sign Out
                      </button>
                    </div>
                  )}
                </div>

                {/* Mobile hamburger */}
                <button
                  onClick={() => setMobileOpen((v) => !v)}
                  className="md:hidden text-white p-2 rounded-lg hover:bg-white/10 transition"
                >
                  {mobileOpen ? <X size={20} /> : <Menu size={20} />}
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="hidden sm:block text-sm text-navy-200 hover:text-white font-medium px-3 py-2 rounded-lg hover:bg-white/10 transition">
                  Sign In
                </Link>
                <Link to="/register" className="btn-gold text-xs px-4 py-2">
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && user && !loading && mode && (
        <div className="md:hidden bg-navy-700 border-t border-white/10 px-4 py-3 space-y-1">
          {/* Role Badge - Mobile */}
          <div className="mb-2">
            <span className="inline-block px-3 py-1 bg-white/10 rounded-full text-xs font-semibold text-white">
              {roleName}
            </span>
          </div>

          <Link
            to="/dashboard"
            onClick={() => setMobileOpen(false)}
            className={`flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-medium transition ${
              isActive("/dashboard") ? mode.activeColor : mode.navColor
            }`}
          >
            <LayoutDashboard size={16} /> Dashboard
          </Link>

          {navFeatures.map(({ id, name, path }) => {
            const Icon = getNavIcon(id);
            return (
              <Link
                key={id}
                to={path}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-medium transition ${
                  isActive(path) ? mode.activeColor : mode.navColor
                }`}
              >
                <Icon size={16} />
                {name}
              </Link>
            );
          })}
          {user.role === "ADMIN" && (
            <Link to="/upload" onClick={() => setMobileOpen(false)}
              className={`flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-medium transition ${
                isActive("/upload") ? "bg-gold-400 text-navy-700" : "text-navy-100 hover:bg-white/10 hover:text-white"
              }`}
            >
              <Upload size={16} /> Upload
            </Link>
          )}
          <div className="border-t border-white/10 pt-2 mt-2">
            <div className="px-3 py-2">
              <p className="text-white text-sm font-semibold">{user.fullName}</p>
              <p className="text-navy-300 text-xs">{user.email}</p>
            </div>
            <button onClick={handleLogout}
              className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-red-400 hover:bg-red-500/10 rounded-xl transition"
            >
              <LogOut size={16} /> Sign Out
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}

// Helper function to get navigation icon by feature ID
function getNavIcon(featureId) {
  const iconMap = {
    'legal-research': Search,
    'precedent-research': GitCompare,
    'judgment-analysis': Gavel,
    'judgment-comparison': GitCompare,
    'legal-reasoning': Brain,
    'legal-trends': TrendingUp,
    'judge-comparison': GitCompare,
    'judge-precedents': Search,
    'judge-reasoning': Brain,
    'judge-synthesis': Scale,
    'advanced-search': Search,
    'advanced-research': Search,
    'criminal-case-research': Search,
    'legal-provisions': FileText,
    'fir-analysis': FileText,
    'citizen-ask-question': Scale,
    'citizen-legal-research': Search,
    'citizen-legal-repository': FileText,
    'citizen-case-analysis': FileText,
    'citizen-find-lawyer': Scale,
    'ask-question': Scale,
    'explain-document': FileText,
    'find-laws': Search,
    'citation-finder': Search,
    'argument-research': Search,
    'case-brief-generation': FileText,
    'investigation-guide': FileText,
    'evidence-research': Search,
    'timeline-analyzer': FileText,
    'understand-rights': Scale,
    'court-procedures': Scale,
    'legal-terms': FileText,
  };
  return iconMap[featureId] || Search;
}
