import { useMode } from "../context/ModeContext";
import { getAvailableFeatures, getComingSoonFeatures } from "../config/modes";
import ComingSoonCard from "./ComingSoonCard";
import { CheckCircle, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function ModeFeatures() {
  const { mode } = useMode();
  const availableFeatures = getAvailableFeatures(mode.id);
  const comingSoonFeatures = getComingSoonFeatures(mode.id);

  return (
    <div className="space-y-8">
      {/* Available Features */}
      {availableFeatures.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Available in {mode.name} Mode
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {availableFeatures.map((feature) => (
              <div key={feature.id} className="card p-5 hover:border-gold-400 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0">
                    <span className="text-2xl">{feature.icon}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-navy-600">{feature.name}</h3>
                    <p className="text-sm text-gray-500 mt-1 leading-relaxed">{feature.description}</p>
                    {feature.path && (
                      <Link 
                        to={feature.path}
                        className="inline-flex items-center gap-1 text-sm text-blue-600 font-medium mt-2 hover:text-blue-700"
                      >
                        Access Now <ArrowRight size={14} />
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Coming Soon Features */}
      {comingSoonFeatures.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Coming Soon in {mode.name} Mode
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {comingSoonFeatures.map((feature) => (
              <ComingSoonCard
                key={feature.id}
                title={feature.name}
                description={feature.description}
                icon={feature.icon}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
