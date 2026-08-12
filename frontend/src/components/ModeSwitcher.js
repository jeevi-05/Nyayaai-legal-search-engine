import { useMode } from "../context/ModeContext";
import { CheckCircle } from "lucide-react";

export default function ModeSwitcher() {
  const { mode } = useMode();

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium">
      <span className="text-lg">{mode.icon}</span>
      <span>{mode.name}</span>
      <CheckCircle size={14} className={`text-${mode.color}-400`} />
    </div>
  );
}
