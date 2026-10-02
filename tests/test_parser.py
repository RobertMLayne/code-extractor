"""Regression checks for public HTML and embedded conversation parsing."""

import json
from pathlib import Path

from extract_code.parser import load_conversations

# Pytest rewrites these test expectations; they do not enforce production security.
# Exclude only B101 on assertions while retaining all other security checks.


def test_plain_html(tmp_path: Path) -> None:
    html = tmp_path / "x.html"
    html.write_text("<html><body><pre>```python\nprint('x')\n```</pre></body></html>")
    convos = load_conversations(html)
    assert convos[0][0] == "chat_export"  # nosec B101
    assert "print('x')" in convos[0][1][0]  # nosec B101


def test_embedded_json_preserves_order_and_isolates_conversations(tmp_path: Path) -> None:
    conversations = [
        {
            "title": "First",
            "mapping": {
                "root": {"parent": None, "children": ["first", "branch"]},
                "first": {
                    "parent": "root",
                    "children": ["nested"],
                    "message": {"content": {"parts": ["first", "ignored extra part"]}},
                },
                "nested": {
                    "parent": "first",
                    "children": [],
                    "message": {"content": {"parts": ["nested"]}},
                },
                "branch": {
                    "parent": "root",
                    "children": [],
                    "message": {"content": {"parts": ["branch"]}},
                },
            },
        },
        {
            "title": "Second",
            "mapping": {
                "root": {"parent": None, "children": ["first"]},
                "first": {
                    "parent": "root",
                    "children": [],
                    "message": {"content": {"parts": ["second"]}},
                },
            },
        },
    ]
    html = tmp_path / "conversations.html"
    html.write_text(f"<script>window.mapping = {json.dumps(conversations)};</script>")

    expected = [("First", ["first", "nested", "branch"]), ("Second", ["second"])]
    assert load_conversations(html) == expected  # nosec B101


def test_invalid_embedded_json_falls_back_to_visible_html(tmp_path: Path) -> None:
    html = tmp_path / "broken-export.html"
    html.write_text("<script>window.mapping = [broken];</script><p>Visible export</p>")

    assert load_conversations(html) == [("chat_export", ["Visible export"])]  # nosec B101
