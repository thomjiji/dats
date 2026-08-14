#!/usr/bin/env python3
"""Convert paired ASCII quotes in Chinese Markdown prose."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

OPEN_DOUBLE = chr(0x201C)
CLOSE_DOUBLE = chr(0x201D)
OPEN_SINGLE = chr(0x2018)
CLOSE_SINGLE = chr(0x2019)

FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")


def is_cjk(char: str) -> bool:
    codepoint = ord(char)
    return (
        0x2E80 <= codepoint <= 0x2FFF
        or 0x3040 <= codepoint <= 0x30FF
        or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xAC00 <= codepoint <= 0xD7AF
        or 0xF900 <= codepoint <= 0xFAFF
    )


def contains_cjk(text: str) -> bool:
    return any(is_cjk(char) for char in text)


def is_escaped(text: str, index: int) -> bool:
    backslashes = 0
    index -= 1
    while index >= 0 and text[index] == "\\":
        backslashes += 1
        index -= 1
    return backslashes % 2 == 1


def is_word_char(char: str) -> bool:
    return char.isascii() and (char.isalnum() or char == "_")


def quote_positions(text: str, quote: str) -> list[int]:
    positions = []
    for index, char in enumerate(text):
        if char != quote or is_escaped(text, index):
            continue
        if (
            quote == "'"
            and index > 0
            and index + 1 < len(text)
            and is_word_char(text[index - 1])
            and is_word_char(text[index + 1])
        ):
            continue
        positions.append(index)
    return positions


def convert_prose_segment(segment: str) -> str:
    if not contains_cjk(segment):
        return segment

    chars = list(segment)
    quote_pairs = (
        ('"', OPEN_DOUBLE, CLOSE_DOUBLE),
        ("'", OPEN_SINGLE, CLOSE_SINGLE),
    )
    for quote, opening, closing in quote_pairs:
        positions = quote_positions(segment, quote)
        for pair_start in range(0, len(positions) - 1, 2):
            chars[positions[pair_start]] = opening
            chars[positions[pair_start + 1]] = closing
    return "".join(chars)


def convert_inline_code(line: str) -> str:
    parts = []
    segment_start = 0
    index = 0
    while index < len(line):
        if line[index] != "`":
            index += 1
            continue

        run_start = index
        while index < len(line) and line[index] == "`":
            index += 1
        run = line[run_start:index]
        closing = line.find(run, index)
        if closing == -1:
            parts.append(convert_prose_segment(line[segment_start:run_start]))
            parts.append(line[run_start:])
            return "".join(parts)

        parts.append(convert_prose_segment(line[segment_start:run_start]))
        parts.append(line[run_start : closing + len(run)])
        index = closing + len(run)
        segment_start = index

    if not parts:
        return convert_prose_segment(line)
    parts.append(convert_prose_segment(line[segment_start:]))
    return "".join(parts)


def is_closing_fence(line: str, fence_char: str, minimum_length: int) -> bool:
    pattern = rf"^[ \t]{{0,3}}{re.escape(fence_char)}{{{minimum_length},}}[ \t]*(?:\r?\n)?$"
    return re.match(pattern, line) is not None


def convert_markdown(text: str) -> str:
    output = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines(keepends=True):
        if fence is not None:
            output.append(line)
            if is_closing_fence(line, fence[0], fence[1]):
                fence = None
            continue

        match = FENCE_RE.match(line)
        if match is not None:
            marker = match.group(1)
            output.append(line)
            fence = (marker[0], len(marker))
            continue

        if line.startswith("    ") or line.startswith("\t"):
            output.append(line)
            continue
        output.append(convert_inline_code(line))
    return "".join(output)


def process_file(path: Path, check: bool) -> bool:
    with path.open("r", encoding="utf-8", newline="") as source:
        original = source.read()
    converted = convert_markdown(original)
    changed = converted != original
    if changed and not check:
        with path.open("w", encoding="utf-8", newline="") as target:
            target.write(converted)
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert paired ASCII quotes in Chinese Markdown prose."
    )
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report files that need conversion without modifying them",
    )
    args = parser.parse_args(argv)

    failed = False
    for path in args.files:
        if not path.is_file():
            print(f"not a file: {path}", file=sys.stderr)
            failed = True
            continue
        if process_file(path, args.check):
            print(path)
            if args.check:
                failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
