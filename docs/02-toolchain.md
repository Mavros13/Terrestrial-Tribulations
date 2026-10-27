# Toolchain: MCreator + Blockbench (v0.3, 2026-10-27)

> **Scope narrowed by docs/03-integration-strategy.md:** content comes from existing mods. MCreator builds only the `tt_bridge` mod, and Blockbench is used for retextures and re-skins. The workflow below still applies, at smaller scale.

## Decision
| Tool | Version | Role |
|---|---|---|
| **MCreator** | 2026.2 (or newer), **Forge 1.20.1** generator | Primary mod-development environment for content: items, weapons, armour, blocks, mobs and bosses, recipes, structures, procedures, GUIs, dimensions |
| **GeckoLib Reborn** (MCreator plugin) | v7.4.2+, supports Forge 1.20.1 in MCreator 2026.2 | Animated entities, armour and items inside MCreator |
| **Blockbench** | latest + **GeckoLib Models & Animations** plugin | Every 3D model and animation (keyframed bones) for mobs, bosses, suits, weapons and NPCs |
| Hand-written Java (custom code inside MCreator, or a small companion mod) | Forge 47.4.x, Java 17 | Systems MCreator's visual editor can't express cleanly: talent-tree UI, server-synced progression, enemy scaling formulas, mythic affixes |

All of these are CANDIDATE until they are installed and a test build launches.

## Workflow
1. **Blockbench:** create a *GeckoLib Animated Model* project. Rig the bones, then animate idle, walk, attack_1..n, telegraph, phase_transition and death. Export `*.geo.json`, `*.animation.json` and a PNG texture. Keep the `.bbmodel` source in `blockbench/models/`.
2. **MCreator:** import the GeckoLib model and animations through the GeckoLib Reborn plugin, then build the entity, item or armour element and wire its animation triggers in procedures.
3. **Commit:** the MCreator workspace (`mcreator/terrestrial_tribulations/`) is plain files and goes in git. Use the `.gitignore` there to exclude `build/`, `.gradle/` and `run/`.
4. **Export:** use MCreator's *Export workspace to mod file* to produce the jar. Then install it into the test instance alongside the other mods in the manifest.

## Split of responsibilities
- **I (Claude, in the cloud) produce:** element specs (stats, recipes, drops and procedures written step by step), animation shot lists with timings, lore and quest text, KubeJS and FTB Quests files, Java custom-code blocks, and textures where feasible. I can also generate starter `.bbmodel` files as JSON. I can't open them in Blockbench to see them, so you must open and check each one before relying on it.
- **You (at home) do:** run MCreator and Blockbench, click through the element setup from my specs, build and launch, and send me the logs.
- **I cannot:** run MCreator, Blockbench or Minecraft from here (they are desktop GUI apps). Nothing counts as working until it has been launched on your PC.

## Rules
- One MCreator workspace for all custom content, with mod ID `terrestrial_tribulations`.
- Element names in lower_snake_case, prefixed by system (`boss_hollow_alpha`, `weapon_riftblade`, `armor_ember_vanguard`).
- Lock an element (*custom code*) only when necessary, and record every locked element in `mcreator/LOCKED_ELEMENTS.md`, because locked elements stop regenerating.
- Animation budget per entity: 40 bones or fewer, 6 or fewer simultaneous particles per attack, 2 or fewer textures at 64×64 to 128×128. That keeps the GTX 1660 Super comfortable.
- Animation naming: `animation.<entity>.<state>` (for example, `animation.hollow_alpha.slam_telegraph`).

## Impact on the plan
- The custom mod `aetherfall-core` becomes the MCreator workspace `terrestrial_tribulations`.
- Superheroes come from **Palladium** and its addons, with no custom hero system. MCreator handles only progression gating around them (recipes, quest unlocks).
- M3 changes from "scaffold the Gradle project" to **"set up the MCreator workspace + Blockbench pipeline, then build one test element end to end."**
