## Context

The repository's charm trees live as Mermaid `.mmd` source files under `docs/mermaid/<exalt_type>/`, rendered through Sphinx. A user prototyped a new markdown format at `docs/markdown/abyssal/Abyssal Day Athletics.md` that embeds the Mermaid diagram in a fenced block and exposes each charm description as a `## heading`, with diagram nodes wrapped in `<a class='internal-link' href='#…'>` anchors (Obsidian convention). This format is more readable in plain markdown viewers and supports cross-file linking via Obsidian.

There are ~100+ source `.mmd` files, many split across `_1`, `_2`, `_3`, … siblings (e.g., `dawn_martial_arts_1.mmd` through `_5.mmd`). The files were hand-authored and are likely to contain inconsistencies. The migration needs to be repeatable as source files evolve.

The user wants a deterministic converter, not an LLM-based one, because the transformation is mechanical and the file count is large enough that token-cost and nondeterminism matter.

## Goals / Non-Goals

**Goals:**
- Reproducible conversion of any single `.mmd` file or a directory tree of them.
- Multi-file groups (`foo_1.mmd`, `foo_2.mmd`, …) merge into one output `.md`, with one fenced ```mermaid block per source file (each block declares `flowchart TD`).
- Headings emitted from click callbacks in order of first appearance across the merged files.
- Strict mode: fail loudly on parse oddities with file:line context. The user fixes the source, reruns. No silent correction except apostrophe normalization.
- Runnable both via a slash command and as a standalone Python script.

**Non-Goals:**
- Replacing the current Sphinx build. The RST + Mermaid pipeline stays usable during migration.
- Round-tripping (markdown → `.mmd`). One-way only.
- Editing source `.mmd` files. The converter only reads them.
- Lenient mode / autocorrection (deferred). Strict-first per user decision.
- A separate "validation" command. Strict-mode failures from the converter itself serve that role.

## Decisions

### D1. Deterministic Python script + thin slash command

`scripts/convert_mermaid.py` does the parsing; `.claude/commands/convert_mermaid.md` is a wrapper that runs the script.

**Why:** The transformation is mechanical (regex / line-by-line state machine). A pure markdown command like `transform_charm.md` would re-do regex work on each run, vary subtly between runs, and burn tokens on ~100 files. A script is reproducible and runnable outside Claude.

**Alternatives considered:**
- Pure markdown slash command (rejected: nondeterministic, expensive at scale).
- A skill with auto-invocation (rejected: this is user-driven, not pattern-matched work).

### D2. Callback header is canonical

When a node's label and its click callback's first line disagree, the callback header wins for both the `## heading` and the `href` target. The label is preserved verbatim as the link's display text (including `<br>`).

**Why:** Labels are abbreviated for diagram readability (forced line breaks, dropped articles). Callback headers carry full punctuation and apostrophes, matching how charms are referred to in prose. The `internal-link` anchor must match the heading exactly.

**Alternatives considered:**
- Label wins (rejected: would force every heading to be the abbreviated form).
- Fail if they disagree (rejected: too strict — abbreviation is a legitimate authorship choice).

A label-vs-header disagreement is *not* an error, but the script will emit a warning so authors can audit unintended drift.

### D3. Strict mode, no lenient fallback (yet)

The script halts on the first unrecoverable parse problem with `file:line` and reason. The user fixes the source `.mmd` and reruns.

**Why:** Per user preference. Building strict-first is ~100 lines; lenient-with-report would be ~300 and front-loads guesswork. We learn what the actual failure modes look like by hitting them, then decide whether a lenient mode is worth building.

**Unrecoverable parse oddities (fail loudly):**
- A `click` callback references a node ID with no matching definition.
- An arrow points to a node ID that is neither defined in this file nor wrapped in a cross-reference subgraph.
- A node is defined but has no `click` callback (no canonical name available).
- A mermaid block has no `flowchart TD` directive.
- A `subgraph` is not closed by `end`.
- Callback content is malformed (unterminated quoted string, missing required field like `Cost:`).

**Recoverable, normalized silently:**
- Typographic `’` → ASCII `'` everywhere.

**Recoverable, warned:**
- Label disagrees with callback header (use header).
- Unusual whitespace / blank lines (normalized to spec).

### D4. Apostrophe normalization is the only silent rewrite

All other content (charm body text, including typos like `automn_leafs_descent`, original phrasing, multi-byte characters in descriptions) is preserved verbatim.

**Why:** The single existing converted example uses ASCII apostrophes throughout, including in headings and hrefs. Mixed apostrophes would silently break anchor matching (`#Raiton's` vs `#Raiton's`). Normalizing once at parse time is safer than per-call-site escaping.

### D5. Subgraphs preserved; all inner nodes wrapped

Including cross-reference subgraphs (charms defined in other files). Local `<a href='#…'>` to a heading not in this file is a "broken" anchor in pure markdown but resolves correctly in Obsidian's `internal-link` system, which is what the format targets.

**Why:** User decision. Preserving structure matches the existing diagram organization (source-book attribution, thematic grouping). Wrapping cross-refs keeps node syntax uniform — no special-casing inside subgraphs.

### D6. One mermaid block per source file, each with its own `flowchart TD`

Per user decision and Mermaid's rendering requirements. Each fenced ```mermaid block is parsed independently by the renderer.

### D7. Filename mapping

`<parent_dir>/<base>_N.mmd` → `<ParentTitle> <BaseTitle>.md`, `_N` suffix stripped, output written to `docs/markdown/<ParentDirAsIs>/<Title>.md`.

Directory title conversion:
- `dragon_blooded` → `Dragon-Blooded`
- `god_blooded` → `God-Blooded`
- Else: `snake_case` → `Title Case` (mechanical word-cap on underscore split).

Base filename conversion: `_N` suffix stripped, then `snake_case` → `Title Case`.

**Why:** User decision. The compound-hyphenated forms are the established prose convention.

### D8. `<br>` in callback bodies → paragraph breaks

Each `<br>` in the description body of a callback becomes a blank line in the markdown output (paragraph break). This matches the existing `Abyssal Day Athletics.md` example.

`<br>` in **node labels** (used to fit long names in the diagram) is preserved verbatim inside the `<a>` tag's inner text — the label's `<br>` is structural for diagram layout, not for prose flow.

## Risks / Trade-offs

- **Strict mode blocks bulk conversion on the first broken file.** → Mitigation: run on small batches (one directory at a time). If too painful, revisit lenient+report.
- **Cross-reference subgraphs produce technically-broken anchors in pure markdown.** → Mitigation: documented as intended (Obsidian-only resolution). Pure-markdown previews of these files will show non-functional links until the target file is opened in Obsidian.
- **Hand-written source apostrophe inconsistency is silently normalized.** → Mitigation: this is the desired behavior; the script logs the normalization counts so authors can spot-check.
- **Label-vs-header disagreement isn't a hard error.** → Mitigation: warnings printed at end of run; author can audit. If silent drift becomes a problem, promote to error in a follow-up.
- **No formal Mermaid grammar.** The script uses regex-based parsing, which can miss exotic Mermaid syntax. → Mitigation: scope is limited to the subset present in this repo. Strict-mode failures surface unsupported syntax immediately.
- **Parser becomes outdated if source files adopt new Mermaid features.** → Mitigation: failures are loud; the converter is small enough to extend.