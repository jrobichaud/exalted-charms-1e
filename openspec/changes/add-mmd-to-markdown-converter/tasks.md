## 1. Project setup

- [ ] 1.1 Create `scripts/` directory at repo root if it does not exist
- [ ] 1.2 Decide on minimum Python version (3.10+ recommended for `match` and modern type hints) and document it in the script header
- [ ] 1.3 Create empty `scripts/convert_mermaid.py` with shebang, module docstring, and `if __name__ == "__main__":` guard

## 2. Core parser

- [ ] 2.1 Implement frontmatter stripper: drop a leading `---\nconfig:\n  theme: dark\n---` block; preserve byte-for-byte if not present
- [ ] 2.2 Implement apostrophe normalizer: replace U+2019 with U+0027 on every line read from source
- [ ] 2.3 Implement line tokenizer that classifies each non-blank line as one of: `flowchart_directive`, `node_def`, `arrow`, `click_open`, `click_continue`, `click_close`, `subgraph_open`, `subgraph_close`, `comment`, `other`
- [ ] 2.4 Track current line number and file path alongside each token for error reporting
- [ ] 2.5 Parse node definitions: extract `(id, label_text, was_quoted)` from `id[Label]` and `id["Label"]` forms; tolerate any leading whitespace
- [ ] 2.6 Parse `click <id> callback "<body>"` blocks; support multi-line bodies terminated by the closing `"`; preserve original content verbatim
- [ ] 2.7 Parse subgraph headers: support `subgraph Name`, `subgraph id[Display]`, `subgraph id["Display"]`; track nesting depth and fail strict on unclosed subgraphs

## 3. Charm model and validation

- [ ] 3.1 Define a `Charm` record: `node_id`, `label_text`, `canonical_name`, `body_lines`, `source_file`, `source_line`, `appearance_index`
- [ ] 3.2 Define a `MermaidBlock` record holding the rewritten lines for one source file's diagram
- [ ] 3.3 Extract `canonical_name` from each callback: take the first non-blank content line of the body
- [ ] 3.4 Build a name index per merge group: `node_id → canonical_name`
- [ ] 3.5 Validate every node has a callback OR is inside a cross-reference subgraph; fail strict otherwise with `file:line: node '<id>' has no callback`
- [ ] 3.6 Validate every arrow target is either a defined node OR present in a cross-reference subgraph in any merged file; fail strict otherwise
- [ ] 3.7 Validate every click block matches a defined node; fail strict on orphan callbacks
- [ ] 3.8 Validate the source contains a `flowchart TD` directive; fail strict if absent
- [ ] 3.9 Detect label-vs-header disagreement (modulo `<br>` placement); emit a warning, never an error

## 4. Output rewriter

- [ ] 4.1 Rewrite each node definition to `id["<a class='internal-link' href='#<canonical>'><label_text></a>"]`; preserve `<br>` inside the inner text
- [ ] 4.2 For nodes inside a cross-reference subgraph (no local callback), use the node's own label text as the canonical name for the href
- [ ] 4.3 Preserve arrow lines verbatim (including `|labels|`, multi-dash variants, leading whitespace)
- [ ] 4.4 Preserve subgraph open/close lines and `direction TB` lines verbatim
- [ ] 4.5 Preserve `%%` comment lines verbatim
- [ ] 4.6 Strip every `click` block and its multi-line body from the diagram output
- [ ] 4.7 Strip the source frontmatter from the diagram output

## 5. Heading body emitter

- [ ] 5.1 Emit `## <canonical_name>` for each charm, ordered by appearance index across all merged files
- [ ] 5.2 Strip the canonical-name line from the start of each callback body before emitting (it becomes the heading)
- [ ] 5.3 Convert each `<br>` in the callback body to a paragraph break (one blank line)
- [ ] 5.4 Collapse trailing whitespace and consecutive blank lines (max one blank line between paragraphs)
- [ ] 5.5 Separate each heading-and-body section from the next with exactly two blank lines (matching the existing example)

## 6. File grouping and filename mapping

- [ ] 6.1 Implement merge-group detection: for input file `foo_N.mmd`, glob `foo_*.mmd` in the same directory and sort by trailing integer
- [ ] 6.2 If no trailing `_N`, treat as a singleton group
- [ ] 6.3 Implement directory-title mapping: `dragon_blooded → Dragon-Blooded`, `god_blooded → God-Blooded`, else `snake_case → Title Case`
- [ ] 6.4 Implement base-title mapping: strip trailing `_N`, then `snake_case → Title Case`
- [ ] 6.5 Compose output filename: `<ParentTitle> <BaseTitle>.md`
- [ ] 6.6 Compose output directory: `docs/markdown/<parent_dir_as_is>/`; create if missing
- [ ] 6.7 Refuse to overwrite an existing output file unless `--force` flag is passed

## 7. CLI

- [ ] 7.1 Accept one positional argument: a `.mmd` file path or a directory path
- [ ] 7.2 If a file: process its merge group only
- [ ] 7.3 If a directory: walk recursively for `.mmd` files, deduplicate into merge groups, process each group
- [ ] 7.4 Add `--force` flag to overwrite existing outputs
- [ ] 7.5 Add `--dry-run` flag that performs validation and prints the would-be outputs without writing
- [ ] 7.6 On strict-mode failure, exit 1 and print `<file>:<line>: <reason>` to stderr
- [ ] 7.7 On success, print a one-line summary per output file written

## 8. Slash command wrapper

- [ ] 8.1 Create `.claude/commands/convert_mermaid.md`
- [ ] 8.2 Frontmatter sets `allowed-tools: Bash(python:*)` (and `disable-model-invocation: true` to keep it user-driven only)
- [ ] 8.3 Body: take `$ARGUMENTS` as a path, invoke `python scripts/convert_mermaid.py "$ARGUMENTS"`, surface stdout/stderr, report exit status

## 9. Validation against the existing example

- [ ] 9.1 Run the converter on `docs/mermaid/abyssal/day_athletics_1.mmd`
- [ ] 9.2 Diff the result against the existing `docs/markdown/abyssal/Abyssal Day Athletics.md`
- [ ] 9.3 Reconcile differences: either fix the converter or update the hand-made example (whichever is wrong); record the rationale in the change
- [ ] 9.4 Re-run until the diff is empty (or only consists of explicitly-allowed differences documented in this task)

## 10. Broader smoke test

- [ ] 10.1 Run the converter on every directory under `docs/mermaid/` with `--dry-run`
- [ ] 10.2 Collect the list of files that fail strict validation
- [ ] 10.3 Triage failures: for each, either fix the source `.mmd` or document why the strict rule is wrong and adjust the converter
- [ ] 10.4 Once all files pass dry-run, run for real (without `--force` initially, to confirm no existing outputs are overwritten unintentionally)

## 11. Verification with `openspec validate`

- [ ] 11.1 Run `openspec validate add-mmd-to-markdown-converter --strict` and resolve any reported issues
