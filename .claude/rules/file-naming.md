# File Naming Conventions

This rule defines the naming conventions for Mermaid diagram files and RST documentation files.

## Mermaid Diagram Files (.mmd)

**Location**: `docs/mermaid/<exalt_type>/`

**Format**: `<caste>_<ability>.mmd`

**Examples:**
- `dawn_archery.mmd`
- `zenith_performance.mmd`
- `water_socialize.mmd`
- `full_moon_brawl.mmd`

## Split Files for Large Charm Trees

When a charm tree is too large for a single file, split it with numbered suffixes:

**Format**: `<caste>_<ability>_<number>.mmd`

**Examples:**
- `dawn_martial_arts_1.mmd`
- `dawn_martial_arts_2.mmd`
- `dawn_martial_arts_3.mmd`
- `dawn_martial_arts_4.mmd`

## Directory Structure

```
docs/mermaid/
├── solar/
│   ├── dawn_archery.mmd
│   ├── dawn_brawl.mmd
│   └── zenith_performance.mmd
├── dragon_blooded/
│   ├── air_linguistics.mmd
│   └── water_socialize.mmd
├── lunar/
│   └── full_moon_brawl.mmd
├── sidereal/
├── abyssal/
└── alchemical/
```

## RST Documentation Files

**Location**: `docs/`

**Format**: `<exalt_type>.rst` (singular or with underscore)

**Examples:**
- `solar.rst`
- `dragon_blooded.rst`
- `lunar.rst`
- `sidereals.rst`

## Exalt Type Names

**Consistent naming across files:**
- `solar` (Solar Exalted)
- `dragon_blooded` (Dragon-Blooded)
- `lunar` (Lunar Exalted)
- `sidereal` or `sidereals` (Sidereal Exalted)
- `abyssal` (Abyssal Exalted)
- `alchemical` (Alchemical Exalted)
- `spirits` (Spirit Charms)
- `arcanoi` (Arcanoi)
- `god_blooded` (God-Blooded)

## Snake Case Convention

All filenames use lowercase with underscores:
- ✓ `dawn_archery.mmd`
- ✓ `water_socialize.mmd`
- ✗ `DawnArchery.mmd`
- ✗ `water-socialize.mmd`

## When to Apply

- When creating new Mermaid diagram files
- When creating new RST documentation files
- When organizing charm trees by Exalt type and caste
- Always follow the existing directory structure