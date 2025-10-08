"""Write code blocks from conversations to disk."""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable, Sequence

from .utils import (
    CODE_BLOCK_RE,
    EXT_MAP,
    comment_tokens,
    hash_code,
    sanitize_filename,
)

LOGGER = logging.getLogger(__name__)


def _process_conversation(
    title: str,
    messages: Sequence[str],
    out_root: Path,
    *,
    deduplicate: bool,
    overwrite: bool,
    add_comment: bool,
) -> int:
    """Save all code blocks from a single conversation.  Return count."""
    folder = out_root / sanitize_filename(title or f"project_{abs(hash(title)) & 0xFFFF:X}")
    folder.mkdir(parents=True, exist_ok=True)

    seen: set[str] = set()
    written = 0

    for i, msg in enumerate(messages, 1):
        for lang_label, code in CODE_BLOCK_RE.findall(msg):
            lang = lang_label.strip().lower() or "text"
            digest = hash_code(code)
            if deduplicate and digest in seen:
                continue
            seen.add(digest)

            ext = EXT_MAP.get(lang, ".txt")
            name = "index" + ext if written == 0 and ext in {".html", ".js"} else f"script{written + 1}{ext}"
            path = folder / name
            if not overwrite and path.exists():
                path = path.with_stem(f"{path.stem}_{written+1}")

            if add_comment:
                prefix, suffix = comment_tokens(lang)
                provenance = f'{prefix}Extracted from "{title}", message #{i}{suffix}'
                code = f"{provenance}\n{code}"

            path.write_text(code, encoding="utf-8")
            written += 1
    LOGGER.info("✔ %s → %d files", title, written)
    return written


def extract_all(
    conversations: Iterable[tuple[str, Sequence[str]]],
    out_root: Path,
    workers: int = 1,
    **kwargs,
) -> int:
    """Dispatch extraction in parallel; return total files."""
    out_root.mkdir(parents=True, exist_ok=True)
    if workers <= 1:
        return sum(_process_conversation(t, m, out_root, **kwargs) for t, m in conversations)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(_process_conversation, t, m, out_root, **kwargs) for t, m in conversations]
        return sum(f.result() for f in as_completed(futs))
