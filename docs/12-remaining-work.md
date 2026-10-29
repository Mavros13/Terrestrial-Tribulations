# What's left: content and performance (2026-10-29)

The owner asked for a list of everything still to build or sort, and for a focus on performance: fast chunk loading, mobs, quests and every GUI should be light, with high, steady FPS. Update this file as items close.

## 1. Content still to develop or sort

### Needs the desktop (only Oscar can do these)
1. **Test session 3** (`docs/11-test-session-3.md`, about 45 min). It covers everything since the morning: karambits, talk quests, shops, Side Paths, pre-generation, weapon skills and the release zip. Most items below are "built but never seen in game".
2. **Weapon looks in game:** check size, hand placement and first-person view for the 19 generated models. Any that look off get hand-tuned in Blockbench (`blockbench/specs/weapons.md`).
3. **Playthrough checks:** one Side Paths tab start to finish, and Chapter 1 on the release zip.

### Built but not yet confirmed in game
- **Weapons:** all 23 abilities, including today's thorn line, flame wave and Ember Hook. The Accord Longsword's Guillotine skill, the bow shots and the dodge/parry abilities are also unconfirmed.
- **Cast animations:** nine `tt:` player animations and the `tt:cast_test` power.
- **Systems:** dimension gates (Ch7 realms, and The End from Ch10), Chunky pre-generation, branding, and Default Options.

### Not built yet
| Item | What it is | Size |
|---|---|---|
| **Gods and Heroes** | The Chapter 7, 8 and 10 hero quests grant its origins. It's All Rights Reserved and Modrinth-only, so it isn't in the CurseForge pack. Players must add it themselves, or those hero rewards need a fallback. | Small to decide. Needs Oscar. |
| **Cast system** (tt_bridge, `design/bridge/cast-system.md`) | Full-body cast animations for spells and powers. Designed, not built (needs MCreator/Java). Optional: everything works without it. | Large. Optional. |
| **Hand-tuned models** | Only for weapons that look wrong after the desktop check. | Per weapon |
| **CurseForge publishing** | Make the pack public: project page, icon (`docs/branding/icon.png`), description. Needs Oscar's account. | Small. Needs Oscar. |

Story quests (Ch1–12 + Side Paths), NPC dialogue, NPC sites (own structures, locked by chapter, `docs/09-story-npcs.md`), shops, boss lore, gates, the skill tree, origins and all 23 weapon models and abilities are written.

## 2. Performance

### Already in the pack
- **Rendering:** Embeddium (Sodium port), ImmediatelyFast, EntityCulling.
- **Memory and loading:** ModernFix, FerriteCore.
- **Server ticking:** Canary (Lithium port).
- **World:** Chunky pre-generates 768 blocks around spawn.
- **Profiling:** Spark.
- **Our own scripts are light:** two server per-tick handlers (one returns at once unless a Gale Vault is active, one runs once a second) and one client tick toggle. Everything else is event-driven.

### Added 2026-10-29 (Forge 1.20.1 builds checked on Modrinth and CurseForge; both mod lists, stage D)
New libraries: Resourceful Config (for Structure Layout Optimizer) and Almanac Lib (for Let Me Despawn). FastSuite uses Placebo, already in. AllTheLeaks is CurseForge-only. **Noisium was dropped**: archived on CurseForge with no files, so it can't go in the CurseForge pack.
| Mod | Helps with | Side |
|---|---|---|
| **Async Locator** | Moves structure searches (Eyes of Ender, explorer maps, dolphins, villager maps) off the main thread. These cause the worst freezes in structure-heavy packs. | Server |
| **Structure Layout Optimizer** | Faster jigsaw structure generation (YUNG's, When Dungeons Arise, CTOV, Dungeons and Taverns), so less chunk-load stutter. | Server |
| **Clumps** | Merges XP orbs. Big win at mob farms, boss deaths and MineColonies. | Both |
| **Let Me Despawn** | Mobs that picked up items still despawn, so mob counts don't creep up over a session. | Server |
| **FastWorkbench / FastFurnace** (FastSuite) | Caches recipe lookups. With Create, Mekanism and many others there are thousands of recipes. Uses Placebo, already in the pack. | Both |
| **AllTheLeaks** | Fixes known memory leaks (world unload, dimension travel), so no slowdown after long sessions. | Both |
| **Dynamic FPS** | Drops to a few FPS when the window is unfocused or minimised: cooler, quieter PC and nothing wasted. | Client |
| **Smooth Boot (Reloaded)** | Lower thread priority during startup, so the PC stays usable while it loads. | Both |

### Settings (no new mods)
- **Done: default video settings for new players**, through Default Options' `config/defaultoptions/options.txt`. It only applies when a player has no `options.txt`, so updates never overwrite anyone's choices.
  - Render distance 10, simulation distance 6.
  - Entity distance 75%, particles Decreased.
  - Clouds Fast, mipmaps 2.
- **Heavy client mods, tuned rather than removed:**
  - Sound Physics Remastered: lower ray count.
  - Wakes Reforged: lower quality.
  - Shaders (Oculus) off by default.
  - FancyMenu and Legendary Tooltips: check their GUI cost with Spark.
- **MineColonies:** cap citizens per colony and use its pathfinding thread setting, since colonies are the biggest steady load.
- **Mob caps:** Champions and Botz Mob Leveling make each mob costlier, so keep vanilla spawn caps (no mod raising them) and check mob counts with Spark.
- **Done: Java arguments.** Recommended G1 settings for 8 GB are in `docs/05-test-build-1-install.md` step 4.

### Measure, don't guess
After the additions, one Spark profile on the desktop covers it:
- spawn on a fresh world
- a running colony
- a boss fight
- flying over new chunks

That shows what's still slow. `/spark profiler --timeout 60` and `/spark tickmonitor` are enough.
