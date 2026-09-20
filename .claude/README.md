# Claude Code Configuration for Exalted Skill Trees

This directory contains skills and rules that enhance Claude Code's ability to work with this Exalted 1st Edition charm documentation project.

## Skills

Skills are invocable commands that automate common workflows. Use them with `/skill-name`.

### Documentation & Code Understanding

- **`/explain`** - Explain how charms, mermaid diagrams, or documentation structure works
  - Example: `/explain dawn_archery`

- **`/prime`** - Get a comprehensive understanding of the documentation structure or specific charm tree
  - Example: `/prime water_socialize`

### Charm Tree Management

- **`/find-charm`** - Find where a specific charm is defined in the documentation
  - Example: `/find-charm Wise Arrow`

- **`/list-entry-charms`** - List all entry-level charms (no prerequisites) for an ability
  - Example: `/list-entry-charms archery`

- **`/analyze-prerequisites`** - Analyze charm prerequisite chains and dependencies
  - Example: `/analyze-prerequisites Accuracy Without Distance`

- **`/check-charm-coverage`** - Check documentation coverage across Exalt types and abilities
  - Example: `/check-charm-coverage solar`

### Creating & Editing

- **`/create-charm-tree`** - Create a new mermaid file for a new ability/caste combination
  - Example: `/create-charm-tree solar dawn archery`

- **`/add-charm`** - Add a new charm to an existing mermaid file
  - Example: `/add-charm docs/mermaid/solar/dawn_archery.mmd [charm-description]`
  - Note: Similar to `/transform_charm` but directly edits files instead of copying to clipboard

### Validation & Quality

- **`/validate-mermaid`** - Validate that mermaid files follow project conventions
  - Example: `/validate-mermaid docs/mermaid/solar/dawn_archery.mmd`

### Build & Preview

- **`/build-docs`** - Build the Sphinx documentation and optionally preview it
  - Example: `/build-docs --preview`

### Git Workflows

- **`/generate-commit-message`** - Generate a commit message for staged changes
  - Example: `/generate-commit-message`

- **`/generate-pr-description`** - Generate PR title and description
  - Example: `/generate-pr-description`

## Rules

Rules are coding conventions that Claude automatically follows when working with your codebase.

- **`mermaid-formatting.md`** - Node IDs, labels, and indentation conventions
- **`click-callback-format.md`** - Exact format for charm description callbacks
- **`prerequisite-arrows.md`** - How to represent prerequisite relationships
- **`subgraph-usage.md`** - When and how to use subgraphs (sourcebooks, cross-refs, themes)
- **`file-naming.md`** - Naming conventions for .mmd and .rst files
- **`rst-structure.md`** - How to organize RST files and reference Mermaid diagrams

## Outputs

The `outputs/` directory is used by skills to save generated artifacts like diagrams and reports.

## Existing Commands

The project already has a custom command in `commands/`:

- **`/transform_charm`** - OCR tool that converts charm descriptions from screenshots to Mermaid format
  - Takes image arguments containing charm descriptions
  - Generates formatted Mermaid nodes with prerequisite arrows
  - Copies result to clipboard

### transform_charm vs add-charm

- **`/transform_charm`**: Processes images → generates Mermaid snippet → copies to clipboard (for manual pasting)
- **`/add-charm`**: Processes text/images → directly edits .mmd file → inserts charm at appropriate location

## Quick Start

1. **Understand the project**: `/prime`
2. **Check coverage**: `/check-charm-coverage`
3. **Find a charm**: `/find-charm Wise Arrow`
4. **Build and preview**: `/build-docs --preview`
5. **Validate a file**: `/validate-mermaid docs/mermaid/solar/dawn_archery.mmd`

## Project Structure

```
.claude/
├── commands/          # Legacy slash commands (still work)
│   └── transform_charm.md
├── skills/           # New skill system (12 skills)
│   ├── explain/
│   ├── find-charm/
│   ├── validate-mermaid/
│   └── ...
├── rules/            # Coding conventions (6 rules)
│   ├── mermaid-formatting.md
│   ├── click-callback-format.md
│   └── ...
└── outputs/          # Generated artifacts
```

## Tips

- All skills are context-aware and understand the Exalted charm structure
- Skills can be chained: find a charm → analyze its prerequisites → validate the file
- Use `/validate-mermaid` before committing changes to ensure formatting consistency
- The `/transform_charm` command is still available for converting screenshots