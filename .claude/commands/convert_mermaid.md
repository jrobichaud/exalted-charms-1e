---
allowed-tools: Bash(python3 scripts/convert_mermaid.py:*)
disable-model-invocation: true
argument-hint: <path-to-.mmd-file-or-directory> [--force] [--dry-run]
---

Run the deterministic `.mmd → markdown` converter at `scripts/convert_mermaid.py`.

Pass `$ARGUMENTS` verbatim to the script. The script:
- Converts a single `.mmd` file (merging `_N` siblings) or a whole directory
- Strips the source `--- config theme ---` frontmatter
- Normalizes typographic apostrophes to ASCII
- Rewrites every `node_id[Label]` as `node_id["<a class='internal-link' href='#<canonical>'>Label</a>"]`
- Emits each click callback as a `## heading` + description body, ordered by appearance
- Writes to `docs/markdown/<exalt_type>/<Title Cased Name>.md`
- Operates in **strict mode** — fails loudly with `file:line: reason` on parse oddities

Flags:
- `--force` overwrite existing outputs
- `--dry-run` validate without writing (continues past failures so you see all of them)

Steps:
1. Run `python3 scripts/convert_mermaid.py $ARGUMENTS`
2. Show stdout and stderr verbatim
3. If exit status is non-zero, report the failure count

Examples:
- `/convert_mermaid docs/mermaid/abyssal/day_athletics_1.mmd`
- `/convert_mermaid docs/mermaid/abyssal/` — converts every group under abyssal/
- `/convert_mermaid docs/mermaid/ --dry-run` — validate the whole tree
