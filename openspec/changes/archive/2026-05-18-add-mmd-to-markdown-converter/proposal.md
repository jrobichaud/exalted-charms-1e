## Why

The repository's charm trees currently live as Mermaid `.mmd` files rendered through Sphinx. We want to migrate them to a markdown format (already prototyped at `docs/markdown/abyssal/Abyssal Day Athletics.md`) where each file embeds the Mermaid diagram in a fenced block and exposes every charm description as a heading the diagram can link to via Obsidian-style `internal-link` anchors. With ~100+ source files and split-file groups (`_1`, `_2`, …) to merge, doing this by hand is slow and error-prone — and the migration will need to be rerun whenever the source `.mmd` files change. A deterministic, reproducible converter is needed.

## What Changes

- Add a Python script `scripts/convert_mermaid.py` that converts a single `.mmd` file (or a directory tree) into the new markdown format.
- Add a thin slash command `.claude/commands/convert_mermaid.md` that invokes the script.
- The converter:
  - Merges split-numbered source files (`foo_1.mmd`, `foo_2.mmd`, …) into one output file, emitting one fenced ```mermaid block per source file (each with its own `flowchart TD`).
  - Strips the source `--- config theme ---` frontmatter.
  - Rewrites every node `node_id[Label]` (or `node_id["Label"]`) as `node_id["<a class='internal-link' href='#Canonical'>Label</a>"]`, where `Canonical` is the callback header (the source of truth) and `Label` is preserved verbatim including `<br>`.
  - Preserves arrows (including labeled `--> |X|` and multi-dash `---->`), subgraphs (wrapping inner nodes including cross-references), and `%%` comments.
  - Strips `click <id> callback "…"` blocks from the diagram and emits each as a `## <Canonical>` heading followed by the description body. Headings are ordered by appearance across all merged files.
  - Converts `<br>` inside callback bodies into paragraph breaks.
  - Normalizes all apostrophes (typographic `’` → ASCII `'`) consistently across headings, hrefs, and body.
  - Maps directory names to titles, preserving compound hyphens (`dragon_blooded` → `Dragon-Blooded`, `god_blooded` → `God-Blooded`; otherwise `snake_case` → `Title Case`). Output filename: `<ParentTitle> <BaseTitle>.md`, `_N` suffix dropped.
- Operates in **strict mode**: any parse oddity (missing callback for a node, orphan click block, undefined arrow target, label/header disagreement, malformed mermaid block) fails loudly with `file:line` + reason. The user fixes the source and reruns. No silent normalization beyond apostrophes.
- The script must also be runnable standalone (`python scripts/convert_mermaid.py <path>`) so bulk conversion does not depend on Claude.

## Capabilities

### New Capabilities
- `mmd-markdown-conversion`: deterministic conversion of Mermaid `.mmd` charm-tree files into the markdown-with-embedded-diagram format used in `docs/markdown/`, including multi-file merging, node rewriting, callback extraction to headings, and strict validation.

### Modified Capabilities

(none — this is purely additive)

## Impact

- **New files**: `scripts/convert_mermaid.py`, `.claude/commands/convert_mermaid.md`.
- **New output directory**: `docs/markdown/<exalt_type>/` populated by the converter (the abyssal example already exists by hand).
- **No changes to source `.mmd` files**, the Sphinx build, or the existing RST layout — those continue to work in parallel during the migration.
- **No new runtime dependencies**: the script is plain Python 3, parsing line-by-line; no third-party Mermaid parser library is needed.
- The slash command is user-triggered only; not registered for auto-invocation.