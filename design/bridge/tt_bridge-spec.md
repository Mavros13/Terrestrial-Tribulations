# tt_bridge: MCreator mod spec (Forge 1.20.1)

A small MCreator workspace (`mcreator/terrestrial_tribulations`, mod ID `tt_bridge`) that does only what KubeJS, datapacks and configs can't.

## 1. Story flags (core)
- Per-player persistent flags (`tt_bridge:flags` capability, or player persistent NBT): `ch1_done`, `ch2_done`, … plus boss flags (`boss_ignis`, `boss_frostmaw`, …).
- Commands: `/tt flag set <player> <flag>`, `/tt flag check`. FTB Quests rewards call these as *command rewards*.
- Every flag is also mirrored to a KubeJS player stage, so KubeJS scripts can read it.

## 2. Weapon abilities marked BRIDGE in weapons.json
| Weapon | Ability | MCreator approach |
|---|---|---|
| Cogwright Breaker | Pressure Release | Item NBT counter, sneak-attack procedure, AoE knock-up |
| Rootstring Bow | Seedshot | Custom ranged item; arrow-hit procedure places temporary briar blocks |
| Prism Ward Staff | Prism Ward | On spell cast (Iron's Spells event) → reflect-shield effect |
| Skyreach Spear | Gale Vault | Right-click launch (+Y velocity), mid-air attack → dive AoE, cancel fall damage |
| Choirbreaker Gauntlets | Overload Punch | Charged use → EMP AoE: Slowness 255 + Weakness on tagged mobs |
| Harbinger's Railblade | Rail Lance | Charged use → raycast beam with particles, piercing damage |
| Abyssal Longbow | Undertow Arrow | Custom projectile: piercing, pulls hit entities |
| Crownshard Karambits | Shard Rend | Teleport chain between 3 nearest hostiles, damage each, brief invulnerability |
| Thornecutter | Sunder the Regent | Damage multiplier vs `#forge:bosses` by missing health; skill removes one effect |
| Emberhold Oathblade | Oath of the Capital | Reads the MineColonies Town Hall level (MineColonies API), scales damage, heals citizens |

## 3. Cross-mod hooks
- MineColonies Town Hall level → story flag `city_stage_N` (unlocks chapters).
- Boss kills (Cataclysm, Mowzie's, Twilight Forest, …) → boss flags.
- Fate swap to Ascendant (Origins API / command `origin set`).
- Gnawblade Pack Mark → tamed Rats target the marked entity.

## 4. Order of work
Flags + commands → Gale Vault and Rail Lance (they prove the projectile/movement pattern) → the rest of the BRIDGE abilities → cross-mod hooks.
