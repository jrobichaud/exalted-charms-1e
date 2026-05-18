---
name: analyze-prerequisites
description: Analyze charm prerequisite chains and dependencies
argument-hint: <charm-name>
---

# Analyze Prerequisites

Analyze the prerequisite chain for a specific charm, showing the full path from entry-level charms.

## Instructions

1. **Find the charm**
   - Use `/find-charm` logic to locate the charm in the documentation
   - Read the .mmd file containing the charm

2. **Build prerequisite tree**
   - Identify direct prerequisites (charms that have arrows pointing to this charm)
   - Recursively find prerequisites of prerequisites
   - Build the full dependency chain back to entry-level charms (those with "Prerequisite Charms: None")

3. **Analyze the chain**
   - Identify all paths from entry-level charms to the target charm
   - Calculate the minimum number of charms needed to reach the target
   - Note the minimum Essence and Ability requirements along each path
   - Identify any cross-ability prerequisites (from other charm trees)

4. **Present findings**
   - Display the prerequisite chain as a tree or path
   - Show the "shortest path" to the target charm
   - List the minimum Essence and Ability requirements
   - Note any alternative paths
   - Calculate total XP cost if relevant (each charm typically costs 8-10 XP)

5. **Visual representation**
   - Consider generating a simplified Mermaid diagram showing just the prerequisite chain
   - Save to `.claude/outputs/` if generated

## Examples

- "/analyze-prerequisites Accuracy Without Distance"
- "/analyze-prerequisites blazing_solar_bolt"

## Output Example

```
Prerequisite Chain for "Accuracy Without Distance"

Path 1 (Shortest):
  1. Wise Arrow (Archery 1, Essence 1) - Entry level
  2. Sight Without Eyes (Archery 3, Essence 1)
  3. Accuracy Without Distance (Archery 5, Essence 1)

Total charms required: 3
Minimum requirements: Archery 5, Essence 1
Estimated XP cost: 24 XP (3 charms × 8 XP)
```