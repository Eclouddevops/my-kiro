import type {
  ChatResponse,
  FileContent,
  FileNode,
  Project,
  Proposal,
} from "./types";

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/**
 * Minimal typed fetch wrapper. An Authorization header is attached when a token
 * is present (phase 4 populates it); credentials never live in client code.
 */
let authToken: string | null = null;

export function setAuthToken(token: string | null): void {
  authToken = token;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };
  if (authToken) headers.Authorization = `Bearer ${authToken}`;

  const res = await fetch(`${BASE_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* non-JSON error body */
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  // 204 / empty bodies
  const text = await res.text();
  return (text ? JSON.parse(text) : undefined) as T;
}

export const api = {
  health: () => request<{ status: string; version: string }>("/api/health"),

  listProjects: () => request<Project[]>("/api/projects"),

  createProject: (name: string) =>
    request<Project>("/api/projects", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),

  tree: (projectId: string) =>
    request<FileNode[]>(`/api/projects/${projectId}/tree`),

  readFile: (projectId: string, path: string) =>
    request<FileContent>(
      `/api/projects/${projectId}/files?path=${encodeURIComponent(path)}`,
    ),

  writeFile: (projectId: string, path: string, content: string) =>
    request<FileContent>(`/api/projects/${projectId}/files`, {
      method: "PUT",
      body: JSON.stringify({ path, content }),
    }),

  chat: (projectId: string, message: string, openFiles: Record<string, string>) =>
    request<ChatResponse>(`/api/projects/${projectId}/chat`, {
      method: "POST",
      body: JSON.stringify({ message, open_files: openFiles }),
    }),

  applyProposals: (projectId: string, proposals: Proposal[]) =>
    request<string[]>(`/api/projects/${projectId}/chat/apply`, {
      method: "POST",
      body: JSON.stringify({ proposals }),
    }),
};
