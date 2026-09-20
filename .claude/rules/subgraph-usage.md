# Subgraph Usage Patterns

This rule defines when and how to use subgraphs to organize charms in Mermaid diagrams.

## Three Types of Subgraphs

### 1. Source Book Attribution

Groups charms by the sourcebook they appear in.

```mermaid
    subgraph Castebook Dawn
        direction TB
        [charms from that book]
    end

    subgraph Core Rulebook
        direction TB
        [charms from core book]
    end
```

### 2. Cross-References

References charms from other ability trees (typically at the top of the file).

```mermaid
    subgraph water_socialize[Water Socialize Charms]
        direction TB
        smooth_water_mirror_soul[Smooth Water<br>Mirror Soul]
    end
```

Note: Use custom label syntax `subgraph id[Display Name]` for cross-references.

### 3. Thematic Organization

Groups related charms by mechanics or concept.

```mermaid
    subgraph high_soul["High Soul (hun)"]
        direction TB
        [related charms]
    end

    subgraph po_soul["Lower Soul (po)"]
        direction TB
        [related charms]
    end
```

## Subgraph Format Requirements

**Always include:**
- `direction TB` (top-to-bottom flow)
- Proper indentation (4 spaces for subgraph declaration)
- 8 spaces for nodes within subgraph

**Example:**

```mermaid
    subgraph Castebook Dawn
        direction TB
        keen_arrow_technique[Keen Arrow Technique]
        keen_arrow_technique --> advanced_charm
    end
```

## When to Use Subgraphs

- **Source books**: When charms come from different sourcebooks (Core, Caste Books, supplements)
- **Cross-references**: When referencing charms from other ability trees
- **Thematic groups**: When charms share a common mechanic or concept (e.g., soul manipulation, combo types)

## When NOT to Use Subgraphs

- Don't create subgraphs for single charms
- Don't nest subgraphs
- Don't use subgraphs just to create visual grouping without semantic meaning

## When to Apply

- When organizing charms from multiple sourcebooks
- When referencing external charm trees
- When charms have clear thematic groupings
- Always maintain consistency with existing diagram organization