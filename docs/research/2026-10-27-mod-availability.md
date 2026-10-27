# Mod availability check: Minecraft 1.20.1 Forge (2026-10-27)

Every `pack/tt-sync/mods.json` entry was checked against the Modrinth API (`/v2/project/<slug>/version?loaders=["forge"]&game_versions=["1.20.1"]`, the same query ModSync makes). Misses were then checked on CurseForge's file lists filtered to 1.20.1. "Newest" means the newest 1.20.1 Forge file on that date.

## Result in one line
- **74 mods download automatically from Modrinth**, after four slug fixes and two additions (Afterswing stays disabled).
- **19 are CurseForge-only**, so they go in ModSync's manual-download pop-up.
- One entry pointed at the wrong mod: **Gods and Heroes**.
- One mod needs CurseForge because its Modrinth copy is outdated: **Epic Fight - Impactful**.

## Fixes made to `mods.json`
| Entry | Problem | Fix |
|---|---|---|
| Create: Steam 'n' Rails | Slug `railways` doesn't exist on Modrinth | `create-steam-n-rails` (1.7.3, Aug 2026) |
| ExtendedAE | Slug `extendedae` doesn't exist | `extended-ae` (1.20-1.4.18, Aug 2026) |
| Bosses of Mass Destruction | `bosses-of-mass-destruction` has no Forge file | `bosses-of-mass-destruction-forge` (1.1.2) |
| Gods and Heroes | `gods-and-heroes` is a **different, Origins-only addon** (Spider-Man, Vampire and other origins, no Palladium) | `gods-and-heroes-palladium` by GC-Morak (1.4, Apr 2025): Speedster, Kryptonian, Jumper, Engineer (Create), Mage (Ars Nouveau), Builder, Size Shifter, Iron Mage (Iron's Spells) |
| Gods and Heroes (Palladium) | Lists **both** Origins (Forge) *and* Fabric Origins (`3BeIrqZR`) as required. On Forge, the Fabric one is a Sinytra Connector build. ModSync would pull it plus Connector, and two Origins mods crash the game | New `skip_dependencies` in `mods.json`; ModSync now never downloads `3BeIrqZR` |
| Epic Fight - Impactful | Modrinth stops at 20.6.4 (Dec 2023), built for an old Epic Fight | CurseForge-only: `impactful-20.14.2.jar` (Mar 2026). After Epic Fight 20.11 it also needs its resource pack and datapack (see its page) |
| Building Gadgets 2 | CurseForge slug is `building-gadgets` (the project kept its old name) | Fixed; file is `BuildingGadgets2-1.0.8` (Aug 2025) |
| Leaves Be Gone | Wasn't in `mods.json` | Added (Modrinth, v8.0.0, needs Puzzles Lib, auto) |
| End overhaul | Undecided | **Nullscape** added; see below |

## CurseForge-only on 1.20.1 Forge (manual download)
| Mod | CurseForge slug | Newest 1.20.1 Forge file |
|---|---|---|
| Passive Skill Tree | passive-skill-tree | PassiveSkillTree-1.20.1-BETA-0.7.6e-all.jar (Jul 2026) |
| PassiveSTJS | passiveskilltreejs | PassiveSTJS-1.20.1-0.2.2.jar (May 2026) |
| FTB Quests | ftb-quests-forge | ftb-quests-forge-2001.4.22.jar (May 2026) |
| FTB Library | ftb-library-forge | ftb-library-forge-2001.2.13.jar (Jun 2026) |
| FTB Teams | ftb-teams-forge | ftb-teams-forge-2001.3.2.jar (Jan 2026) |
| FTB Ultimine | ftb-ultimine-forge | ftb-ultimine-forge-2001.1.8.jar (Apr 2026) |
| MineColonies | minecolonies | minecolonies-1.20.1-1.1.1302-snapshot.jar (Oct 2026, snapshot only) |
| Structurize | structurize | structurize-1.20.1-1.0.821-snapshot.jar (Sep 2026) |
| Multi-Piston | multi-piston | multipiston-1.20-0.0.47-snapshot.jar (Oct 2025) |
| BlockUI | blockui | blockui-1.20.1-1.0.193.jar (Jan 2026) |
| Domum Ornamentum | domum-ornamentum | domum_ornamentum-1.20.1-1.0.304-snapshot-universal.jar (Aug 2026) |
| The Twilight Forest | the-twilight-forest | twilightforest-1.20.1-4.3.2508-universal.jar (Jun 2024) |
| Botz Mob Leveling | botz-mob-leveling | botzmobleveling-1.0.7.jar (Jun 2026) |
| Goner's Armor Trims | goners-armor-trims | beta-goners_armor_trims-1.0.7-forge-1.20.1.jar (Jan 2025, **beta only**) |
| Cosmetic Armor Reworked | cosmetic-armor-reworked | cosmeticarmorreworked-1.20.1-v1a.jar (Jun 2023) |
| Building Gadgets 2 | building-gadgets | BuildingGadgets2-1.0.8 (Aug 2025) |
| Catalogue | catalogue | Catalogue 1.8.0 (Sep 2023) |
| Configured | configured | Configured 2.2.3 (Mar 2024) |
| Epic Fight - Impactful | epic-fight-impactful | impactful-20.14.2.jar (Mar 2026) |

That's 19 mods to add by hand (Test Build 1 needs the first 11; the rest are stage D). Prism Launcher can add them straight from its own CurseForge browser (Edit instance → Mods → Download mods → CurseForge), so no website visits are needed.

## Superhero packs vs Palladium 4.5.9
Palladium 4.5.9 (Aug 23, 2026) is the newest 1.20.1 Forge build.
| Pack | Newest 1.20.1 Forge | Required mods (auto-downloaded) | Verdict |
|---|---|---|---|
| FSang18's Heroes | 12.5.7 (Oct 18, 2026) | Palladium, PantheonSent (1.1.1), Curios, GeckoLib, KubeJS, Pehkui, Packet Fixer | ✅ Released after 4.5.9 and actively updated |
| Satsu Iron Man Addon | 3.6.0 (Sep 18, 2026) | None declared; the page says to put armour in a Curios slot (Curios is already in the pack) | ✅ Released after 4.5.9 |
| Gods and Heroes (Palladium) | 1.4 (Apr 27, 2025) | Palladium, KubeJS, Pehkui, Origins (Forge) | ⚠️ Older than 4.5.9, so it needs a first-launch test. Its powers are **origins on the selection screen**. Our Heritage + Fate layers mean players would see a third choice at character creation. To keep the "Shard-Born awakenings" plan, hide its layer and grant its origins by command at each Crown Shard. Do that once its layer and origin IDs are known from the first launch |

## Combat add-ons
- **NeonSword:** the CurseForge page says it works with Epic Fight "20.11 and 20.9" (range `(,20.9.7] ∪ [20.11.2,)`, only 20.10 excluded). Epic Fight 20.14.17 falls in that range. Modrinth has 0.3.0 (Jan 2026), client-only. ✅
- **Afterswing:** nothing on Modrinth or CurseForge for 1.20.1 Forge. It stays disabled. Impactful + NeonSword cover its role.
- **Epic Fight - Impactful:** see the fixes table above.

## End overhaul: recommendation
| Option | 1.20.1 Forge | Notes |
|---|---|---|
| **Nullscape** (Stardust Labs) | ✅ v1.2.8, covers 1.20–1.20.6 (Sep 2024) | Same team as Terralith and Incendium, so all three dimensions share one style. Terrain only, no new items, light on performance. The earlier "no 1.20.1 build" note was wrong |
| BetterEnd: Before Dawn (Forge port) | ✅ 20.0.12.1 (Oct 2026) | Unofficial port that needs BCLib + WunderLib. Adds many blocks, items and mobs (more balancing, more to load) |
| YUNG's Better End Island only | ✅ | Only changes the central island and dragon fight |

**Chosen: Nullscape + YUNG's Better End Island** (added at stage D). The Ch11 Ender Dragon fight keeps YUNG's arena; Nullscape makes the outer End feel alien without adding loot that competes with our weapons. Nullscape says it's incompatible with most End worldgen mods (it names Better End as the exception). YUNG's Better End Island only touches the main island, but **check both together in Test Build 2**. To switch to BetterEnd later, swap the `nullscape` entry for `betterend-forge`.

## Other notes from the check
- **The Aether**'s 1.20.1 files are named `…-neoforge.jar` but are tagged for Forge too. NeoForge for 1.20.1 is still Forge-compatible, so that's expected.
- **ImmediatelyFast**'s newest Forge builds are named `+1.20.4`, but the author tags them for 1.20–1.20.4. If it causes trouble, pin `"version": "1.2.4+1.20.1"`.
- **MineColonies family** only has snapshot builds on 1.20.1 (already noted in docs/07).
- **Easy NPC** downloads as the `easy_npc_bundle` jar (7.15.0), with its two dependencies auto-resolved.

## Sources
- Modrinth API v2 (`api.modrinth.com/v2/project/<slug>/version`, `/v2/search`), queried 2026-10-27.
- CurseForge project file lists (`curseforge.com/minecraft/mc-mods/<slug>/files/all?version=1.20.1`) and cfwidget (`api.cfwidget.com`), 2026-10-27.
- NeonSword CurseForge page (Epic Fight version range); Gods and Heroes (Palladium) and Nullscape project pages on Modrinth.
