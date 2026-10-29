# 3D model map for the 23 weapons (draft, 2026-10-28)

> **Decision (2026-10-28): we build our own models.** The Fantasy pack can't be loaded on Forge, so `tools/gen_models.py` generates our own 3D models and animated textures in the colours and styles picked below (see `blockbench/previews/_sheet.png`). The karambits keep the Karambit Vault x Punchy parents.

Owner's direction (2026-10-28): the weapons keep their powers, but look like the 3D resource-pack weapons, **built into each item** (no anvil renaming). Items are still obtained through the story, crafting and quests.

## How each pack can be used
| Pack | License | Usable on Forge 1.20.1? | How |
|---|---|---|---|
| Karambit Vault x Punchy 2.2.1 (Modrinth `karambits`) | All Rights Reserved | ✅ Its models live at `minecraft:item/<tier>_sword` and `minecraft:item/skins/<name>`, so they're normal models | `model_parent` in `weapons.json`. The player enables the pack, and nothing is copied. Side effect: every vanilla sword also becomes a karambit |
| Fantasy 3D Weapons CIT (nongko) 1.20B | All Rights Reserved | ❌ Its 84 models are only under `assets/minecraft/optifine/cit/`, which Forge's model loader never reads, and a parent path can't reach them | Needs the author's permission to copy the models into our pack, or a local-only conversion. See the decision in the project thread. Its 17 animated textures work on Forge; its `_e` emissive layers are OptiFine-only |

## Proposed picks
Picks are based on family, shape and the dominant texture colours measured from each pack (first frame). Every pick should be checked in-game.

| # | Weapon | Pack | Model | Why |
|---|---|---|---|---|
| 1 | Frontier Cleaver | Fantasy | iron_broadsword | Plain and crude, which suits tier 1 |
| 2 | Rustbite Karambit | Karambit Vault | item/iron_sword | Steel grey #829396 (wired) |
| 3 | Ashfang Karambit | Karambit Vault | item/skins/magma | Dark with ember #E66410 (wired) |
| 4 | Accord Longsword | Fantasy | grand_claymore | Steel with a brass guard (#C89858) |
| 5 | Gnawblade | Fantasy | iron_dagger | Short and plain |
| 6 | Rootstring Bow | — | none (no bows in either pack) | Own Blockbench model |
| 7 | Thornwatch Halberd | Fantasy | iron_halberd | Halberd shape, bronze-wood shaft |
| 8 | Cogwright Breaker | Fantasy | gilded_phoenix_greataxe | Copper and gold (#C08058, #E8C868) |
| 9 | Prism Ward Staff | Fantasy | opaline_lance | Pale gold with an arcane blue-violet (#6848E0) |
| 10 | Hollowbane Tachi | Fantasy | gloomsteel_katana | Black with violet tones, katana |
| 11 | Cinder Crown | Fantasy | vaelith | Red and black, animated flame, large |
| 12 | Frostmaw Fang | Karambit Vault | item/diamond_sword | Icy teal #32C2BD (wired) |
| 13 | Wroughtnaut Bulwark | Fantasy | black_iron_greataxe | Dark iron with rust tones |
| 14 | Skyreach Spear | Fantasy | heavenly_partisan | Gold partisan |
| 15 | Hydra's Tri-Edge | Fantasy | sacrificial_cleaver | Venom green (#B8F848, #88E010) |
| 16 | Undergloom Scythe | Fantasy | windreaper | Dark teal scythe |
| 17 | Sculkheart Dagger | Fantasy | azure_dagger | Cyan, animated |
| 18 | Choirbreaker Gauntlets | — | none (no fist weapons) | Own Blockbench model |
| 19 | Harbinger's Railblade | Fantasy | zenith | Gunmetal with neon green (#10C078) |
| 20 | Abyssal Longbow | — | none | Own Blockbench model |
| 21 | Crownshard Karambits | Karambit Vault | item/golden_sword | Gold #E8D579 (wired) |
| 22 | Thornecutter | Fantasy | nocturne | Void black, emissive |
| 23 | Emberhold Oathblade | Fantasy | winterthorn | White with crimson (#C01020) |

The Blockbench briefs (`blockbench/specs/weapons.md`) still apply to the three weapons with no pack match.
