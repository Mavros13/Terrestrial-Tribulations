# Terrestrial Tribulations: full mod list (v1, 2026-10-27)

Target: **Minecraft 1.20.1 · Forge 47.4.x · Java 17**. Status key:
- ✅ **source-verified:** format or IDs checked in the mod's own source code on GitHub
- 🔎 **web-verified:** a 1.20.1 Forge file was seen in search results
- ❔ **to verify:** probably exists, not yet checked
- ⚠️ **issue noted**

A mod becomes CONFIRMED only after it loads in your instance (ModSync's `lock.json` records the exact files).

**Availability check (2026-10-27):** every entry was checked on Modrinth and CurseForge for a 1.20.1 Forge file. 74 download automatically; 19 are CurseForge-only (manual download, 11 of them in Test Build 1). Details, file names and fixes: [`docs/research/2026-10-27-mod-availability.md`](research/2026-10-27-mod-availability.md).

Stages in `pack/tt-sync/mods.json`: **A/B/C = Test Build 1**, **D = Test Build 2** (world, bosses, tech, magic, accessories). Stage D only loads when `stage.txt` says `D`.

## Story-critical
| Mod | Role in the story | Status | Notes |
|---|---|---|---|
| FTB Quests (+ FTB Library, FTB Teams) | The campaign book | ✅ format · 🔎 | 1.20.1 build is CurseForge-only, so it's a manual download |
| Easy NPC | Maera, Doran, Rhosk and other named NPCs | 🔎 6.25.0 | Dialogue scripts in `design/npcs/` |
| MineColonies (+ Structurize, MultiPiston, BlockUI, Domum Ornamentum) | Emberhold: Town Hall levels 1–5 = city stages | 🔎 | Snapshot builds only since 2024; cap the colony size for performance |
| Origins (Forge) | Heritage + Fate layers | ✅ format · 🔎 1.10.0.9 | Archived; avoid Forge 47.2.0 |
| Passive Skill Tree (+ PassiveSTJS) | Talent tree, points from XP | ✅ format · 🔎 | `tt:shardborn` tree generated |
| Palladium + FSang18's Heropack + Satsu Iron Man Addon + Gods and Heroes (Palladium edition) | Superheroes and the Iron Choir villains | 🔎 4.5.9; FSang18 12.5.7 and Satsu 3.6.0 released after it; Gods and Heroes 1.4 needs a launch test | **Existing packs only** (no custom heroes). Story fit: `design/story/heroes-integration.md` |
| L_Ender's Cataclysm | Ignis, Harbinger, Leviathan, Netherite Monstrosity, Ender Guardian… | 🔎 | Chapter 6–9 bosses |
| Mowzie's Mobs | Frostmaw, Ferrous Wroughtnaut, Umvuthi | 🔎 | Chapter 5–6 bosses |
| Bosses of Mass Destruction | Night Lich, Obsidilith, Gauntlet, Void Blossom | 🔎 1.1.2 | Needs CerbonsAPI |
| Alex's Caves (+ Citadel) | Five cave biomes, bosses | ❔ | Official 1.20.1 build |
| The Twilight Forest | Twilight Shard (Naga → Lich → Hydra → Ur-Ghast …) | ❔ | 1.20.1 build exists (well known) |
| The Aether | Aether Shard (Slider, Valkyrie Queen, Sun Spirit) | ❔ | |
| The Undergarden | Undergarden Shard | ❔ | |
| Deeper and Darker | Otherside Shard | ❔ | |
| Blue Skies | Everbright and Everdawn (the 5th and 6th dimensions) | ❔ | |

## Combat and animation
| Mod | Status | Notes |
|---|---|---|
| Epic Fight | ✅ format · 🔎 20.14.x | Our 22 melee weapons have capability files |
| Epic Fight - Impactful | 🔎 CurseForge-only | Hit-stop and screen shake. Modrinth copy is 2023 (too old); use impactful-20.14.2 from CurseForge, plus its resource pack and datapack |
| NEpicloob NeonSword | 🔎 | Author's range: Epic Fight ≤20.9.7 or ≥20.11.2, so 20.14 is supported |
| Epic Fight EDP (Extended Datapacks) | ✅ CurseForge-only, stage D | 2.5.5 for 1.20.1 Forge (Oct 2026). Needs SL Library, SLM: Epic Fight and SLM: Shader (all added). Custom innate skills from JSON; see docs/research/2026-10-27-epic-fight-data-formats.md |
| CompatLink - Epic Fight Weapons Compat | 🔎 | Needs Epic Fight 20.14.17+ |
| Simply Swords | ❔ | Loot weapons |
| Marium's Soulslike Weaponry | 🔎 1.4.8 | Legendary loot weapons |
| Wakes (Forge port) | 🔎 1.0.5 | Water trails |
| ~~Afterswing~~ | ⚠️ | Not on Modrinth or CurseForge for 1.20.1 Forge (rechecked 2026-10-27). Dropped |

## RPG systems
| Mod | Status | Notes |
|---|---|---|
| Champions Unofficial | 🔎 2.1.12.x | Elite affixes, extensible with KubeJS |
| Apotheosis (+ Placebo, Apothic Attributes) | ❔ | Loot rarity, affixes and gems. Disable its bosses if they overlap with Champions |
| Armor Set Bonuses | 🔎 20.14.0 | Data-driven set bonuses |
| Botz Mob Leveling | 🔎 | Region and dimension scaling |
| Iron's Spells 'n Spellbooks | ✅ attribute IDs · 🔎 3.15.6 | Magic #1 (combat) |
| Ars Nouveau | ❔ | Magic #2 (utility and automation) |

## Technology and automation
| Mod | Status | Notes |
|---|---|---|
| Create 6 | 🔎 | |
| Create: Steam 'n' Rails, Crafts & Additions, Enchantment Industry | 🔎 | Check each is compatible with Create 6 |
| Applied Energistics 2 (+ ExtendedAE, AE2WTLib) | ❔ | |
| Mekanism + Mekanism Generators | 🔎 10.4.16.80 | **Quarry = Digital Miner**, plus power, pipes and generators (one coherent stack) |
| ~~Powah, Pipez~~ | | Dropped as redundant with Mekanism |
| Core Utilities | 🔎 2.0.0 (CF 1379111 / 9343420, Modrinth core-utilities) | Owner's request (2026-10-28). Solar panels, generators, crusher/alloy smelter, crop harvester, mob grinder, block breaker/placer, item pipes, backpacks, mob net. No dependencies (JEI optional). Overlaps Mekanism's power/quarry; Mekanism's Digital Miner stays the story quarry |
| Rats (+ Citadel) | 🔎 8.1.3 | Rat Guild (Nib) |

## Accessories and cosmetics
| Mod | Status | Notes |
|---|---|---|
| Curios API | ❔ | |
| Artifacts | ❔ | Loot accessories |
| Relics (+ deps) | 🔎 | Upgradeable relics |
| Relicera | 🔎 1.1.4 | More Curios accessories |
| Elytra Slot | 🔎 3.5.1 | Needs Curios |
| Elytra Trims (+ Kotlin for Forge) | 🔎 3.10.0 | |
| Goner's Armor Trims | 🔎 1.0.4 | ⚠️ Replaces "More Armor Trims", which has no Forge 1.20.1 build I could find |
| Cosmetic Armor Reworked | ❔ | Armour transmog |
| Karambit Vault x Punchy (resource pack) | 🔎 | ⚠️ Punchy animations are Fabric-only. Our own karambits need our own models (or the author's permission) |
| Default Options (+ Balm) | ✅ 18.0.5 | Switches Karambit Vault x Punchy on once per player without shipping `options.txt` (2026-10-29) |

## World generation and structures
| Mod | Status | Notes |
|---|---|---|
| Terralith | ❔ | Terrain and biomes |
| ~~Tectonic~~ | 🔎 ⚠️ | 1.20.1 build is unmaintained; skipped to keep world generation stable |
| YUNG's API + Better Dungeons / Mineshafts / Strongholds / Desert Temples / Ocean Monuments / Witch Huts / Nether Fortress / End Island | ❔ | |
| ChoiceTheorem's Overhauled Village | ❔ | Villages (chosen over Towns & Towers to avoid overlap) |
| Dungeons and Taverns | 🔎 3.0.1 | |
| When Dungeons Arise | ❔ | Reduce its density in config |
| Incendium | 🔎 5.3.x | Nether |
| **Nullscape** | 🔎 1.2.8 | **End overhaul (chosen 2026-10-27)**, Stardust Labs like Terralith and Incendium. Check alongside YUNG's Better End Island in Test Build 2 |
| ~~BetterEnd: Before Dawn (Forge port)~~ | 🔎 | Not chosen: unofficial port, needs BCLib + WunderLib, adds lots of loot. Swap in if Nullscape disappoints |

## Building and quality of life
| Mod | Status |
|---|---|
| JEI, Jade | ✅ Modrinth IDs |
| Xaero's Minimap + World Map | ❔ |
| Mouse Tweaks, Quark (+ Zeta, trimmed config), AppleSkin, FTB Ultimine | ❔ |
| Sophisticated Backpacks (+ Core) | ❔ |
| Construction Wand, Building Gadgets 2 | ❔ |
| Handcrafted, Supplementaries (+ Moonlight), Macaw's Doors/Roofs/Bridges, Medieval Deco | 🔎 / ❔ |
| Leaves Be Gone | 🔎 v8.0.0 (Modrinth) |
| Catalogue + Configured (Forge's "Mod Menu") | ❔ |

## Interface and audio
| Mod | Status |
|---|---|
| FancyMenu (+ Konkrete, Melody) | ❔ (title screen) |
| Legendary Tooltips (+ Prism lib) | ❔ |
| Enhanced Boss Bars (resource pack + compat mod for Cataclysm and Aether) | 🔎 v1.6 |
| AmbientSounds, Sound Physics Remastered | ❔ |

## Performance
Embeddium, Oculus (optional shaders), ModernFix, FerriteCore, EntityCulling, ImmediatelyFast, Canary, Spark, Chunky (pre-generate the spawn area).

## Other
- **CreeperMax123:** I found no CurseForge author page. Their known work is mostly vanilla mob **resource packs** (Better Vanilla Mobs, Better Illagers and others). They're candidates for an optional visual pack. Check them alongside Epic Fight's mob models.

## Still open
1. ~~End overhaul~~: decided, Nullscape + YUNG's Better End Island (see the research note).
2. Apotheosis + Champions overlap: decide after Test Build 2.
3. Palladium hero packs: fill in the story-gate namespaces after the first launch (`kubejs/exported/tt_item_namespaces.json`).
4. Gods and Heroes (Palladium) adds its powers as origins on the selection screen. Decide after the first launch whether to hide its layer and grant powers by command at each Crown Shard.
