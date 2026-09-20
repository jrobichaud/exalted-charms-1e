---
name: create-charm-tree
description: Create a new mermaid file for a new ability/caste combination
argument-hint: <exalt-type> <caste> <ability>
disable-model-invocation: true
---

# Create Charm Tree

Create a new Mermaid diagram file for a new Exalt type, caste, and ability combination.

## Instructions

1. **Get parameters**
   - Exalt type: solar, dragon_blooded, lunar, sidereal, abyssal, alchemical, etc.
   - Caste: dawn, zenith, air, water, full_moon, etc.
   - Ability: archery, brawl, socialize, etc.
   - Combine into filename: `<caste>_<ability>.mmd`

2. **Check if file exists**
   - Look for existing file at `docs/mermaid/<exalt_type>/<caste>_<ability>.mmd`
   - If it exists, ask if user wants to create a numbered variant (e.g., `_2.mmd`)
   - For large charm trees, files are split (e.g., dawn_martial_arts_1.mmd through _4.mmd)

3. **Create the file structure**
   ```mermaid
   ---
   config:
     theme: dark
   ---
   flowchart TD

       [charm nodes go here]
   ```

4. **Add to RST file**
   - Find the appropriate RST file (e.g., `docs/solar.rst`)
   - Add a reference to the new diagram in the correct section
   - Format: `.. mermaid:: ./mermaid/<exalt_type>/<caste>_<ability>.mmd`

5. **Provide next steps**
   - Confirm files were created
   - Suggest using `/add-charm` or `/transform_charm` to add charms
   - Suggest running `/build-docs --preview` to see the changes

## Examples

- "/create-charm-tree solar dawn archery"
- "/create-charm-tree dragon_blooded water socialize"
- "/create-charm-tree lunar full_moon survival"

## Notes

This creates the file structure. Use `/transform_charm` (for screenshots) or `/add-charm` (for direct editing) to populate it with charms.