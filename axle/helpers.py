"""Helper utilities for working with AXLE.

This module provides utilities for string manipulation, on top of AXLE core transformations.
"""

import re


def remove_comments(
    code: str,
    include_module_docs: bool = False,
    include_docstrings: bool = False,
) -> str:
    """Remove comments from Lean code, including multi-line comments.

    Args:
        code: The Lean source code.
        include_module_docs: If True, keep module docs (/-! ... -/).
        include_docstrings: If True, keep docstrings (/-- ... -/).
    """
    OUT, LINE, BLOCK, STRING = 0, 1, 2, 3
    state = OUT
    block_depth = 0
    keep_block = False
    string_delim = ""
    i, n = 0, len(code)
    result = []

    while i < n:
        two = code[i : i + 2]
        three = code[i : i + 3]
        ch = code[i]

        if state == OUT:
            if ch in ('"', "'"):
                state = STRING
                string_delim = ch
                result.append(ch)
                i += 1
            elif three == "/--":
                # Docstring
                state = BLOCK
                block_depth = 1
                keep_block = include_docstrings
                if keep_block:
                    result.append(three)
                i += 3
            elif three == "/-!":
                # Module doc
                state = BLOCK
                block_depth = 1
                keep_block = include_module_docs
                if keep_block:
                    result.append(three)
                i += 3
            elif two == "--":
                state = LINE
                i += 2
            elif two == "/-":
                state = BLOCK
                block_depth = 1
                keep_block = False
                i += 2
            else:
                result.append(ch)
                i += 1

        elif state == STRING:
            result.append(ch)
            if ch == "\\" and i + 1 < n:
                # Escape sequence - include next char and skip it
                result.append(code[i + 1])
                i += 2
            elif ch == string_delim:
                state = OUT
                i += 1
            else:
                i += 1

        elif state == LINE:
            if ch == "\n":
                result.append("\n")
                state = OUT
            i += 1

        else:  # BLOCK
            if two == "/-":
                block_depth += 1
                if keep_block:
                    result.append(two)
                i += 2
            elif two == "-/":
                block_depth -= 1
                if keep_block:
                    result.append(two)
                i += 2
                if block_depth == 0:
                    state = OUT
                    keep_block = False
            else:
                if keep_block:
                    result.append(ch)
                i += 1

    return "".join(result)


def inline_lean_messages(
    code: str,
    messages: list[str],
    prefix: str = "/- ",
    suffix: str = " -/",
) -> str:
    """Inline Lean compiler messages as comments in the source code.

    Messages with line numbers are inserted after the corresponding line.
    Messages on the same line are sorted by column position.
    Unmatched messages are appended at the end.

    Args:
        code: The source code to annotate.
        messages: List of compiler messages to inline.
        prefix: String to prepend to each message (default: "/- " for Lean comments).
        suffix: String to append to each message (default: " -/" for Lean comments).

    Example messages:
        -:1:23: info: unsolved goals at sorry
        -:1:23-1:30: info: unsolved goals at sorry (with endPos)
        file_1:1:0: info: renaming `foo` -> `foo_1`
        Missing required declaration 'requiredTheorem'
    """
    # Parse messages: file_name:line_no:line_pos[-end_line:end_pos]: message
    pattern = re.compile(r"^[^:]+:(\d+):(\d+)(?:-\d+:\d+)?:")
    messages_by_line: dict[int, list[tuple[int, str]]] = {}
    unmatched: list[str] = []

    for msg in messages:
        msg = msg.strip()
        if match := pattern.match(msg):
            line_no, col_no = int(match.group(1)), int(match.group(2))
            messages_by_line.setdefault(line_no, []).append((col_no, msg))
        else:
            unmatched.append(msg)

    def format_messages(msgs: list[tuple[int, str]]) -> list[str]:
        return [f"{prefix}{msg}{suffix}" for _, msg in sorted(msgs)]

    lines = code.splitlines()

    # Collect messages for lines beyond code length into unmatched
    for line_no, msgs in messages_by_line.items():
        if line_no > len(lines):
            unmatched.extend(msg for _, msg in msgs)

    # Prepend line 0 messages
    result = format_messages(messages_by_line.get(0, []))
    for i, line in enumerate(lines):
        result.append(line)
        result.extend(format_messages(messages_by_line.get(i + 1, [])))

    if unmatched:
        result.append("\n")
        result.extend(f"{prefix}{msg}{suffix}" for msg in unmatched)

    return "\n".join(result)
