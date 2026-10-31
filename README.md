# Terrestrial Tribulations

A story-driven fantasy action-RPG modpack for **Minecraft 1.20.1 (Forge 47.4.18)**: Epic Fight combat, Palladium superheroes, Iron's Spells, Origins and Fates, Passive Skill Tree, MineColonies capital, FTB Quests campaign.

## Play the full pack (recommended)

**Use the ModSync / Modrinth instance.** It downloads Modrinth mods at launch, including **Gods and Heroes (Palladium)** (`gods-and-heroes-palladium`), which is required for the Chapter 7 / 8 / 10 Shard-Born awakenings. That mod is All Rights Reserved and Modrinth-only, so it cannot ship inside the CurseForge-format zip.

1. Prism → **Add Instance** → **Import**.
2. Paste: `https://github.com/Mavros13/Terrestrial-Tribulations/raw/main/dist/Terrestrial-Tribulations-TestBuild1.zip` (Test Build 2: swap `TestBuild2` for `TestBuild1`).
3. Set memory to **8 GB** if needed, then **Launch**. ModSync pulls Modrinth jars (log: `minecraft/tt-sync/sync-report.txt`).
4. Add any **CurseForge-only** mods Prism lists: Edit → Mods → Download mods → **CurseForge** tab (newest **1.20.1 Forge**). Skip duplicates already in the mods folder. If Gods and Heroes offers Fabric **Origins**, skip it — the pack already has Origins (Forge).

Beta release zip (when published): same idea — prefer the ModSync-built instance over a CurseForge-only import so awakenings are included. What's in the pack: [CHANGELOG.md](CHANGELOG.md).

## CurseForge-format zip (incomplete for awakenings)

Prism → Import → `…/dist/Terrestrial-Tribulations-TestBuild1-CurseForge.zip` (or the versioned `…-0.9.0-CurseForge.zip`). Prism downloads every listed mod from CurseForge. **Gods and Heroes is not in that list** (ARR / not on CurseForge), so Ch7/8/10 awakening rewards will silently no-op until you play via ModSync or otherwise install `gods-and-heroes-palladium` from Modrinth. FSang18 and Satsu hero packs are in the CurseForge zip.

What to test: [docs/06-testing-guide.md](docs/06-testing-guide.md).

## Repository map
| Path | What |
|---|---|
| `docs/` | Design and decisions: kickoff, mod research, toolchain, integration strategy, combat and skills, testing |
| `design/weapons/` | Weapon roster (`ROSTER.md`) and data (`weapons.json`) |
| `design/npcs/`, `design/skills/`, `design/bridge/` | NPC dialogue scripts, custom skill-tree design, tt_bridge mod spec |
| `pack/` | The instance's `minecraft/` folder: KubeJS scripts and assets, Origins/Fates datapack, FTB Quests, ModSync |
| `prism/` | Prism instance files |
| `tools/` | Generators: `build_content.py`, `gen_quests.py`, `build_prism.py` (rebuilds the zips), `build_curseforge.py` |
| `manifest/` | Mod manifest and research status |

Rebuild after changes: `python3 tools/build_prism.py`
