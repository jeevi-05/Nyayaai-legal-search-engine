import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useMode } from "../context/ModeContext";
import { getDashboard } from "../services/dashboardService";
import { getCount } from "../services/documentService";
import {
  BookOpen, Search, Gavel, Brain, CheckCircle, Users,
  ArrowRight, LayoutDashboard, MessageCircle, Scale, FileText
} from "lucide-react";

const ROLE_COLORS = {
  ADMIN:    "bg-red-100 text-red-700",
  JUDGE:    "bg-purple-100 text-purple-700",
  LAWYER:   "bg-blue-100 text-blue-700",
  POLICE:   "bg-orange-100 text-orange-700",
  CIVILIAN: "bg-emerald-100 text-emerald-700",
};

function StatCard({ icon: Icon, label, value, sub, color }) {
  return (
    <div className="card p-5">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 ${color}`}>
        <Icon size={18} strokeWidth={2} />
      </div>
      <p className="text-2xl font-bold text-navy-600">{value}</p>
      <p className="text-sm font-semibold text-gray-700 mt-0.5">{label}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  );
}

function ActionCard({ icon: Icon, title, desc, path, color, mode }) {
  return (
    <Link to={path} className="card p-5 flex items-start gap-4 group hover:border-gold-400">
      <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${color}`}>
        <Icon size={20} strokeWidth={2} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-semibold text-navy-600 group-hover:text-gold-500 transition-colors">{title}</p>
        <p className="text-sm text-gray-500 mt-1 leading-relaxed">{desc}</p>
      </div>
      <ArrowRight size={16} className="text-gray-300 group-hover:text-gold-400 transition-colors shrink-0 mt-1" />
    </Link>
  );
}

function FeatureChip({ feature }) {
  return (
    <div className="flex items-center gap-2 bg-navy-50 border border-navy-100 rounded-xl px-4 py-3">
      <CheckCircle size={15} className="text-emerald-500 shrink-0" />
      <span className="text-sm text-navy-600 font-medium">{feature}</span>
    </div>
  );
}

const FEATURE_ICONS = {
  'citizen-ask-question': MessageCircle,
  'citizen-legal-research': Search,
  'citizen-legal-repository': BookOpen,
  'citizen-case-analysis': FileText,
};

function getFeatureIcon(featureId) {
  return FEATURE_ICONS[featureId] || Search;
}

function getFeatureColor(featureId) {
  const colors = {
    'citizen-ask-question': 'bg-emerald-50 text-emerald-600',
    'citizen-legal-research': 'bg-blue-50 text-blue-600',
    'citizen-legal-repository': 'bg-purple-50 text-purple-600',
    'citizen-case-analysis': 'bg-amber-50 text-amber-600',
  };
  return colors[featureId] || 'bg-blue-50 text-blue-600';
}

export default function DashboardPage() {
  const { user } = useAuth();
  const { mode } = useMode();
  const [dashboard, setDashboard] = useState(null);
  const [documentCount, setDocumentCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const role = (() => { try { return JSON.parse(localStorage.getItem("user"))?.role || "CIVILIAN"; } catch { return "CIVILIAN"; } })();
    getDashboard()
      .then((r) => setDashboard(r.data))
      .catch(() => setDashboard({ role, dashboard_name: "Dashboard", features: [] }))
      .finally(() => setLoading(false));
    getCount().then((r) => setDocumentCount(r.data.data)).catch(() => {});
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <div className="w-10 h-10 border-2 border-navy-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-500 text-sm">Loading your dashboard...</p>
      </div>
    );
  }

  const roleColor = ROLE_COLORS[dashboard.role] || "bg-gray-100 text-gray-700";

  return (
    <div className="space-y-8">

      {/* Welcome banner */}
      <div className="bg-navy-600 rounded-3xl p-7 flex flex-col md:flex-row justify-between items-start md:items-center gap-5 relative overflow-hidden">
        <div className="absolute -right-10 -top-10 w-48 h-48 rounded-full bg-white/5 pointer-events-none" />
        <div className="absolute right-20 bottom-0 w-32 h-32 rounded-full bg-white/5 pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-2">
            <LayoutDashboard size={16} className="text-gold-400" />
            <span className="text-gold-400 text-xs font-semibold uppercase tracking-widest">Dashboard</span>
          </div>
          <h1 className="text-2xl font-bold text-white">Welcome back, {user?.fullName}</h1>
          <p className="text-navy-200 text-sm mt-1">{user?.email}</p>
        </div>
        <span className={`badge ${roleColor} text-sm px-4 py-2 font-bold relative z-10`}>
          {dashboard.role}
        </span>
      </div>

      {/* Mode Info */}
      <div className="bg-navy-50 border border-navy-100 rounded-2xl p-5">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-navy-100">
            <span className="text-2xl">{mode.icon}</span>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-navy-900">{mode.name}</h3>
            <p className="text-sm text-navy-700 mt-1">{mode.description}</p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Overview</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard icon={BookOpen}  label="Legal Documents"  value={documentCount} sub="Repository records"   color="bg-blue-50 text-blue-600" />
          <StatCard icon={Users}     label="Role"             value={dashboard.role}                            color="bg-purple-50 text-purple-600" />
          <StatCard icon={Search}    label="Research"         value="Active"         sub="Case search enabled" color="bg-emerald-50 text-emerald-600" />
          <StatCard icon={Brain}     label="AI Support"       value="Ready"          sub="Decision assistance" color="bg-amber-50 text-amber-600" />
        </div>
      </div>

      {/* Quick actions - Mode specific */}
      <div>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {mode.features.slice(0, 4).map((feature) => {
            const Icon = getFeatureIcon(feature.id);
            const color = getFeatureColor(feature.id);
            return (
              <ActionCard
                key={feature.id}
                icon={Icon}
                title={feature.name}
                desc={feature.description}
                path={feature.path || "/research"}
                color={color}
                mode={mode.id}
              />
            );
          })}
        </div>
      </div>

      {/* Available features */}
      {dashboard.features?.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Available Features</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {dashboard.features.map((feature, i) => (
              <FeatureChip key={i} feature={feature} />
            ))}
          </div>
        </div>
      )}

      {/* Status */}
      <div className="flex items-start gap-3 bg-emerald-50 border border-emerald-200 rounded-2xl px-5 py-4">
        <CheckCircle size={18} className="text-emerald-600 shrink-0 mt-0.5" />
        <div>
          <p className="text-emerald-700 font-semibold text-sm">Role-Based Dashboard Active</p>
          <p className="text-emerald-600 text-xs mt-0.5">
            Your dashboard is dynamically configured based on your registered user role.
          </p>
        </div>
      </div>

    </div>
  );
}
