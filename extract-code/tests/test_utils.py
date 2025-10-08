"""Public API."""
from importlib.metadata import version as _v

from .cli import main as _main
from .extractor import extract_all
from .parser import load_conversations
from .utils import comment_tokens, hash_code, sanitize_filename

__all__ = [
    "extract_all",
    "load_conversations",
    "comment_tokens",
    "hash_code",
    "sanitize_filename",
    "main",
]

__version__: str = _v("extract-code")
main = _main  # re‑export for convenience
