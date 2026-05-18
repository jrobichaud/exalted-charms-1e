---
name: check-charm-coverage
description: Check documentation coverage across Exalt types and abilities
argument-hint: [exalt-type]
---

# Check Charm Coverage

Analyze which charm trees have been documented and which are missing.

## Instructions

1. **Determine scope**
   - If `$1` is provided, focus on that Exalt type (solar, dragon_blooded, etc.)
   - Otherwise, check all Exalt types

2. **Expected structure**

   **Solar Exalted:**
   - Dawn: Archery, Brawl, Martial Arts, Melee, Thrown
   - Zenith: Endurance, Performance, Presence, Resistance, Survival
   - Twilight: Craft, Investigation, Lore, Medicine, Occult
   - Night: Athletics, Awareness, Dodge, Larceny, Stealth
   - Eclipse: Bureaucracy, Linguistics, Ride, Sail, Socialize

   **Dragon-Blooded:**
   - Air: Linguistics, Lore, Occult, Stealth, Thrown
   - Earth: Awareness, Craft, Endurance, Resistance
   - Fire: Athletics, Dodge, Melee, Presence, Socialize
   - Water: Brawl, Bureaucracy, Investigation, Larceny, Martial Arts, Sail
   - Wood: Archery, Medicine, Performance, Ride, Survival

   **Lunar, Sidereal, Abyssal:** (Check against sourcebooks)

3. **Check what exists**
   - List all .mmd files in each Exalt type directory
   - Compare against expected abilities for each caste
   - Note any missing combinations

4. **Report findings**
   - Show completion percentage for each Exalt type
   - List documented charm trees
   - Highlight missing charm trees
   - Note any extra/unexpected files

## Examples

- "/check-charm-coverage" - check all Exalt types
- "/check-charm-coverage solar" - check only Solar Exalted
- "/check-charm-coverage dragon_blooded" - check only Dragon-Blooded

## Output Example

```
Solar Exalted Coverage: 95% (19/20)

✓ Dawn Caste (5/5)
  - Archery, Brawl, Martial Arts (split), Melee, Thrown

✓ Zenith Caste (5/5)
  - Endurance, Performance, Presence, Resistance, Survival

✗ Twilight Caste (4/5)
  - Craft, Investigation, Lore, Medicine
  - Missing: Occult

✓ Night Caste (5/5)
  - Athletics, Awareness, Dodge, Larceny, Stealth
```