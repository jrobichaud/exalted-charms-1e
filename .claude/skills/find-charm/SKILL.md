---
name: find-charm
description: Find where a specific charm is defined in the documentation
argument-hint: <charm-name>
---

# Find Charm

Find where a specific charm is defined in the Mermaid diagrams.

## Instructions

1. **Get the charm name**
   - Use `$1` as the charm name
   - Convert to snake_case for searching (e.g., "Wise Arrow" → "wise_arrow")

2. **Search for the charm**
   - Use Grep to search all .mmd files in docs/mermaid/ for the node ID
   - Pattern to search: the snake_case charm name as a node ID
   - Look in all subdirectories (solar, dragon_blooded, lunar, etc.)

3. **Report findings**
   - File path where the charm is defined
   - Line number of the node definition
   - Show the charm's full description from the click callback
   - List any prerequisites (charms that point to this one)
   - List any dependent charms (charms this one points to)

4. **If not found**
   - Suggest similar charm names found in the documentation
   - Check if the charm might be spelled differently or in a different format

## Examples

- "/find-charm Wise Arrow"
- "/find-charm accuracy_without_distance"
- "/find-charm Blazing Solar Bolt"