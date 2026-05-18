# Prerequisite Arrow Conventions

This rule defines how prerequisite relationships between charms are represented with arrows.

## Arrow Direction

**Critical**: Arrows point FROM prerequisite TO dependent charm.

```mermaid
prerequisite_charm --> new_charm
```

This means: "prerequisite_charm is required before learning new_charm"

## Multiple Prerequisites

When a charm has multiple prerequisites, create separate arrows:

```mermaid
prerequisite_one --> advanced_charm
prerequisite_two --> advanced_charm
```

## Arrow Placement

- Place arrow declarations immediately after the node they point from
- Group related arrows together
- Maintain consistent ordering (top-to-bottom in the tree hierarchy)

## Example from Codebase

```mermaid
    wise_arrow[Wise Arrow]

    sight_without_eyes[Sight Without Eyes]
    wise_arrow --> sight_without_eyes

    accuracy_without_distance[Accuracy Without Distance]
    sight_without_eyes --> accuracy_without_distance

    there_is_no_wind[There Is No Wind]
    sight_without_eyes --> there_is_no_wind
```

This shows:
- `wise_arrow` is an entry-level charm (no prerequisites)
- `sight_without_eyes` requires `wise_arrow`
- Both `accuracy_without_distance` and `there_is_no_wind` require `sight_without_eyes`

## Cross-Ability Prerequisites

When a charm requires charms from a different ability tree, include those charms in a cross-reference subgraph at the top of the file:

```mermaid
    subgraph water_socialize[Water Socialize Charms]
        direction TB
        smooth_water_mirror_soul[Smooth Water<br>Mirror Soul]
    end

    # Then in the main tree:
    smooth_water_mirror_soul --> your_new_charm
```

## When to Apply

- When creating charm trees
- When adding new charms that have prerequisites
- When validating charm relationships
- Always check that arrows point in the correct direction (prerequisite → dependent)