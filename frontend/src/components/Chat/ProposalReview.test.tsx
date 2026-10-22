import { describe, expect, it, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ProposalReview } from "./ProposalReview";
import { useIdeStore } from "../../store/ideStore";

describe("ProposalReview", () => {
  beforeEach(() => {
    useIdeStore.setState({ proposals: [] });
  });

  it("renders nothing when there are no proposals", () => {
    const { container } = render(<ProposalReview />);
    expect(container).toBeEmptyDOMElement();
  });

  it("lists proposals with action badges", () => {
    useIdeStore.setState({
      proposals: [
        { path: "src/main.py", action: "write", content: "x" },
        { path: "old.py", action: "delete", content: null },
      ],
    });
    render(<ProposalReview />);
    expect(screen.getByText("src/main.py")).toBeInTheDocument();
    expect(screen.getByText("old.py")).toBeInTheDocument();
    expect(screen.getByText(/Proposed changes \(2\)/)).toBeInTheDocument();
  });

  it("clears proposals when rejected", () => {
    useIdeStore.setState({
      proposals: [{ path: "a.py", action: "write", content: "y" }],
    });
    render(<ProposalReview />);
    fireEvent.click(screen.getByText("Reject"));
    expect(useIdeStore.getState().proposals).toHaveLength(0);
  });
});
