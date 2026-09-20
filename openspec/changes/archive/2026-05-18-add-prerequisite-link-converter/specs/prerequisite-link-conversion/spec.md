## ADDED Requirements

### Requirement: Heading index built from all markdown files

The script SHALL scan every `*.md` file under `docs/markdown/` and build an index of `## Charm Name` headings, recording for each heading the file path it appears in. The index MUST distinguish canonical names that appear in exactly one file from names that appear in multiple files (duplicate names).

#### Scenario: Single-file heading indexed
- **WHEN** `docs/markdown/abyssal/Abyssal Day Athletics.md` contains `## Raiton's Nimble Perch` and no other file does
- **THEN** the index records that name with a single file path and marks it non-duplicate

#### Scenario: Duplicate-name heading flagged
- **WHEN** `## Ox-Body Technique` appears as a heading in five separate files
- **THEN** the index records all five file paths and marks the name as duplicate

#### Scenario: Mermaid content excluded
- **WHEN** the script encounters lines starting with `## ` inside a fenced ` ```mermaid ` block
- **THEN** those lines MUST NOT be indexed as charm headings

### Requirement: Prerequisite line detection and continuation joining

The script SHALL detect each `Prerequisite Charms:` line in the prose section of every markdown file (outside fenced code blocks) and join multi-line continuations into one logical reference list before resolution.

#### Scenario: Single-line prereq detected
- **WHEN** a file contains `Prerequisite Charms: Fault-Finding Scrutiny`
- **THEN** the script processes that single line as one reference list

#### Scenario: Missing space after colon tolerated
- **WHEN** a file contains `Prerequisite Charms:Decay Resistance Preparation` with no space after the colon
- **THEN** the script processes it as if the space were present

#### Scenario: Trailing-comma continuation joined
- **WHEN** a `Prerequisite Charms:` line ends with `,` and the next non-blank line is neither a known field header (`Cost:`, `Duration:`, `Type:`, `Minimum`, another `Prerequisite Charms:`, a `## ` heading) nor a fenced-block delimiter
- **THEN** the next line is concatenated to the current one with a single space separator, and consumption continues until the trailing-comma condition no longer holds

#### Scenario: Mermaid block content not processed
- **WHEN** a `Prerequisite Charms:` substring appears inside a fenced ` ```mermaid ` block
- **THEN** the script MUST NOT rewrite it

### Requirement: Reference text preprocessing

After capturing the prereq body, the script SHALL strip extraction artifacts before resolution.

#### Scenario: `<br>` stripped from a name
- **WHEN** a captured body contains `Shaping the Once-Living<br> Form`
- **THEN** the script replaces `<br>` (with surrounding whitespace) with a single space, yielding `Shaping the Once-Living Form`

#### Scenario: Whitespace collapsed
- **WHEN** the captured body contains runs of multiple spaces or tabs
- **THEN** runs are collapsed to single spaces and the body is trimmed

### Requirement: Comma-aware splitting

The script SHALL split the cleaned prereq body into individual reference pieces, preserving any canonical heading that contains a literal comma.

#### Scenario: Plain comma split
- **WHEN** the body is `Wise Arrow, Sight Without Eyes`
- **THEN** the script produces two pieces: `Wise Arrow` and `Sight Without Eyes`

#### Scenario: Comma-containing heading preserved
- **WHEN** the body is `One Weapon, Two Blows` and `One Weapon, Two Blows` exists as a canonical heading
- **THEN** the script produces exactly one piece: `One Weapon, Two Blows`

#### Scenario: Comma-containing heading mixed with other pieces
- **WHEN** the body is `One Weapon, Two Blows, Iron Whirlwind Attack`
- **THEN** the script produces two pieces: `One Weapon, Two Blows` and `Iron Whirlwind Attack`

#### Scenario: Empty and None pieces dropped
- **WHEN** a split produces an empty piece or a piece equal to `None`
- **THEN** that piece is dropped from the output reference list

#### Scenario: Already-linked piece passed through
- **WHEN** a piece begins with `[[`
- **THEN** the script leaves it unmodified (idempotency)

### Requirement: Resolution cascade

For each unlinked reference piece, the script SHALL attempt resolution through an ordered cascade and use the first matching rule. The cascade is:

1. **Same-file exact** — piece equals a heading in the current file.
2. **Cross-file exact for unique names** — piece equals a heading that exists in exactly one other file and is not in the duplicate-name set.
3. **Punct/case/whitespace normalization** — piece normalizes (lowercase, strip non-alphanumeric) to a canonical heading.
4. **Plural-aware normalization** — piece normalizes (additionally stripping trailing `s` per word boundary) to a canonical heading.
5. **Paren-suffix-stripped heading** — heading with a trailing `(SUBTITLE)` removed equals the piece.
6. **`(Placeholder)` substitution** — a heading containing one or more `(Word)` slots produces a regex (case-insensitive, slot = non-greedy `[A-Za-z ]+?`, optional trailing `s`) that matches the piece.
7. **Meta-ref core extraction** — strip leading `All (three|five|two|four|N) `, leading `Appropriate `, trailing ` Charms?`, trailing ` for the appropriate <word>`, then re-run rules 1–6 against the stripped core.
8. **Unresolved** — leave plain, record in report.

#### Scenario: Same-file exact wins over cross-file
- **WHEN** piece `Terrestrial Circle Sorcery` exists as a heading in both the current file and four others
- **THEN** the same-file occurrence is selected as the link target

#### Scenario: Cross-file refused for duplicate names
- **WHEN** piece `Ox-Body Technique` is referenced in a file that does not define it, and `Ox-Body Technique` exists as a heading in multiple other files
- **THEN** rule 2 MUST NOT match; the cascade continues; if no other rule matches, the piece is left plain

#### Scenario: Cross-file accepted for unique names
- **WHEN** piece `Flesh-Mending Discipline` is referenced in a file that does not define it, and `Flesh-Mending Discipline` exists as a heading in exactly one other file
- **THEN** rule 2 matches and produces a cross-file link

#### Scenario: Punct/case drift canonicalized
- **WHEN** piece is `Wolf Endurance Method` and a heading `Wolf-Endurance Method` exists
- **THEN** rule 3 matches and the resolved canonical is `Wolf-Endurance Method`

#### Scenario: Plural drift canonicalized
- **WHEN** piece is `Fists of Iron Technique` and a heading `Fist of Iron Technique` exists
- **THEN** rule 4 matches and the resolved canonical is `Fist of Iron Technique`

#### Scenario: SMA paren suffix bridged
- **WHEN** piece is `Astrology Interruption Method` and a heading `Astrology Interruption Method (HUA JI)` exists
- **THEN** rule 5 matches and the resolved canonical is `Astrology Interruption Method (HUA JI)`

#### Scenario: Multi-word placeholder slot matched
- **WHEN** piece is `Heightened Smell and Taste Method` and a heading `Heightened (Sense) Methods` exists
- **THEN** rule 6 matches and the resolved canonical is `Heightened (Sense) Methods`

#### Scenario: Meta-ref core extracted
- **WHEN** piece is `All three (Material) Withering Method Charms`
- **THEN** rule 7 strips `All three ` and ` Charms`, yielding `(Material) Withering Method`, which matches a heading and is selected as the canonical

#### Scenario: Generic count meta-ref left plain
- **WHEN** piece is `Any three Lore Charms` and no heading matches after meta-ref stripping
- **THEN** the piece is left plain text and recorded in the report

### Requirement: Wikilink formatting

Each resolved piece SHALL be rewritten according to its match category:

- Rules 1, 3, 4 producing a same-file canonical → `[[#Canonical]]` (no alias).
- Rules 2, 3, 4 producing a cross-file canonical → `[[OtherFile#Canonical|Original]]`.
- Rule 5 → `[[#Canonical with (SUBTITLE)]]` if same-file, else `[[OtherFile#Canonical with (SUBTITLE)|Original]]`.
- Rules 6, 7 → `[[#Canonical|Original]]` if same-file, else `[[OtherFile#Canonical|Original]]`.

The cross-file `OtherFile` part is the file basename without the `.md` extension (matching Obsidian's wikilink convention).

#### Scenario: Same-file exact emits bare link
- **WHEN** piece `Wise Arrow` resolves to a same-file heading `Wise Arrow`
- **THEN** the emitted link is `[[#Wise Arrow]]`

#### Scenario: Same-file fuzzy emits bare link (Option A canonicalize)
- **WHEN** piece `Wolf Endurance Method` resolves via rule 3 to same-file heading `Wolf-Endurance Method`
- **THEN** the emitted link is `[[#Wolf-Endurance Method]]` (no alias)

#### Scenario: Cross-file unique emits aliased link
- **WHEN** piece `Flesh-Mending Discipline` resolves to `Abyssal Daybreak Medicine.md`'s heading
- **THEN** the emitted link is `[[Abyssal Daybreak Medicine#Flesh-Mending Discipline|Flesh-Mending Discipline]]`

#### Scenario: Meta-ref preserves original wording in alias
- **WHEN** piece `All three (Material) Withering Method Charms` resolves to same-file heading `(Material) Withering Method`
- **THEN** the emitted link is `[[#(Material) Withering Method|All three (Material) Withering Method Charms]]`

#### Scenario: SMA paren-suffix link points to full heading
- **WHEN** piece `Astrology Interruption Method` resolves to a heading `Astrology Interruption Method (HUA JI)` in the same file
- **THEN** the emitted link is `[[#Astrology Interruption Method (HUA JI)]]` (no alias because rule 5 canonicalizes silently like rules 3-4)

### Requirement: Output line rewriting

The script SHALL replace the original `Prerequisite Charms:` line (and any joined continuation lines) with a single output line.

#### Scenario: Multi-line input collapses to one output line
- **WHEN** the source contains `Prerequisite Charms: A,\nB` across two lines and both pieces resolve
- **THEN** the output is one line `Prerequisite Charms: <link to A>, <link to B>`

#### Scenario: Missing space after colon normalized
- **WHEN** the source contains `Prerequisite Charms:Decay Resistance Preparation`
- **THEN** the output line is `Prerequisite Charms: [[#Decay Resistance Preparation]]` (space inserted)

#### Scenario: Pieces preserved in source order
- **WHEN** the source contains `Prerequisite Charms: B, A, C`
- **THEN** the output preserves the order: linked B, then linked A, then linked C, separated by `, `

### Requirement: Idempotency

Running the script twice on the same input MUST produce the same output.

#### Scenario: Second run is a no-op
- **WHEN** the script runs against a directory it has already converted
- **THEN** no file's content changes between the first and second run

#### Scenario: Already-linked piece preserved
- **WHEN** the source contains `Prerequisite Charms: [[Abyssal Daybreak Medicine#Flesh-Mending Discipline|Flesh-Mending Discipline]], Decay Resistance Preparation`
- **THEN** the existing wikilink is preserved unchanged and only the unlinked piece is processed

### Requirement: Mermaid block isolation

The script SHALL NOT modify any line that is inside a fenced ` ```mermaid ` block.

#### Scenario: Fenced block ignored
- **WHEN** a file contains a fenced ` ```mermaid ... ``` ` block at the top, including subgraph nodes with `Prerequisite Charms:` substrings inside callbacks
- **THEN** every line inside that block is emitted unchanged

#### Scenario: Multiple fenced blocks in one file handled
- **WHEN** a file contains two consecutive ` ```mermaid ... ``` ` blocks (from merged source mmd files)
- **THEN** the script correctly tracks fence state for both blocks and rewrites only lines outside them

### Requirement: Report file generation

The script SHALL emit `docs/markdown/.prereq_report.md` listing every unresolved reference piece with its source file and line, grouped by category.

#### Scenario: Report emitted with categorized entries
- **WHEN** the run produces unresolved pieces
- **THEN** `.prereq_report.md` is written with two sections: "Generic count meta-refs" and "Genuinely missing from corpus", each listing entries as `- \`<piece>\` — <file>:<line>`

#### Scenario: Empty report still written
- **WHEN** every prereq piece resolved
- **THEN** the report file is still written, containing both section headers and an explicit "(none)" note under each

### Requirement: In-place rewrite scope

The script SHALL discover its target directory relative to its own location (parent_dir / `docs` / `markdown`) and rewrite every `*.md` file there in-place.

#### Scenario: No command-line arguments accepted
- **WHEN** the script is invoked with arguments
- **THEN** the script exits with a usage error

#### Scenario: Discovery via script path
- **WHEN** the script is invoked as `python scripts/link_prerequisites.py` from the repo root
- **THEN** the script processes files under `docs/markdown/` (sibling to `scripts/`)

#### Scenario: Files outside markdown directory untouched
- **WHEN** the script runs
- **THEN** no file outside `docs/markdown/` is read for output rewriting (the heading index reads only `docs/markdown/`)
