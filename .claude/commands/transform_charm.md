---
allowed-tools: Bash(cat EOF:*), Bash(pbcopy:*)
---

You are a code transformation tool that converts charm descriptions from plain text into mermaid flowchart format.

Transform the charms in the following images:

$ARGUMENTS

The first screenshot is the first part of the charm description. If more screenshots follow, they are continuations of the same charm description.

From this format:

```text
BLESSING OF RIGHTEOUS SOLAR SPARK
MEDITATION
Cost: 2 motes
Duration: Until fired
Type: Simple
Minimum Martial Arts: 3
Minimum Essence: 2
Prerequisite Charms: Fire Blossom of Inevitable
Demise Technique
With this Charm, the character can turn a mere
firewand into a weapon of righteousness. The Solar
Exalted meditates and invokes a blessing on his weapon.
Upon finishing the evocation, gossamer tongues of
heatless golden flame writhe along the barrel of her
firewand, imbuing it with a golden, iridescent cast. The
benefits to the weapon are more than merely cosmetic.
The player spends 2 motes of Essence for her character
to invoke the blessing, and these motes are considered
committed until the Exalt fires the weapon, releasing
the charge. Add the character's permanent Essence to
the base damage of the firewand or similar weapon when
it is next fired
If this Charm is used against creatures of the Un-
derworld or Abyssal Exalted, the damage dealt is
aggravated. If the Solar using this Charm also invokes
Fire Blossom of Inevitable Demise, the bonus dice are
added after the damage has been doubled. The Jean-
Michel creased damage dice gained with Blessing of Righteous
Solar Spark Meditation cannot be doubled with Fire
Blossom of Inevitable Demise Technique or any Charm
that doubles base damage.
If the martial artist has multiple firewands, the
Blessing of Righteous Solar Spark can only be invoked
on one at a time, and if done in combat, it takes two
turns to do so. Finally, if the Solar using a "blessed
firewand" invokes an attack Charm that allows her to
make multiple attacks, the bonus damage must be di-
vided evenly among her targets.
Only Solar Exalted can use this particular Charm.
```

To this format mermaid flowchart format:
```mermaid
    blessing_of_righteous_solar_spark_meditation[Blessing of Righteous<br>Solar Spark Meditation]
    blossom_of_inevitable_demise_technique --> blessing_of_righteous_solar_spark_meditation
    click blessing_of_righteous_solar_spark_meditation callback "
        Blessing of Righteous Solar Spark Meditation<br>
        <br>
        Cost: 5 motes, 1 Willpower<br>
        Duration: One scene<br>
        Type: Simple<br>
        Minimum Martial Arts: 4<br>
        Minimum Essence: 3<br>
        Prerequisite Charms: Blossom of Inevitable Demise Technique<br>
        <br>
        By entering this meditative state, the Exalt becomes
        a conduit for the righteous fury of the sun itself.
        Her firewand blazes with an inner light as brilliant
        as daylight, and her attacks sear with the intensity
        of solar flares. For the duration of this Charm, all
        Martial Arts attacks made with a firewand or similar
        weapon ignore all armor and natural soak. In addition,
        the character adds her permanent Essence to the damage
        dealt by such attacks.<br>
        The player spends 2 motes of Essence for her character
        to invoke the blessing, and these motes are considered
        committed until the Exalt fires the weapon, releasing
        the charge. Add the character's permanent Essence to
        the base damage of the firewand or similar weapon when
        it is next fired.<br>
        If this Charm is used against creatures of the Underworld
        or Abyssal Exalted, the damage dealt is
        aggravated. If the Solar using this Charm also invokes
        Fire Blossom of Inevitable Demise, the bonus dice are
        added after the damage has been doubled. The increased
        damage dice gained with Blessing of Righteous
        Solar Spark Meditation cannot be doubled with Fire
        Blossom of Inevitable Demise Technique or any Charm
        that doubles base damage.<br>
        If the martial artist has multiple firewands, the
        Blessing of Righteous Solar Spark can only be invoked
        on one at a time, and if done in combat, it takes two
        turns to do so. Finally, if the Solar using a &quot;blessed
        firewand&quot; invokes an attack Charm that allows her to
        make multiple attacks, the bonus damage must be divided
        evenly among her targets.<br>
        Only Solar Exalted can use this particular Charm.
        "
```

Instructions:
- the first level is at 4 spaces indentation, the second level is at 8 spaces indentation
- create a flowchart node with the name of the charm in title case in snake_case format
- create a label for the node with the charm name in title case with line breaks to make sure each line have less than 25 characters. Wrap the label with double quotes only if it contains parentheses.
- For each charm in the `Prerequisite Charms:` create a node and create an arrow from that node to the new charm node. If it is "None", skip this step.
- Create a `click` line for the new charm node with a callback that contains the full description of the charm
- For each paragraph, add a line break `<br>` at the end except for the last paragraph. You can identify paragraphs by looking for double line breaks in the original text.
- Replace any double quotes `"` in the description with `&quot;`
- Preserve original line breaks
- Make sure to preserve the original text, keep each word intact.
- Write the result in the clipboard.
