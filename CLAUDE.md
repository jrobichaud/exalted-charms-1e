# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Sphinx documentation project for Exalted 1st Edition tabletop RPG charms (magical abilities). The documentation uses Mermaid flowcharts to visualize charm trees, showing prerequisites and progression paths. Each charm node contains the full charm description in an interactive tooltip.

## Build and Development Commands

Build the HTML documentation:
```bash
cd docs
make html
```

The built documentation will be in `docs/_build/html/`.

Install dependencies:
```bash
pip install -r docs/requirements.txt
```

Auto-rebuild on changes:
```bash
cd docs
sphinx-autobuild . _build/html
```

## Documentation Structure

The documentation is organized by Exalt type and caste:

- **docs/*.rst**: ReStructuredText files organized by Exalt type (solar, dragon_blooded, lunar, etc.)
- **docs/mermaid/**: Contains all Mermaid flowchart files (.mmd) organized by:
  - Exalt type (solar/, dragon_blooded/, lunar/, etc.)
  - Within each type: caste_ability.mmd (e.g., dawn_archery.mmd, zenith_endurance.mmd)

The RST files reference Mermaid diagrams using:
```rst
.. mermaid:: ./mermaid/solar/dawn_archery.mmd
```

## Mermaid Flowchart Format

Charms are represented as Mermaid flowchart nodes with specific conventions:

**Node Structure:**
- Node ID: snake_case version of charm name
- Node Label: Title Case with `<br>` for line breaks (max 25 chars per line)
- Labels with parentheses must be wrapped in double quotes

**Arrows:** Prerequisites point to dependent charms:
```mermaid
prerequisite_charm --> new_charm
```

**Interactive Descriptions:** Each node has a click callback containing:
```mermaid
click charm_name callback "
    Charm Name<br>
    <br>
    Cost: X motes<br>
    Duration: ...<br>
    Type: ...<br>
    Minimum [Ability]: X<br>
    Minimum Essence: X<br>
    Prerequisite Charms: ...<br>
    <br>
    [Description paragraphs with <br> between them]
    "
```

**Special Characters:** Use `&quot;` for quotes within descriptions.

**Indentation:**
- First level nodes: 4 spaces
- Second level nodes: 8 spaces

**Subgraphs:** Used to group and organize charms in three ways:

1. **Source Book Attribution** - Groups charms by the sourcebook they appear in:
   ```mermaid
   subgraph Castebook Dawn
       direction TB
       [charms from that book]
   end
   ```

2. **Cross-references** - References charms from other ability trees (typically at the top of the file):
   ```mermaid
   subgraph water_socialize[Water Socialize Charms]
       direction TB
       [referenced charms]
   end
   ```

3. **Thematic Organization** - Groups related concepts or mechanics:
   ```mermaid
   subgraph high_soul["High Soul (hun)"]
       [related nodes]
   end
   ```

Subgraphs always include `direction TB` (top-to-bottom) and content is indented:
- Subgraph declaration: 4 spaces
- Nodes within subgraph: 8 spaces

## Custom Slash Command

The repository includes a `/transform_charm` command (.claude/commands/transform_charm.md) that converts charm descriptions from plain text (typically screenshots) into the Mermaid flowchart format. This command:
- Takes image arguments containing charm descriptions
- Extracts charm name, stats, prerequisites, and description
- Generates properly formatted Mermaid nodes with prerequisite arrows
- Copies result to clipboard

## Deployment

GitHub Actions automatically builds and deploys to GitHub Pages on push to main branch (see .github/workflows/gh.yml).

## Content Organization

Charms are organized by:
1. **Exalt Type**: Solar, Dragon-Blooded, Lunar, Sidereal, Abyssal, Alchemical
2. **Caste**: Each type has specific castes (e.g., Solar: Dawn, Zenith, Twilight, Night, Eclipse)
3. **Ability**: Each caste has associated abilities (e.g., Dawn: Archery, Brawl, Martial Arts, Melee, Thrown)

Large charm trees may be split across multiple files (e.g., dawn_martial_arts_1.mmd through dawn_martial_arts_4.mmd).

## Sphinx Configuration

The project uses:
- **Theme**: groundwork-sphinx-theme
- **Extensions**: sphinx.ext.autodoc, sphinxcontrib.mermaid
- **Custom CSS**: docs/_static/css/mermaid.css for styling flowcharts
- **Logo**: docs/_static/logo.webp
