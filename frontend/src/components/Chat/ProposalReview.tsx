import { useIdeStore } from "../../store/ideStore";

/**
 * Proposed file operations from the AI. Nothing is written until the user
 * approves (R-SEC5). Review is per-batch for the MVP; per-file accept/reject
 * arrives in phase 2.
 */
export function ProposalReview() {
  const proposals = useIdeStore((s) => s.proposals);
  const applyProposals = useIdeStore((s) => s.applyProposals);
  const dismissProposals = useIdeStore((s) => s.dismissProposals);

  if (proposals.length === 0) return null;

  return (
    <div className="proposals" role="region" aria-label="Proposed changes">
      <div className="proposals-head">
        Proposed changes ({proposals.length}) — review before applying
      </div>
      <ul className="proposals-list">
        {proposals.map((p) => (
          <li key={p.path} className="proposal">
            <span className={`badge badge-${p.action}`}>{p.action}</span>
            <span className="proposal-path" title={p.path}>
              {p.path}
            </span>
          </li>
        ))}
      </ul>
      <div className="proposals-actions">
        <button className="apply" onClick={() => void applyProposals()}>
          Apply all
        </button>
        <button className="reject" onClick={dismissProposals}>
          Reject
        </button>
      </div>
    </div>
  );
}
