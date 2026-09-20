## Why

The markdown charm files in `docs/markdown/` (produced by the prior `mmd-markdown-conversion`) embed every charm's prerequisites as plain prose: `Prerequisite Charms: Raiton's Nimble Perch`. Obsidian renders these as flat text — no navigation, no backlinks, no broken-link surfacing. To make the corpus usable as an Obsidian vault, every prerequisite reference must be rewritten as an Obsidian wikilink that resolves to the correct `## Charm Name` heading (same-file or cross-file). With 1,567 prerequisite occurrences across 149 files, doing this by hand is intractable; and the source data has enough drift (hyphenation, plurals, SMA Chinese subtitles, `(Placeholder)`-style headings, multi-word placeholder slots, line wraps, embedded commas) that naïve find-and-replace will miss most of them. A one-time deterministic converter — combined with a small handful of source-data fixes the user has already shepherded — gets us to ~99% coverage with the remainder logged for manual review.

## What Changes

- Add a Python script `scripts/link_prerequisites.py` that walks `docs/markdown/`, rewrites every `Prerequisite Charms:` reference into Obsidian wikilink syntax, and emits a report file listing any unresolved names.
- The converter:
  - Builds an index of every `## Charm Name` heading across the corpus, keyed canonically and by normalized forms (case+punct, plural-aware, paren-suffix-stripped, `(Placeholder)`-substituted).
  - For each `Prerequisite Charms:` line in each file: joins trailing-comma continuations into one logical line, strips stray `<br>` artifacts, splits on commas with a pre-pass that recognizes comma-containing canonical headings (currently only `One Weapon, Two Blows`), then resolves each piece through a fixed cascade:
    1. Exact heading in same file → `[[#Canon]]`
    2. Exact heading in exactly one other file → `[[File#Canon|Original]]`
    3. Normalized case/punct match (Option A — silent canonicalize) → `[[#Canon]]` or cross-file form
    4. Normalized + plural-aware match → as above
    5. Trailing `(...)`-suffix stripped from heading (SMA Chinese subtitles like `(HUA JI)`) → link points to the full heading
    6. `(Placeholder)` substitution (single or multi-word slot, e.g. `Heightened (Sense) Methods` matching `Heightened Smell and Taste Method`) → `[[#Canon|Original]]`
    7. Meta-ref core extraction — strip `All (three|five|N) `, ` Charms?`, `^Appropriate `, ` for the appropriate \w+` — then re-run cascade against the core, with the original wording preserved as the link alias (Fork 2 rule).
    8. None of the above → leave plain text, log to report.
- **Same-file precedence for duplicate-name charms**: if a name has `## ` headings in multiple files (`Ox-Body Technique`, `Terrestrial Circle Sorcery`, `Celestial Circle Sorcery`, `Entombed Mind Technique`), the converter MUST only link when a same-file heading exists. It never picks a cross-file target arbitrarily for a duplicated name.
- Operates in **single-pass, in-place** mode: rewrites files under `docs/markdown/` directly. The user has the markdown checked in; rollback is `git checkout`.
- Emits `docs/markdown/.prereq_report.md` listing each unresolved name with file path, line number, and the original prereq line — sorted by file for review.
- The script is **runnable standalone** (`python scripts/link_prerequisites.py`) with no arguments; it discovers `docs/markdown/` from the script location.

## Capabilities

### New Capabilities
- `prerequisite-link-conversion`: deterministic rewriting of `Prerequisite Charms:` prose references into Obsidian wikilink syntax, with a documented resolution cascade, same-file precedence for duplicate-name charms, and a report file for unresolved references.

### Modified Capabilities

(none — purely additive to the docs pipeline)

## Impact

- **New files**: `scripts/link_prerequisites.py`, `docs/markdown/.prereq_report.md` (generated).
- **Modified files**: every `docs/markdown/**/*.md` whose body contains a `Prerequisite Charms:` line will have those lines rewritten in-place. The mermaid fenced blocks at the top of each file are left untouched.
- **No changes to** `.mmd` sources, the Sphinx build, `scripts/convert_mermaid.py`, or RST files.
- **No new runtime dependencies**: plain Python 3, regex-based.
- One-time run. The script is preserved in `scripts/` for future re-runs if `mmd-markdown-conversion` is rerun and overwrites the markdown.
