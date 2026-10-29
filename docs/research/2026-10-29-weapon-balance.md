# Weapon balance sheet (2026-10-29)

All 23 custom weapons from `design/weapons/weapons.json`, by tier. **Damage x speed** is a rough damage-per-second figure, not Epic Fight's real output: Epic Fight scales each animation's hits, and greatswords and scythes hit several targets. Use it to spot values that are far out of line, then judge in game. For scale, a vanilla netherite sword is 8 damage x 1.6 speed = 12.8.

| Tier | Weapon | Type (Epic Fight) | Damage | Speed | Damage x speed | Durability | Chapter |
|---|---|---|---|---|---|---|---|
| 1 | Frontier Cleaver | sword | 4.5 | 1.6 | 7.2 | 120 | Ch1 |
| 2 | Rustbite Karambit | dagger | 6 | 1.8 | 10.8 | 250 | Ch1 |
| 3 | Ashfang Karambit | dagger | 7 | 2.0 | 14.0 | 600 | Ch2 |
| 3 | Accord Longsword | longsword | 8 | 1.4 | 11.2 | 750 | Ch2 |
| 3 | Gnawblade | dagger | 5.5 | 2.0 | 11.0 | 500 | Rats line |
| 3 | Rootstring Bow | bow | - | - | bow | 400 | Ch3 |
| 4 | Hollowbane Tachi | tachi | 9.5 | 1.4 | 13.3 | 1800 | Ch4 |
| 4 | Cogwright Breaker | axe | 11.5 | 1.0 | 11.5 | 1400 | Ch3-5 |
| 4 | Thornwatch Halberd | spear | 9.5 | 1.2 | 11.4 | 1100 | Ch5 |
| 4 | Prism Ward Staff | staff | 5 | 1.2 | 6.0 | 1000 | Ch5 |
| 5 | Frostmaw Fang | dagger | 10 | 2.0 | 20.0 | 1600 | Ch6 |
| 5 | Cinder Crown | greatsword | 15 | 0.9 | 13.5 | 2000 | Ch6 |
| 5 | Wroughtnaut Bulwark | axe | 12 | 1.0 | 12.0 | 2600 | Ch5-6 |
| 6 | Sculkheart Dagger | dagger | 10.5 | 2.0 | 21.0 | 1900 | Ch7 |
| 6 | Hydra's Tri-Edge | sword | 12.5 | 1.6 | 20.0 | 2400 | Ch7 |
| 6 | Skyreach Spear | spear | 13 | 1.2 | 15.6 | 2200 | Ch7 |
| 6 | Undergloom Scythe | greatsword | 14 | 1.1 | 15.4 | 2300 | Ch7 |
| 7 | Choirbreaker Gauntlets | fist | 12 | 2.4 | 28.8 | 3000 | Ch8 |
| 7 | Harbinger's Railblade | longsword | 15 | 1.4 | 21.0 | 3200 | Ch9 |
| 7 | Abyssal Longbow | bow | - | - | bow | 3000 | Ch9 |
| 8 | Crownshard Karambits | dagger | 17 | 2.2 | 37.4 | unbreakable | Ch10 |
| 8 | Emberhold Oathblade | sword | 19 | 1.6 | 30.4 | unbreakable | Ch12 |
| 8 | Thornecutter | greatsword | 22 | 0.9 | 19.8 | unbreakable | Ch11 |

## What stands out

1. **Karambits lead every tier they're in.** Ashfang (14.0) beats the rest of tier 3 (about 11), Frostmaw Fang (20.0) matches the tier 6 weapons a chapter early, and Crownshard (37.4) is almost double Thornecutter (19.8) in the same tier. If they feel too strong in game, the simplest fix is speed 2.0 to 1.8 on Frostmaw Fang and Crownshard (damage stays, so the story weight is kept).
2. **Thornecutter is the weakest tier 8 weapon on paper** (19.8, below the tier 6 Sculkheart Dagger at 21.0). It's the Chapter 11 dragon-slayer, and a greatsword hits several targets per swing, so it may be fine. If it feels flat, raise damage 22 to 25.
3. **Prism Ward Staff** (6.0) is half its tier. It's Ilsabet's caster weapon, and its value is the ability, so this is likely intended.
4. **Durability jumps** from 120 (Frontier Cleaver) to 250 (Rustbite). That's fine for a Chapter 1 starter, which is meant to be replaced quickly.

None of these are changed yet. They're for your desktop test: if a weapon feels off, say which and I'll adjust its numbers in `weapons.json`.
