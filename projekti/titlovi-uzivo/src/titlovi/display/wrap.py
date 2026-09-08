"""Прелом текста на редове по броју знакова (за конзолни приказ и тестове)."""

from __future__ import annotations


def wrap_words(words, max_chars: int):
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > max_chars:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def last_lines(text: str, max_chars: int, n: int):
    lines = wrap_words(text.split(), max_chars)
    return lines[-n:] if n else lines
