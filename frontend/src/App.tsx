import { useEffect } from "react";
import { IDELayout } from "./layout/IDELayout";
import { useIdeStore } from "./store/ideStore";

export function App() {
  const loadProjects = useIdeStore((s) => s.loadProjects);
  const error = useIdeStore((s) => s.error);
  const clearError = useIdeStore((s) => s.clearError);

  useEffect(() => {
    void loadProjects();
  }, [loadProjects]);

  return (
    <>
      <IDELayout />
      {error && (
        <div className="toast" role="alert" onClick={clearError}>
          {error} <span className="toast-dismiss">(click to dismiss)</span>
        </div>
      )}
    </>
  );
}
