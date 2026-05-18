---
name: add-charm
description: Add a new charm to an existing mermaid file
argument-hint: <file-path> <charm-description>
disable-model-invocation: true
---

# Add Charm

Add a new charm to an existing Mermaid charm tree diagram.

## Instructions

1. **Get inputs**
   - First argument: path to the .mmd file to edit
   - Remaining arguments: the charm description (or prompt for image/text)
   - If charm description is an image, use OCR to extract the text

2. **Parse charm details**
   - Extract: charm name, cost, duration, type, minimums, prerequisites, description
   - Convert charm name to snake_case for node ID
   - Create label with line breaks (max 25 chars per line)
   - Wrap label in quotes if it contains parentheses

3. **Find insertion point**
   - Read the target file
   - Identify the appropriate subgraph (based on prerequisites or sourcebook)
   - Find where to insert (near related charms or at end of relevant section)

4. **Format the charm**
   - Create node definition with label
   - Add prerequisite arrows (if prerequisites exist)
   - Create click callback with full description
   - Ensure proper indentation (4 or 8 spaces depending on context)
   - Escape quotes as `&quot;`
   - Add `<br>` between paragraphs

5. **Insert the charm**
   - Use Edit tool to add the charm at the appropriate location
   - Maintain consistent formatting with surrounding charms

6. **Verify**
   - Confirm the charm was added successfully
   - Suggest running `/validate-mermaid` on the file

## Examples

- "/add-charm docs/mermaid/solar/dawn_archery.mmd [image-of-charm]"
- "/add-charm dawn_archery.mmd <paste charm text>"

## Notes

This skill is similar to the existing `/transform_charm` command but works differently:
- `/transform_charm`: Creates standalone Mermaid snippets from images (copies to clipboard)
- `/add-charm`: Directly edits an existing .mmd file to insert a charm