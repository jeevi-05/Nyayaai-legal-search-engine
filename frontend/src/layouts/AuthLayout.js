import { Outlet, Link } from "react-router-dom";
import { Scale, Shield, BookOpen, Gavel } from "lucide-react";

const TRUST_ITEMS = [
  { icon: Gavel,    label: "Supreme Court", sub: "Landmark judgments" },
  { icon: BookOpen, label: "Acts & Statutes", sub: "500+ legal documents" },
  { icon: Shield,   label: "Secure & Private", sub: "JWT-secured sessions" },
];

export default function AuthLayout() {
  return (
    <div className="min-h-screen flex bg-slate-50">

      {/* Left branding panel */}
      <div className="hidden lg:flex lg:w-[46%] bg-navy-600 flex-col justify-between px-12 py-12 relative overflow-hidden">

        {/* Decorative circles */}
        <div className="absolute -top-24 -right-24 w-80 h-80 rounded-full bg-white/5 pointer-events-none" />
        <div className="absolute -bottom-32 -left-16 w-96 h-96 rounded-full bg-white/5 pointer-events-none" />
        <div className="absolute top-1/2 right-8 w-40 h-40 rounded-full bg-gold-400/10 pointer-events-none" />

        {/* Logo */}
        <Link to="/" className="flex items-center gap-3 relative z-10">
          <div className="w-11 h-11 bg-gold-400 rounded-xl flex items-center justify-center shadow-lg">
            <Scale size={22} className="text-navy-700" strokeWidth={2.5} />
          </div>
          <div>
            <span className="text-white font-bold text-xl tracking-tight">NyayaAI</span>
            <span className="block text-gold-400 text-[10px] font-semibold tracking-widest uppercase">Legal Intelligence Platform</span>
          </div>
        </Link>

        {/* Main copy */}
        <div className="relative z-10 space-y-6">
          <div>
            <p className="section-label text-gold-400">Trusted by Legal Professionals</p>
            <h2 className="text-3xl font-bold text-white leading-snug mt-2">
              Empowering Citizens &<br />Legal Professionals
            </h2>
            <p className="text-navy-200 mt-4 leading-relaxed text-sm max-w-xs">
              AI-driven Indian legal research — search judgments, analyze precedents, and explore constitutional documents instantly.
            </p>
          </div>

          {/* Trust items */}
          <div className="space-y-3">
            {TRUST_ITEMS.map(({ icon: Icon, label, sub }) => (
              <div key={label} className="flex items-center gap-3 bg-white/8 rounded-xl px-4 py-3 border border-white/10">
                <div className="w-8 h-8 bg-gold-400/20 rounded-lg flex items-center justify-center shrink-0">
                  <Icon size={16} className="text-gold-400" />
                </div>
                <div>
                  <p className="text-white text-sm font-semibold">{label}</p>
                  <p className="text-navy-300 text-xs">{sub}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom note */}
        <p className="text-navy-400 text-xs relative z-10">
          © 2025 NyayaAI · Secure Legal Research Platform
        </p>
      </div>

      {/* Right form panel */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">

          {/* Mobile logo */}
          <div className="lg:hidden text-center mb-8">
            <Link to="/" className="inline-flex items-center gap-2.5">
              <div className="w-9 h-9 bg-navy-600 rounded-xl flex items-center justify-center">
                <Scale size={18} className="text-gold-400" strokeWidth={2.5} />
              </div>
              <div className="text-left">
                <span className="block text-navy-600 font-bold text-lg">NyayaAI</span>
                <span className="block text-gold-500 text-[10px] font-semibold tracking-widest uppercase">Legal Intelligence</span>
              </div>
            </Link>
          </div>

          <div className="bg-white rounded-3xl shadow-card-hover border border-gray-100 p-8">
            <Outlet />
          </div>

          <p className="text-center text-xs text-gray-400 mt-5">
            © 2025 NyayaAI Legal Intelligence Platform
          </p>
        </div>
      </div>
    </div>
  );
}
