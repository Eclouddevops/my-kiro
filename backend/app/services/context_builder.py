"""Assemble project context for the LLM within a token budget (R7).

Token counting uses a cheap heuristic (≈4 chars/token) to stay dependency-free;
it can be swapped for a real tokenizer later. Oldest history and largest files
are trimmed first so the most relevant, recent context survives.
"""
from __future__ import annotations

from dataclasses import dataclass


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


@dataclass
class ContextBuilder:
    token_budget: int = 12000

    def build_messages(
        self,
        history: list[dict],
        user_message: str,
        file_tree: list[str] | None = None,
        open_files: dict[str, str] | None = None,
    ) -> list[dict]:
        """Return a message list for BedrockService.converse within budget."""
        budget = self.token_budget
        messages: list[dict] = []

        # 1) The new user message always gets included.
        user_block = user_message
        if file_tree:
            tree_str = "\n".join(sorted(file_tree))
            user_block = f"Project files:\n{tree_str}\n\n{user_message}"
        if open_files:
            file_sections = []
            for path, content in open_files.items():
                section = f"--- {path} ---\n{content}"
                if estimate_tokens(section) <= budget // 2:
                    file_sections.append(section)
                    budget -= estimate_tokens(section)
            if file_sections:
                user_block = (
                    "Open files:\n" + "\n\n".join(file_sections) + "\n\n" + user_block
                )

        final_user = {"role": "user", "content": user_block}
        budget -= estimate_tokens(user_block)

        # 2) Fill remaining budget with most-recent history first.
        trimmed: list[dict] = []
        for msg in reversed(history):
            cost = estimate_tokens(msg.get("content", ""))
            if cost > budget:
                break
            trimmed.append(msg)
            budget -= cost
        trimmed.reverse()

        messages.extend(trimmed)
        messages.append(final_user)
        return messages
