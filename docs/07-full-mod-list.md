# Terrestrial Tribulations: full mod list (v1, 2026-10-27)

Target: **Minecraft 1.20.1 · Forge 47.4.x · Java 17**. Status key:
- ✅ **source-verified:** format or IDs checked in the mod's own source code on GitHub
- 🔎 **web-verified:** a 1.20.1 Forge file was seen in search results
- ❔ **to verify:** probably exists, not yet checked
- ⚠️ **issue noted**

A mod becomes CONFIRMED only after it loads in your instance (ModSync's `lock.json` records the exact files).

Stages in `pack/tt-sync/mods.json`: **A/B/C = Test Build 1**, **D = Test Build 2** (world, bosses, tech, magic, accessories). Stage D only loads when `stage.txt` says `D`.

## Story-critical
| Mod | Role in the story | Status | Notes |
|---|---|---|---|
| FTB Quests (+ FTB Library, FTB Teams) | The campaign book | ✅ format · 🔎 | 1.20.1 build is CurseForge-only, so it's a manual download |
| Easy NPC | Maera, Doran, Rhosk and other named NPCs | 🔎 6.25.0 | Dialogue scripts in `design/npcs/` |
| MineColonies (+ Structurize, MultiPiston, BlockUI, Domum Ornamentum) | Emberhold: Town Hall levels 1–5 = city stages | 🔎 | Snapshot builds only since 2024; cap the colony size for performance |
| Origins (Forge) | Heritage + Fate layers | ✅ format · 🔎 1.10.0.9 | Archived; avoid Forge 47.2.0 |
| Passive Skill Tree (+ PassiveSTJS) | Talent tree, points from XP | ✅ format · 🔎 | `tt:shardborn` tree generated |
| Palladium + FSang18's Heropack + Satsu Iron Man Addon + Gods and Heroes | Superheroes and the Iron Choir villains | 🔎 4.5.9 | **Existing packs only** (no custom heroes). Story fit: `design/story/heroes-integration.md` |
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
| Epic Fight - Impactful | 🔎 | Hit-stop and screen shake |
| NEpicloob NeonSword | 🔎 ⚠️ | Listed for Epic Fight 20.9/20.11; test it on 20.14 |
| Epic Fight EDP (Extended Datapacks) | 🔎 ⚠️ | 1.20.1 backport may lag; needed for data-driven weapon skills |
| CompatLink - Epic Fight Weapons Compat | 🔎 | Needs Epic Fight 20.14.17+ |
| Simply Swords | ❔ | Loot weapons |
| Marium's Soulslike Weaponry | 🔎 1.4.8 | Legendary loot weapons |
| Wakes (Forge port) | 🔎 1.0.5 | Water trails |
| ~~Afterswing~~ | ⚠️ | No 1.20.1 Forge file found |

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
| BetterEnd (Forge port) | 🔎 ⚠️ | Unofficial port; End overhaul. Nullscape has no 1.20.1 build |

## Building and quality of life
| Mod | Status |
|---|---|
| JEI, Jade | ✅ Modrinth IDs |
| Xaero's Minimap + World Map | ❔ |
| Mouse Tweaks, Quark (+ Zeta, trimmed config), AppleSkin, FTB Ultimine | ❔ |
| Sophisticated Backpacks (+ Core) | ❔ |
| Construction Wand, Building Gadgets 2 | ❔ |
| Handcrafted, Supplementaries (+ Moonlight), Macaw's Doors/Roofs/Bridges, Medieval Deco | 🔎 / ❔ |
| Leaves Be Gone | ❔ ⚠️ no Forge 1.20.1 result yet |
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
1. End overhaul: BetterEnd Forge port, or YUNG's Better End Island only.
2. Apotheosis + Champions overlap: decide after Test Build 2.
3. Palladium hero packs: fill in the story-gate namespaces after the first launch (`kubejs/exported/tt_item_namespaces.json`).
