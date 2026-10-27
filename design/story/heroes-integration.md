# Superheroes in the story: existing Palladium packs only

**Rule (owner, 2026-10-27): no custom suits or heroes.** We use existing Palladium addon packs as they are, and connect them to the story with quests, lore, recipe and stage gates, NPC dialogue and villain encounters.

## Packs (1.20.1 Forge, Palladium 4.5.9)
| Pack | Why | Status |
|---|---|---|
| **FSang18's Heropack** | Largest 1.20.1 roster (174k downloads), many heroes and weapons | 🔎 12.5.7 (Oct 2026, after Palladium 4.5.9); needs PantheonSent, KubeJS, Pehkui, Packet Fixer (auto-downloaded) |
| **Satsu Iron Man Addon** | Real progression built in: arc reactor → blueprint holder (unlock suits with XP) → Mark suits with charging and upgrades | 🔎 3.x (tested with Palladium 4.5.9) |
| **Gods and Heroes (Palladium edition)**, by GC-Morak | Speedster, Kryptonian and Jumper power sets (also Engineer, Mage, Builder, Size Shifter, Iron Mage) | 🔎 1.4 (Apr 2025), needs a launch test. ⚠️ It gives its powers as **origins** (it needs Origins Forge), not suits. Note: the Modrinth slug `gods-and-heroes` is a different, Origins-only addon |
| Vector HUD + Satsu compat | Optional: suit HUD | 🔎 |

Their exact item IDs and namespaces get filled in after the first launch, from `kubejs/exported/tt_item_namespaces.json` (written by `tt_story_gates.js`).

## How they fit the lore
| In the pack | In Velmora |
|---|---|
| Satsu's **arc reactor** | An **Old Engine heart**: Tinker-King power cores found in Cogwright ruins. Pell learns to rekindle them |
| Satsu's **Mark suits** | **Engine-plate**: the armour of the Tinker-Kings' honour guard, rebuilt Mark by Mark |
| Satsu suits worn by enemies | **The Iron Choir**: a cult that looted Old Engine plate before you did |
| FSang18 heroes | **Echoes**: champions of other realms whose legends cling to Crown Shards. Each hero item is an "echo" you recover in a dimension |
| Gods and Heroes power sets | **Shard-Born awakenings**: speed, strength and leaping that your Crown Shards unlock in you |

## Progression gates (KubeJS stage + quest)
| Stage | Granted by | Unlocks |
|---|---|---|
| `tt_ch8_heroes` | Ch8 opening quest: "The Engine Heart" (bring Pell an Old Engine core) | Wearing or using any gated hero item (`tt_story_gates.json`) |
| `tt_ch9_marks` | Ch9: defeat the first Iron Choir Herald | Higher Satsu Marks. The pack's own XP blueprint costs stay as an extra gate |
| `tt_ch10_echoes` | Ch10 Mythic Crucible tier I | FSang18 top-tier heroes |
| Gods and Heroes awakenings | One per Crown Shard collected (Ch7+) | Speedster → Jumper → Kryptonian, in that order. Because they're origins, hide the pack's layer at character creation and grant each one by command (`/origin set`) from the Crown Shard quest. Layer and origin IDs come from the first launch |

Recipes: the pack recipes for top-tier items get **story materials** added by KubeJS (boss drops: Harbinger core, Leviathan scale, Crown Shard Fragment), so the strongest suits can't be built early. They're also gated by the stage.

## Villains (existing content, re-themed)
- **Iron Choir footsoldiers:** Easy NPC hostile NPCs, or MineColonies raiders, wearing Satsu Mark suits (visual), with Champions affixes for their mechanics.
- **Choir Heralds (Ch9):** L_Ender's Cataclysm's **The Harbinger**, renamed in lore as the Choir's war-machine. Its drop feeds the Mark upgrades.
- **Ch8 rival:** a duel against an Iron Choir prototype (a Cataclysm Netherite Monstrosity encounter in a Cogwright ruin).

## Still to do after the first launch
1. Read `tt_item_namespaces.json`, then fill `namespaces`/`items` in `kubejs/config/tt_story_gates.json`.
2. Look up item IDs with `/kubejs dump_registry minecraft:item` and write the recipe additions.
3. Write the Ch8–Ch10 hero quests (once the quest book work starts).
