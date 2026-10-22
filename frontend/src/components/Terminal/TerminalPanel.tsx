import "./terminal.css";

/**
 * Placeholder terminal panel. Phase 3 replaces the static body with an
 * xterm.js instance wired to the backend WebSocket exec stream (build/test
 * output). The panel shell and styling land now so the layout is complete.
 */
export function TerminalPanel() {
  return (
    <div className="terminal">
      <div className="terminal-tabs">
        <div className="terminal-tab active">TERMINAL</div>
        <div className="terminal-tab">OUTPUT</div>
      </div>
      <div className="terminal-body">
        <span className="terminal-prompt">$</span> Build and test output will
        stream here once code execution is enabled.
      </div>
    </div>
  );
}
