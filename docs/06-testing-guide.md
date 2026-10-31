# Testing guide: Test Build 1 (Prism)

Replaces the CurseForge-app instructions in docs/05. The mod stages and checklist in docs/05 still apply.

## Import (recommended: ModSync / Modrinth)
Prism → **Add Instance** → **Import** → paste:
`https://github.com/Mavros13/Terrestrial-Tribulations/raw/main/dist/Terrestrial-Tribulations-TestBuild1.zip`

Memory is preset to 8 GB (G1GC). Test Build 2: swap `TestBuild2` for `TestBuild1`. On Launch, ModSync downloads Modrinth jars. CurseForge-only mods are added by hand (step 2 below). **Gods and Heroes was dropped** (2026-10-31): character layers are **Origins Heritage + Fate**; Palladium **FSang18** and **Satsu** stay.

## Import (CurseForge-format zip)
Prism → **Add Instance** → **Import** → paste:
`https://github.com/Mavros13/Terrestrial-Tribulations/raw/main/dist/Terrestrial-Tribulations-TestBuild1-CurseForge.zip`

Prism downloads every mod listed in the CurseForge manifest. Set memory to **8 GB** (Edit → Settings → Java). FSang18 and Satsu are in this zip; Origins Heritage + Fate are the character layers.

## First launch
1. Press **Launch**. With the ModSync instance, Prism shows the pre-launch log: `[TT ModSync] Downloading …` for each mod.
2. ModSync instance only: if a **"manual downloads"** window appears, choose *Stop launch*. These mods are CurseForge-only, so add them from inside Prism: right-click the instance → **Edit** → **Mods** → **Download mods** → **CurseForge** tab. Search each listed name, pick the newest **1.20.1 Forge** file, then **Review and confirm**. If Prism offers extra dependencies, skip any already in the mods folder (ModSync installed them from Modrinth; a second copy can crash the game). Then press Launch again. If Prism says a mod blocks third-party downloads, use the website link in `tt-sync/MANUAL_DOWNLOADS.html` instead.
3. Java: Prism needs **Java 17** for 1.20.1. If it asks, let it auto-download Java 17, or select it in Settings → Java.

## Stages (only if something crashes)
`minecraft/tt-sync/stage.txt` controls which mods load: `A` = core only, `B` = + story and city, `C` = all of Test Build 1 (the default), `D` = Test Build 2 (adds world generation, dimensions, bosses, Create/AE2/Mekanism, magic, accessories, quality of life; see docs/07). Change it to `A`, launch, then `B`, then `C` to find which group breaks. ModSync removes the jars it installed for higher stages automatically.

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

Weapons now have generated 3D models (held in hand) with 32×32 icons; see `docs/08-test-session-2.md` for the session that checks them. Abilities marked "[Prototype]" in tooltips are not active yet.
