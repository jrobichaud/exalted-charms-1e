#!/usr/bin/env python3
"""
convert_mermaid.py — Convert Mermaid .mmd charm-tree files into the
markdown-with-embedded-diagram format used under docs/markdown/.

Requires Python 3.10+.

Usage:
    python scripts/convert_mermaid.py <path-or-dir> [--force] [--dry-run]

Strict mode: any parse oddity (orphan click, undefined arrow target, node
without callback, missing flowchart directive, unclosed subgraph) fails
loudly with `file:line: reason`. Fix the source and rerun.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import NoReturn

if sys.version_info < (3, 10):
    raise SystemExit("convert_mermaid.py requires Python 3.10 or newer")


# ---------- Regexes ----------

RE_FRONTMATTER_DELIM = re.compile(r"^---\s*$")
RE_FLOWCHART = re.compile(r"^\s*flowchart\s+(?:TD|TB|BT|LR|RL)\s*$")
RE_COMMENT = re.compile(r"^\s*%%")
RE_DIRECTION = re.compile(r"^\s*direction\s+\w+\s*$")
RE_NODE = re.compile(r'^(\s*)([a-zA-Z_]\w*)\[("?)(.+?)\3\]\s*$')
RE_ARROW = re.compile(
    r'^(\s*)([a-zA-Z_]\w*)\s+(-{2,})>\s*(?:\|[^|]*\|\s*)?([a-zA-Z_]\w*)\s*$'
)
RE_INVISIBLE_LINK = re.compile(
    r'^(\s*)([a-zA-Z_]\w*)\s+~~~\s+([a-zA-Z_]\w*)\s*$'
)
RE_SUBGRAPH_OPEN = re.compile(r"^\s*subgraph\s+(.+?)\s*$")
RE_SUBGRAPH_END = re.compile(r"^\s*end\s*$")
RE_CLICK_OPEN = re.compile(r'^\s*click\s+([a-zA-Z_]\w*)\s+callback\s+"(.*)$')
RE_CROSS_REF_HEADER = re.compile(r'^[a-zA-Z_]\w*\[.+\]\s*$')
RE_NUMERIC_SUFFIX = re.compile(r"^(.+?)_(\d+)$")

DIR_TITLE_MAP = {
    "dragon_blooded": "Dragon-Blooded",
    "god_blooded": "God-Blooded",
}


# ---------- Data ----------

@dataclass
class Node:
    node_id: str
    label: str           # raw label content between brackets (may include <br>)
    was_quoted: bool
    line: int            # 1-indexed source line
    indent: str          # leading whitespace of the original line
    in_cross_ref: bool


@dataclass
class Click:
    node_id: str
    body: list[str]      # body lines verbatim between opening and closing quotes
    open_line: int


@dataclass
class ParsedFile:
    path: Path
    nodes: dict[str, Node] = field(default_factory=dict)
    clicks: dict[str, Click] = field(default_factory=dict)
    appearance: list[str] = field(default_factory=list)   # click IDs in source order
    arrow_targets: list[tuple[int, str]] = field(default_factory=list)
    arrow_sources: list[tuple[int, str]] = field(default_factory=list)
    diagram_lines: list[str] = field(default_factory=list)  # rewritten mermaid body


# ---------- Helpers ----------

def fail(path: Path, line: int | None, msg: str) -> NoReturn:
    prefix = str(path) if line is None else f"{path}:{line}"
    print(f"{prefix}: {msg}", file=sys.stderr)
    sys.exit(1)


def warn(path: Path, line: int | None, msg: str) -> None:
    prefix = str(path) if line is None else f"{path}:{line}"
    print(f"{prefix}: warning: {msg}", file=sys.stderr)


def normalize_apostrophes(s: str) -> str:
    return s.replace("’", "'")


def strip_frontmatter(lines: list[str]) -> tuple[list[str], int]:
    """Drop a leading `---` ... `---` block. Returns (remaining_lines, lines_dropped)."""
    if not lines or not RE_FRONTMATTER_DELIM.match(lines[0]):
        return lines, 0
    for i in range(1, len(lines)):
        if RE_FRONTMATTER_DELIM.match(lines[i]):
            return lines[i + 1:], i + 1
    return lines, 0


def title_case_words(s: str) -> str:
    return " ".join(w.capitalize() for w in s.split("_"))


def dir_title(dir_name: str) -> str:
    return DIR_TITLE_MAP.get(dir_name, title_case_words(dir_name))


def base_title(base_stem: str) -> str:
    stripped = RE_NUMERIC_SUFFIX.sub(r"\1", base_stem)
    return title_case_words(stripped)


def merge_group(path: Path) -> list[Path]:
    """For foo_N.mmd return all foo_<int>.mmd siblings sorted by N. Else [path]."""
    m = RE_NUMERIC_SUFFIX.match(path.stem)
    if not m:
        return [path]
    base = m.group(1)
    parent = path.parent
    candidates = []
    for p in parent.glob(f"{base}_*.mmd"):
        mm = RE_NUMERIC_SUFFIX.match(p.stem)
        if mm and mm.group(1) == base:
            candidates.append((int(mm.group(2)), p))
    return [p for _, p in sorted(candidates)]


def output_path_for(group: list[Path], repo_root: Path) -> Path:
    first = group[0]
    parent_dir = first.parent.name
    base_stem = RE_NUMERIC_SUFFIX.sub(r"\1", first.stem)
    out_name = f"{dir_title(parent_dir)} {base_title(base_stem)}.md"
    return repo_root / "docs" / "markdown" / parent_dir / out_name


def is_cross_ref_subgraph(header_body: str) -> bool:
    return bool(RE_CROSS_REF_HEADER.match(header_body))


# ---------- Parsing ----------

def parse_file(path: Path) -> ParsedFile:
    raw = path.read_text(encoding="utf-8").splitlines()
    raw = [normalize_apostrophes(line) for line in raw]
    body_lines, fm_offset = strip_frontmatter(raw)

    pf = ParsedFile(path=path)
    subgraph_stack: list[tuple[int, bool]] = []   # (open_line, is_cross_ref)
    flowchart_seen = False

    i = 0
    n = len(body_lines)
    while i < n:
        line = body_lines[i]
        src_line_no = fm_offset + i + 1
        stripped = line.strip()

        if not stripped:
            pf.diagram_lines.append(line)
            i += 1
            continue

        if RE_FLOWCHART.match(line):
            flowchart_seen = True
            pf.diagram_lines.append(line)
            i += 1
            continue

        if RE_COMMENT.match(line):
            pf.diagram_lines.append(line)
            i += 1
            continue

        if RE_DIRECTION.match(line):
            pf.diagram_lines.append(line)
            i += 1
            continue

        if stripped.startswith("subgraph"):
            m = RE_SUBGRAPH_OPEN.match(line)
            if not m:
                fail(path, src_line_no, f"malformed subgraph header: {line.rstrip()!r}")
            header_body = m.group(1)
            subgraph_stack.append((src_line_no, is_cross_ref_subgraph(header_body)))
            pf.diagram_lines.append(line)
            i += 1
            continue

        if RE_SUBGRAPH_END.match(line):
            if not subgraph_stack:
                fail(path, src_line_no, "'end' without matching 'subgraph'")
            subgraph_stack.pop()
            pf.diagram_lines.append(line)
            i += 1
            continue

        m_click = RE_CLICK_OPEN.match(line)
        if m_click:
            click_id = m_click.group(1)
            after = m_click.group(2)
            body: list[str] = []
            opened_at = src_line_no

            # Single-line callback?
            stripped_after = after.rstrip()
            if stripped_after.endswith('"'):
                body.append(stripped_after[:-1])
                i += 1
            else:
                if after:
                    body.append(after)
                i += 1
                terminated = False
                while i < n:
                    cont = body_lines[i]
                    rstripped = cont.rstrip()
                    if rstripped == '"':
                        terminated = True
                        i += 1
                        break
                    if rstripped.endswith('"'):
                        body.append(rstripped[:-1])
                        terminated = True
                        i += 1
                        break
                    body.append(cont)
                    i += 1
                if not terminated:
                    fail(path, opened_at, f"click for '{click_id}' not terminated by '\"'")

            if click_id in pf.clicks:
                fail(path, opened_at, f"duplicate click for '{click_id}'")
            pf.clicks[click_id] = Click(node_id=click_id, body=body, open_line=opened_at)
            pf.appearance.append(click_id)
            continue

        m_arrow = RE_ARROW.match(line)
        if m_arrow:
            source_id = m_arrow.group(2)
            target_id = m_arrow.group(4)
            pf.arrow_sources.append((src_line_no, source_id))
            pf.arrow_targets.append((src_line_no, target_id))
            pf.diagram_lines.append(line)
            i += 1
            continue

        m_inv = RE_INVISIBLE_LINK.match(line)
        if m_inv:
            # Invisible link: validation is permissive — target can be a subgraph id
            # rather than a node id, so don't enforce node-existence on either side.
            pf.diagram_lines.append(line)
            i += 1
            continue

        m_node = RE_NODE.match(line)
        if m_node:
            indent = m_node.group(1)
            node_id = m_node.group(2)
            quoted = m_node.group(3) == '"'
            label_text = m_node.group(4)
            if node_id in pf.nodes:
                fail(path, src_line_no, f"duplicate node '{node_id}'")
            in_cr = bool(subgraph_stack and subgraph_stack[-1][1])
            pf.nodes[node_id] = Node(
                node_id=node_id,
                label=label_text,
                was_quoted=quoted,
                line=src_line_no,
                indent=indent,
                in_cross_ref=in_cr,
            )
            # Placeholder: real rewrite happens after we know group-level canonical names.
            pf.diagram_lines.append(line)
            i += 1
            continue

        fail(path, src_line_no, f"unrecognized line: {line.rstrip()!r}")

    if not flowchart_seen:
        fail(path, None, "missing 'flowchart TD' directive")
    if subgraph_stack:
        fail(path, subgraph_stack[-1][0], "subgraph not closed by 'end'")

    return pf


# ---------- Validation & rewriting at the merge-group level ----------

def canonical_name_from_click(click: Click, path: Path) -> str:
    """First non-blank content line of the body, with <br> tags treated as spaces."""
    for raw in click.body:
        stripped = raw.strip()
        if not stripped:
            continue
        stripped = re.sub(r"<br\s*/?>", " ", stripped)
        stripped = re.sub(r"\s+", " ", stripped).strip()
        if stripped:
            return stripped
    fail(path, click.open_line, f"click for '{click.node_id}' has empty body")


def label_visible_text(label: str) -> str:
    """Strip <br> tags from a node label to compare against a canonical name."""
    return re.sub(r"<br\s*/?>", " ", label).strip()


def rewrite_node_line(raw: str, node: Node, canonical: str) -> str:
    indent = node.indent
    inner = node.label  # preserve <br> verbatim
    href = canonical
    return f"{indent}{node.node_id}[\"<a class='internal-link' href='#{href}'>{inner}</a>\"]"


def render_diagram_block(pf: ParsedFile, canonical: dict[str, str]) -> list[str]:
    """Walk pf.diagram_lines and substitute node-definition placeholders."""
    out: list[str] = []
    for raw in pf.diagram_lines:
        m_node = RE_NODE.match(raw)
        if m_node:
            node_id = m_node.group(2)
            if node_id in pf.nodes:
                out.append(rewrite_node_line(raw, pf.nodes[node_id], canonical[node_id]))
                continue
        out.append(raw)
    return out


def render_charm_section(canonical: str, body: list[str]) -> list[str]:
    """
    Render a charm body as markdown.
      - drop the leading canonical-name line (it becomes the ## heading)
      - dedent (strip common leading whitespace)
      - each trailing <br> on a line is dropped
      - a line consisting solely of <br> (after dedent) becomes a blank line
    """
    # Find the first non-blank line and skip it (it's the canonical/header)
    body_iter = iter(body)
    seen_header = False
    raw_body: list[str] = []
    for line in body_iter:
        if not seen_header:
            if line.strip() == "":
                continue
            seen_header = True
            continue
        raw_body.append(line)

    # Drop trailing blank lines from the source body
    while raw_body and not raw_body[-1].strip():
        raw_body.pop()

    # Compute common indent (minimum non-zero indent among non-blank lines)
    indents: list[int] = []
    for ln in raw_body:
        if ln.strip():
            indents.append(len(ln) - len(ln.lstrip()))
    common = min(indents) if indents else 0

    out: list[str] = [f"## {canonical}", ""]
    paragraph_pending_blank = False
    for raw in raw_body:
        # Dedent
        ln = raw[common:] if raw[:common].strip() == "" else raw.lstrip()
        stripped = ln.rstrip()

        # Bare <br> line → blank line / paragraph break
        if stripped == "<br>" or stripped == "":
            # Collapse consecutive blanks
            if out and out[-1] != "":
                out.append("")
            continue

        # Drop trailing <br>
        if stripped.endswith("<br>"):
            stripped = stripped[: -len("<br>")].rstrip()

        if not stripped:
            if out and out[-1] != "":
                out.append("")
            continue

        out.append(stripped)

    # Strip trailing blanks within the section
    while len(out) > 2 and out[-1] == "":
        out.pop()

    return out


def process_group(group: list[Path], out_path: Path, force: bool, dry_run: bool) -> None:
    parsed = [parse_file(p) for p in group]

    # Group-level indices
    all_nodes: dict[str, tuple[ParsedFile, Node]] = {}
    all_clicks: dict[str, tuple[ParsedFile, Click]] = {}
    cross_ref_ids: set[str] = set()

    for pf in parsed:
        for nid, node in pf.nodes.items():
            if nid in all_nodes:
                prev = all_nodes[nid][1]
                fail(pf.path, node.line, f"duplicate node '{nid}' (also at {all_nodes[nid][0].path}:{prev.line})")
            all_nodes[nid] = (pf, node)
            if node.in_cross_ref:
                cross_ref_ids.add(nid)
        for nid, click in pf.clicks.items():
            if nid in all_clicks:
                prev = all_clicks[nid][1]
                fail(pf.path, click.open_line, f"duplicate click for '{nid}' (also at {all_clicks[nid][0].path}:{prev.open_line})")
            all_clicks[nid] = (pf, click)

    # Validate: every click references a defined node
    for nid, (pf, click) in all_clicks.items():
        if nid not in all_nodes:
            fail(pf.path, click.open_line, f"click callback references undefined node '{nid}'")

    # Validate: every node has a callback unless it's a cross-ref node
    for nid, (pf, node) in all_nodes.items():
        if nid in cross_ref_ids:
            continue
        if nid not in all_clicks:
            fail(pf.path, node.line, f"node '{nid}' has no callback")

    # Validate: every arrow target and source resolves
    for pf in parsed:
        for line_no, tgt in pf.arrow_targets:
            if tgt not in all_nodes:
                fail(pf.path, line_no, f"arrow target '{tgt}' is undefined")
        for line_no, src in pf.arrow_sources:
            if src not in all_nodes:
                fail(pf.path, line_no, f"arrow source '{src}' is undefined")

    # Compute canonical names
    canonical: dict[str, str] = {}
    for nid, (pf, node) in all_nodes.items():
        if nid in all_clicks:
            cn = canonical_name_from_click(all_clicks[nid][1], all_clicks[nid][0].path)
        else:
            # Cross-ref node — fall back to its label's visible text
            cn = label_visible_text(node.label)
        canonical[nid] = cn

    # Warn on label-vs-header drift
    for nid, (pf, node) in all_nodes.items():
        if nid not in all_clicks:
            continue
        visible = label_visible_text(node.label)
        if visible != canonical[nid]:
            warn(
                pf.path,
                node.line,
                f"label '{visible}' disagrees with callback header '{canonical[nid]}' for node '{nid}'",
            )

    # Build the per-file rewritten diagram blocks
    output_parts: list[str] = []
    for pf in parsed:
        diagram = render_diagram_block(pf, canonical)
        # Trim leading blank lines so the block opens cleanly
        while diagram and not diagram[0].strip():
            diagram.pop(0)
        # Trim trailing blank lines
        while diagram and not diagram[-1].strip():
            diagram.pop()
        output_parts.append("```mermaid\n\n" + "\n".join(diagram) + "\n\n```")

    # Build the heading sections in appearance order across all files
    heading_sections: list[str] = []
    for pf in parsed:
        for nid in pf.appearance:
            cn = canonical[nid]
            section = render_charm_section(cn, all_clicks[nid][1].body)
            heading_sections.append("\n".join(section))

    # Assemble final markdown
    body = "\n\n".join(output_parts) + "\n\n\n" + "\n\n\n".join(heading_sections) + "\n"

    if dry_run:
        print(f"[dry-run] would write {out_path}")
        return

    if out_path.exists() and not force:
        fail(out_path, None, "output exists; pass --force to overwrite")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8")
    print(f"wrote {out_path}")


# ---------- CLI ----------

def collect_groups(target: Path) -> list[list[Path]]:
    if target.is_file():
        return [merge_group(target)]
    elif target.is_dir():
        all_files = sorted(target.rglob("*.mmd"))
        seen: set[Path] = set()
        groups: list[list[Path]] = []
        for p in all_files:
            if p in seen:
                continue
            g = merge_group(p)
            for m in g:
                seen.add(m)
            groups.append(g)
        return groups
    else:
        print(f"{target}: not a file or directory", file=sys.stderr)
        sys.exit(2)


def find_repo_root(start: Path) -> Path:
    """Walk up from `start` looking for a `docs/` sibling."""
    cur = start.resolve()
    while cur != cur.parent:
        if (cur / "docs").is_dir():
            return cur
        cur = cur.parent
    # fallback: assume cwd
    return Path.cwd()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Convert .mmd charm trees to embedded-mermaid markdown.")
    parser.add_argument("target", help=".mmd file or directory")
    parser.add_argument("--force", action="store_true", help="overwrite existing outputs")
    parser.add_argument("--dry-run", action="store_true", help="validate and report without writing")
    args = parser.parse_args(argv)

    target = Path(args.target)
    if not target.exists():
        print(f"{target}: does not exist", file=sys.stderr)
        return 2

    repo_root = find_repo_root(target)
    groups = collect_groups(target)

    failures = 0
    for group in groups:
        out_path = output_path_for(group, repo_root)
        try:
            process_group(group, out_path, force=args.force, dry_run=args.dry_run)
        except SystemExit as e:
            if e.code == 0:
                continue
            failures += 1

    if failures:
        print(f"\n{failures} group(s) failed validation", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
