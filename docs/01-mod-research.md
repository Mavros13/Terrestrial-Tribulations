# Mod research and version decision (v0.2, 2026-10-27)

**Method:** web search only. Direct access to modrinth.com and curseforge.com is blocked by this environment's network policy, so every row is **CANDIDATE (web evidence)**. A row becomes CONFIRMED only after its exact file is downloaded and launched.

**Priority order:** story-building mods (quests, NPCs and dialogue, bosses, dungeons, dimensions), then gameplay pillars, then QoL and performance.

## 1. Which Minecraft versions are possible
- **Create** (required) has releases only up to **1.21.1**, with nothing for 1.21.2+ or 26.x. That rules out every version newer than 1.21.1.
- The finalists are **1.20.1 Forge** and **1.21.1 NeoForge**. 1.21.1 still hosts the largest active packs (for example, Better MC BMC5).

## 2. Compatibility matrix

✅ = a build was found · ⚠️ = only a fork, port or alternative exists · ❌ = none found · ? = not searched yet

### Story-critical mods
| Mod | Role | 1.20.1 Forge | 1.21.1 NeoForge | Evidence (latest seen) |
|---|---|---|---|---|
| FTB Quests (+ Library, Teams) | Quest book | ✅ | ✅ | 2101.1.23 (Mar 2026) |
| Easy NPC | NPCs, dialogue, trades | ✅ | ✅ | 6.25.0 bundle, with conditional dialogs |
| BRNTalk | Branching NPC dialogue | ? | ✅ | MIT, NeoForge 1.21.1 |
| Custom NPCs Unofficial | Heavy NPC/quest system | ? | ✅ (first release) | Dialogue depth unverified |
| L_Ender's Cataclysm | Bosses | ✅ | ✅ | 3.24 |
| Bosses of Mass Destruction | Bosses | ✅ | ✅ | 1.3.3 (Jul 2026) |
| Mowzie's Mobs | Bosses and mobs | ✅ | ✅ | 1.8.2 |
| Alex's Caves | Biomes and bosses | ✅ (official) | ⚠️ unofficial port 2.0.8 | Community port |
| Twilight Forest | Dimension, boss progression | ✅ | ✅ | 4.8.3344 (Mar 2026) |
| The Aether | Dimension | ✅ | ✅ | 1.5.10 |
| The Undergarden | Dimension | ✅ | ✅ | 0.9.4 (Dec 2025) |
| Deeper and Darker | Dimension | ✅ | ✅ | 1.4.1 |
| Blue Skies | Dimensions | ✅ | ? | Not found |
| When Dungeons Arise | Dungeons | ✅ | ✅ | 2.1.68 |
| YUNG's suite | Dungeons and structures | ✅ | ✅ | Better Dungeons 5.1.4 |
| CTOV (ChoiceTheorem's Overhauled Village) | Villages | ✅ | ✅ | 3.6.3 (Mar 2026), needs Lithostitched |
| Dungeons & Taverns | Structures | ✅ | ? | |
| **Palladium + addons** | **Superheroes** | ✅ **4.5.9 (Aug 2026), many addons** | ❌ **no confirmed build**; "Palladium 5 / 1.21+" not shipped | Decisive gap |
| Marvel Superheroes | Superheroes (alternative) | ? | ✅ 2.1.0-pre5 | Pre-release, IP-themed |

### Gameplay pillars
| Mod | 1.20.1 Forge | 1.21.1 NeoForge | Notes |
|---|---|---|---|
| Create 6 | ✅ | ✅ | |
| AE2 | ✅ | ✅ 19.2.15 | |
| Iron's Spells 'n Spellbooks | ✅ 3.15.6 | ✅ 3.15.6 | Addons mostly 1.21.1 |
| Ars Nouveau | ✅ | ✅ 5.11.4 (May 2026) | |
| Better Combat | ✅ | ✅ 2.3.0 | Client and server versions must match |
| Combat Roll | ✅ | ✅ 2.0.x | |
| Simply Swords | ✅ | ✅ 1.61.3 | |
| Rats | ✅ 8.1.3 (official) | ⚠️ **Rats: Reborn 9.0.0** (May 2026, reworked, first release) | |
| Quarry | RFTools / Mekanism | ✅ Create: Quarry, Industrial Foregoing, Mekanism 10.7 Digital Miner | 1.21.1 has more options |
| Curios / Elytra Slot | ✅ | ✅ | Elytra Slot is NeoForge-only on new versions |
| Elytra Trims | ✅ 3.x (+ Kotlin for Forge) | ? | |
| Wakes | ✅ Forge port 1.0.5 | ✅ Wakes Reforged | |
| Sophisticated Backpacks | ✅ | ✅ 3.25.28 | |
| KubeJS | ✅ 2001.6 | ✅ 2101.7.2 | |
| Origins-style | ✅ | ✅ Neo Origins 1.3.0 | Custom Fates planned anyway |
| Sodium-family rendering | Embeddium | ✅ Sodium 0.8.12 + Iris for NeoForge | 1.21.1 renders better |

## 3. Decision: **Minecraft 1.21.1 + NeoForge (21.1.x), Java 21**

Why it beats 1.20.1:
1. It is the **newest version where Create exists**, and you said newer is better when it works.
2. Every story-critical mod has a 1.21.1 build, and the dialogue tooling is **better** there (Easy NPC conditional dialogs, BRNTalk).
3. It has more quarry options, a better renderer (real Sodium and Iris), and active maintenance. Many 1.20.1 mods are winding down.
4. Iron's Spells addons are now mostly on 1.21.1.

**What we give up, and how we cover it:**
| Gap | Plan |
|---|---|
| **Palladium superheroes** | Build our own **suit-and-powers system in `aetherfall-core`** (GeckoLib suits, flight, energy blasts, gated by story). This was already a custom-development candidate for gating. Evaluate *Marvel Superheroes* as a supplementary source of suits; it is pre-release and uses Marvel IP, so it would be optional. |
| Original Rats | Use **Rats: Reborn** and test it carefully. If it is unstable, fall back to a custom "Rat Guild" worker system. |
| Alex's Caves | Use the unofficial port, or drop it. It is not story-critical. |
| Blue Skies | Unknown. We still have five or more dimensions without it (Twilight, Aether, Undergarden, Deeper & Darker, plus a custom Convergence dimension). |

**When to reverse this decision:** if a confirmed Palladium 1.21.1 build with addons appears before M4, nothing changes except dropping the custom suits. If Rats: Reborn *and* the custom suits both prove infeasible, revisit 1.20.1.

## 4. Still to verify (not searched yet)
Artifacts, Relics, More Armor Trims, Elytra Trims (1.21.1), Building Gadgets 2, Construction Wand, Powah, Pipez, Create addons (Steam 'n' Rails, Crafts & Additions, Enchantment Industry), ExtendedAE, Incendium, Nullscape, Terralith or Tectonic, Towns & Towers, Dungeons & Taverns, Blue Skies, AmbientSounds, Sound Physics Remastered, FancyMenu, Legendary Tooltips, Enhanced Boss Bars, Cosmetic Armor, Xaero's, JEI, Jade, Quark, FTB Ultimine, Mouse Tweaks, Leaves Be Gone, ModernFix, FerriteCore, EntityCulling, ImmediatelyFast, Spark, Chunky, GeckoLib, the CreeperMax123 projects.
