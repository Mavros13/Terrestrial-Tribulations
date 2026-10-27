# Testing guide: Test Build 1 (Prism)

Replaces the CurseForge-app instructions in docs/05. The mod stages and checklist in docs/05 still apply.

## Import
See the README: Prism → Add Instance → Import → paste the zip URL. Memory is preset to 8 GB, with G1GC flags.

## First launch
1. Press **Launch**. Prism shows the pre-launch log: `[TT ModSync] Downloading …` for each mod.
2. If a **"manual downloads"** window appears: choose *Open download pages + stop launch*, download each listed mod's newest **1.20.1 Forge** file into the `mods` folder that opens, then press Launch again.
3. Java: Prism needs **Java 17** for 1.20.1. If it asks, let it auto-download Java 17, or select it in Settings → Java.

## Stages (only if something crashes)
`minecraft/tt-sync/stage.txt` controls which mods load: `A` = core only, `B` = + story and city, `C` = everything (the default). Change it to `A`, launch, then `B`, then `C` to find which group breaks. ModSync removes the jars it installed for higher stages automatically.

## What our own content should show
| Check | Expected |
|---|---|
| JEI search `@kubejs` or `tt:` | 23 weapons + 4 materials, each with its own coloured icon |
| Hover a weapon | Tier and rarity line, gold ability name, description, lore, chapter line |
| Rustbite Karambit stats | **6 attack damage, 1.8 attack speed** (iron sword: 6 / 1.6) |
| Craft the Frontier Cleaver / Rustbite Karambit | Recipes in JEI work |
| Epic Fight battle mode with a karambit | Dagger moveset; greatswords use the greatsword moveset |
| Frostmaw Fang: hit a mob 5 times | Mob freezes (Slowness) and takes extra damage |
| Hydra's Tri-Edge: 3 hits in a row | Extra damage + poison |
| New world | Origins asks for **Heritage** (incl. Ashborn, Verdant Kin, Cogkin, Skyborn) and then **Fate** (9 Fates) |
| Quest book | Chapters: *Welcome to Velmora*, *Chapter 1: The Broken Frontier*, *Combat Fundamentals* |

## Send back
`logs/latest.log` (or the crash report), `tt-sync/sync-report.txt` and `tt-sync/lock.json` (the exact mod versions that were downloaded). Upload them to https://mclo.gs or paste them in chat. Note anything that looks wrong.

Known placeholders: textures are 16×16 stand-ins until the Blockbench models exist. Abilities marked "[Prototype]" in tooltips are not active yet.
