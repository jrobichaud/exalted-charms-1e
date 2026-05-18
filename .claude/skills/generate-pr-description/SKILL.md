---
name: generate-pr-description
description: Generate PR title and description
argument-hint: [parent-branch]
---

# Generate PR Description

Analyze the git diff between the parent branch and the current branch and create a pull request title and description.

**Parent branch:** Use "$1" if provided, otherwise default to "main"

## Instructions

1. Use `git diff <parent-branch>...HEAD` and `git log <parent-branch>..HEAD` to analyze changes
2. Generate a concise, descriptive PR title
3. Write a description summarizing what changed

### Guidelines

- Title should clearly describe what charms/documentation was added or changed
- Description should list the specific Exalt types, castes, and abilities affected
- Mention if new sourcebooks or charm trees were added
- Note any formatting or structural changes
- Be concise and direct

## Output Format

Print the title and description in code blocks so they can be easily copied:

---

**PR title:**

```
Add Lunar Full Moon Brawl charms
```

**PR description:**

```
## Summary

Added charm trees for Lunar Exalted Full Moon caste Brawl ability.

## Changes

- Created `lunar/full_moon_brawl.mmd` with 23 charms
- Added reference to `lunar.rst`
- Includes charms from Core Rulebook and Lunar sourcebook

## Notes

- All charms follow the standard Mermaid format conventions
- Prerequisite chains verified against sourcebooks
```

---