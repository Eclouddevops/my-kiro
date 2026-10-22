from app.services.context_builder import ContextBuilder, estimate_tokens


def test_estimate_tokens_nonzero():
    assert estimate_tokens("") == 1
    assert estimate_tokens("abcd") == 1


def test_new_message_always_included():
    b = ContextBuilder(token_budget=50)
    msgs = b.build_messages(history=[], user_message="build an app")
    assert msgs[-1]["role"] == "user"
    assert "build an app" in msgs[-1]["content"]


def test_history_trimmed_to_budget_recent_first():
    # Budget 5 tokens. "go" (1) leaves 4. "recent" (1) leaves 3. The old
    # message costs ceil(40/4)=10 tokens and must be dropped.
    b = ContextBuilder(token_budget=5)
    history = [
        {"role": "user", "content": "x" * 40},      # old, expensive (10 tokens)
        {"role": "assistant", "content": "recent"},  # recent, cheap (1 token)
    ]
    msgs = b.build_messages(history=history, user_message="go")
    contents = [m["content"] for m in msgs]
    assert "recent" in contents  # recent kept
    assert ("x" * 40) not in contents  # old dropped


def test_file_tree_included():
    b = ContextBuilder(token_budget=500)
    msgs = b.build_messages(
        history=[], user_message="go", file_tree=["a.py", "b.py"]
    )
    assert "a.py" in msgs[-1]["content"]
    assert "b.py" in msgs[-1]["content"]
