# Test Build 2: required libraries check (2026-10-28)

A CurseForge-format pack doesn't resolve dependencies, so every required library must be listed in `modpack/curseforge-mods.json` itself. I read the "Relations" page of the exact pinned file on curseforge.com (`/files/<fileID>/dependencies`) for each add-on whose libraries weren't obvious. **Result: every required library is already in the list. Nothing is missing.**

| Mod (pinned file) | Required libraries | In our list |
|---|---|---|
| The Aether (1.20.1-1.5.2-neoforge) | Cumulus and Curios, both **embedded** in the jar | nothing needed |
| Bosses of Mass Destruction (BOMD-Forge 1.1.2) | CERBON's API, Cloth Config API, GeckoLib | ✓ all three |
| Relicera 1.2.5 | Curios API (Twilight Forest optional) | ✓ |
| Botz Mob Leveling 1.0.7 | none | |
| Armor Set Bonuses 20.14.0 | none | |
| Marium's Soulslike Weaponry 1.4.10 | AttributeFix, GeckoLib, Ranged Weapon API | ✓ all three |
| Wakes Reforged 1.4.1 | none (Valkyrien Skies, Nifty Ships optional) | |
| Champions Unofficial 20.1.1.6 | Architectury API (Jade, KubeJS optional) | ✓ |
| Epic Fight EDP 2.5.5 | Epic Fight, SL Library, SLM: Epic Fight, SLM: Shader | ✓ all four |
| Epic Fight Impactful | Epic Fight | ✓ |
| NEpicloob NeonSword | none | |
| Elytra Trims 3.10.0 | Kotlin for Forge (YACL optional) | ✓ |
| Elytra Slot 6.4.4 | Caelus API, Curios API | ✓ |
| Simply Swords 1.70.2 | Architectury API, Fzzy Config, Simply Tooltips (Better Combat optional) | ✓ all three |
| Artifacts 9.5.19 | Architectury API, Cloth Config API, Curios API | ✓ all three |
| Create: Enchantment Industry 2.5.4b | Create, Create: Dragons Plus | ✓ |
| Create: Steam 'n' Rails 1.7.3 | Create | ✓ |
| L_Ender's Cataclysm 3.31 | Curios API, Lionfish API | ✓ |
| Mowzie's Mobs 1.8.2 | GeckoLib | ✓ |
| Alex's Caves 2.0.2 | Citadel | ✓ |
| Blue Skies 1.3.31 | Structure Gel API (Lucent, Music Manager optional) | ✓ |
| Apotheosis 7.4.8 | Apothic Attributes, Patchouli, Placebo | ✓ all three |
| ExtendedAE 1.4.21 | Applied Energistics 2, Glodium, GuideME | ✓ all three |
| FancyMenu 3.9.14 | Konkrete, Melody | ✓ |
| Legendary Tooltips 1.4.5 | Iceberg, Prism Lib | ✓ |
| Ars Nouveau, Rats, The Undergarden, Deeper and Darker, Twilight Forest, Incendium, Nullscape, Goner's Armor Trims | none listed | |

The rest are well-known pairs already covered in the list: Quark needs Zeta, Supplementaries needs Moonlight Lib, Sophisticated Backpacks needs Sophisticated Core, Handcrafted needs Resourceful Lib, AmbientSounds needs CreativeCore, CTOV needs Lithostitched, the YUNG's mods need YUNG's API, and Iron's Spells needs Iron's Lib, playerAnimator, GeckoLib, Curios and Caelus.

## Incompatibilities to keep in mind
- **Apotheosis** marks **Better Combat** as incompatible. We use Epic Fight, not Better Combat, so it doesn't apply, but don't add Better Combat later (Simply Swords offers it as optional).
- **ImmediatelyFast** is pinned to a `+1.20.4` Forge build that the author tags for 1.20–1.20.4. Already noted in `2026-10-27-mod-availability.md`, together with the fallback pin.

## What this does not cover
Libraries can also clash with one another at runtime (mixins, version ranges). Only a launch shows that. Test Build 2 still goes through the A → B → C → D stage bisect in `docs/06-testing-guide.md` if it crashes.

## Server test, 2026-10-28 (laptop, `tools/server_test.ps1` with `TT_STAGES=A,B,C,D`)
118 mods (client-only ones skipped), reached Done after three fixes; our scripts and data load with 0 errors; Core Utilities 2.0.0 loads clean.
- **Sophisticated Backpacks 3.26.17 needs Sophisticated Core 1.5.17+**, which has no 1.20.1 release yet (newest is 1.5.15.2427). Pinned the matching pair: Backpacks 3.26.14.2226 (9271152) + Core 1.5.15.2427 (9279280).
- **SLM: Shader is not client-only**: Epic Fight EDP requires it on the server too.
- **Canary** `entity.collisions.movement` mixin clashes with another stage D mod (startup crash). Disabled in `pack/config/canary.properties`.
- Not ours, not blocking: Palladium logs 131x `PackData.getId() ... packData is null`: harmless. In Palladium 1.20/main `AddonPackManager.beginLoading` logs "Skipping ... not been marked as an addonpack" for every ordinary mod resource pack but has no `return`, so it goes on to call `packData.getId()` and the catch logs the NPE. One line per mod jar with a pack.mcmeta (more mods in stage D, so more lines); real addon packs still load; CoreWithStuff ~44 broken loot tables; tags pointing at absent mods (Ad Astra, tacz, wares); Lootr compat mixins without Lootr; 0-weight spawn entries in some biome data.
- Palladium loads 1081 powers, 44 suit-set powers, 20 item powers, 36 universes; our `tt:` powers parse with 0 errors. **Broken powers in the hero packs** (they parse-fail, so they do nothing; don't build quests or rewards on them): FSang Heroes `energy_weapons`, `iron_man_shield`, `magneto_helmet`, `dark_matter`, the `inhibitor_collar` powers, `fsang_hero:dampened`; Satsu Iron Man item powers `armor_place` and `marks/mark_48/main`.
