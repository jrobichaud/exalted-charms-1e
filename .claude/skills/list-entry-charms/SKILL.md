---
name: list-entry-charms
description: List all entry-level charms (no prerequisites) for an ability
argument-hint: <ability-or-file>
---

# List Entry Charms

Find and list all entry-level charms (those with "Prerequisite Charms: None") in a charm tree.

## Instructions

1. **Identify the target**
   - If `$1` is a file path, read that file
   - If it's an ability name (e.g., "archery"), find all relevant .mmd files
   - If it's in format "caste_ability" (e.g., "dawn_archery"), find that specific file

2. **Search for entry charms**
   - Look for all click callbacks containing "Prerequisite Charms: None"
   - Extract charm name, minimum ability, minimum essence
   - Note which subgraph they're in (if any)

3. **Present findings**
   - List each entry-level charm with its requirements
   - Group by subgraph if applicable
   - Show the node labels (formatted charm names)
   - Note the minimum requirements needed to learn any charm in this tree

## Examples

- "/list-entry-charms archery" - all archery entry charms
- "/list-entry-charms dawn_archery.mmd"
- "/list-entry-charms docs/mermaid/solar/dawn_archery.mmd"

## Output Example

```
Entry-Level Charms for Dawn Archery

1. Wise Arrow
   - Minimum Archery: 1
   - Minimum Essence: 1
   - Cost: 1 mote per die
   - Type: Supplemental

2. Keen Arrow Technique (from Castebook Dawn)
   - Minimum Archery: 2
   - Minimum Essence: 1
   - Cost: 3 motes
   - Type: Simple

Minimum requirements to start this charm tree:
  - Archery 1, Essence 1
```