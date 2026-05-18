---
name: validate-mermaid
description: Validate that mermaid files follow project conventions
argument-hint: <file-path>
---

# Validate Mermaid

Validate that a Mermaid diagram file follows the project's charm formatting conventions.

## Instructions

1. **Read the target file**
   - Use `$1` as the file path, or ask which file to validate
   - Read the entire .mmd file

2. **Check formatting conventions**

   **Node structure:**
   - Node IDs are snake_case
   - Labels use Title Case with `<br>` for line breaks
   - Labels have max 25 chars per line
   - Labels with parentheses are wrapped in double quotes

   **Click callbacks:**
   - Each node has a click callback with charm description
   - Cost, Duration, Type, Minimum [Ability], Minimum Essence, Prerequisite Charms present
   - Description paragraphs separated by `<br>`
   - Double quotes escaped as `&quot;`

   **Indentation:**
   - First level nodes: 4 spaces
   - Second level nodes (in subgraphs): 8 spaces

   **Subgraphs:**
   - Include `direction TB`
   - Used for sourcebooks, cross-references, or thematic organization

   **Prerequisites:**
   - Arrows point from prerequisite to dependent charm
   - Format: `prerequisite_charm --> new_charm`

3. **Report findings**
   - List any formatting violations found
   - Suggest corrections for each issue
   - If file is valid, confirm it follows all conventions

## Examples

- "/validate-mermaid docs/mermaid/solar/dawn_archery.mmd"
- "/validate-mermaid" (will prompt for file path)