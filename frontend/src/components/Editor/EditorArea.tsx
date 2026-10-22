import { useEffect } from "react";
import Editor from "@monaco-editor/react";
import { useIdeStore } from "../../store/ideStore";
import { languageForPath } from "./language";
import "./editor.css";

export function EditorArea() {
  const tabs = useIdeStore((s) => s.tabs);
  const activeTab = useIdeStore((s) => s.activeTab);
  const setActiveTab = useIdeStore((s) => s.setActiveTab);
  const editTab = useIdeStore((s) => s.editTab);
  const saveTab = useIdeStore((s) => s.saveTab);
  const closeTab = useIdeStore((s) => s.closeTab);

  const active = tabs.find((t) => t.path === activeTab) ?? null;

  // Ctrl/Cmd+S saves the active tab.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        if (active) void saveTab(active.path);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [active, saveTab]);

  return (
    <div className="editor-area">
      <div className="tabs" role="tablist">
        {tabs.map((t) => (
          <div
            key={t.path}
            role="tab"
            aria-selected={t.path === activeTab}
            className={t.path === activeTab ? "tab active" : "tab"}
            onClick={() => setActiveTab(t.path)}
          >
            <span>{t.path.split("/").pop()}</span>
            {t.dirty && <span className="dot" title="Unsaved changes">●</span>}
            <button
              className="close"
              aria-label={`Close ${t.path}`}
              onClick={(e) => {
                e.stopPropagation();
                closeTab(t.path);
              }}
            >
              ×
            </button>
          </div>
        ))}
      </div>

      {active ? (
        <>
          <div className="editor-host">
            <Editor
              height="100%"
              theme="vs-dark"
              path={active.path}
              language={languageForPath(active.path)}
              value={active.content}
              onChange={(value) => editTab(active.path, value ?? "")}
              options={{
                fontSize: 13,
                minimap: { enabled: false },
                automaticLayout: true,
                scrollBeyondLastLine: false,
              }}
            />
          </div>
          <div className="editor-hint">
            {active.path}
            {active.dirty ? " • unsaved — press Ctrl+S to save" : " • saved"}
          </div>
        </>
      ) : (
        <div className="editor-empty">
          Open a file from the Explorer, or ask the AI to generate one.
        </div>
      )}
    </div>
  );
}
