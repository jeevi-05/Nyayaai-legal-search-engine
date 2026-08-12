import { useState } from "react";
import { Info } from "lucide-react";

export default function ComingSoonCard({ title, description, icon = "⏳" }) {
  const [showInfo, setShowInfo] = useState(false);

  return (
    <div className="card p-5 border-dashed border-gray-300 hover:border-gray-400 transition-colors">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center flex-shrink-0">
          <span className="text-2xl">{icon}</span>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-navy-600">{title}</h3>
          <p className="text-sm text-gray-500 mt-1 leading-relaxed">{description}</p>
          
          <div className="mt-3 flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-gray-100 rounded-lg">
              <Info size={12} className="text-gray-500" />
              <span className="text-xs font-medium text-gray-600">Coming Soon</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
