"""Rewrite ``Prerequisite Charms:`` prose lines in ``docs/markdown/`` as Obsidian wikilinks.

Implements the cascade described in ``openspec/specs/prerequisite-link-conversion/spec.md``:
exact same-file, exact cross-file (unique names only), normalized punct/case,
plural-aware, paren-suffix-stripped, ``(Placeholder)`` substitution, and meta-ref
core extraction. Unresolved references are left as plain text and recorded in
``docs/markdown/.prereq_report.md``.

The script is idempotent: re-running it produces no diff. It takes no arguments
and discovers ``docs/markdown/`` relative to its own location.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


SCRIPT_DIR = Path(__file__).resolve().parent
MD_ROOT = SCRIPT_DIR.parent / "docs" / "markdown"
REPORT_PATH = MD_ROOT / ".prereq_report.md"

FIELD_HEADER = re.compile(
    r"^(Cost|Duration|Type|Minimum [A-Za-z]+|Minimum Essence|Prerequisite Charms)\s*:"
)
HEADING = re.compile(r"^## (.+?)\s*$")
PREREQ_LINE = re.compile(r"^Prerequisite Charms:\s*(.*)$")
FENCE = re.compile(r"^```")
MERMAID_FENCE_OPEN = re.compile(r"^```mermaid\b")
PAREN_SUFFIX = re.compile(r"\s*\([^)]+\)\s*$")
PLACEHOLDER_SLOT = re.compile(r"\\\([A-Z][a-z]+\\\)")


def iter_md_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md") if p.name != REPORT_PATH.name)


def _normalize(s: str, depluralize: bool = False) -> str:
    s = s.lower()
    if depluralize:
        s = re.sub(r"s\b", "", s)
    return re.sub(r"[^a-z0-9]+", "", s)


def _iter_lines_with_fence(text: str) -> Iterator[tuple[int, str, bool]]:
    in_mermaid = False
    for i, line in enumerate(text.splitlines(), 1):
        if not in_mermaid and MERMAID_FENCE_OPEN.match(line):
            yield i, line, False  # fence opener itself is part of the block
            in_mermaid = True
            continue
        if in_mermaid:
            yield i, line, True
            if FENCE.match(line):
                in_mermaid = False
            continue
        yield i, line, False


@dataclass(frozen=True)
class HeadingIndex:
    headings_by_file: dict[Path, set[str]]
    heading_locations: dict[str, list[Path]]
    duplicate_names: set[str]
    comma_headings: set[str]
    norm_index: dict[str, str]
    norm_plural_index: dict[str, str]
    paren_stripped: dict[str, str]
    placeholder_patterns: list[tuple[re.Pattern[str], str]]


def build_heading_index(files: Iterable[Path]) -> HeadingIndex:
    headings_by_file: dict[Path, set[str]] = defaultdict(set)
    heading_locations: dict[str, list[Path]] = defaultdict(list)
    for f in files:
        text = f.read_text(encoding="utf-8")
        for _, line, in_mermaid in _iter_lines_with_fence(text):
            if in_mermaid:
                continue
            m = HEADING.match(line)
            if not m:
                continue
            name = m.group(1).strip()
            headings_by_file[f].add(name)
            heading_locations[name].append(f)

    duplicate_names = {n for n, locs in heading_locations.items() if len(locs) > 1}
    comma_headings = {n for n in heading_locations if "," in n}

    norm_index, norm_plural_index = _build_norm_indexes(heading_locations, duplicate_names)
    paren_stripped = _build_paren_stripped_index(heading_locations)
    placeholder_patterns = _build_placeholder_patterns(heading_locations)

    return HeadingIndex(
        headings_by_file=dict(headings_by_file),
        heading_locations=dict(heading_locations),
        duplicate_names=duplicate_names,
        comma_headings=comma_headings,
        norm_index=norm_index,
        norm_plural_index=norm_plural_index,
        paren_stripped=paren_stripped,
        placeholder_patterns=placeholder_patterns,
    )


def _build_norm_indexes(
    heading_locations: dict[str, list[Path]],
    duplicate_names: set[str],
) -> tuple[dict[str, str], dict[str, str]]:
    norm_index: dict[str, str] = {}
    norm_plural_index: dict[str, str] = {}

    def add(idx: dict[str, str], key: str, name: str) -> None:
        existing = idx.get(key)
        if existing is None:
            idx[key] = name
            return
        if existing == name:
            return
        # Collision on a distinct canonical: prefer the unique-name one.
        existing_dup = existing in duplicate_names
        new_dup = name in duplicate_names
        if existing_dup and not new_dup:
            idx[key] = name

    for name in heading_locations:
        add(norm_index, _normalize(name), name)
        add(norm_plural_index, _normalize(name, depluralize=True), name)
    return norm_index, norm_plural_index


def _build_paren_stripped_index(heading_locations: dict[str, list[Path]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for name in heading_locations:
        if PAREN_SUFFIX.search(name):
            base = PAREN_SUFFIX.sub("", name).strip()
            if base and base not in heading_locations:
                out.setdefault(base, name)
    return out


def _build_placeholder_patterns(
    heading_locations: dict[str, list[Path]],
) -> list[tuple[re.Pattern[str], str]]:
    patterns: list[tuple[re.Pattern[str], str]] = []
    for name in heading_locations:
        if not re.search(r"\([A-Z][a-z]+\)", name):
            continue
        pat = re.escape(name)
        pat = PLACEHOLDER_SLOT.sub("[A-Za-z ]+?", pat)
        if pat.endswith("s"):
            pat = pat[:-1] + "s?"
        patterns.append((re.compile(f"^{pat}$", re.IGNORECASE), name))
    return patterns


@dataclass(frozen=True)
class PrereqBlock:
    start_line: int  # 1-based, inclusive
    end_line: int  # 1-based, inclusive
    body: str
    original_line: str  # first source line, for the report


def find_prereq_blocks(text: str) -> list[PrereqBlock]:
    lines = list(_iter_lines_with_fence(text))
    out: list[PrereqBlock] = []
    i = 0
    while i < len(lines):
        line_no, line, in_mermaid = lines[i]
        if in_mermaid or not PREREQ_LINE.match(line):
            i += 1
            continue
        m = PREREQ_LINE.match(line)
        body = m.group(1)
        start = line_no
        end = line_no
        original = line
        # Consume trailing-comma continuations
        while body.rstrip().endswith(",") and i + 1 < len(lines):
            next_no, next_line, next_in_mermaid = lines[i + 1]
            if next_in_mermaid:
                break
            stripped = next_line.strip()
            if not stripped:
                break
            if FIELD_HEADER.match(stripped) or HEADING.match(stripped) or FENCE.match(stripped):
                break
            body = body + " " + stripped
            end = next_no
            i += 1
        out.append(PrereqBlock(start_line=start, end_line=end, body=body, original_line=original))
        i += 1
    return out


def clean_body(body: str) -> str:
    body = re.sub(r"\s*<br\s*/?>\s*", " ", body)
    body = re.sub(r"\s+", " ", body)
    return body.strip()


def split_pieces(body: str, comma_headings: set[str]) -> list[str]:
    # Lock comma-containing headings behind sentinel tokens so the split skips them.
    locks: dict[str, str] = {}
    masked = body
    for idx, name in enumerate(sorted(comma_headings, key=len, reverse=True)):
        if name in masked:
            token = f"\x00CHL{idx}\x00"
            locks[token] = name
            masked = masked.replace(name, token)

    pieces: list[str] = []
    for raw in masked.split(","):
        piece = raw.strip()
        if not piece or piece.lower() == "none":
            continue
        for token, name in locks.items():
            piece = piece.replace(token, name)
        pieces.append(piece)
    return pieces


@dataclass(frozen=True)
class Resolution:
    canonical: str | None  # heading name to link to (None when unresolved)
    target_file: Path | None  # file containing the canonical (None when same-file or unresolved)
    rule: int  # 1..8
    alias: str | None  # display text when an alias is needed; None means bare link or unresolved
    original: str  # the prereq piece as it appeared in source


def _is_same_file(name: str, current_file: Path, idx: HeadingIndex) -> bool:
    return name in idx.headings_by_file.get(current_file, set())


def _resolve_with_canonical(
    canonical: str,
    current_file: Path,
    idx: HeadingIndex,
) -> tuple[Path | None, int]:
    """Return (target_file_or_None_if_same_file, rule_used) for an already-resolved canonical."""
    if _is_same_file(canonical, current_file, idx):
        return None, 1
    if canonical in idx.duplicate_names:
        # Cross-file refused for duplicates; caller should treat as unresolved.
        return None, 0
    locations = idx.heading_locations.get(canonical, [])
    if len(locations) == 1:
        return locations[0], 2
    return None, 0


def resolve(piece: str, current_file: Path, idx: HeadingIndex) -> Resolution:
    # Rules 1 & 2: exact match
    if piece in idx.heading_locations:
        if _is_same_file(piece, current_file, idx):
            return Resolution(piece, None, 1, None, piece)
        if piece not in idx.duplicate_names:
            locs = idx.heading_locations[piece]
            if len(locs) == 1:
                return Resolution(piece, locs[0], 2, piece, piece)

    # Rule 3: normalized (punct/case)
    n = _normalize(piece)
    if n in idx.norm_index:
        canon = idx.norm_index[n]
        target, used = _resolve_with_canonical(canon, current_file, idx)
        if used:
            alias = piece if used == 2 else None  # cross-file gets alias=original to display
            return Resolution(canon, target, 3, alias, piece)

    # Rule 4: plural-aware
    nd = _normalize(piece, depluralize=True)
    if nd in idx.norm_plural_index:
        canon = idx.norm_plural_index[nd]
        target, used = _resolve_with_canonical(canon, current_file, idx)
        if used:
            alias = piece if used == 2 else None
            return Resolution(canon, target, 4, alias, piece)

    # Rule 5: paren-suffix stripped
    if piece in idx.paren_stripped:
        canon = idx.paren_stripped[piece]
        target, used = _resolve_with_canonical(canon, current_file, idx)
        if used:
            alias = piece if used == 2 else None
            return Resolution(canon, target, 5, alias, piece)

    # Rule 6: placeholder substitution — always alias with original piece
    for pat, canon in idx.placeholder_patterns:
        if pat.match(piece):
            target, used = _resolve_with_canonical(canon, current_file, idx)
            if used:
                return Resolution(canon, target, 6, piece, piece)

    # Rule 7: meta-ref core extraction
    core = piece
    core = re.sub(r"^All\s+(?:three|five|two|four|\d+)\s+", "", core, flags=re.IGNORECASE)
    core = re.sub(r"^Appropriate\s+", "", core, flags=re.IGNORECASE)
    core = re.sub(r"\s+for the appropriate \w+$", "", core, flags=re.IGNORECASE)
    core = re.sub(r"\s+Charms?$", "", core, flags=re.IGNORECASE)
    core = core.strip()
    if core != piece and core:
        inner = resolve(core, current_file, idx)
        if inner.canonical is not None:
            return Resolution(inner.canonical, inner.target_file, 7, piece, piece)

    return Resolution(None, None, 8, None, piece)


def format_link(res: Resolution, current_file: Path) -> str:
    if res.canonical is None:
        return res.original
    if res.target_file is None:
        if res.alias and res.alias != res.canonical:
            return f"[[#{res.canonical}|{res.alias}]]"
        return f"[[#{res.canonical}]]"
    file_stem = res.target_file.stem
    if res.alias and res.alias != res.canonical:
        return f"[[{file_stem}#{res.canonical}|{res.alias}]]"
    return f"[[{file_stem}#{res.canonical}|{res.canonical}]]"


def _passthrough_link(piece: str) -> bool:
    return piece.startswith("[[")


def rewrite_file(
    path: Path,
    idx: HeadingIndex,
    unresolved: list[tuple[str, Path, int, str]],
) -> bool:
    text = path.read_text(encoding="utf-8")
    blocks = find_prereq_blocks(text)
    if not blocks:
        return False

    src_lines = text.splitlines(keepends=False)
    keep_newline = text.endswith("\n")

    # Build a map of source line numbers (1-based) → action.
    # For each block, the start line is replaced by the rewritten line; lines
    # start+1 .. end are deleted.
    replacements: dict[int, str] = {}
    deletions: set[int] = set()

    for block in blocks:
        cleaned = clean_body(block.body)
        if cleaned.lower() == "none":
            new_line = "Prerequisite Charms: None"
            replacements[block.start_line] = new_line
            for ln in range(block.start_line + 1, block.end_line + 1):
                deletions.add(ln)
            continue
        pieces = split_pieces(cleaned, idx.comma_headings)
        rendered: list[str] = []
        for piece in pieces:
            if _passthrough_link(piece):
                rendered.append(piece)
                continue
            res = resolve(piece, path, idx)
            rendered.append(format_link(res, path))
            if res.canonical is None:
                unresolved.append((piece, path, block.start_line, block.original_line))
        new_line = "Prerequisite Charms: " + ", ".join(rendered)
        replacements[block.start_line] = new_line
        for ln in range(block.start_line + 1, block.end_line + 1):
            deletions.add(ln)

    out_lines: list[str] = []
    for i, line in enumerate(src_lines, 1):
        if i in deletions:
            continue
        if i in replacements:
            out_lines.append(replacements[i])
        else:
            out_lines.append(line)

    new_text = "\n".join(out_lines) + ("\n" if keep_newline else "")
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


GENERIC_META = re.compile(r"^(Any|one|One complete)\b", re.IGNORECASE)


def categorize_unresolved(piece: str) -> str:
    return "generic-meta" if GENERIC_META.match(piece) else "missing-or-typo"


def write_report(unresolved: list[tuple[str, Path, int, str]]) -> None:
    by_cat: dict[str, list[tuple[str, Path, int, str]]] = {
        "generic-meta": [],
        "missing-or-typo": [],
    }
    for entry in unresolved:
        by_cat[categorize_unresolved(entry[0])].append(entry)
    for cat in by_cat:
        by_cat[cat].sort(key=lambda e: (str(e[1]), e[2], e[0]))

    lines: list[str] = []
    lines.append("# Prerequisite Link Conversion — Unresolved References")
    lines.append("")
    lines.append("Generated by `scripts/link_prerequisites.py`. Each entry is a prereq piece the")
    lines.append("cascade could not resolve to a `## Charm Name` heading.")
    lines.append("")
    lines.append("## Generic count meta-refs (no link target exists)")
    lines.append("")
    if by_cat["generic-meta"]:
        for piece, path, line_no, _orig in by_cat["generic-meta"]:
            rel = path.relative_to(MD_ROOT.parent.parent)
            lines.append(f"- `{piece}` — {rel}:{line_no}")
    else:
        lines.append("(none)")
    lines.append("")
    lines.append("## Genuinely missing from corpus")
    lines.append("")
    if by_cat["missing-or-typo"]:
        for piece, path, line_no, _orig in by_cat["missing-or-typo"]:
            rel = path.relative_to(MD_ROOT.parent.parent)
            lines.append(f"- `{piece}` — {rel}:{line_no}")
    else:
        lines.append("(none)")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(
            "usage: link_prerequisites.py  (no arguments; operates on docs/markdown/)",
            file=sys.stderr,
        )
        return 2

    files = iter_md_files(MD_ROOT)
    idx = build_heading_index(files)

    unresolved: list[tuple[str, Path, int, str]] = []
    changed = 0
    prereq_count = 0
    for f in files:
        text_before = f.read_text(encoding="utf-8")
        blocks_before = len(find_prereq_blocks(text_before))
        if rewrite_file(f, idx, unresolved):
            changed += 1
        prereq_count += blocks_before

    write_report(unresolved)
    print(
        f"Rewrote {prereq_count} prereq lines across {changed} files; "
        f"{len(unresolved)} unresolved (see {REPORT_PATH.relative_to(MD_ROOT.parent.parent)})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
