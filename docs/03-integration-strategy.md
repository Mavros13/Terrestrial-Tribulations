# Integration strategy: build the pack from existing mods (v0.4, 2026-10-27)

**Owner direction:** don't build mobs, bosses, NPCs, weapons, armour or recipes from scratch. Combine the best existing, heavily animated mods, re-theme them to fit the story, and connect them with a small **bridge mod**. MCreator and Blockbench are supporting tools, not the main production line.

All mods are CANDIDATE for 1.20.1 Forge (web evidence only) until a launch test.

## 1. How existing mods get "edited" to fit the story (no jar modification)
| Layer | What it changes | Tool |
|---|---|---|
| **KubeJS** (server, startup, client scripts) | Recipes, progression gates, item renames and tooltips, lore, mob stats, loot, events, custom items | Plain JS in `pack/kubejs/` |
| **Datapacks** | Loot tables, structure and biome spawns, advancements, Pufferfish skill trees, Epic Fight weapon movesets, armour set bonuses | JSON in `pack/kubejs/data/` or `datapacks/` |
| **Resource pack** | Renames through lang overrides, retextures, re-modelled GeckoLib entities and items, sounds, UI theme | Blockbench + `resourcepacks/terrestrial_tribulations/` |
| **Configs** | Difficulty, spawn rates, boss stats, structure density | `pack/config/` |
| **FTB Quests and Easy NPC presets** | Story delivery, dialogue, quest givers | SNBT and NPC preset files |
| **Bridge mod `tt_bridge`** (MCreator, with custom code where needed) | Things the above can't do: story flags, a chapter state machine, links between mods (for example, a MineColonies Town Hall level that unlocks a story chapter, or a Palladium suit gated behind a boss kill) | MCreator workspace |

Rules: **never redistribute modified jars.** All changes live in our own scripts, packs and bridge mod. Other modpacks are studied for *structure and mod choices only*; we don't copy their quest text, lore or assets.

## 2. Which existing mod covers each design system
| Design system (from the kickoff) | Existing mod(s) | Re-theme and bridge work |
|---|---|---|
| **Animated combat, dodge, parry, lock-on** | **Epic Fight** 20.14.x (Jan 2026; full player and mob animations, lock-on, skills, many addons such as Nightfall and a Twilight Forest compat addon) | Assign Epic Fight movesets to Simply Swords, Soulslike and Cataclysm weapons with datapacks. *Replaces Better Combat* because Epic Fight has deeper animation. Fallback: Better Combat + Combat Roll if it conflicts with Palladium |
| **Character levels, talents, ~100 nodes, 16 passives** | **Passive Skill Tree** + PassiveSTJS (see docs/04) | Custom story and QoL skills scripted in KubeJS |
| **Ten Fates** | **Origins (Forge)**, with a "Fate" layer next to the "Origin" layer (see docs/04) | Origins datapacks |
| **Five active abilities** | Epic Fight skills (dodge, guard, weapon innates) + Iron's Spells spells unlocked per Fate | Bridge mod binds unlocks to quest flags |
| **Enemy scaling + elites** | **Champions Unofficial** (elite ranks and affixes, KubeJS-extensible) + **Botz Mob Leveling** (scaling by distance, structure and dimension) | Configure region tiers to match story regions |
| **Loot rarity, affixes, gems, mythic gear** | **Apotheosis** (Adventure module: affix loot, rarities, gems, bosses) | Rarity names and colours re-themed through lang overrides and config |
| **Weapons** | Simply Swords, Marium's Soulslike Weaponry (1.4.8, Jun 2026), Cataclysm and Twilight boss weapons, Iron's Spells staves | Renamed into tiers with KubeJS, lore tooltips |
| **Armour sets + set bonuses** | Boss and dimension armour from existing mods + **Armor Set Bonuses** (data-driven, 1.20.1 Forge) | Bonuses defined per set as data |
| **Accessories and artifacts** | Curios, Artifacts, Relics (to verify) | Artifact upgrade recipes in KubeJS |
| **Magic ×2** | Iron's Spells 'n Spellbooks (combat), Ars Nouveau (utility and automation) | Story factions: Lumen Conclave |
| **Superheroes** | **Palladium 4.5.9** + selected addon packs | Bridge mod gates suits behind story and boss flags. Iron Choir villains use Palladium powers |
| **Capital city, 5 stages** | **MineColonies** (Town Hall levels 1–5 = our 5 city stages; workers, guards, raids, building styles) | City stage = Town Hall level, read by the bridge mod to unlock chapters. A custom MineColonies style pack (Blockbench/schematics) is optional later |
| **Story NPCs + dialogue** | **Easy NPC** 6.25.0 (dialogue, trades, actions) | Maera, Doran, Ilsabet and others as Easy NPC presets placed in the colony |
| **Quest book** | FTB Quests | 285 quests as planned |
| **Bosses** | L_Ender's Cataclysm, Mowzie's Mobs, Bosses of Mass Destruction (1.20.1 build to verify), Alex's Caves, Twilight Forest, Aether, plus ChaosBosses (25 bosses, to evaluate) | Each boss is assigned a story role. The final boss **Malric** is an existing boss re-skinned in Blockbench through the resource pack, with stats and phases set by KubeJS. A fully custom model only if no base fits |
| **Dimensions** | Twilight Forest, Aether, Undergarden, Deeper and Darker, Blue Skies (to verify), plus the Nether and End overhauls | Each is mapped to a Crown Shard |
| **Rats automation** | Rats 8.1.3 | Faction: Nib the rat-catcher |
| **Create / AE2 / quarry / power** | Create 6 + addons, AE2, Mekanism + Generators (Digital Miner is the quarry), Core Utilities (early-game solar, generators, harvesters, mob grinder, item pipes) | Cogwright Guild quest line: Core Utilities is the Guild's starter kit, Mekanism its advanced tier |

## 3. What Blockbench and MCreator are still used for
- **Blockbench:** retextures and re-models of existing mobs and bosses for story characters (Malric, Iron Choir heralds, Hollowed variants), done as resource-pack overrides of GeckoLib geo and animation files. Also used for the occasional unique item model.
- **MCreator (`tt_bridge`):** story-flag storage, chapter progression, cross-mod triggers (boss kill → flag → unlock recipe or suit), small custom items such as Crown Shards and story keys, and a few commands that KubeJS and FTB Quests call.

## 4. Reference modpacks to study (structure and mod choices only)
Atom's Grand Adventure (Forge 1.20.1, origins, 14 classes, quest-driven), Volvecraft RPG (14 classes, 70+ quests, 30+ bosses), Dawn of Larston (story-driven dark fantasy), Realms of Ascension (Pufferfish skills + raid bosses), Legends Reborn RPG (classes and bosses).

## 5. Risks this strategy introduces
| Risk | Mitigation |
|---|---|
| Epic Fight + Palladium + Iron's Spells animation conflicts | First test build includes exactly these three. Fall back to Better Combat if needed |
| MineColonies performance (many citizens) | Cap the colony size, profile with Spark |
| Apotheosis + Champions both add elite bosses | Disable Apotheosis's bosses or Champions' tier 4+ (decide in testing) |
| Several mods are unofficial ports (Champions Unofficial) or archived (Origins Forge) | Avoid archived mods. Track ports in the manifest |
