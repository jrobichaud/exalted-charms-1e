---
name: explain
description: Explain how charms, mermaid diagrams, or documentation structure works
argument-hint: [file, charm, or feature]
---

# Explain

Provide a clear explanation of how something in this Exalted documentation project works.

## Instructions

1. **Identify what to explain**: Use `$ARGUMENTS` to determine the target

   - File path → explain that file's purpose and structure
   - Charm name → find and explain that specific charm and its prerequisites
   - Feature name → explain how that aspect of the documentation works

2. **Gather context**

   - Read the relevant RST files and Mermaid diagrams
   - Identify prerequisite charms and dependencies
   - Look at the organization structure (Exalt type → Caste → Ability)
   - Check how charms are grouped (by sourcebook, theme, etc.)

3. **Explain clearly**
   - Start with a high-level summary (1-2 sentences)
   - For charms: explain stats, prerequisites, what it does
   - For diagrams: explain the charm tree structure and organization
   - For documentation: explain how files are organized and referenced
   - Note any important conventions or formatting rules

## Examples

- "/explain zenith_performance" - explains the Zenith Performance charm tree
- "/explain dawn_martial_arts_1.mmd" - explains that specific mermaid diagram
- "/explain subgraphs" - explains how subgraphs are used to organize charms