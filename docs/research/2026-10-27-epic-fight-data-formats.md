# Epic Fight data formats for our 23 weapons (2026-10-27)

**Question:** can our custom `tt:` weapons get their moveset, swing trail and innate skill from data alone? This checks what `tools/build_content.py` writes against Epic Fight's own source code.

**Sources:**
- Epic Fight's GitHub repo, branch `1.20.1` at 20.15.1 (Oct 26, 2026). The relevant files are unchanged since tag 20.14.15.1, so they also cover our pinned 20.14.17.
- The Epic Fight EDP wiki (`Sleys-g/ExtendedDatapacks`).
- CurseForge file pages.

## 1. Weapon capability: correct as generated
- **File:** `data/<item namespace>/capabilities/weapons/<item path>.json`, read by `ItemCapabilityReloadListener`. Ours is `data/tt/capabilities/weapons/<id>.json`, which is right.
- **Keys read:**
  - `type`: a preset such as `epicfight:sword`, or a custom type.
  - `attributes`: a style name (`common`, `one_hand`, `two_hand`, …) mapping to `armor_negation`, `impact`, `max_strikes`, `damage_bonus` or `speed_bonus`.
  - `collider` and `custom_tags`.
  - `variations`, for conditional capabilities.
- **Unknown keys are silently ignored.** The `_tt_trail_color` key we wrote did nothing, so it has been removed.
- **Presets on 1.20.1:** axe, fist, hoe, pickaxe, shovel, sword, spear, greatsword, uchigatana, tachi, longsword, dagger, bow, crossbow, trident and shield. Every `ef` value in `weapons.json` maps to one of these.

## 2. Swing trails: moved to item skins (fixed)
- **Where they live:** trails are a **client resource**, not data: `assets/<ns>/item_skins/<item>.json` (`ItemSkinsReloadListener` → `RenderItemBase`).
- **Format:**
  ```json
  {"trail": {"color": [r,g,b], "begin_pos": [x,y,z], "end_pos": [x,y,z], "lifetime": 4, "interpolations": 5,
             "texture_path": "epicfight:textures/particle/swing_trail.png", "particle_type": "epicfight:swing_trail",
             "block_light": 15, "sky_light": 15}}
  ```
  - Colours are 0–255.
  - Positions are in blocks along the `Tool_R` joint, with −Z running down the blade.
- **What the build now writes:** `assets/tt/item_skins/<id>.json` for all 21 melee weapons, in each weapon's registry trail colour.
  - Begin and end positions are copied from Epic Fight's own skins for the same preset (`iron_sword`, `iron_dagger`, `iron_longsword`, `iron_tachi`, `iron_greatsword`, `iron_spear`, `iron_axe`).
  - The fist position is a guess, because Epic Fight's glove has no trail.
  - Elite (tier 5) and stronger weapons get full-brightness trails.
- **Fitted to the 3D models (2026-10-28):** `build_content.py` (`model_trail`) now sets each melee weapon's begin/end Z from its model: the bottom of the striking part to the tip, converted to blocks with the model's third-person scale and a factor calibrated on the vanilla sword (whose sprite matches Epic Fight's `iron_sword` trail). Results sit close to the presets (longsword end −1.45 vs −1.5, spear −2.17 vs −2.0), which is a good sign; still to be checked in-game.

## 3. Innate skills: base Epic Fight can only *choose*, not *create*
- **Built-in skills only.** Skills are a code-registered Forge registry. Data can assign a registered innate skill per style, but only inside a **custom weapon type** (`data/<ns>/capabilities/weapons/types/<name>.json`, key `innate_skills`). A per-item capability file cannot. `skill_parameters/` data retunes a skill globally, for every weapon that uses it.
- **Built-in innate skills on 1.20.1:**
  - sweeping_edge, dancing_edge
  - the_guillotine, grasping_spire, heartpiercer
  - steel_whirlwind, battojutsu, rushing_tempo
  - relentless_combo, sharp_stab, liechtenauer
  - eviscerate, blade_rush, wrathful_lighting
  - tsunami, everlasting_allegiance
- **Every hit an innate skill deals carries the runtime damage tag `epicfight:weapon_innate`** (`EpicFightDamageSource.is`). KubeJS can test for it, which gives us a "rider": the family's built-in skill does the motion, and KubeJS adds our effect to its hits.
- **Riders added to `pack/kubejs/server_scripts/tt_abilities.js`** (untested):

| Weapon | Built-in skill used | KubeJS rider | Still needs EDP or tt_bridge |
|---|---|---|---|
| Ashfang Karambit | Eviscerate | Fire 3 s, then the next hit within 2 s does +50% | Hooking behind the target (EDP `teleport` TARGET_BEHIND) |
| Accord Longsword | Sharp Stab / Liechtenauer | Strength I + Resistance I 6 s to you, players and your tamed animals within 8 blocks | MineColonies guards as allies |
| Thornwatch Halberd | Heartpiercer / Grasping Spire | Slowness II 5 s + 2 damage/s for 5 s | The thorn line left on the ground |
| Hollowbane Tachi | Rushing Tempo | Strips invisibility; double damage to entities listed in `TT_HOLLOWED` (empty for now) | The list of "Hollowed" mobs |
| Cinder Crown | Steel Whirlwind | Every enemy hit burns 5 s | The 10-block flame line |

- **Skill charge, not cooldowns.** Innate skills in Epic Fight fill a charge gauge by landing hits, so the roster's "12 s cooldown" figures become gauge costs when the EDP skills are written.
- **Reversal Cut (Rustbite) and Iron Recoil (Wroughtnaut) move to tt_bridge.** They trigger on a successful dodge or parry. Epic Fight reports those only through its internal player-event listener (`DODGE_SUCCESS_EVENT`), which neither data nor KubeJS can reach. `weapons.json`, the roster and `design/bridge/tt_bridge-spec.md` are updated.

## 4. The EDP add-on: custom innate skills from JSON (added at stage D)
**Epic Fight - EDP (Extended Datapacks)** by Sleys is CurseForge-only, with no Modrinth copy.
- **1.20.1 Forge file:** `EF-ExtendedDatapacks-2.5.5-1.20.1+[Forge].jar` (project 1309609, file 9121028, Oct 10, 2026).
- **Required libraries:** all listed in both mod lists, at stage D.
  - SL Library 1.7 (1497274 / 9121010)
  - SLM: Epic Fight 1.4 (1499933 / 9120966)
  - SLM: Shader 3.0.1 (1497920 / 9202391); Oculus is optional.

What its wiki documents (v2.4.6+):
- **New named innate skills** (simple, combo, sequential, conditional, holdable and charged). Each one is any existing animation plus damage multiplier, armour negation, impact, stun type, sounds and hit particle.
- **Where skill files go:** in a modpack, `config/epicfight_edp/innate_skill_builder/<kind>/*.json`, with a `modid` field set. A weapon type then names the skill under `innate_skills`.
- **Animation events:** `teleport` (including behind the target), `command_payload` (runs a command as the caster), `invulnerability`, laser damage along a line or at a target, chaining animations, and particles and trails.
- **Also:** weapon categories, per-style weapon models, advanced swing trails, and guard-skill category mapping.

What this could move off tt_bridge, to be confirmed when the skills are written:

| Weapon | Ability | EDP route |
|---|---|---|
| Ashfang Karambit | Ember Hook | `teleport` TARGET_BEHIND, then a slash |
| Harbinger's Railblade | Rail Lance | `laser_line_world_damage` |
| Crownshard Karambits | Shard Rend | `teleport` per target + `invulnerability` |
| Skyreach Spear | Gale Vault | `teleport` WORLD +Y, then a plunging attack |
| Cinder Crown / Thornwatch Halberd | Flame and thorn lines | `command_payload` placing short-lived blocks or effects |

**Why stage D and not Test Build 1:**
- Test Build 1 hasn't been launched yet, and four new mods would add risk.
- None of our EDP skill files exist yet.
- EDP doesn't state a minimum Epic Fight version, so confirm 2.5.5 loads with Epic Fight 20.14.17 in Test Build 2. If it doesn't, move Epic Fight to the newest 20.15.x in both lists.

## 5. Decision (2026-10-29): built-in skills + KubeJS, no EDP skill files
Checked against Epic Fight's 1.20.1 source before writing the EDP skills:
- **EDP simple innate skills would change other weapons.** A simple innate skill is "an existing animation plus properties", and Epic Fight's `SimpleWeaponInnateSkill.registerPropertiesToAnimation` writes those properties onto the animation's phases. Animations are shared: every skill animation already belongs to a built-in skill, and the unused attack animations are the ones Epic Fight's mobs swing. So a `tt:` skill on `eviscerate_first` would retune Eviscerate on every dagger in the pack, and one on `mob_longsword1` would buff every zombie with a sword. EDP's wiki says virtual animations can't be used for skills, and its animation registry needs our own animation files. EDP's source isn't public and its jar can't be fetched from the container, so EDP can't be checked to work differently.
- **Hits from EDP skills may also lose the `epicfight:weapon_innate` tag.** Epic Fight's built-in skills add it themselves (`EpicFightSkills`: `SOURCE_TAG` = `WEAPON_INNATE`), and EDP's skill fields have no source-tag option, so our KubeJS riders could stop seeing the hits.
- **What we did instead** (`impl: "INNATE"` in `weapons.json`):
  - Each of the 5 weapons keeps a built-in innate skill, and the whole ability is now in `server_scripts/tt_abilities.js`, using the same tools as the active abilities:
    - Ember Hook (Eviscerate): the first skill hit moves you behind the target.
    - Briar Line (Grasping Spire / Heartpiercer): a real 6-block thorn line on the ground for 5 s.
    - Flame Wake (Steel Whirlwind): a 10-block flame wave along your facing.
    - Rallying Strike and Soul Severance: unchanged.
  - A weapon can name a different built-in skill with an `innate` field. `build_content.py` then writes a **custom weapon type** (`data/tt/capabilities/weapons/types/<id>.json`, `WeaponTypeReloadListener`): a copy of the family's preset (combos, motions, collider, styles; animation IDs from `Animations.java`) with `innate_skills` swapped. The capability file points at `tt:<id>`.
    - Used once: the **Accord Longsword gets The Guillotine** (an overhead leap-strike, matching "overhead strike"), and Sharp Stab with a shield.
    - Data types can't set a preset's extra reach (spear, greatsword) or code-only style switches. So only families without those get templates (`TYPE_TEMPLATES`).
    - Battojutsu was rejected for the tachi: `BattojutsuSkill` reads the sheath flag from the weapon-passive slot, which a tachi doesn't fill.
- EDP stays in the pack at stage D, for animation events and visuals later.

## Still unverified (needs a launch)
- The Accord Longsword's custom type loads (selftest `epic_fight_weapons` fails for it if the type is missing) and The Guillotine plays with the longsword moveset otherwise unchanged.
- The ground lines and the hook teleport in `tt_abilities.js` (`ttGroundLine`, Ember Hook).
- The KubeJS calls in the riders: `Java.loadClass` of `TagKey`, `Registries`, `ResourceLocation` and `MobEffects`, plus `event.source.is(TagKey)` on Epic Fight's damage source.
- Whether a multi-hit innate skill fires the rider once per hit. The Rallying Strike rider has a 1 s guard for that.
- That the item-skin trail positions look right on our placeholder (flat) items. Epic Fight draws the trail from the joint, not the model, so it should.
