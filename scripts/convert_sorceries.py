#!/usr/bin/env python3
"""
convert_sorceries.py — Convert sorcery RST files (docs/sorceries/*.rst) into
the flat Obsidian markdown format used under docs/markdown/sorceries/.

Unlike charms, sorceries have no mermaid tree and no prerequisite schema —
just a name, a Cost/Target line-block, and a description (sometimes with an
embedded RST grid table). The RST source preserves every original book line
as its own line-block line (`| `), including mid-word wrap hyphenation
(e.g. "Cha-" / "risma"). This script reflows that into normal paragraphs,
dropping wrap hyphens ("Cha-" + "risma" -> "Charisma") except for the small
set of real compound words in KEEP_HYPHEN that happen to wrap at their own
hyphen ("hand-to-" + "hand" -> "hand-to-hand").

Usage:
    python scripts/convert_sorceries.py <rst-file> [<rst-file> ...] [--dry-run]

Writes docs/markdown/sorceries/<stem>.md for each input.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

LABEL_LINE_RE = re.compile(
    r"^(\*\*[A-Za-z][\w' ]*\*\*\s*:|[A-Z][A-Za-z][A-Za-z ]{0,22}:)"
)
BORDER_RE = re.compile(r"^\+[-=+]+\+$")
TABLE_ROW_RE = re.compile(r"^\|.*\|$")
HYPHEN_WORD_RE = re.compile(r"([A-Za-z]+)-$")
LEADING_WORD_RE = re.compile(r"^([A-Za-z]+)")

# (prefix, suffix) pairs, lowercased, where the line-wrap hyphen is part of a
# real compound word and must be kept rather than dropped. Found by checking
# every ambiguous join in this corpus against the source book text.
KEEP_HYPHEN = {
    ("to", "hand"),  # hand-to-hand
    ("essence", "using"),  # Essence-using
    ("wide", "beamed"),  # wide-beamed
    ("still", "living"),  # still-living
    ("ear", "shaped"),  # ear-shaped
    ("two", "die"),  # two-die
    ("u", "shan"),  # Yu-Shan (source has it as "Y u-Shan")
    ("and", "yellow"),  # red-and-yellow
    ("self", "effacement"),  # self-effacement
}


@dataclass
class Sorcery:
    name: str
    cost: str
    target: str
    body: list[str]  # rendered chunks: paragraphs or markdown tables


def split_blocks(raw_lines: list[str]) -> list[tuple[str, list[str]]]:
    """Split the file into (title, body_lines) blocks on '<title>\\n.....' headers.

    The underline length is not compared to the title: RST requires it be at
    least as long, but the source has at least one title ("Curse of
    Unyielding Mist") where a typo makes the underline too short. A bare
    all-dots line preceded by a blank line is otherwise unambiguous — no
    such line occurs inside a spell body in this corpus.
    """
    title_starts = []
    for i in range(len(raw_lines) - 1):
        line, underline = raw_lines[i], raw_lines[i + 1]
        if (
            line.strip()
            and len(underline) >= 3
            and set(underline) == {"."}
            and (i == 0 or raw_lines[i - 1].strip() == "")
        ):
            title_starts.append(i)

    blocks = []
    for k, start in enumerate(title_starts):
        title = raw_lines[start].strip()
        body_start = start + 2
        body_end = title_starts[k + 1] - 1 if k + 1 < len(title_starts) else len(raw_lines)
        body = raw_lines[body_start:body_end]
        while body and body[-1].strip() == "":
            body.pop()
        blocks.append((title, body))
    return blocks


def strip_field(line: str, label: str) -> str | None:
    m = re.match(rf"^\|\s*{label}:\s*(.*)$", line)
    return m.group(1) if m else None


def is_blank(line: str) -> bool:
    """A blank line, or RST line-block's own blank marker: a bare '|'."""
    return line.strip() in ("", "|")


def dehyphenate_decision(prefix_word: str, suffix_word: str) -> bool:
    """Return True if the trailing hyphen should be DROPPED (word wrap), False to keep it (real hyphen)."""
    if (prefix_word.lower(), suffix_word.lower()) in KEEP_HYPHEN:
        return False
    return True  # default: wrap-hyphen is far more common in this corpus


def reflow_paragraph_lines(raw: list[str]) -> str:
    """Join a run of line-block lines (no blank separators) into one paragraph/label line,
    respecting label-line breaks and wrap-hyphenation."""
    pieces: list[str] = []
    for text in raw:
        if not pieces:
            pieces.append(text)
            continue
        if LABEL_LINE_RE.match(text):
            pieces.append("\n" + text)
            continue
        prev = pieces[-1]
        hyph = HYPHEN_WORD_RE.search(prev)
        if hyph:
            prefix_word = hyph.group(1)
            lead = LEADING_WORD_RE.match(text)
            suffix_word = lead.group(1) if lead else ""
            drop = dehyphenate_decision(prefix_word, suffix_word)
            if drop:
                pieces[-1] = prev[: hyph.start()] + prefix_word + text
            else:
                pieces[-1] = prev[: hyph.start()] + prefix_word + "-" + text
        else:
            pieces[-1] = prev + " " + text
    return "".join(pieces)


def rst_table_to_markdown(row_lines: list[str]) -> str:
    rows: list[list[str]] = []
    for line in row_lines:
        if BORDER_RE.match(line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    if not rows:
        return ""
    ncols = max(len(r) for r in rows)
    out = ["| " + " | ".join(rows[0] + [""] * (ncols - len(rows[0]))) + " |"]
    out.append("| " + " | ".join(["---"] * ncols) + " |")
    for r in rows[1:]:
        out.append("| " + " | ".join(r + [""] * (ncols - len(r))) + " |")
    return "\n".join(out)


def is_field_continuation(value: str, next_line: str) -> bool:
    """Cost/Target values occasionally wrap onto a second physical line (e.g.
    "Cost: 10 motes ... (maximum" / "20 additional motes)"). Treat the next
    line as a continuation, rather than the start of the body, if it looks
    like a wrapped sentence fragment: starts lowercase, or the value so far
    has an unmatched opening paren."""
    text = next_line[2:] if next_line.startswith("| ") else next_line
    if text[:1].islower():
        return True
    return value.count("(") > value.count(")")


def parse_body(body: list[str]) -> tuple[str, str, list[str]]:
    cost = ""
    target = ""
    i = 0
    n = len(body)
    while i < n:
        line = body[i]
        if cost == "" and (v := strip_field(line, "Cost")) is not None:
            cost = v
            i += 1
            while i < n and not is_blank(body[i]) and is_field_continuation(cost, body[i]):
                cost += " " + body[i][2:]
                i += 1
            continue
        if target == "" and (v := strip_field(line, "Target")) is not None:
            target = v
            i += 1
            while i < n and not is_blank(body[i]) and is_field_continuation(target, body[i]):
                target += " " + body[i][2:]
                i += 1
            continue
        if is_blank(line):
            i += 1
            continue
        break

    rest = body[i:]
    chunks: list[str] = []
    para_buf: list[str] = []

    def flush_para():
        if para_buf:
            chunks.append(("PARA", reflow_paragraph_lines(para_buf)))
            para_buf.clear()

    j = 0
    m = len(rest)
    while j < m:
        line = rest[j]
        if BORDER_RE.match(line):
            flush_para()
            table_lines = [line]
            j += 1
            while j < m and (BORDER_RE.match(rest[j]) or TABLE_ROW_RE.match(rest[j])):
                table_lines.append(rest[j])
                j += 1
            chunks.append(("TABLE", rst_table_to_markdown(table_lines)))
            continue
        if is_blank(line):
            flush_para()
            j += 1
            continue
        if not line.startswith("| "):
            # Stray non-line-block content (shouldn't normally happen); keep as-is.
            para_buf.append(line)
            j += 1
            continue
        para_buf.append(line[2:])
        j += 1
    flush_para()

    body_out = [content for _, content in chunks]
    return cost, target, body_out


def parse_rst(path: Path) -> list[Sorcery]:
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    sorceries = []
    for title, body in split_blocks(raw_lines):
        cost, target, body_out = parse_body(body)
        sorceries.append(Sorcery(name=title, cost=cost, target=target, body=body_out))
    return sorceries


def render_markdown(sorceries: list[Sorcery]) -> str:
    parts = []
    for s in sorceries:
        parts.append(f"## {s.name}\n")
        parts.append(f"Cost: {s.cost}")
        parts.append(f"Target: {s.target}")
        if s.body:
            parts.append("")
            parts.append("\n\n".join(s.body))
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("targets", nargs="+")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    out_dir = Path("docs/markdown/sorceries")
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    for target in args.targets:
        path = Path(target)
        sorceries = parse_rst(path)
        md = render_markdown(sorceries)
        out_path = out_dir / (path.stem + ".md")
        print(f"{path} -> {out_path}: {len(sorceries)} sorceries")
        if not args.dry_run:
            out_path.write_text(md, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
