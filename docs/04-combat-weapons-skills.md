# Combat feel, custom weapons, Origins and Passive Skill Tree (v0.5, 2026-10-27)

Owner decisions on 2026-10-27: keep Epic Fight; add sword trails and Afterswing; add Karambit Vault x Punchy; build **new** weapons (not retextures) through existing mods; Origins is in; **Passive Skill Tree replaces Pufferfish's Skills**.

## 1. Combat visuals stack (1.20.1 Forge)
| Mod | Role | Status / notes |
|---|---|---|
| Epic Fight 20.14.x | Animations, movesets, lock-on, skills | CANDIDATE |
| **NEpicloob NeonSword** | Glowing Epic Fight swing trails | CANDIDATE. Page lists Epic Fight 20.9/20.11 compatibility, so **check it against 20.14**. Not OptiFine-compatible (we use Oculus) |
| **Afterswing** (paperdev_) | Swing trails, hit and critical sparks, draw-weapon flourish; works with Epic Fight | ⚠️ **Listed for Fabric and NeoForge only (latest file 1.21.1 NeoForge, Oct 2026). I could not find a Forge 1.20.1 file.** Check its Files tab at home. If there is none: use Epic Fight - Impactful + NeonSword instead, or ask the author about a 1.20.1 Forge build |
| Epic Fight - Impactful | Hit stop and screen shake | CANDIDATE |
| CompatLink - Epic Fight Weapons Compat | Gives modded weapons Epic Fight movesets and trails | CANDIDATE (needs Epic Fight 20.14.17+) |
| Epic Fight EDP (Extended Datapacks) | Data-driven innate skills, animation events and weapon categories | ✅ 2.5.5 for 1.20.1 Forge, added at stage D (docs/research/2026-10-27-epic-fight-data-formats.md) |
| **Karambit Vault x Punchy** | 3D karambit models, inspect animations, sounds | ⚠️ It is a **resource pack that replaces sword visuals**, not a weapon mod. Its "Punchy" animations target the **Punchy mod, which is Fabric-only**, and renamable variants need **CIT Resewn (Fabric)**. On Forge we keep its 3D models but lose Punchy's first-person animations unless a Forge equivalent is found. Reusing its models on *our own* new karambit items needs the author's permission. See §2 |

## 2. Weapons
**Clarified by the owner (2026-10-27): only karambits are new weapons.** Every other weapon comes from existing mods (Simply Swords, Soulslike Weaponry, boss drops, Iron's Spells and so on). Those are re-themed with KubeJS (names, lore, stat tweaks, recipe and story gates) and Epic Fight movesets, not re-registered.

The karambit family is the exception: each karambit is a **new registered item** with its own ID, stats, moveset and ability:

| Layer | Provided by |
|---|---|
| Item registration (ID, tier, damage, speed, durability, rarity) | **KubeJS** `StartupEvents.registry('item')` |
| 3D model + texture | **Blockbench** (our own), exported as item models in the KubeJS assets folder |
| Moveset, trail and hitbox | Epic Fight weapon capability datapack (weapon category: dagger, sword, longsword, greatsword, spear, tachi and so on) |
| Innate or active ability | Epic Fight EDP innate skills (JSON) + KubeJS events for effects that EDP can't express |
| Story hook | FTB Quests reward or unlock + KubeJS recipe gate + lore tooltip |

**Karambits:** add a "Karambit" weapon family (dagger moveset: fast combos, short reach, high crits) as new items. Visuals: either license or recreate the Karambit Vault look in Blockbench. Spec format (karambits only): `design/weapons/_TEMPLATE.md`, first example: `design/weapons/ashfang_karambit.md`.

## 3. Origins (+ Fates)
- **Origins (Forge) 1.10.0.9** for 1.20.1: works but is **archived** (no more updates). Known issue: **do not use Forge 47.2.0**. Accept the risk and pin a working Forge build in M1.
- Two Origins *layers*: **Origin** (race and heritage: our lore races) and **Fate** (the 10 classes). Both are data-driven Origins datapacks, so no coding is needed.

## 4. Passive Skill Tree (Daripher) replaces Pufferfish's Skills
- A Path of Exile–style tree GUI, with skill points earned from **experience**, as the owner requested.
- **PassiveSTJS** (KubeJS addon, 1.20.1-0.2.2, May 2026; tested on Forge 47.4.18 + KubeJS 2001.6.5) lets us **script new skills and trees** instead of hand-writing JSON.
- Planned additions to the stock tree:
  - **Story skills:** Shard-Born keystones unlocked by chapter flags (for example, *Shardsense* after Ch4, *Convergent* after Ch10).
  - **Fate clusters:** a starting cluster per Fate, linked to the Origins Fate layer.
  - **Quality-of-life skills:** extra reach, faster crop growth near the player, magnet pickup, reduced hunger drain, backpack slot upgrade, cheaper repair, night vision in caves.
  - **The ~100 stat nodes and 16 passives** from the kickoff, rebuilt as PST nodes.

## 5. Manifest changes
Added: NeonSword, Afterswing (⚠️ loader check), Epic Fight - Impactful, CompatLink, Epic Fight EDP, Karambit Vault x Punchy (resource pack), Passive Skill Tree, PassiveSTJS, Origins (Forge).
Removed: Pufferfish's Skills and Attributes.
