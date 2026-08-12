import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";
import { Scale } from "lucide-react";

export default function MainLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
      <footer className="bg-navy-600 border-t border-white/10 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 bg-gold-400 rounded-md flex items-center justify-center">
                <Scale size={14} className="text-navy-700" strokeWidth={2.5} />
              </div>
              <span className="text-white font-semibold text-sm">NyayaAI</span>
              <span className="text-navy-300 text-xs">Legal Intelligence Platform</span>
            </div>
            <p className="text-navy-400 text-xs text-center">
              © 2025 NyayaAI · AI-Powered Legal Research for Indian Law · All rights reserved
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
