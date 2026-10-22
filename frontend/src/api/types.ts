export interface Project {
  id: string;
  name: string;
}

export interface FileNode {
  path: string;
  is_dir: boolean;
  size: number;
}

export interface FileContent {
  path: string;
  content: string;
}

export interface Proposal {
  path: string;
  action: "write" | "delete";
  content: string | null;
}

export interface ChatResponse {
  reply: string;
  proposals: Proposal[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}
