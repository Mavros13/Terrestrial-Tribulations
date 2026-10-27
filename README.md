# Terrestrial Tribulations

A story-driven fantasy action-RPG modpack for **Minecraft 1.20.1 (Forge 47.4.18)**: Epic Fight combat, Palladium superheroes, Iron's Spells, Origins and Fates, Passive Skill Tree, MineColonies capital, FTB Quests campaign.

## Play Test Build 1 (Prism Launcher)
**Import by URL (fully automatic)**
1. Prism → **Add Instance** → **Import**.
2. Paste: `https://github.com/Mavros13/Terrestrial-Tribulations/raw/main/dist/Terrestrial-Tribulations-TestBuild1-CurseForge.zip`
3. OK. Prism downloads every mod from CurseForge itself (no manual downloads). Set memory to 8 GB (Edit → Settings → Java), then **Launch**.

This is a CurseForge-format modpack zip (`manifest.json` + `overrides/`), built by `tools/build_curseforge.py` from `modpack/curseforge-mods.json`. The CurseForge app can import the same file. Gods and Heroes (Palladium) is Modrinth-only, so add it from Prism's Modrinth tab if wanted.

**Fallback: ModSync instance.** `…/dist/Terrestrial-Tribulations-TestBuild1.zip` downloads mods from Modrinth at launch (**TT ModSync**); CurseForge-only mods are then added by hand through Prism's CurseForge tab. Its log is `minecraft/tt-sync/sync-report.txt`.

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
