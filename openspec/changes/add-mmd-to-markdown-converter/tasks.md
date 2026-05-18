## 1. Project setup

- [x] 1.1 Create `scripts/` directory at repo root if it does not exist
- [x] 1.2 Decide on minimum Python version (3.10+ recommended for `match` and modern type hints) and document it in the script header
- [x] 1.3 Create empty `scripts/convert_mermaid.py` with shebang, module docstring, and `if __name__ == "__main__":` guard

## 2. Core parser

- [x] 2.1 Implement frontmatter stripper: drop a leading `---\nconfig:\n  theme: dark\n---` block; preserve byte-for-byte if not present
- [x] 2.2 Implement apostrophe normalizer: replace U+2019 with U+0027 on every line read from source
- [x] 2.3 Implement line tokenizer that classifies each non-blank line as one of: `flowchart_directive`, `node_def`, `arrow`, `click_open`, `click_continue`, `click_close`, `subgraph_open`, `subgraph_close`, `comment`, `other`
- [x] 2.4 Track current line number and file path alongside each token for error reporting
- [x] 2.5 Parse node definitions: extract `(id, label_text, was_quoted)` from `id[Label]` and `id["Label"]` forms; tolerate any leading whitespace
- [x] 2.6 Parse `click <id> callback "<body>"` blocks; support multi-line bodies terminated by the closing `"`; preserve original content verbatim
- [x] 2.7 Parse subgraph headers: support `subgraph Name`, `subgraph id[Display]`, `subgraph id["Display"]`; track nesting depth and fail strict on unclosed subgraphs

## 3. Charm model and validation

- [x] 3.1 Define a `Charm` record: `node_id`, `label_text`, `canonical_name`, `body_lines`, `source_file`, `source_line`, `appearance_index`
- [x] 3.2 Define a `MermaidBlock` record holding the rewritten lines for one source file's diagram
- [x] 3.3 Extract `canonical_name` from each callback: take the first non-blank content line of the body (with embedded `<br>` collapsed to spaces — handles label-style headers in some files)
- [x] 3.4 Build a name index per merge group: `node_id → canonical_name`
- [x] 3.5 Validate every node has a callback OR is inside a cross-reference subgraph; fail strict otherwise with `file:line: node '<id>' has no callback`
- [x] 3.6 Validate every arrow target is either a defined node OR present in a cross-reference subgraph in any merged file; fail strict otherwise
- [x] 3.7 Validate every click block matches a defined node; fail strict on orphan callbacks
- [x] 3.8 Validate the source contains a `flowchart <direction>` directive (any of TD/TB/BT/LR/RL — the spec said TD but several files use LR/TB and direction is rendering-only); fail strict if absent
- [x] 3.9 Detect label-vs-header disagreement (modulo `<br>` placement); emit a warning, never an error

## 4. Output rewriter

- [x] 4.1 Rewrite each node definition to `id["<a class='internal-link' href='#<canonical>'><label_text></a>"]`; preserve `<br>` inside the inner text
- [x] 4.2 For nodes inside a cross-reference subgraph (no local callback), use the node's own label text as the canonical name for the href
- [x] 4.3 Preserve arrow lines verbatim (including `|labels|`, multi-dash variants, leading whitespace, and `~~~` invisible links)
- [x] 4.4 Preserve subgraph open/close lines and `direction TB` lines verbatim
- [x] 4.5 Preserve `%%` comment lines verbatim
- [x] 4.6 Strip every `click` block and its multi-line body from the diagram output
- [x] 4.7 Strip the source frontmatter from the diagram output

## 5. Heading body emitter

- [x] 5.1 Emit `## <canonical_name>` for each charm, ordered by appearance index across all merged files
- [x] 5.2 Strip the canonical-name line from the start of each callback body before emitting (it becomes the heading)
- [x] 5.3 A bare `<br>` line in the callback body becomes a paragraph break (blank line); a `<br>` at end of a content line is a line-ending marker and is dropped (matches the existing Abyssal Day Athletics example's behavior for stat-block lines)
- [x] 5.4 Collapse trailing whitespace and consecutive blank lines (max one blank line between paragraphs)
- [x] 5.5 Separate each heading-and-body section from the next with exactly two blank lines (matching the existing example)

## 6. File grouping and filename mapping

- [x] 6.1 Implement merge-group detection: for input file `foo_N.mmd`, glob `foo_<int>.mmd` siblings in the same directory and sort by trailing integer (filter so non-numeric siblings like `foo_bar.mmd` don't get pulled in)
- [x] 6.2 If no trailing `_N`, treat as a singleton group
- [x] 6.3 Implement directory-title mapping: `dragon_blooded → Dragon-Blooded`, `god_blooded → God-Blooded`, else `snake_case → Title Case`
- [x] 6.4 Implement base-title mapping: strip trailing `_N`, then `snake_case → Title Case`
- [x] 6.5 Compose output filename: `<ParentTitle> <BaseTitle>.md`
- [x] 6.6 Compose output directory: `docs/markdown/<parent_dir_as_is>/`; create if missing
- [x] 6.7 Refuse to overwrite an existing output file unless `--force` flag is passed

## 7. CLI

- [x] 7.1 Accept one positional argument: a `.mmd` file path or a directory path
- [x] 7.2 If a file: process its merge group only
- [x] 7.3 If a directory: walk recursively for `.mmd` files, deduplicate into merge groups, process each group
- [x] 7.4 Add `--force` flag to overwrite existing outputs
- [x] 7.5 Add `--dry-run` flag that performs validation and prints the would-be outputs without writing
- [x] 7.6 On strict-mode failure, exit 1 and print `<file>:<line>: <reason>` to stderr (dry-run continues past failures across groups so the user can see the full picture; write mode halts on first failure to avoid partial state)
- [x] 7.7 On success, print a one-line summary per output file written

## 8. Slash command wrapper

- [x] 8.1 Create `.claude/commands/convert_mermaid.md`
- [x] 8.2 Frontmatter sets `allowed-tools: Bash(python3 scripts/convert_mermaid.py:*)` (and `disable-model-invocation: true` to keep it user-driven only)
- [x] 8.3 Body: take `$ARGUMENTS` as a path, invoke `python3 scripts/convert_mermaid.py $ARGUMENTS`, surface stdout/stderr, report exit status

## 9. Validation against the existing example

- [x] 9.1 Run the converter on `docs/mermaid/abyssal/day_athletics_1.mmd`
- [x] 9.2 Diff the result against the existing `docs/markdown/abyssal/Abyssal Day Athletics.md`
- [x] 9.3 Reconcile differences: the 19 differing lines are all typographic-apostrophe normalizations (e.g. `Raiton’s` → `Raiton's`). This is exactly the spec's intended behavior (D4: apostrophe normalization is the only silent rewrite). The hand-made example had typographic apostrophes in callback bodies that weren't normalized at hand-conversion time. The converter's output is the new source of truth; the example is overwritten in 9.4.
- [x] 9.4 Re-ran the converter with `--force`; the example now matches converter output. All remaining diffs would only re-appear if typographic apostrophes were reintroduced into the source `.mmd`.

## 10. Broader smoke test

- [x] 10.1 Ran the converter on `docs/mermaid/` with `--dry-run`. 138 groups validate, 16 fail strict mode.
- [x] 10.2 Failing groups (deferred to authoring follow-up — each is a real source/syntax issue strict mode correctly surfaces):

  **Cross-reference subgraph using bare `subgraph Name` instead of the conventional bracketed form `subgraph id[Display Name]` — FIXED in source (12 occurrences across 11 files; perception_1 had two such blocks):**
  - `abyssal/daybreak_craft_1.mmd` — `Medicine` → `medicine[Medicine Charms]`
  - `abyssal/daybreak_medicine_1.mmd` — `Craft` → `craft[Craft Charms]` (and updated the `~~~` link target)
  - `abyssal/moonshadow_linguistics_1.mmd` — `Occult` → `occult[Occult Charms]`
  - `arcanoi/evoke_the_ancient_clay_1.mmd` — `Common` → `common[Common Charms]`
  - `arcanoi/tangled_web_arts_1.mmd` — `Essence-Measuring Thief Arts` → `essence_measuring_thief_arts[Essence-Measuring Thief Arts]`
  - `dragon_blooded/air_linguistics_1.mmd` — `Lore` → `lore[Lore Charms]`
  - `lunar/interaction_knowledge_1.mmd` — `Perception Charms` → `perception[Perception Charms]`
  - `lunar/perception_1.mmd` — `Interaction and Knowledge` → `interaction_and_knowledge[Interaction and Knowledge Charms]` AND `Shapeshifting Charms` → `shapeshifting[Shapeshifting Charms]`
  - `lunar/ranged_combat_1.mmd` — `Melee Combat Charms` → `melee_combat[Melee Combat Charms]`
  - `solar/dawn_brawl.mmd` — `Endurance` → `endurance[Endurance Charms]`
  - `trinity/dreaming_pearl_courtesan_style.mmd` — `Solar Eclipse Socialize` → `solar_eclipse_socialize[Solar Eclipse Socialize Charms]`

  **Duplicate node definitions across the `_1`/`_2` files of a merge group (2 groups, still deferred):**
  - `dragon_blooded/earth_craft_1.mmd:7` and `earth_craft_2.mmd:42` both define `stone_carving_fingers_form`
  - `lunar/unarmed_combat_1.mmd:9` and `unarmed_combat_2.mmd:9` both define `body_weapon_technique`

  **Unsupported Mermaid syntax variants (3 groups, still deferred):**
  - `others/souls.mmd:15` — uses diamond decision-node syntax `id{Label}` (not currently parsed)
  - `spirits/compassion_2.mmd:235` and `spirits/conviction_2.mmd:120` — use inline node definitions inside arrow lines (`a --> b[Label]`), which the parser does not yet support

- [x] 10.3 Triage decision: the 11 cross-reference subgraph bugs were fixed at the source by adding the bracketed `id[Display]` form (and a matching `direction TB`). The remaining 5 failures (2 duplicate-node, 3 unsupported syntax) are deferred — duplicates need an authoring decision about which `_N` file owns each charm, and the syntax variants warrant a parser-extension change of their own.
- [x] 10.4 Ran the converter for real on the full tree after fixes: **149 groups converted successfully**, written to `docs/markdown/<exalt_type>/`. 5 groups remain unconverted pending the deferred fixes above.

## 11. Verification with `openspec validate`

- [x] 11.1 Ran `openspec validate add-mmd-to-markdown-converter --strict`. Result: `Change 'add-mmd-to-markdown-converter' is valid`.
