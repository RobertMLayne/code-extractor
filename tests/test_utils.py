"""Regression checks for extraction options through the public package."""

from pathlib import Path

from extract_code import extract_all


def test_extraction_deduplicates_and_preserves_existing_files(tmp_path: Path) -> None:
    conversation = [("Example / export", ["```python\nprint('hello')\n```"] * 2)]
    count = extract_all(
        conversation, tmp_path, deduplicate=True, overwrite=False, add_comment=True
    )
    assert count == 1
    folder = tmp_path / "Example _ export"
    original = folder / "script1.py"
    expected = "# Extracted from \"Example / export\", message #1\nprint('hello')\n"
    assert original.read_text(encoding="utf-8") == expected

    count = extract_all(
        conversation, tmp_path, deduplicate=True, overwrite=False, add_comment=False
    )
    assert count == 1
    assert original.read_text(encoding="utf-8") == expected
    assert (folder / "script1_1.py").read_text(encoding="utf-8") == "print('hello')\n"
