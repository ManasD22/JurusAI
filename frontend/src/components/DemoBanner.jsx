import { Info } from "lucide-react";
import useDemoMode from "./useDemoMode.js";

// Shown when the backend is unreachable and the app is serving local demo data.
export default function DemoBanner() {
  const demo = useDemoMode();
  if (!demo) return null;
  return (
    <div className="banner">
      <Info size={16} />
      <span>
        Demo mode — the JurisAI backend isn't connected, so responses are sample data.
        Start the Django server to use live AI features.
      </span>
    </div>
  );
}
