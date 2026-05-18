---
name: generate-commit-message
description: Generate a commit message for staged changes
disable-model-invocation: true
---

# Generate Commit Message

Analyze staged changes and generate a single-line commit message.

## Instructions

1. **Check for staged changes**
   - Run `git diff --cached` to see what's staged
   - If nothing is staged, check `git status` and suggest what to stage

2. **Check project conventions**
   - Run `git log --oneline -10` to see recent commit style
   - This project uses simple, descriptive commit messages
   - Focus on what was changed (e.g., "Add Fire Aspect charms", "Fix typos in Dawn Archery")

3. **Generate a single-line commit message**

## Best Practices

- **Concise** - keep it short and descriptive
- **Imperative mood** - "Add charm" not "Added charm" or "Adds charm"
- **Capitalize** the first letter
- **No period** at the end
- **Be specific** about what Exalt type, caste, or ability was changed

## Output

Print the commit message in a code block:

```
Add Water Aspect Socialize charms
```