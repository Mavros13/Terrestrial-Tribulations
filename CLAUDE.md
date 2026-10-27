# Terrestrial Tribulations: instructions for Claude sessions

## Where things live
- **GitHub is the single source of truth:** `Mavros13/Terrestrial-Tribulations` (branch `main`). Every pack file, doc and tool lives here. Commit and push all work.
- **The owner's laptop is for research only.** Use its browser (CurseForge, Modrinth, mod wikis) to verify mods, versions, file names, item and entity IDs. **Don't store pack files on the laptop** beyond a temporary clone you delete when done. Write findings into the repo (usually `docs/07-full-mod-list.md`, `pack/tt-sync/mods.json`, or `docs/research/`).
- The owner plays and tests on a **home desktop with Prism Launcher**, importing `dist/Terrestrial-Tribulations-TestBuild1.zip` by its raw GitHub URL.

## Decisions already made (don't re-litigate)
- **Minecraft 1.20.1, Forge 47.4.x (never 47.2.0), Java 17.** Chosen for Palladium.
- **Use existing mods and adapt them to the story.** Don't create custom mobs, bosses, NPCs, suits or heroes. Exception: the owner asked for **custom weapons as new items** (`design/weapons/`, implemented with KubeJS + Epic Fight data + Blockbench models).
- **Superheroes: existing Palladium packs only** (FSang18's Heropack, Satsu Iron Man Addon, Gods and Heroes), wired into the story with gates and lore (`design/story/heroes-integration.md`).
- Combat: Epic Fight (+ Impactful, NeonSword). Talents: **Passive Skill Tree** (not Pufferfish). Origins (Forge) with Heritage + Fate layers.
- Capital city: MineColonies (Town Hall level = city stage) + Easy NPC for story characters.
- Quarry, power and pipes: Mekanism (Digital Miner). Every weapon has a unique colour scheme and a unique ability.
- **Quest book: don't expand it until the mod list is final** (owner's instruction). It has 17 quests now.
- Tools: MCreator only for the small `tt_bridge` mod (`design/bridge/`); Blockbench for weapon models.

## How the repo works
- `tools/build_prism.py` regenerates everything and builds `dist/…TestBuild1.zip`. It runs `build_content.py` (weapons from `design/weapons/weapons.json`), `gen_quests.py`, `gen_origins.py` and `gen_skilltree.py`. **Edit the generators or their data, never the generated files.**
- `pack/` is the instance's `minecraft/` folder. `pack/tt-sync/ModSync` downloads mods from Modrinth at launch, based on `pack/tt-sync/mods.json`. Stages: A/B/C = Test Build 1, D = Test Build 2.
- Formats were checked against each mod's source on GitHub (see the docstrings in the tools). Keep doing that, or verify on the official pages from the laptop.

## Current status (2026-10-27)
- Test Build 1 is built but **not yet tested in-game**.
- Next research tasks (good for the laptop browser):
  1. Confirm Modrinth slugs / CurseForge availability for every `mods.json` entry; mark which are CurseForge-only.
  2. Check that FSang18's Heropack, Satsu Iron Man Addon and Gods and Heroes have 1.20.1 Forge files compatible with Palladium 4.5.9.
  3. Check whether Afterswing, Leaves Be Gone, BetterEnd (Forge port) and NeonSword (with Epic Fight 20.14) work on 1.20.1 Forge.
  4. Decide the End overhaul.
- After the owner's first launch: fill `pack/kubejs/config/tt_story_gates.json` from `kubejs/exported/tt_item_namespaces.json`.
