import { useEffect, useState } from "react";
import { isDemoMode, onDemoModeChange } from "../api/client";

// Reactively tracks whether the app is currently serving local demo data
// (because the backend is unreachable).
export default function useDemoMode() {
  const [demo, setDemo] = useState(isDemoMode());
  useEffect(() => onDemoModeChange(setDemo), []);
  return demo;
}
