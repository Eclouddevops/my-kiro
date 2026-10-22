import { useState } from "react";
import { useIdeStore } from "../../store/ideStore";
import { ProposalReview } from "./ProposalReview";
import "./chat.css";

export function ChatPanel() {
  const messages = useIdeStore((s) => s.messages);
  const chatBusy = useIdeStore((s) => s.chatBusy);
  const sendChat = useIdeStore((s) => s.sendChat);
  const activeProjectId = useIdeStore((s) => s.activeProjectId);
  const [input, setInput] = useState("");

  const onSend = () => {
    const msg = input.trim();
    if (!msg || chatBusy) return;
    void sendChat(msg);
    setInput("");
  };

  return (
    <div className="chat">
      <div className="chat-title">AI Assistant</div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-hint">
            Describe what you want to build. The AI can propose files, which you
            review before they are written.
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`msg msg-${m.role}`}>
            <div className="msg-role">{m.role === "user" ? "You" : "AI"}</div>
            <div className="msg-body">{m.content}</div>
          </div>
        ))}
        {chatBusy && <div className="msg msg-assistant typing">AI is thinking…</div>}
      </div>

      <ProposalReview />

      <div className="chat-input">
        <textarea
          aria-label="Message the AI"
          placeholder={
            activeProjectId
              ? "Ask the AI to build or change something…"
              : "Create or select a project first"
          }
          disabled={!activeProjectId || chatBusy}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
        />
        <button disabled={!activeProjectId || chatBusy} onClick={onSend}>
          Send
        </button>
      </div>
    </div>
  );
}
