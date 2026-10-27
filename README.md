# Terrestrial Tribulations

A story-driven fantasy action-RPG modpack for **Minecraft 1.20.1 (Forge 47.4.18)**: Epic Fight combat, Palladium superheroes, Iron's Spells, Origins and Fates, Passive Skill Tree, MineColonies capital, FTB Quests campaign.

## Play Test Build 1 (Prism Launcher)
**Option A: import by URL (easiest)**
1. Prism → **Add Instance** → **Import**.
2. Paste: `https://github.com/Mavros13/Terrestrial-Tribulations/raw/main/dist/Terrestrial-Tribulations-TestBuild1.zip`
3. OK, then **Launch**.

**Option B: drag and drop.** Download the zip above and drag it onto the Prism window.

On the first launch, **TT ModSync** runs before the game starts. It downloads every mod (and its dependencies) from Modrinth into the instance's `mods/` folder. This takes a few minutes the first time.
If any mod is only on CurseForge, a window pops up and offers to open the download pages. Drop those files into the `mods/` folder (Prism: right-click the instance → **Folder**), then launch again.

After launching, read `minecraft/tt-sync/sync-report.txt` in the instance folder. What to test: [docs/06-testing-guide.md](docs/06-testing-guide.md).

## Repository map
| Path | What |
|---|---|
| `docs/` | Design and decisions: kickoff, mod research, toolchain, integration strategy, combat and skills, testing |
| `design/weapons/` | Weapon roster (`ROSTER.md`) and data (`weapons.json`) |
| `design/npcs/`, `design/skills/`, `design/bridge/` | NPC dialogue scripts, custom skill-tree design, tt_bridge mod spec |
| `pack/` | The instance's `minecraft/` folder: KubeJS scripts and assets, Origins/Fates datapack, FTB Quests, ModSync |
| `prism/` | Prism instance files |
| `tools/` | Generators: `build_content.py`, `gen_quests.py`, `build_prism.py` (rebuilds the zip) |
| `manifest/` | Mod manifest and research status |

Rebuild after changes: `python3 tools/build_prism.py`
