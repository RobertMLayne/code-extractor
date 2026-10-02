# tests/test_parser.py
from extract_code.parser import load_conversations


def test_plain_html(tmp_path):
    html = tmp_path / "x.html"
    html.write_text("<html><body><pre>```python\nprint('x')\n```</pre></body></html>")
    convos = load_conversations(html)
    assert convos[0][0] == "chat_export"
    assert "print('x')" in convos[0][1][0]
