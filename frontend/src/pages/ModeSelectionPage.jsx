import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { MODES_LIST, getModeById } from "../config/modes";
import { useMode } from "../context/ModeContext";
import { Scale, ChevronRight, CheckCircle } from "lucide-react";

export default function ModeSelectionPage() {
  const [selectedMode, setSelectedMode] = useState(null);
  const [isSelecting, setIsSelecting] = useState(false);
  const navigate = useNavigate();
  const { switchMode } = useMode();

  const handleModeSelect = (modeId) => {
    setSelectedMode(modeId);
    setIsSelecting(true);
    
    // Switch mode and navigate to dashboard
    setTimeout(() => {
      switchMode(modeId);
      navigate("/dashboard");
    }, 500);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <div className="bg-navy-600 py-6 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gold-400 rounded-lg flex items-center justify-center">
              <Scale size={24} className="text-navy-700" strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="text-white font-bold text-2xl tracking-tight">NyayaAI</h1>
              <p className="text-gold-400 text-sm font-semibold tracking-widest uppercase">AI-Powered Legal Intelligence</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-navy-900 mb-4">
            Choose Your NyayaAI Mode
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Select the mode that best fits your role to get a tailored legal intelligence experience
          </p>
        </div>

        {/* Mode Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {MODES_LIST.map((mode) => (
            <div
              key={mode.id}
              onClick={() => handleModeSelect(mode.id)}
              className={`
                relative group cursor-pointer
                bg-white rounded-2xl p-6
                border-2 transition-all duration-300
                hover:shadow-xl hover:-translate-y-1
                ${selectedMode === mode.id 
                  ? `border-${mode.color}-400 shadow-lg` 
                  : "border-gray-100 hover:border-gray-200"
                }
              `}
            >
              {/* Selected indicator */}
              {selectedMode === mode.id && (
                <div className="absolute top-4 right-4">
                  <div className="w-6 h-6 bg-emerald-500 rounded-full flex items-center justify-center">
                    <CheckCircle size={14} className="text-white" />
                  </div>
                </div>
              )}

              {/* Mode Icon */}
              <div className={`
                w-16 h-16 rounded-xl flex items-center justify-center mb-6
                ${mode.bg} ${mode.accent}
              `}>
                <span className="text-4xl">{mode.icon}</span>
              </div>

              {/* Mode Title */}
              <h3 className="text-xl font-bold text-navy-900 mb-2">
                {mode.name}
              </h3>

              {/* Mode Description */}
              <p className="text-gray-600 mb-6">
                {mode.description}
              </p>

              {/* Features Preview */}
              <div className="space-y-2 mb-6">
                {mode.features.slice(0, 3).map((feature) => (
                  <div key={feature.id} className="flex items-center gap-2 text-sm">
                    <span className="text-gray-400">{feature.icon}</span>
                    <span className="text-gray-700">{feature.name}</span>
                    {feature.status === 'coming-soon' && (
                      <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">
                        Coming Soon
                      </span>
                    )}
                  </div>
                ))}
              </div>

              {/* Enter Button */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <span className="text-sm font-medium text-navy-600">
                  Enter {mode.name} Mode
                </span>
                <div className={`
                  w-8 h-8 rounded-lg flex items-center justify-center
                  transition-colors duration-300
                  ${selectedMode === mode.id 
                    ? `bg-${mode.color}-500 text-white` 
                    : "bg-gray-100 text-gray-400 group-hover:bg-gray-200"
                  }
                `}>
                  <ChevronRight size={16} />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Info Section */}
        <div className="mt-12 bg-blue-50 rounded-2xl p-6 border border-blue-100">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <Scale size={20} className="text-blue-600" />
            </div>
            <div>
              <h4 className="font-semibold text-blue-900 mb-2">
                All Modes Use the Same Core Platform
              </h4>
              <p className="text-sm text-blue-800 leading-relaxed">
                Regardless of your selected mode, you'll have access to the same powerful 
                NyayaAI features including legal search, document analysis, and AI assistance. 
                The mode only changes how these features are presented and which role-specific 
                tools are highlighted.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-navy-600 border-t border-white/10 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-navy-400 text-xs text-center">
            © 2025 NyayaAI · AI-Powered Legal Research for Indian Law
          </p>
        </div>
      </div>
    </div>
  );
}
