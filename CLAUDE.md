# Terrestrial Tribulations: instructions for Claude sessions

## Where things live
- **GitHub is the single source of truth:** `Mavros13/Terrestrial-Tribulations` (branch `main`). Every pack file, doc and tool lives here. Commit and push all work.
- **The owner's laptop is for research only.** Use its browser (CurseForge, Modrinth, mod wikis) to verify mods, versions, file names, item and entity IDs. **Don't store pack files on the laptop** beyond a temporary clone you delete when done. Write findings into the repo (usually `docs/07-full-mod-list.md`, `pack/tt-sync/mods.json`, or `docs/research/`).
- The owner plays and tests on a **home desktop with Prism Launcher**, importing `dist/Terrestrial-Tribulations-TestBuild1-CurseForge.zip` by its raw GitHub URL (CurseForge-format pack: Prism downloads every mod itself). Prism has **both Modrinth and CurseForge built in** (Edit instance → Mods → Download mods), so CurseForge-only mods are added from inside Prism, not by visiting the website.

## Decisions already made (don't re-litigate)
- **Minecraft 1.20.1, Forge 47.4.x (never 47.2.0), Java 17.** Chosen for Palladium.
- **Use existing mods and adapt them to the story.** Don't create custom mobs, bosses, NPCs, suits or heroes. Exception: the owner asked for **custom weapons as new items** (`design/weapons/`, implemented with KubeJS + Epic Fight data + Blockbench models).
- **Superheroes: existing Palladium packs only** (FSang18's Heropack, Satsu Iron Man Addon, Gods and Heroes (Palladium edition)), wired into the story with gates and lore (`design/story/heroes-integration.md`).
- Combat: Epic Fight (+ Impactful, NeonSword). Talents: **Passive Skill Tree** (not Pufferfish). Origins (Forge) with Heritage + Fate layers.
- Capital city: MineColonies (Town Hall level = city stage) + Easy NPC for story characters.
- Quarry, power and pipes: Mekanism (Digital Miner). Every weapon has a unique colour scheme and a unique ability.
- **Quest book: don't expand it until the mod list is final** (owner's instruction). It has 17 quests now.
- Tools: MCreator only for the small `tt_bridge` mod (`design/bridge/`); Blockbench for weapon models (briefs and pipeline: `blockbench/specs/weapons.md`; drop exports in `blockbench/exports/weapons/` and the build installs them).

## How the repo works
- `tools/build_prism.py` regenerates everything and builds `dist/…TestBuild1.zip`. It runs `build_content.py` (weapons from `design/weapons/weapons.json`), `gen_quests.py`, `gen_origins.py` and `gen_skilltree.py`. **Edit the generators or their data, never the generated files.**
- **Two mod lists, keep them in step:** `modpack/curseforge-mods.json` (CurseForge project + file IDs, every library listed explicitly, used by `tools/build_curseforge.py` for the main CurseForge-format zips) and `pack/tt-sync/mods.json` (Modrinth, for the fallback ModSync instance). When a mod is added or changed, update both.
- `pack/` is the instance's `minecraft/` folder. `pack/tt-sync/ModSync` downloads mods from Modrinth at launch, based on `pack/tt-sync/mods.json`. Stages: A/B/C = Test Build 1, D = Test Build 2.
- Formats were checked against each mod's source on GitHub (see the docstrings in the tools). Keep doing that, or verify on the official pages from the laptop.

## Current status (2026-10-27, after the availability check)
- Test Build 1 is built but **not yet tested in-game**.
- Done: every `mods.json` entry checked on Modrinth and CurseForge (`docs/research/2026-10-27-mod-availability.md`). 74 auto-download; 19 are CurseForge-only (11 in Test Build 1). Slugs fixed; Gods and Heroes now points at the **Palladium edition**; ModSync gained `skip_dependencies` to block the Fabric Origins it would otherwise pull in. End overhaul decided: **Nullscape + YUNG's Better End Island**. Afterswing dropped (no 1.20.1 Forge build).
- The cloud container can't reach Modrinth or CurseForge with curl; research goes through web fetches. The laptop's sandbox has no network either, so its browser (computer use) is the only on-laptop route. Nothing pack-related is stored on the laptop.
- Epic Fight data checked against its 1.20.1 source (`docs/research/2026-10-27-epic-fight-data-formats.md`): trails now go in `assets/tt/item_skins/`; EDP weapons use the family's built-in innate skill plus a KubeJS rider until custom skills are written with the **EDP add-on** (added at stage D with SL Library, SLM: Epic Fight, SLM: Shader).
- After the owner's first launch: fill `pack/kubejs/config/tt_story_gates.json` from `kubejs/exported/tt_item_namespaces.json`, and read the Gods and Heroes origin layer IDs.
