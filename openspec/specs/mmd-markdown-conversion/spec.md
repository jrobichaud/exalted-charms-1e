# mmd-markdown-conversion Specification

## Purpose

Defines the behavior of the `.mmd` to Obsidian-flavored markdown converter that rewrites Mermaid charm diagrams and extracts click-callback descriptions as `## <Canonical Name>` headings, with merge handling for split-numbered sibling files.

## Requirements

### Requirement: Convert a single source file

The converter SHALL accept a single `.mmd` file path and emit one markdown file containing the rewritten diagram and extracted charm headings.

#### Scenario: Single-file conversion of a well-formed source

- **WHEN** `scripts/convert_mermaid.py docs/mermaid/abyssal/day_athletics_1.mmd` is run
- **THEN** the script writes `docs/markdown/abyssal/Abyssal Day Athletics.md`
- **AND** the output contains exactly one fenced ```mermaid block
- **AND** the block declares `flowchart TD` on its own line
- **AND** every node defined in the source appears in the block with its label wrapped in `<a class='internal-link' href='#<canonical name>'>…</a>`
- **AND** every click callback in the source is emitted as a `## <canonical name>` heading followed by its description body, in source order
- **AND** no `click … callback "…"` block appears in the output

#### Scenario: Source file has no click callbacks

- **WHEN** the script is run on a `.mmd` file containing a node with no matching `click` block
- **THEN** the script exits with non-zero status
- **AND** stderr reports `<file>:<line>: node '<id>' has no callback`

### Requirement: Merge split-numbered source files

The converter SHALL detect sibling files sharing a base name with a trailing `_<N>` suffix (e.g., `foo_1.mmd`, `foo_2.mmd`) and merge them into a single output markdown file.

#### Scenario: Merge multi-part source

- **WHEN** the script is run on a directory containing `dawn_martial_arts_1.mmd` through `dawn_martial_arts_5.mmd`
- **THEN** exactly one output file `Solar Dawn Martial Arts.md` is written
- **AND** the output contains exactly five fenced ```mermaid blocks, one per source file
- **AND** the blocks appear in numeric order (`_1`, `_2`, `_3`, `_4`, `_5`)
- **AND** each block declares its own `flowchart TD`
- **AND** the `## <canonical name>` headings appear after all mermaid blocks in order of first appearance across the merged files

#### Scenario: Single-file group with `_1` suffix only

- **WHEN** the script is run on `day_athletics_1.mmd` and no `_2`+ siblings exist
- **THEN** the output filename strips the `_1` suffix
- **AND** the output contains exactly one mermaid block

### Requirement: Convert a directory tree

The converter SHALL accept a directory path and convert every `.mmd` file beneath it, grouping split-numbered siblings as defined above.

#### Scenario: Convert an entire exalt-type directory

- **WHEN** `scripts/convert_mermaid.py docs/mermaid/abyssal/` is run
- **THEN** every `.mmd` file under that directory is processed
- **AND** outputs are written to `docs/markdown/abyssal/`
- **AND** files in split-numbered groups are merged into one output each

### Requirement: Rewrite node definitions with internal-link anchors

The converter SHALL rewrite every Mermaid node definition so its label text is wrapped in an Obsidian-compatible internal-link anchor whose `href` matches the canonical charm name from the click callback.

#### Scenario: Unquoted simple label

- **WHEN** the source contains `raitons_nimble_perch[Raiton's Nimble Perch]`
- **AND** the matching callback's first content line is `Raiton's Nimble Perch`
- **THEN** the output contains `raitons_nimble_perch["<a class='internal-link' href='#Raiton's Nimble Perch'>Raiton's Nimble Perch</a>"]`

#### Scenario: Quoted label with parentheses

- **WHEN** the source contains `enhanced_attribute_technique["Enhanced (Attribute) Technique"]`
- **THEN** the output contains `enhanced_attribute_technique["<a class='internal-link' href='#Enhanced (Attribute) Technique'>Enhanced (Attribute) Technique</a>"]`

#### Scenario: Label with `<br>` line breaks

- **WHEN** the source contains `essence_fangs_and_scales_technique[Essence Fangs and<br>Scales Technique]`
- **AND** the callback header is `Essence Fangs and Scales Technique`
- **THEN** the output contains `essence_fangs_and_scales_technique["<a class='internal-link' href='#Essence Fangs and Scales Technique'>Essence Fangs and<br>Scales Technique</a>"]`
- **AND** the `<br>` inside the `<a>` inner text is preserved verbatim

#### Scenario: Label disagrees with callback header (warning, not error)

- **WHEN** a node's label text and its callback's first line differ in any way other than `<br>` placement
- **THEN** the script emits a warning identifying the file, node ID, label, and header
- **AND** the script uses the callback header as the canonical name for both heading and href
- **AND** the script continues processing without failing

### Requirement: Preserve arrows, subgraphs, and comments

The converter SHALL preserve Mermaid arrows, subgraph blocks, and `%%` comment lines from the source into the rewritten mermaid block, modifying only the node label syntax.

#### Scenario: Arrows preserved including labels and multi-dash

- **WHEN** the source contains `enhanced_attribute_technique --> |Strength| infirmity_inflicting_gesture` and `raitons_nimble_perch ----> shadow_races_the_light`
- **THEN** both lines appear in the output mermaid block exactly as written

#### Scenario: Subgraphs preserved with inner nodes rewritten

- **WHEN** the source contains a `subgraph Castebook Dawn` ... `end` block with charm nodes inside
- **THEN** the output preserves the subgraph wrapper line, its `direction TB` line, and the closing `end`
- **AND** every node inside the subgraph is rewritten with the internal-link anchor

#### Scenario: Cross-reference subgraph nodes are wrapped even without local callbacks

- **WHEN** the source contains a cross-reference subgraph like `subgraph water_socialize[Water Socialize Charms]` whose inner nodes refer to charms defined in a different file
- **THEN** the inner nodes are still wrapped in `<a class='internal-link' href='#<label>'>...</a>`
- **AND** no `## heading` is emitted for these cross-referenced charms
- **AND** the canonical name for the href falls back to the node's own label text (since no local callback exists)

#### Scenario: Comments preserved

- **WHEN** the source contains a line starting with `%%`
- **THEN** the line appears verbatim in the output mermaid block

### Requirement: Strip frontmatter and click blocks

The converter SHALL remove the source's `--- config theme ---` frontmatter and all `click … callback "…"` blocks from the rewritten mermaid block.

#### Scenario: Drop frontmatter

- **WHEN** the source begins with `---\nconfig:\n  theme: dark\n---`
- **THEN** no `---` block appears anywhere in the output

#### Scenario: Strip click blocks

- **WHEN** the source contains `click wise_arrow callback "..."` (multi-line, terminated by closing `"`)
- **THEN** no `click` lines or callback string content appear inside the output mermaid block
- **AND** the callback's contents are emitted as a `## heading` + body section after all mermaid blocks

### Requirement: Emit charm headings from callbacks

The converter SHALL emit each click callback as a `## <canonical name>` heading followed by the charm's description body, ordered by first appearance across all merged source files.

#### Scenario: Standard charm body emitted under heading

- **WHEN** a callback contains the standard fields `Cost:`, `Duration:`, `Type:`, `Minimum <Ability>:`, `Minimum Essence:`, `Prerequisite Charms:`, followed by description paragraphs
- **THEN** the output contains a `## <Canonical Name>` heading
- **AND** the stat lines appear in order, each on its own line, in the body
- **AND** description paragraphs appear after the stat block separated by blank lines

#### Scenario: `<br>` in callback body becomes paragraph break

- **WHEN** the callback description contains a mid-paragraph `<br>` separating two paragraphs
- **THEN** the corresponding output has a blank line between the two paragraphs
- **AND** no literal `<br>` text remains in the body

#### Scenario: Heading order matches first-appearance order

- **WHEN** files `foo_1.mmd` and `foo_2.mmd` are merged
- **AND** `foo_1.mmd` defines charms A, B
- **AND** `foo_2.mmd` defines charms C, D
- **THEN** the output headings appear in order A, B, C, D

### Requirement: Normalize apostrophes

The converter SHALL replace every typographic apostrophe (`’`, U+2019) with an ASCII apostrophe (`'`, U+0027) in all output text: headings, hrefs, node labels, and callback body content.

#### Scenario: Apostrophe normalization is consistent

- **WHEN** a source callback header contains `Raiton’s Nimble Perch` (typographic)
- **THEN** the output `## heading`, the `href='#…'`, the `<a>` inner text, and every body reference all use `Raiton's` (ASCII)
- **AND** no `’` character appears anywhere in the output

### Requirement: Filename and directory mapping

The converter SHALL compute the output filename from the source path using the parent directory name and base filename, with compound-hyphenated directory names preserved.

#### Scenario: Single-word parent directory

- **WHEN** the input is `docs/mermaid/lunar/full_moon_brawl.mmd`
- **THEN** the output path is `docs/markdown/lunar/Lunar Full Moon Brawl.md`

#### Scenario: Compound-hyphenated parent directory

- **WHEN** the input is `docs/mermaid/dragon_blooded/fire_dodge_1.mmd`
- **THEN** the output path is `docs/markdown/dragon_blooded/Dragon-Blooded Fire Dodge.md`

#### Scenario: god_blooded parent directory

- **WHEN** the input is `docs/mermaid/god_blooded/<base>_1.mmd`
- **THEN** the parent component of the output filename is `God-Blooded`

#### Scenario: Numeric suffix is stripped

- **WHEN** the input filename is `day_athletics_1.mmd`
- **THEN** the output filename's base is `Abyssal Day Athletics` (no `_1`, no `1`)

### Requirement: Strict-mode failures

The converter SHALL halt on unrecoverable parse problems and report the file and line number of the failure.

#### Scenario: Orphan click block

- **WHEN** the source contains `click ghost_id callback "..."` but no node `ghost_id[...]` is defined anywhere in the file or its merge siblings
- **THEN** the script exits with non-zero status
- **AND** stderr reports `<file>:<line>: click callback references undefined node 'ghost_id'`

#### Scenario: Arrow to undefined node

- **WHEN** the source contains `foo --> bar` and `bar` is not defined as a node and not present in any cross-reference subgraph in this or sibling files
- **THEN** the script exits with non-zero status
- **AND** stderr reports `<file>:<line>: arrow target 'bar' is undefined`

#### Scenario: Node without callback

- **WHEN** the source contains `foo[Foo]` but no `click foo callback "..."` block exists in this or sibling files (and `foo` is not inside a cross-reference subgraph)
- **THEN** the script exits with non-zero status
- **AND** stderr reports `<file>:<line>: node 'foo' has no callback`

#### Scenario: Missing flowchart directive

- **WHEN** the source contains nodes but no `flowchart TD` line
- **THEN** the script exits with non-zero status
- **AND** stderr reports `<file>: missing 'flowchart TD' directive`

#### Scenario: Unterminated subgraph

- **WHEN** the source opens a `subgraph` but the file ends without a matching `end`
- **THEN** the script exits with non-zero status
- **AND** stderr reports `<file>:<line>: subgraph not closed by 'end'`

### Requirement: Slash command wrapper

The repository SHALL expose a `.claude/commands/convert_mermaid.md` slash command that invokes the Python script and surfaces its output.

#### Scenario: Slash command invocation

- **WHEN** the user runs `/convert_mermaid docs/mermaid/abyssal/`
- **THEN** the command runs `python scripts/convert_mermaid.py docs/mermaid/abyssal/`
- **AND** the script's stdout and stderr are shown to the user
- **AND** non-zero exit status is reported as a failure
