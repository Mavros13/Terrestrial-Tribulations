# AETHERFALL — Project Kickoff Package (v0.1)

> Working title: **Aetherfall: The Sundered Crown**.
> Status legend: **CONFIRMED** (I checked the exact file against the target), **CANDIDATE** (project known to exist; the exact release and compatibility are not yet checked), **CUSTOM** (we write it), **REJECTED**.
> **Nothing in this document has been verified against live CurseForge or Modrinth pages yet.** Every mod row is CANDIDATE until Milestone 1 (manifest verification) runs. Version numbers are from my knowledge and must be re-checked.

---

## A. Version recommendation

| Criterion | **1.20.1 Forge (47.x)** | 1.21.1 NeoForge (21.1.x) | 1.20.1 Fabric |
|---|---|---|---|
| Create + addons | Create 6 available, largest addon pool | Create 6 available, addon pool growing | Create Fabric lags behind |
| AE2 + addons | Mature | Mature | Available |
| Better Combat / Combat Roll | Yes | Yes | Yes |
| Iron's Spells 'n Spellbooks | Yes | Yes | No (Forge only) |
| Ars Nouveau | Yes | Yes | No |
| Superheroes (Palladium + addon packs) | Strongest ecosystem | Partial, check per addon | Yes (Palladium is multiloader) |
| Rats | 1.20.1 Forge port exists (check) | **Uncertain** | No |
| FTB Quests | Yes (SNBT) | Yes (SNBT) | Yes |
| KubeJS | 2001.6.x, very well documented | 2101.x, different API in places | Yes |
| Structure mods (YUNG's, Dungeons & Taverns, CTOV) | Full | Most | Most |
| Java | 17 | 21 | 17 |
| Risk | Older and frozen, but stable | Newer, some gaps | Missing two key magic mods |

**Recommendation: Minecraft 1.20.1, Forge 47.4.x, Java 17.** This is the only target where *every* pillar (Rats, two magic systems, Palladium superheroes, Create 6, AE2, Better Combat, CTOV, FTB Quests) is likely available at once. Forge 1.20.1 is a dead end for new Minecraft features, so the migration target is **1.21.1 NeoForge**. That port should be reconsidered once Rats and the Palladium addons are confirmed there.

Limitations: there are no vanilla 1.21 features (trial chambers, mace). Some mods have stopped updating on 1.20.1. Custom Java mods will need a real port later, not just a recompile.

## B. Hardware-aware architecture

Target machine: Ryzen 7 5800XT, 32 GB of DDR4-2400, a GTX 1660 Super (6 GB) and 1080p.

**Layers**
1. **Foundation:** Forge, libraries, and performance mods (Embeddium, ModernFix, FerriteCore, EntityCulling, ImmediatelyFast, Radium-port/Canary, C2ME is Fabric-only so we skip it). All are CANDIDATE.
2. **Content mods:** existing mods chosen by category.
3. **Glue:** KubeJS scripts for recipes, gates and tags, datapacks for loot and worldgen tuning, and FTB Quests SNBT.
4. **Custom mod `aetherfall-core`:** levels, Fates, talents, active abilities, enemy scaling, city stages, artifacts and the mythic framework. It is server-authoritative and exposes a small API to KubeJS.
5. **Presentation:** a resource pack (UI theme, Enhanced Boss Bars, rarity colours) plus optional shader presets.

**Preliminary budgets** (to be replaced by measured numbers after the baseline):

| Metric | Budget |
|---|---|
| Mod count | about 180–230 jars, including libraries |
| JVM heap | 10 GB to start (`-Xmx10G -Xms10G`). Measure, then tune within 8–12 GB |
| Cold startup | under 4 minutes |
| FPS without shaders, 12 chunks, ordinary terrain | 60 or more |
| FPS in the capital (full stage) | 45 or more |
| Server MSPT, single player, large Create factory | under 35 ms |
| Shader preset | Complementary *Reimagined* at low, or BSL at low. Optional only. Expect 30–45 FPS on the 1660S |

**Top technical risks**

| # | Risk | Mitigation |
|---|---|---|
| R1 | The world-generation stack (Terralith, Tectonic and structures) causes generation stutter and conflicts | Choose one terrain mod, add structure mods one at a time, pre-generate the spawn region with Chunky |
| R2 | Better Combat conflicts with Epic Fight-style systems | Pick **Better Combat + Combat Roll** only and reject Epic Fight |
| R3 | The custom mod's scope (talents, city, mythic) | Ship in vertical slices, with a data-driven design (JSON nodes) |
| R4 | Superhero powers trivialise progression | Gate Palladium suits through KubeJS recipes plus `aetherfall-core` flags |
| R5 | Entity load from NPCs, rats and Create contraptions | Cap populations, use EntityCulling, profile with Spark |
| R6 | Redistribution licences | Ship as a CurseForge manifest that references files, never bundled jars |

## C. Mod research matrix (all CANDIDATE unless marked otherwise)

| Category | Pick | Purpose | Notes / conflicts |
|---|---|---|---|
| Recipes and info | JEI, Jade | Recipe viewer and tooltips | Reject REI and EMI to avoid duplication |
| Map | Xaero's Minimap + World Map | Map | Reject JourneyMap (heavier and redundant) |
| QoL | Mouse Tweaks, Quark (trimmed config), Inventory Profiles Next *or* Quark sorting, FTB Ultimine, Leaves Be Gone (Forge port?), AppleSkin | Quality of life | Quark overlaps with sorting, so disable one |
| Mod menu | Catalogue (the Forge equivalent of Mod Menu) | Config UI | Mod Menu is Fabric-only |
| Backpacks | Sophisticated Backpacks | Upgradeable bags | |
| Building | Construction Wand, Building Gadgets 2 | Builder tools | |
| Accessories | Curios API, Artifacts, Relics, Elytra Slot | Trinket ecosystem | Check that Elytra Slot works with Curios on Forge |
| Trims | More Armor Trims, Elytra Trims (+ Extensions) | Cosmetics | Elytra Trims needs a Forge build; may need Sinytra Connector, otherwise REJECT |
| Combat | Better Combat, Combat Roll, Simply Swords, Shield Expansion(?) | Animated combat, dodges, weapon movesets | Combat Roll provides the dodge. Parry comes from CUSTOM code |
| Anim / VFX | playerAnimator (Better Combat dependency), GeckoLib, Visuality, Particle Rain (optional) | | Watch the particle budget |
| Mobs / AI | Enhanced AI-style mods are avoided; CUSTOM behaviour goals are used for named enemies | | |
| Bosses | L_Ender's Cataclysm, Bosses of Mass Destruction, Mowzie's Mobs, Alex's Caves (also a dimension-like biome) | Boss roster | Tune difficulty with KubeJS |
| Magic 1 | **Iron's Spells 'n Spellbooks** | Combat spellcasting | |
| Magic 2 | **Ars Nouveau** | Utility, glyph crafting, automation | The two systems are distinct: action versus crafting |
| Superheroes | Palladium + compatible addon packs (for example, power packs) | Suits and powers | Choose addon packs only after testing |
| Create | Create 6, Create: Steam 'n' Rails, Create Crafts & Additions (electricity), Create Enchantment Industry, Create Slice & Dice | Engineering | Keep to five addons or fewer |
| Storage | AE2, AE2 Things(?), ExtendedAE | Digital storage | No Refined Storage |
| Logistics / power | Mekanism (*generators* plus pipes) **or** Pipez plus Powah | Pipes, energy, generators | Recommend **Pipez + Powah** (light) and reject full Mekanism for scope |
| Quarry | Industrial Foregoing laser drill, *or* Mekanism Digital Miner, *or* RFTools Builder quarry | Area mining | Recommend the RFTools Builder quarry card, or Create contraption drills plus "Create: Ore Excavation" veins. Decide in the Phase 3 test |
| Rats | Rats (1.20.1 Forge) | Labour automation | If no stable 1.20.1 build exists, use a CUSTOM "Rat Guild" system or drop it |
| Worldgen | Terralith **or** Tectonic (choose one), YUNG's suite, Dungeons & Taverns, CTOV, Towns & Towers, When Dungeons Arise (reduced density), Incendium + Nullscape (Nether and End) | Exploration | CTOV and Towns & Towers both alter villages, so check for overlap |
| Dimensions | Twilight Forest, Blue Skies (two dims), The Aether, Undergarden, Deeper & Darker | 5+ dimensions | Recommend Twilight Forest, Aether, Undergarden, Deeper & Darker, and Blue Skies (optional) |
| NPC / dialogue | Easy NPC (supports dialog and trading) and CUSTOM dialogue hooks | Capital NPCs | Must verify Easy NPC's branching dialogue |
| Quests | FTB Quests, FTB Library, FTB Teams, FTB XMod Compat | Quest book | |
| Transmog | Cosmetic Armor Reworked (armor only); weapons through CUSTOM code | Appearance | |
| Audio | AmbientSounds 5, Sound Physics Remastered | Atmosphere | Sound Physics costs CPU, so leave it off in the Performance preset |
| Water | Wakes | Water trails | Fabric-only, so likely REJECT on Forge |
| UI | Enhanced Boss Bars (RP), FancyMenu (title screen), Legendary Tooltips | UI identity | |
| Perf | Embeddium, Oculus (shaders), ModernFix, FerriteCore, EntityCulling, ImmediatelyFast, Canary, Spark (profiler), Chunky (pre-generation) | Performance | |
| Scripting | KubeJS 2001, Rhino, Architectury | Glue | |

**CreeperMax123 projects:** I have not reviewed them yet. This is part of Milestone 1.
**Redundancies removed:** REI/EMI, JourneyMap, Refined Storage, Epic Fight, a second terrain overhaul, and multiple pipe mods.

## D. Story foundation

**World: Velmora.** Seven hundred years ago, the **Aether Crown** linked every realm through the *Convergence*, a lattice of ley-lines that powered both magic and the "Old Engines" of the Tinker-Kings. The last Crown-Bearer, **Queen Ysolde**, shattered the Crown to stop a coup. That act, the **Sundering**, broke the realms apart and scattered seven *Crown Shards* across dimensions.

**Antagonist: Malric Thorne, the Hollow Regent.** He was Ysolde's chancellor. He was killed at the Sundering, but he survived as a consciousness inside the Convergence. He is not evil for its own sake: he believes the Sundering doomed Velmora to slow decay, and that only a forced re-Convergence under one will can save it, at the cost of all free will. His agents include the **Hollowed** (soul-husk mobs), the **Iron Choir** (a technocratic villain cult that wields reverse-engineered superhero suits) and corrupted dimension wardens.

**Factions**
- **The Ember Accord:** frontier survivors and the player's first allies (the city's founders).
- **Lumen Conclave:** arcane scholars (Iron's Spells and Ars Nouveau).
- **Cogwright Guild:** engineers who revere the Old Engines (Create and AE2).
- **The Thornwatch:** a militaristic remnant of the old kingdom. They are allies, but their ends are suspect.
- **The Iron Choir:** villains (the superhero antagonist line).
- **Verdant Pact:** nature or Twilight keepers, neutral.

**Central mystery:** Why does the player survive Hollow corruption? The answer is that the player is a **Shard-Born**, a person grown from a fragment of the Crown itself. Every Shard collected makes the player stronger *and* makes Malric's voice clearer. The final choice is to reforge the Crown (and become a new tyrant), to let Malric absorb it, or to **shatter it permanently**, which is the canonical ending and frees the realms while ending the Convergence.

**Campaign (12 chapters)**

| Ch | Title | Beat | Climax |
|---|---|---|---|
| 1 | The Broken Frontier | The player wakes in an ash field and survives the first night | Hollow pack ambush |
| 2 | The First Settlement | Find Ember Accord refugees and found **Emberhold** (city stage 1) | Defend the outpost (wave event) |
| 3 | Echoes of the Old World | Ruins and Old Engine fragments; Create is introduced | Ruined Foundry guardian |
| 4 | The Awakening | The first Shard reacts to the player; Fate selection unlocks | Mirror duel against your Hollow self |
| 5 | Kingdoms in Conflict | Choose between the Conclave and the Cogwrights (both remain available) | Thornwatch siege |
| 6 | The Arcane & Mechanical Age | Full magic and AE2 progression; city stage 3 | Nether: Incendium boss |
| 7 | The Shattered Realms | Aether, Twilight Forest and Undergarden Shards | Dimension wardens |
| 8 | The Rise of Heroes | Palladium suit research; the Iron Choir is revealed | Choir Herald (villain) |
| 9 | War of the Realms | Kingdom defence and faction armies; city stage 4 | Siege of Emberhold |
| 10 | The Mythic Crucible | Artifact forge and mythic armour | Ender Dragon rematch / Cataclysm bosses |
| 11 | The Final Convergence | Enter the Convergence dimension (Deeper & Darker reskin or CUSTOM) | **Malric, the Hollow Regent** (3 phases) |
| 12 | Beyond the Throne | Ending choice, mythic tiers and postgame; city stage 5 | Infinite Crucible |

## E. Progression blueprint

**Equipment tiers**

| Tier | Name | Source | Gate | Approx. damage (sword) |
|---|---|---|---|---|
| 1 | Primitive | Flint, wood, stone | none | 4–5 |
| 2 | Reinforced | Copper, iron | Ch1 | 6 |
| 3 | Adventurer | Steel (Create mixing) or Simply Swords iron | Ch3 + level 10 | 7–8 |
| 4 | Veteran | Diamond + Thornwatch reputation | Ch5, level 20 | 9 |
| 5 | Elite | Netherite + Iron's Spells/Cataclysm mats | Ch6, level 30 | 10–11 |
| 6 | Relic | Dimension materials | Ch7, level 40 | 12–13 |
| 7 | Legendary | Boss cores + Artifact Forge | Ch9–10, level 50 | 14–16 |
| 8 | Mythic | Crown Shard fragments + mythic tier | Ch11+, level 60 | 17–20 + affix |

**Levels:** maximum level 60 (prestige "Paragon" levels after that grant cosmetics and minor stats). Curve: `xpToNext(L) = round(100 * L^1.6)`. Sources are mob kills (scaled by mob tier relative to player level, with **0% XP for mobs 10 or more levels below** the player), quests (the main source), first-time boss kills, discoveries, and crafting milestones. One talent point every 2 levels gives 30, plus about 10 from quests, for **about 40 points total**. Respec uses a *Tome of Unbinding* (crafted; the first one is free).

**Ten Fates** (chosen in Ch4; a second Fate opens at level 40 as a hybrid; Ascendant needs Ch10 and two Fates at rank 5):
Vanguard, Duelist, Warden, Ranger, Arcanist, Spellweaver, Reaper, Summoner, Artificer, Ascendant. Each Fate grants one core passive and modifies the five active abilities (for example, Arcanist's Dash leaves a frost trail).

**16 core passives** (a core ring that every Fate can reach)
1. Iron Hide (+armour per tier) · 2. Second Wind (heal under 30% HP, 90 s cooldown) · 3. Keen Edge (+crit chance) · 4. Executioner (+damage under 25% HP) · 5. Ley Attunement (+mana regen) · 6. Spell Echo (chance to recast) · 7. Bloodthirst (lifesteal on crit) · 8. Bulwark (perfect block refunds stamina) · 9. Fleetfoot (+dodge distance) · 10. Hunter's Mark (ranged hits mark) · 11. Packleader (+summon damage) · 12. Overclock (+machine-gear and suit energy efficiency) · 13. Scavenger (+loot rolls) · 14. Unbroken (poise) · 15. Shardsense (reveals nearby secrets) · 16. Convergent (+5% to all stats per Fate at rank 5)

**Five actives** (bound to keys R, F, G, V and the Ultimate on Z)
1. **Riftstep:** a dash with short i-frames (6 ticks) and a 4 s cooldown
2. **Shard Burst:** an AoE nova whose element depends on the Fate
3. **Aegis:** a 3 s shield that converts absorbed damage to the next hit
4. **Call of the Crown:** summons Fate-flavoured allies for 15 s
5. **Ascension (Ultimate):** 10 s of a transformed state that charges from combat

**About 100 stat nodes:** 10 branches of 10 nodes each: Strength, Vitality, Precision, Defence, Arcana, Mobility, Critical, Regeneration, Dominion (summons), Machinery. Nodes grant +1.5–3% per node, with every 5th node a "notable" worth double. With about 40 points, a character fills **about 4 branches**, which forces a build choice.

**Progression map**
```
Lvl 1-10  Ch1-3  Tier 1-3  Create basics   City: Outpost→Village
Lvl10-25  Ch4-5  Tier 3-4  Fate, magic     City: Village→Town
Lvl25-40  Ch6-8  Tier 5-6  AE2, dims, suits City: Town→Capital
Lvl40-60  Ch9-11 Tier 7-8  Artifacts, final City: Capital→Legendary
60+       Ch12   Mythic+   Crucible tiers I-X
```

## F. Quest architecture

**Format:** FTB Quests on 1.20.1 stores data as **SNBT** under `config/ftbquests/quests/` (`data.snbt`, `chapters/*.snbt`, `chapter_groups.snbt`, `reward_tables/`). IDs are 16-character hexadecimal strings. Before generating files, I will export a known-good sample from a real instance and match its schema exactly.

**Allocation (285 quests)**

| Group | Chapters | Count |
|---|---|---|
| Main story | Ch1–12 campaign (one tab each) | 96 |
| Fundamentals | Welcome, First Night, Survival, Exploration, Combat, Equipment | 40 |
| Character | Levels & Origins, Talent Tree | 14 |
| Magic | Iron's Spells, Ars Nouveau | 30 |
| Tech | Create, AE2, Logistics & Power, Rats, Quarry | 45 |
| World | Capital, Factions, Dungeons, Nether, End, Dimensions | 30 |
| Endgame | Legendary gear, Superheroes, Artifacts, Mythic, Kingdom, Endgame crafting, Postgame | 22 |
| Secrets | Collections and hidden achievements | 8 |
| **Total** | | **285** |

Branching: each main chapter has one critical path (marked with a gold frame) and optional side quests. Tech and magic tabs depend only on soft milestones such as "own a crafting table" and never on story beats, except for the advanced tiers. Ch5 has a non-exclusive faction choice: both paths unlock their own rewards, and the story requires either one. That is implemented with FTB Quests' `or` dependency mode.

**Sample opening quest (full)**

> **Q1.1 — "Ash and Embers"** · Main Story · Chapter 1 *The Broken Frontier*
> *Context:* You wake in grey ash with no memory and a faint warmth in your chest. Something is calling you. Smoke rises to the east.
> *Dialogue (journal voice):* "Breathe. Stand. Whatever happened here, the night will not wait for answers."
> **Objectives**
> 1. Punch a tree and collect 8 `#minecraft:logs`
> 2. Craft a `minecraft:crafting_table`
> 3. Craft 1 `minecraft:wooden_pickaxe` *or* `minecraft:stone_pickaxe`
> **Rewards:** 4× `minecraft:bread`, 1× `minecraft:torch` ×8, 150 Aetherfall XP (a custom reward through the `aetherfall-core` command `/aetherfall xp add @p 150`, run as a *command reward*)
> **Prerequisites:** none (auto-visible). **Unlocks:** Q1.2 "Shelter Before Dark", Welcome-tab tutorials.
> **Multiplayer:** team progress (FTB Teams). Any member completing a task counts it for the team; rewards go to each member. **Repeatable:** no. **Failure:** none.
> **Testing notes:** confirm the tag task accepts stripped logs; confirm the command reward fires once per player, not once per team.

## G. Capital city plan — **Emberhold**

| Stage | Trigger | Unlocks |
|---|---|---|
| 1 Outpost | Ch2 start | Elder Maera (quests), campfire, 1 tent, basic trader |
| 2 Village | Ch2 end + 200 building-material contribution | Blacksmith Doran, farms, palisade, inn |
| 3 Town | Ch5 + faction choice | Conclave tower (Mage Ilsabet), Cogwright workshop (Engineer Pell), market, Rat-catcher Nib |
| 4 Capital | Ch8 + Thornwatch reputation | Barracks (Captain Rhosk), Artifact Forge, diplomat hall, walls |
| 5 Legendary | Ch11 complete | Crown Plaza, Mythic Crucible gate, elite vendors, monuments |

**NPC roster (initial):** Elder Maera (mentor and story), Doran (blacksmith, weapons), Hesta (armourer), Ilsabet (enchanter, Conclave), Pell (engineer, Cogwrights), Ostra (alchemist), Fenwick (merchant, backpacks and curios), Nib (rat-catcher), Captain Rhosk (guards, Thornwatch), Wren (scout, exploration quests), Archivist Sol (lore and collections), "The Stranger" (secretly an Iron Choir infiltrator).

**Mechanism (CUSTOM):** each stage is a set of **pre-built NBT structure templates** stamped into a reserved city plot. The plot is a protected region recorded in `aetherfall-core` world SavedData, and players cannot build inside unbuilt plots. Stage upgrades never overwrite blocks outside the plot. NPCs are Easy NPC entities spawned by a stage script. The stage state is server-persistent and synchronised to all players.

## H. Development roadmap

| M | Milestone | Output |
|---|---|---|
| M0 | This kickoff | Docs, repo layout, manifest format ✅ |
| M1 | Verify the manifest | Every core mod checked against its CurseForge or Modrinth file for 1.20.1 Forge |
| M2 | **Baseline instance** | Forge, performance mods, JEI, Jade, FTB Quests, KubeJS, Better Combat and Combat Roll. Launch and create a world |
| M3 | `aetherfall-core` skeleton | Gradle (ForgeGradle 6, Java 17), levels, XP, command, capability, sync packet |
| M4 | **Vertical slice** | Ch1–2 quests (about 15), first boss, level 1→10, Riftstep ability, city stage 1→2 |
| M5 | Worldgen pass | Terrain, structures, pre-generation, performance capture |
| M6 | Fates and talents UI | |
| M7 | Magic and tech tabs | |
| M8 | Dimensions, Ch6–8 | |
| M9 | Endgame: artifacts, mythic, superheroes | |
| M10 | Polish, multiplayer QA, release | |

**First playable build = M4 vertical slice.** Acceptance criteria:
1. The pack launches cleanly. The log has no `ERROR` from our code and no missing-dependency messages.
2. A new world reaches spawn in under 60 s and the player is placed in the Emberhold plot area.
3. Quests Q1.1–Q2.x complete in order, rewards deliver, and the data survives a relog.
4. Level progression from 1 to 10 is possible in roughly 60–90 minutes of play, and the XP survives a restart.
5. Riftstep works, is server-validated, and plays its animation.
6. The "Hollow Pack Alpha" mini-boss can be beaten with Tier 2–3 gear.
7. Completing Ch2 upgrades the city to stage 2 without touching player blocks.
8. Everything above also works with two players on a dedicated server.
9. At least 60 FPS on your PC without shaders at 12 chunks, measured with Spark plus F3.

## I. Initial deliverables (in this repo)

```
aetherfall/
├─ docs/00-kickoff.md          ← this file (the project specification v0.1)
├─ docs/risk-register.md
├─ manifest/mods.yaml           ← versioned mod manifest (format defined; entries CANDIDATE)
├─ manifest/SCHEMA.md
├─ pack/                        ← becomes the instance's game dir (config, kubejs, ftbquests)
├─ mods-src/aetherfall-core/    ← custom Forge mod (M3)
├─ resourcepacks/ datapacks/
├─ tests/                       ← test plans + checklists
└─ tools/                       ← validators (quest-ID checker, manifest checker)
```

**What I can produce now, without the game:** design documents, the manifest, KubeJS scripts, SNBT drafts, Java source and Gradle build files, test plans and a quest-ID validator.
**What needs your real instance:** confirming exact jar compatibility, the first launch and logs, compiling against Forge (possibly here if Gradle can download Forge through the proxy; untested), all in-game behaviour, FPS and MSPT, multiplayer, and visual checks.

## Ranked first five tasks
1. **Verify the core manifest (M1):** check about 40 foundation and core-pillar mods against their real 1.20.1 Forge files and change their status to CONFIRMED or REJECTED. Decide the Rats, Elytra Trims and Wakes question.
2. **Build the baseline instance (M2):** you install Forge 47.4.x in Prism or CurseForge with the M2 list; I provide the exact list and the JVM arguments, and we review the first `latest.log`.
3. **Scaffold `aetherfall-core` (M3):** Gradle project, mod ID `aetherfall`, the player-progression capability, XP and level commands, and a sync packet.
4. **Export a sample FTB Quests chapter** from your instance, so I generate Ch1–2 SNBT against the real schema.
5. **Write the vertical-slice content:** Ch1–2 quests, a Hollow Pack Alpha spec, the Emberhold stage 1 and 2 templates, and the Riftstep ability.
