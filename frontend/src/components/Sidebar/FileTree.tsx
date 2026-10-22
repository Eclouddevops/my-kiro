import { useIdeStore } from "../../store/ideStore";

/** Renders the flat path list as an indented tree view. */
export function FileTree() {
  const tree = useIdeStore((s) => s.tree);
  const openFile = useIdeStore((s) => s.openFile);
  const activeTab = useIdeStore((s) => s.activeTab);
  const activeProjectId = useIdeStore((s) => s.activeProjectId);

  if (!activeProjectId) {
    return <div className="tree-empty">Select a project</div>;
  }
  if (tree.length === 0) {
    return <div className="tree-empty">No files yet</div>;
  }

  return (
    <ul className="file-tree">
      {tree.map((node) => {
        const depth = node.path.split("/").length - 1;
        const name = node.path.split("/").pop() ?? node.path;
        if (node.is_dir) {
          return (
            <li
              key={node.path}
              className="tree-node dir"
              style={{ paddingLeft: 8 + depth * 12 }}
            >
              📁 {name}
            </li>
          );
        }
        return (
          <li
            key={node.path}
            className={
              node.path === activeTab ? "tree-node file active" : "tree-node file"
            }
            style={{ paddingLeft: 8 + depth * 12 }}
            onClick={() => void openFile(node.path)}
            title={node.path}
          >
            📄 {name}
          </li>
        );
      })}
    </ul>
  );
}
