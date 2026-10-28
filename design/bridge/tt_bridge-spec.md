# tt_bridge: MCreator mod spec (Forge 1.20.1)

A small MCreator workspace (`mcreator/terrestrial_tribulations`, mod ID `tt_bridge`) that does only what KubeJS, datapacks and configs can't.

## 1. Story flags (core)
- Per-player persistent flags (`tt_bridge:flags` capability, or player persistent NBT): `ch1_done`, `ch2_done`, … plus boss flags (`boss_ignis`, `boss_frostmaw`, …).
- Commands: `/tt flag set <player> <flag>`, `/tt flag check`. FTB Quests rewards call these as *command rewards*.
- Every flag is also mirrored to a KubeJS player stage, so KubeJS scripts can read it.

## 2. Weapon abilities (moved to KubeJS, 2026-10-28)
All 12 abilities first listed here now run in KubeJS (`pack/kubejs/server_scripts/tt_active_abilities.js`, bows in `startup_scripts/tt_bows.js`, Iron's spell hook in `startup_scripts/tt_forge_events.js`). KubeJS reaches Epic Fight's dodge and parry listeners, MineColonies' colony manager and Iron's spell event through their Java APIs, so none of them needs Java. tt_bridge can still upgrade them later (the cast system in section 5 for proper body animation, GeckoLib weapons, a real ground-flame line for Flame Wake and thorn line for Briar Line).

## 3. Cross-mod hooks
- MineColonies Town Hall level → story flag `city_stage_N` (unlocks chapters).
- Boss kills (Cataclysm, Mowzie's, Twilight Forest, …) → boss flags.
- Fate swap to Ascendant (Origins API / command `origin set`).
- Gnawblade Pack Mark → tamed Rats target the marked entity.

## 4. Order of work
Flags + commands → Gale Vault and Rail Lance (they prove the projectile/movement pattern) → the rest of the BRIDGE abilities → cross-mod hooks.

## 5. Cast system
Active abilities share one cast system (windup, release, channel, recovery; data in `data/tt/casts/`; our own player animations, effects and camera shake). Design: `design/bridge/cast-system.md`. Build it together with Rail Lance, the first ability in the order above.
