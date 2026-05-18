## 1. Script scaffolding

- [x] 1.1 Create `scripts/link_prerequisites.py` with a `main()` entry point that takes no arguments, computes `MD_ROOT = Path(__file__).resolve().parent.parent / "docs" / "markdown"`, and exits with a usage error if any argument is given
- [x] 1.2 Add a top-level docstring summarizing the conversion contract and pointing to `openspec/specs/prerequisite-link-conversion/spec.md`

## 2. Heading index

- [x] 2.1 Implement `iter_md_files(MD_ROOT)` yielding every `*.md` path under `docs/markdown/`
- [x] 2.2 Implement `build_heading_index(files)` that returns `(headings_by_file, heading_locations, duplicate_names, comma_headings)`, scanning each file line-by-line and toggling a fence-state flag so that `## ` lines inside fenced ` ```mermaid ` blocks are NOT indexed
- [x] 2.3 Implement `build_norm_indexes(heading_locations)` producing `norm_index` (lowercase + non-alnum stripped → canonical) and `norm_plural_index` (additionally strip word-boundary trailing `s`); when two distinct canonicals collide on the same normalized form, prefer the unique-name canonical and skip the duplicate
- [x] 2.4 Implement `build_paren_stripped_index(heading_locations)` mapping `base_form → canonical_with_(suffix)` for every heading where a trailing `(...)` exists
- [x] 2.5 Implement `build_placeholder_patterns(heading_locations)` returning a list of `(compiled_regex, canonical)` tuples; each `(Word)` slot in a heading becomes a non-greedy `[A-Za-z ]+?` capture, the regex is fully anchored, case-insensitive, and a trailing `s` is made optional

## 3. Prereq line parsing

- [x] 3.1 Implement a per-file streaming reader that emits `(line_number, line_text, in_mermaid_block)` tuples, with `in_mermaid_block` toggling on `^```mermaid` and back off on `^```` while inside
- [x] 3.2 Implement `find_prereq_blocks(lines)` yielding `(start_line, end_line, body_text)` tuples, where `body_text` is the captured text after `Prerequisite Charms:` joined across trailing-comma continuations; halt continuation on blank lines, on lines matching the known-field regex (`^(Cost|Duration|Type|Minimum [A-Za-z]+|Minimum Essence|Prerequisite Charms):`), on `^## `, or on `^```` (fence)
- [x] 3.3 Implement `clean_body(body)` that strips `<br>` (with surrounding whitespace), collapses runs of whitespace, and trims

## 4. Comma-aware split

- [x] 4.1 Implement `split_pieces(body, comma_headings)` that first replaces every occurrence of each `comma_heading` with a placeholder token (e.g. `\x00N\x00`), splits the result on `,`, strips each piece, restores placeholder tokens, drops empty/`None` pieces, and passes through any piece beginning with `[[` unchanged

## 5. Resolution cascade

- [x] 5.1 Implement `resolve(piece, current_file, heading_indexes)` returning a `Resolution` value carrying canonical name, source file, match rule (1–8), and a flag for whether the link should include an alias
- [x] 5.2 Implement rule 1 (same-file exact) and rule 2 (cross-file exact for non-duplicate names) with explicit `name not in duplicate_names` guard for rule 2
- [x] 5.3 Implement rules 3 and 4 (normalized + plural-aware), routing the resolved canonical back through 1/2 to choose link form
- [x] 5.4 Implement rule 5 (paren-suffix-stripped match), preserving the canonical's full `(...)` suffix in the link target
- [x] 5.5 Implement rule 6 (`(Placeholder)` substitution) using the compiled patterns from 2.5; on match, link to the canonical with the original piece as alias
- [x] 5.6 Implement rule 7 (meta-ref core extraction): apply substitutions `^All (three|five|two|four|\d+)\s+`, `^Appropriate\s+`, `\s+Charms?$`, `\s+for the appropriate \w+$` (case-insensitive), then recursively call `resolve` on the stripped core; on hit, alias = original piece
- [x] 5.7 Implement rule 8 (unresolved): return a `Resolution` flagged as unresolved, carrying the original piece for the report

## 6. Link formatting

- [x] 6.1 Implement `format_link(resolution, current_file)` producing the wikilink string per the formatting table in `design.md` Decision 4 — `[[#X]]`, `[[#X|alias]]`, `[[File#X]]`, or `[[File#X|alias]]`
- [x] 6.2 Ensure cross-file `File` is the basename without `.md` (e.g. `Abyssal Daybreak Medicine`)
- [x] 6.3 For unresolved resolutions, return the original piece text verbatim (no wrapping)

## 7. File rewriting

- [x] 7.1 Implement `rewrite_file(path, heading_indexes, unresolved_collector)` that streams the file, accumulates a new line list, and for each detected `Prerequisite Charms:` block (found via `find_prereq_blocks`) replaces the source lines with a single output line of the form `Prerequisite Charms: <formatted pieces joined by ", ">`; never modify lines inside a fenced mermaid block; insert a single space after `Prerequisite Charms:` even if the source omitted it
- [x] 7.2 Write the rewritten content back to `path` only if it differs from the original (avoids touching mtime on no-op files)
- [x] 7.3 Append each unresolved piece into `unresolved_collector` as a tuple of `(piece, file_path, source_line_number, original_body)`

## 8. Report generation

- [x] 8.1 Implement `categorize_unresolved(piece)` returning `"generic-meta"` if `piece` matches `^(Any|one|One complete)\b` (case-insensitive), else `"missing-or-typo"`
- [x] 8.2 Implement `write_report(unresolved_collector, report_path)` that writes `docs/markdown/.prereq_report.md` with two sections — "Generic count meta-refs (no link target exists)" and "Genuinely missing from corpus" — each listing entries sorted by `(file, line)` in the format `- \`<piece>\` — <relative_file_path>:<line>`; if a section has no entries, emit `(none)` under it

## 9. End-to-end wiring

- [x] 9.1 In `main()`, run: build heading index → for each markdown file under `MD_ROOT` call `rewrite_file` → write report → print a one-line summary `"Rewrote N prereq lines across M files; K unresolved (see docs/markdown/.prereq_report.md)"`
- [x] 9.2 Verify idempotency by running the script twice in a row in a scratch state and confirming `git diff` is empty after the second run

## 10. Manual validation

- [x] 10.1 Run the script once; review `git diff docs/markdown/` and confirm: (a) mermaid blocks are untouched, (b) the user's pre-existing cross-file link in `Abyssal Daybreak Craft.md` is preserved unchanged, (c) the `One Weapon, Two Blows` reference resolves as a single link
- [x] 10.2 Open `docs/markdown/.prereq_report.md` and confirm it lists the expected ~12 leftovers (8 generic meta-refs + ~4 truly-missing names) without any false-positive entries from previously-resolvable references
- [x] 10.3 Open three or four sample files in Obsidian (one solar, one abyssal, one lunar, one sidereal SMA file with paren-suffix headings) and confirm wikilinks render and navigate correctly
