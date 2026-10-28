# Weapon balance check (2026-10-28)

Each weapon's chapter, tier and damage compared with the progression table in `docs/00-kickoff.md` (section E: tier gates by chapter and sword damage per tier: T1 4–5, T2 6, T3 7–8, T4 9, T5 10–11, T6 12–13, T7 14–16, T8 17–20) and the progression map (Ch1–3 tiers 1–3, Ch4–5 tiers 3–4, Ch6–8 tiers 5–6, Ch9–11 tiers 7–8). "Rate" is damage × attack speed, a rough guide only: under Epic Fight the attack-speed attribute scales the animation speed, but combos, innate skills and our ability riders matter as much.

| Weapon | Ch | Tier | Dmg | Speed | Rate | Verdict |
|---|---|---|---|---|---|---|
| Frontier Cleaver | 1 | 1 | 4.5 | 1.6 | 7.2 | fits |
| Rustbite Karambit | 1 | 2 | 6 | 1.8 | 10.8 | fits |
| Ashfang Karambit | 2 | 3 | 7 | 2.0 | 14.0 | fits (fast family) |
| Accord Longsword | 2 | 3 | 8 | 1.4 | 11.2 | fits |
| Gnawblade | Rats | 3 | 5.5 | 2.0 | 11.0 | fits (side line) |
| Cogwright Breaker | 3–5 | 4 | 11.5 | 1.0 | 11.5 | fits (heavy hitter, slow) |
| **Hollowbane Tachi** | **4** | **5 → 4** | **11 → 9.5** | 1.4 | 15.4 → 13.3 | **was out of band**: Ch4 is tiers 3–4, and at tier 5 it beat every Ch5 weapon. Lowered to tier 4 / 9.5 |
| Thornwatch Halberd | 5 | 4 | 9.5 | 1.2 | 11.4 | fits (+1 reach) |
| Prism Ward Staff | 5 | 4 | 5 | 1.2 | 6.0 | fits (a caster's staff; its value is the ward) |
| Wroughtnaut Bulwark | 5–6 | 5 | 12 | 1.0 | 12.0 | fits its roster chapter; **note**: `design/story/boss-roles.md` puts the Ferrous Wroughtnaut in **Ch3**. If the boss stays in Ch3, the weapon should come later (a Ch5 reforge quest), or drop to tier 3–4. Owner's call |
| Cinder Crown | 6 | 5 | 15 | 0.9 | 13.5 | fits |
| Frostmaw Fang | 6 | 5 | 10 | 2.0 | 20.0 | high for Ch6; fine for a hard optional boss. Watch in play |
| Skyreach Spear | 7 | 6 | 13 | 1.2 | 15.6 | fits |
| Hydra's Tri-Edge | 7 | 6 | 12.5 | 1.6 | 20.0 | fits |
| Undergloom Scythe | 7 | 6 | 14 | 1.1 | 15.4 | fits |
| Sculkheart Dagger | 7 | 6 | 10.5 | 2.0 | 21.0 | fits (fast family) |
| Choirbreaker Gauntlets | 8 | 7 | 12 | 2.4 | 28.8 | **highest rate before Ch10.** Fists are Epic Fight's fastest family, so per-hit is low by design. Watch in play; if it melts bosses, drop speed to 2.0 |
| Harbinger's Railblade | 9 | 7 | 15 | 1.4 | 21.0 | fits |
| Crownshard Karambits | 10 | 8 | 17 | 2.2 | 37.4 | fits (endgame) |
| Thornecutter | 11 | 8 | 22 | 0.9 | 19.8 | fits; Sunder the Regent adds its boss bonus |
| Emberhold Oathblade | 12 | 8 | 19 | 1.6 | 30.4 | fits (postgame) |

Bows (Rootstring Ch3, Abyssal Ch9) shoot through `startup_scripts/tt_bows.js` with base arrow damage 2.0 + tier × 0.25 (vanilla bow 2.0), so they scale gently and their abilities carry them.

**Changed:** Hollowbane Tachi tier 5 → 4, damage 11 → 9.5 (`design/weapons/weapons.json`, `design/weapons/ROSTER.md`).
**For the in-game test:** Frostmaw Fang and Choirbreaker Gauntlets are the two to watch.
