"""Utility helpers: comment tokens, hashing, sanitising, regex."""
from __future__ import annotations

import hashlib
import re
from typing import Final, Tuple

__all__ = [
    "EXT_MAP",
    "COMMENT_PREFIX",
    "comment_tokens",
    "hash_code",
    "sanitize_filename",
    "CODE_BLOCK_RE",
]

# language → file extension
EXT_MAP: Final[dict[str, str]] = {
    "python": ".py",
    "py": ".py",
    "javascript": ".js",
    "js": ".js",
    "jsx": ".js",
    "typescript": ".ts",
    "ts": ".ts",
    "java": ".java",
    "c": ".c",
    "cpp": ".cpp",
    "c++": ".cpp",
    "html": ".html",
    "xml": ".xml",
    "json": ".json",
    "bash": ".sh",
    "shell": ".sh",
    "sh": ".sh",
    "ruby": ".rb",
    "perl": ".pl",
    "php": ".php",
    "r": ".r",
    "go": ".go",
    "rust": ".rs",
    "sql": ".sql",
}

# language → (prefix, suffix)
COMMENT_PREFIX: Final[dict[str, Tuple[str, str]]] = {
    **{k: ("# ", "") for k in ("python", "py", "bash", "sh", "shell", "r")},
    **{k: ("// ", "") for k in ("javascript", "js", "typescript", "ts", "java", "c", "cpp", "c++", "go", "rust")},
    **{k: ("<!-- ", " -->") for k in ("html", "xml")},
    "json": ("// ", ""),
    "sql": ("-- ", ""),
}
DEFAULT_PREFIX: Final[Tuple[str, str]] = ("# ", "")

CODE_BLOCK_RE: Final[re.Pattern[str]] = re.compile(
    r"```([^\n]*)\n(.*?)```", flags=re.DOTALL
)

# ---------------------------------------------------------------------------


def comment_tokens(lang: str) -> Tuple[str, str]:
    """Return comment (prefix, suffix) for *lang* or a safe default."""
    return COMMENT_PREFIX.get(lang, DEFAULT_PREFIX)


def hash_code(text: str) -> str:
    """SHA‑256 hex digest for deduplication / provenance."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sanitize_filename(name: str) -> str:
    """Make a string OS‑safe by replacing disallowed characters."""
    return re.sub(r"[^A-Za-z0-9_.\- ]+", "_", name).strip()
