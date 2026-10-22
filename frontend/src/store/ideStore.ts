import { create } from "zustand";
import { api } from "../api/client";
import type { ChatMessage, FileNode, Project, Proposal } from "../api/types";

export interface OpenTab {
  path: string;
  content: string;
  dirty: boolean;
}

interface IdeState {
  // projects
  projects: Project[];
  activeProjectId: string | null;
  // files
  tree: FileNode[];
  tabs: OpenTab[];
  activeTab: string | null;
  // chat
  messages: ChatMessage[];
  proposals: Proposal[];
  chatBusy: boolean;
  error: string | null;

  // actions
  loadProjects: () => Promise<void>;
  createProject: (name: string) => Promise<void>;
  selectProject: (id: string) => Promise<void>;
  refreshTree: () => Promise<void>;
  openFile: (path: string) => Promise<void>;
  setActiveTab: (path: string) => void;
  editTab: (path: string, content: string) => void;
  saveTab: (path: string) => Promise<void>;
  closeTab: (path: string) => void;
  sendChat: (message: string) => Promise<void>;
  applyProposals: () => Promise<void>;
  dismissProposals: () => void;
  clearError: () => void;
}

export const useIdeStore = create<IdeState>((set, get) => ({
  projects: [],
  activeProjectId: null,
  tree: [],
  tabs: [],
  activeTab: null,
  messages: [],
  proposals: [],
  chatBusy: false,
  error: null,

  loadProjects: async () => {
    try {
      const projects = await api.listProjects();
      set({ projects });
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  createProject: async (name) => {
    try {
      const project = await api.createProject(name);
      set((s) => ({ projects: [...s.projects, project] }));
      await get().selectProject(project.id);
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  selectProject: async (id) => {
    set({
      activeProjectId: id,
      tabs: [],
      activeTab: null,
      messages: [],
      proposals: [],
    });
    await get().refreshTree();
  },

  refreshTree: async () => {
    const id = get().activeProjectId;
    if (!id) return;
    try {
      const tree = await api.tree(id);
      set({ tree });
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  openFile: async (path) => {
    const id = get().activeProjectId;
    if (!id) return;
    const existing = get().tabs.find((t) => t.path === path);
    if (existing) {
      set({ activeTab: path });
      return;
    }
    try {
      const file = await api.readFile(id, path);
      set((s) => ({
        tabs: [...s.tabs, { path, content: file.content, dirty: false }],
        activeTab: path,
      }));
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  setActiveTab: (path) => set({ activeTab: path }),

  editTab: (path, content) =>
    set((s) => ({
      tabs: s.tabs.map((t) =>
        t.path === path ? { ...t, content, dirty: true } : t,
      ),
    })),

  saveTab: async (path) => {
    const id = get().activeProjectId;
    const tab = get().tabs.find((t) => t.path === path);
    if (!id || !tab) return;
    try {
      await api.writeFile(id, path, tab.content);
      set((s) => ({
        tabs: s.tabs.map((t) =>
          t.path === path ? { ...t, dirty: false } : t,
        ),
      }));
      await get().refreshTree();
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  closeTab: (path) =>
    set((s) => {
      const tabs = s.tabs.filter((t) => t.path !== path);
      const activeTab =
        s.activeTab === path ? (tabs[tabs.length - 1]?.path ?? null) : s.activeTab;
      return { tabs, activeTab };
    }),

  sendChat: async (message) => {
    const id = get().activeProjectId;
    if (!id) return;
    set((s) => ({
      messages: [...s.messages, { role: "user", content: message }],
      chatBusy: true,
      error: null,
    }));
    const openFiles: Record<string, string> = {};
    for (const t of get().tabs) openFiles[t.path] = t.content;
    try {
      const res = await api.chat(id, message, openFiles);
      set((s) => ({
        messages: [...s.messages, { role: "assistant", content: res.reply }],
        proposals: res.proposals,
        chatBusy: false,
      }));
    } catch (e) {
      set({ error: (e as Error).message, chatBusy: false });
    }
  },

  applyProposals: async () => {
    const id = get().activeProjectId;
    const proposals = get().proposals;
    if (!id || proposals.length === 0) return;
    try {
      await api.applyProposals(id, proposals);
      set({ proposals: [] });
      await get().refreshTree();
    } catch (e) {
      set({ error: (e as Error).message });
    }
  },

  dismissProposals: () => set({ proposals: [] }),
  clearError: () => set({ error: null }),
}));
