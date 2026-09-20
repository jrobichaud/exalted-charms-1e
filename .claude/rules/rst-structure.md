# RST Documentation Structure

This rule defines how ReStructuredText files should be organized to reference Mermaid diagrams.

## File Organization

Each Exalt type has its own RST file that organizes charms by caste and ability.

**Pattern:**
```rst
Exalt Type Charms
=================

Caste Name
----------

Ability Name
^^^^^^^^^^^^
.. mermaid:: ./mermaid/<exalt_type>/<caste>_<ability>.mmd
```

## Heading Hierarchy

1. **Title** (single `=` underline): Exalt type (e.g., "Solar Charms")
2. **Section** (single `-` underline): Caste name (e.g., "Dawn Caste")
3. **Subsection** (single `^` underline): Ability name (e.g., "Archery")

## Example from Codebase

```rst
Solar Charms
============

Dawn Caste
----------

Archery
^^^^^^^
.. mermaid:: ./mermaid/solar/dawn_archery.mmd

Brawl
^^^^^
.. mermaid:: ./mermaid/solar/dawn_brawl.mmd

Martial Arts
^^^^^^^^^^^^
.. mermaid:: ./mermaid/solar/dawn_martial_arts_1.mmd
.. mermaid:: ./mermaid/solar/dawn_martial_arts_2.mmd
.. mermaid:: ./mermaid/solar/dawn_martial_arts_3.mmd
.. mermaid:: ./mermaid/solar/dawn_martial_arts_4.mmd

Zenith Caste
------------

Endurance
^^^^^^^^^
.. mermaid:: ./mermaid/solar/zenith_endurance.mmd
```

## Multiple Diagrams for One Ability

When an ability has multiple diagram files (for large charm trees), list them sequentially:

```rst
Martial Arts
^^^^^^^^^^^^
.. mermaid:: ./mermaid/solar/dawn_martial_arts_1.mmd
.. mermaid:: ./mermaid/solar/dawn_martial_arts_2.mmd
.. mermaid:: ./mermaid/solar/dawn_martial_arts_3.mmd
.. mermaid:: ./mermaid/solar/dawn_martial_arts_4.mmd
```

## Mermaid Directive Format

```rst
.. mermaid:: ./mermaid/<exalt_type>/<filename>.mmd
```

**Important:**
- Always use relative path starting with `./mermaid/`
- No blank line between directive and path
- Path must point to existing .mmd file

## Caste Order

**Solar:** Dawn, Zenith, Twilight, Night, Eclipse

**Dragon-Blooded:** Air, Earth, Fire, Water, Wood

**Lunar:** Full Moon, Changing Moon, No Moon

**Sidereal:** Journeys, Serenity, Battles, Secrets, Endings

## When to Apply

- When creating new RST files for Exalt types
- When adding references to new Mermaid diagrams
- When organizing abilities within castes
- Always maintain consistent heading hierarchy and formatting