# Click Callback Formatting

This rule defines the exact format for charm description click callbacks in Mermaid diagrams.

## Standard Format

Every charm node must have a click callback with this exact structure:

```mermaid
click charm_name callback "
    Charm Name<br>
    <br>
    Cost: X motes [, Y Willpower]<br>
    Duration: ...<br>
    Type: Simple|Supplemental|Reflexive<br>
    Minimum [Ability]: X<br>
    Minimum Essence: X<br>
    Prerequisite Charms: None|Charm Name[, Charm Name...]<br>
    <br>
    [Description paragraph 1]<br>
    [Description paragraph 2]<br>
    [Description paragraph N]
    "
```

## Important Details

1. **Indentation**: Click callbacks use 4 spaces for first-level charms, 8 spaces for subgraph charms
2. **Blank lines**: Represented as `<br>` alone on a line (after charm name, after prerequisites)
3. **Paragraph breaks**: Each paragraph ends with `<br>` except the last one
4. **Quotes**: Escape double quotes in description as `&quot;`
5. **Preserve text**: Keep original text exactly as it appears in source material (typos included)

## Field Requirements

**Always include:**
- Charm Name (Title Case)
- Cost
- Duration
- Type
- Minimum [Ability Name]: X
- Minimum Essence: X
- Prerequisite Charms: (even if "None")
- Description text

## Example from Codebase

```mermaid
click wise_arrow callback "
    Wise Arrow<br>
    <br>
    Cost: 1 mote per die<br>
    Duration: Instant<br>
    Type: Supplemental<br>
    Minimum Archery: 1<br>
    Minimum Essence: 1<br>
    Prerequisite Charms: None<br>
    <br>
    The character extends her anima into the world around
    her, and joins archer, target and arrow into a single being. Truly,
    the arrow knows the way to the target, for that is its natural
    home. For each mote of Essence the player spends, he may add
    1 die to an Archery attack roll, but the number of bonus dice
    added to any single roll cannot exceed her normal Dexterity +
    Archery dice pool. The player must declare how much Essence
    she is going to use in this Charm prior to making the attack roll."
```

## When to Apply

- When adding new charms to diagrams
- When converting text/screenshot charms to Mermaid format
- When validating existing charm descriptions
- Always preserve original text exactly as written (including grammar/spelling)