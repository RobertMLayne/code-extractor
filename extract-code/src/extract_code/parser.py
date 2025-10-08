"""HTML / JSON parsing into (title, [messages]) tuples."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Sequence, Tuple

from bs4 import BeautifulSoup  # type: ignore[import]
from bs4.element import Tag

LOGGER = logging.getLogger(__name__)

__all__ = ["load_conversations"]

Convo = Tuple[str, List[str]]


def _from_json(script_tag: Tag) -> List[Convo]:
    text: str = script_tag.string or ""
    try:
        start, end = text.index("["), text.rindex("]")
        data = json.loads(text[start : end + 1])
    except (ValueError, json.JSONDecodeError):
        LOGGER.debug("Embedded JSON decode failed")
        return []

    convos: List[Convo] = []
    for convo in data:
        title = convo.get("title", "conversation")
        mapping = convo.get("mapping", {})
        roots = [
            mid
            for mid, node in mapping.items()
            if node.get("parent") is None and node.get("children")
        ]
        msgs: List[str] = []

        def dfs(node_id: str) -> None:
            node = mapping.get(node_id, {})
            msg = node.get("message")
            if msg:
                parts = msg.get("content", {}).get("parts") or []
                if parts:
                    msgs.append(parts[0])
            for kid in node.get("children", []):
                dfs(kid)

        for r in roots:
            for kid in mapping[r]["children"]:
                dfs(kid)
        convos.append((title, msgs))
    return convos


def load_conversations(html_path: Path) -> List[Convo]:
    """Return a list of conversations from *html_path*."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")

    script = soup.find(
        "script",
        string=lambda s: s and ("mapping" in s.lower() or "json" in s.lower()),
    )
    if script:
        convos = _from_json(script)  # precise ChatGPT export path
        if convos:
            return convos

    text = soup.get_text(separator="\n")
    return [("chat_export", [text])]
