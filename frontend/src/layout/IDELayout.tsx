import { Sidebar } from "../components/Sidebar/Sidebar";
import { EditorArea } from "../components/Editor/EditorArea";
import { ChatPanel } from "../components/Chat/ChatPanel";
import { TerminalPanel } from "../components/Terminal/TerminalPanel";
import "./layout.css";

export function IDELayout() {
  return (
    <div className="ide">
      <div className="ide-activitybar">
        <div className="activity-icon active" title="Explorer">
          ▦
        </div>
        <div className="activity-icon" title="Source Control">
          ⎇
        </div>
      </div>
      <div className="ide-sidebar">
        <Sidebar />
      </div>
      <div className="ide-main">
        <div className="ide-editor">
          <EditorArea />
        </div>
        <div className="ide-terminal">
          <TerminalPanel />
        </div>
      </div>
      <div className="ide-chat">
        <ChatPanel />
      </div>
    </div>
  );
}
