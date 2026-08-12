import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import {
  Scale, Search, BookOpen, Gavel, Shield, Brain,
  ArrowRight, CheckCircle, FileText, Zap
} from "lucide-react";

const FEATURES = [
  {
    icon: Gavel,
    title: "Supreme Court Intelligence",
    desc: "AI-assisted search across landmark judgments and constitutional bench decisions since 1950.",
    badge: "SC Judgments",
    color: "bg-blue-50 text-blue-600",
  },
  {
    icon: BookOpen,
    title: "Legal Knowledge Repository",
    desc: "Comprehensive library of Acts, High Court orders, IPC, CrPC, and constitutional documents.",
    badge: "500+ Documents",
    color: "bg-purple-50 text-purple-600",
  },
  {
    icon: Search,
    title: "Intelligent Case Research",
    desc: "Find related precedents, similar cases, and relevant legal sections with semantic search.",
    badge: "AI Search",
    color: "bg-emerald-50 text-emerald-600",
  },
  {
    icon: Brain,
    title: "AI Legal Assistant",
    desc: "Decision support powered by machine learning — analyze precedent strength and case relevance.",
    badge: "AI Powered",
    color: "bg-amber-50 text-amber-600",
  },
  {
    icon: FileText,
    title: "Case Document Analysis",
    desc: "Upload case PDFs and receive instant similarity analysis against the legal knowledge base.",
    badge: "PDF Analysis",
    color: "bg-rose-50 text-rose-600",
  },
  {
    icon: Shield,
    title: "Secure Legal Workspace",
    desc: "Role-based access for citizens, lawyers, judges, and police with JWT-secured sessions.",
    badge: "Role-Based",
    color: "bg-navy-50 text-navy-600",
  },
];

const STATS = [
  { value: "500+", label: "Legal Documents" },
  { value: "6",    label: "User Roles" },
  { value: "AI",   label: "Powered Search" },
  { value: "24/7", label: "Availability" },
];

const ROLES = ["Citizens", "Lawyers", "Judges", "Police Officers", "Legal Researchers", "Law Students"];

function FeatureCard({ icon: Icon, title, desc, badge, color }) {
  return (
    <div className="card p-6 group cursor-default">
      <div className="flex items-start justify-between mb-4">
        <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${color}`}>
          <Icon size={20} strokeWidth={2} />
        </div>
        <span className={`badge ${color} text-[10px]`}>{badge}</span>
      </div>
      <h3 className="font-semibold text-navy-600 mb-2 group-hover:text-gold-500 transition-colors">{title}</h3>
      <p className="text-sm text-gray-500 leading-relaxed">{desc}</p>
    </div>
  );
}

export default function HomePage() {
  const { user, loading } = useAuth();
  if (!loading && user) return <Navigate to="/dashboard" replace />;

  return (
    <div className="space-y-20 py-4">

      {/* Hero */}
      <section className="text-center max-w-4xl mx-auto pt-8">
        <div className="inline-flex items-center gap-2 bg-navy-50 border border-navy-100 text-navy-600 text-xs font-semibold px-4 py-2 rounded-full mb-6">
          <Zap size={12} className="text-gold-500" />
          AI-Powered · Indian Legal System · Trusted by Professionals
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-navy-600 leading-tight mb-6">
          AI-Powered Legal Intelligence<br />
          <span className="text-gold-400">for Indian Law</span>
        </h1>

        <p className="text-gray-500 text-lg leading-relaxed mb-10 max-w-2xl mx-auto">
          Search judgments, analyze precedents, explore legal documents and simplify legal research with artificial intelligence — built for the Indian judiciary.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-3 mb-12">
          <Link to="/register" className="btn-primary text-base px-8 py-3 rounded-2xl">
            Start Research <ArrowRight size={16} />
          </Link>
          <Link to="/login" className="btn-outline text-base px-8 py-3 rounded-2xl">
            Sign In
          </Link>
        </div>

        {/* Roles */}
        <div className="flex flex-wrap justify-center gap-2">
          {ROLES.map((r) => (
            <span key={r} className="inline-flex items-center gap-1.5 text-xs text-gray-500 bg-white border border-gray-200 px-3 py-1.5 rounded-full shadow-sm">
              <CheckCircle size={11} className="text-emerald-500" />
              {r}
            </span>
          ))}
        </div>
      </section>

      {/* Stats bar */}
      <section className="bg-navy-600 rounded-3xl px-8 py-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {STATS.map(({ value, label }) => (
            <div key={label}>
              <p className="text-3xl font-bold text-gold-400">{value}</p>
              <p className="text-navy-200 text-sm mt-1">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section>
        <div className="text-center mb-10">
          <p className="section-label">Platform Capabilities</p>
          <h2 className="text-3xl font-bold text-navy-600">Everything a Legal Professional Needs</h2>
          <p className="text-gray-500 mt-3 max-w-xl mx-auto text-sm">
            A comprehensive legal intelligence platform designed for the Indian legal ecosystem.
          </p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map((f) => <FeatureCard key={f.title} {...f} />)}
        </div>
      </section>

      {/* CTA */}
      <section className="bg-gradient-to-br from-navy-600 to-navy-800 rounded-3xl p-10 text-center">
        <div className="w-14 h-14 bg-gold-400 rounded-2xl flex items-center justify-center mx-auto mb-5">
          <Scale size={26} className="text-navy-700" strokeWidth={2.5} />
        </div>
        <h2 className="text-2xl font-bold text-white mb-3">Ready to Transform Your Legal Research?</h2>
        <p className="text-navy-200 text-sm mb-7 max-w-md mx-auto">
          Join legal professionals across India using NyayaAI for faster, smarter legal research.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-3">
          <Link to="/register" className="btn-gold px-8 py-3 rounded-2xl text-base">
            Create Free Account <ArrowRight size={16} />
          </Link>
          <Link to="/login" className="inline-flex items-center justify-center gap-2 border-2 border-white/30 text-white hover:bg-white/10 font-semibold text-base px-8 py-3 rounded-2xl transition-all">
            Sign In
          </Link>
        </div>
      </section>

    </div>
  );
}
