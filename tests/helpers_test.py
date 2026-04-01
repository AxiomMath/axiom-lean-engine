"""Tests for AXLE helper functions."""

from axle.helpers import inline_lean_messages, remove_comments


def test_remove_comments_nested_block() -> None:
    """Nested block comments should be handled correctly."""
    code = "/- outer /- inner -/ outer -/ def x := 1"
    result = remove_comments(code)
    assert "def x := 1" in result
    assert "outer" not in result
    assert "inner" not in result


def test_remove_comments_preserves_strings() -> None:
    """Comment-like syntax inside strings should not be removed."""
    code = 'def x := "-- not a comment"'
    result = remove_comments(code)
    assert '"-- not a comment"' in result


def test_remove_comments_handles_escaped_quotes() -> None:
    """Escaped quotes in strings should not end the string early."""
    code = r'def x := "he said \"hello\"" -- comment'
    result = remove_comments(code)
    assert r'"he said \"hello\""' in result
    assert "comment" not in result


def test_remove_comments_mixed_doc_types() -> None:
    """Both module docs and docstrings can be selectively kept."""
    code = "/-! module doc -/\n/-- docstring -/\n/- regular comment -/\ndef x := 1"

    # Keep only module docs
    result = remove_comments(code, include_module_docs=True, include_docstrings=False)
    assert "/-! module doc -/" in result
    assert "docstring" not in result
    assert "regular comment" not in result

    # Keep only docstrings
    result = remove_comments(code, include_module_docs=False, include_docstrings=True)
    assert "module doc" not in result
    assert "/-- docstring -/" in result
    assert "regular comment" not in result

    # Keep both
    result = remove_comments(code, include_module_docs=True, include_docstrings=True)
    assert "/-! module doc -/" in result
    assert "/-- docstring -/" in result
    assert "regular comment" not in result


def test_remove_comments_nested_in_module_doc() -> None:
    """Nested block comments within module docs should be handled."""
    code = "/-! outer /- nested -/ outer -/\ndef x := 1"
    result = remove_comments(code, include_module_docs=True)
    assert "/-! outer /- nested -/ outer -/" in result
    assert "def x := 1" in result


def test_remove_comments_docstring_at_eof() -> None:
    """Docstring at end of file with no trailing newline."""
    code = "def x := 1\n/-- final docstring -/"
    result = remove_comments(code, include_docstrings=True)
    assert "def x := 1" in result
    assert "/-- final docstring -/" in result


def test_remove_comments_line_comment_at_eof() -> None:
    """Line comment at end of file with no trailing newline."""
    code = "def x := 1 -- final comment"
    result = remove_comments(code)
    assert "def x := 1" in result
    assert "final comment" not in result


def test_inline_lean_messages_unmatched() -> None:
    """Messages without line numbers should still be included."""
    code = "def x := 1"
    messages = ["General warning"]
    result = inline_lean_messages(code, messages)
    assert "/- General warning -/" in result


def test_inline_lean_messages_multiple_same_line() -> None:
    """Multiple messages on the same line should all be included."""
    code = "def x := 1"
    messages = ["-:1:0: warning: a", "-:1:5: warning: b"]
    result = inline_lean_messages(code, messages)
    assert "warning: a" in result
    assert "warning: b" in result


def test_inline_lean_messages_with_endpos() -> None:
    """Messages with endPos (line:col-line:col format) should be parsed correctly."""
    code = "def x := 1"
    messages = ["-:1:4-1:10: error: type mismatch"]
    result = inline_lean_messages(code, messages)
    assert "def x := 1" in result
    assert "/- -:1:4-1:10: error: type mismatch -/" in result


def test_inline_lean_messages_mixed_formats() -> None:
    """Messages with and without endPos should both work."""
    code = "def x := 1\ndef y := 2"
    messages = [
        "-:1:4: warning: without endPos",
        "-:2:4-2:10: warning: with endPos",
    ]
    result = inline_lean_messages(code, messages)
    assert "without endPos" in result
    assert "with endPos" in result
