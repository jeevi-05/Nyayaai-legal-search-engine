import { createContext, useContext, useEffect, useState } from "react";
import { getModeById } from "../config/modes";

const ModeContext = createContext(null);

export function ModeProvider({ children }) {
  const [mode, setMode] = useState(getModeById('judicial'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load mode from localStorage
    const savedMode = localStorage.getItem("nyayaai_mode");
    if (savedMode && getModeById(savedMode)) {
      setMode(getModeById(savedMode));
    } else {
      // Default to Judicial Intelligence Mode
      setMode(getModeById('judicial'));
    }
    setLoading(false);
  }, []);

  const value = {
    mode,
    loading,
  };

  return <ModeContext.Provider value={value}>{children}</ModeContext.Provider>;
}

export const useMode = () => {
  const context = useContext(ModeContext);
  if (!context) {
    // Default to Judicial Intelligence Mode if context not available
    return {
      mode: getModeById('judicial'),
      loading: false,
    };
  }
  return context;
};
