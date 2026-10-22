import { useState } from "react";
import { useIdeStore } from "../../store/ideStore";
import { FileTree } from "./FileTree";
import "./sidebar.css";

export function Sidebar() {
  const projects = useIdeStore((s) => s.projects);
  const activeProjectId = useIdeStore((s) => s.activeProjectId);
  const selectProject = useIdeStore((s) => s.selectProject);
  const createProject = useIdeStore((s) => s.createProject);
  const [newName, setNewName] = useState("");

  const onCreate = () => {
    const name = newName.trim();
    if (!name) return;
    void createProject(name);
    setNewName("");
  };

  return (
    <div className="sidebar">
      <div className="sidebar-section">
        <div className="sidebar-title">Projects</div>
        <ul className="project-list">
          {projects.map((p) => (
            <li
              key={p.id}
              className={p.id === activeProjectId ? "project active" : "project"}
              onClick={() => void selectProject(p.id)}
            >
              {p.name}
            </li>
          ))}
          {projects.length === 0 && (
            <li className="project empty">No projects yet</li>
          )}
        </ul>
        <div className="new-project">
          <input
            aria-label="New project name"
            placeholder="New project name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onCreate()}
          />
          <button onClick={onCreate}>+</button>
        </div>
      </div>

      <div className="sidebar-section grow">
        <div className="sidebar-title">Explorer</div>
        <FileTree />
      </div>
    </div>
  );
}
