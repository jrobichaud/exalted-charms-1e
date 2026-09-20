# Mermaid Formatting Conventions

This rule defines how Mermaid flowchart files should be formatted for charm diagrams.

## File Structure

Every .mmd file must start with:

```mermaid
---
config:
  theme: dark
---
flowchart TD
```

## Node ID Conventions

- **Format**: snake_case version of charm name
- **Example**: "Wise Arrow" → `wise_arrow`
- **Example**: "Accuracy Without Distance" → `accuracy_without_distance`

## Node Label Formatting

- **Case**: Title Case with first letter of each major word capitalized
- **Line breaks**: Use `<br>` to split long names
- **Max length per line**: 25 characters
- **Parentheses**: If label contains parentheses, wrap entire label in double quotes

**Examples:**

```mermaid
wise_arrow[Wise Arrow]
accuracy_without_distance[Accuracy Without<br>Distance]
"high_soul[High Soul (hun)]"  # Quotes because of parentheses
```

## Indentation Rules

**First level (not in subgraph)**: 4 spaces

```mermaid
    wise_arrow[Wise Arrow]
```

**Second level (inside subgraph)**: 8 spaces

```mermaid
    subgraph Castebook Dawn
        direction TB
        keen_arrow_technique[Keen Arrow Technique]
    end
```

## When to Apply

- When creating new charm diagrams
- When editing existing charm diagrams
- When validating diagram formatting
- Always maintain consistency with existing files