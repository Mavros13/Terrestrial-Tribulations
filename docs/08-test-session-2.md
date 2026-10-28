# Test session 2: weapons, abilities and cast animations (about 55 minutes)

Do the steps in order. Each one has what to look for. If something is wrong, write down the step number and what you saw, or take a screenshot. Nothing needs to be fixed during the session. Send everything back at the end.

## 0. Get the new build (5 min)
The newest pack is on the work branch, not on `main` yet, so import it from this link (Prism → **Add Instance** → **Import**):

`https://github.com/Mavros13/Terrestrial-Tribulations/raw/claude/project-thread-gnjvhs/dist/Terrestrial-Tribulations-TestBuild1-CurseForge.zip`

This makes a fresh instance, so your old instance and its worlds stay as they are. Set memory to 8 GB (Edit → Settings → Java), as before. Once pull request #1 is merged, the usual `main` link carries the same build.

## 1. Make a test world (3 min)
Create a new world: **Creative**, **Allow Cheats: ON**. Pick any Heritage and Fate. Then run:
```
/gamerule doDaylightCycle false
/time set day
/kubejs stages add @p tt_ch8_heroes
```
Then run the self-test once: `/kubejs custom_command tt_selftest`. The chat stays quiet; it writes `[TT] selftest ...` lines to `logs/kubejs/server.log`, which you send back at the end. It passed 180/180 on the test server, so this just confirms the same in singleplayer.

## 2. Weapon looks (15 min)
Give yourself the weapons that got new models. Hold each one in first person and look at it in third person (F5), then put it in an item frame:
```
/give @p tt:sculkheart_dagger
/give @p tt:frontier_cleaver
/give @p tt:accord_longsword
/give @p tt:emberhold_oathblade
/give @p tt:undergloom_scythe
/give @p tt:thornwatch_halberd
/give @p tt:harbingers_railblade
/give @p tt:rootstring_bow
```
For each one, check:
- **Look:** is it a real 3D shape and not a purple-and-black cube? Does the glow animate?
- **Size:** does it look right for the weapon (dagger small, halberd long)?
- **First person:** does it sit in the hand, or does it cover the screen or float away from the hand?
- **Inventory icon:** is it a clear picture of the weapon?

The other 15 weapons: `/give @p tt:<id>` with ids from JEI (search `@kubejs`). A quick look at each in the hand is enough.

## 3. Swings and trails (5 min)
Switch to **Survival** (`/gamemode survival`). Press **R** for Epic Fight battle mode. Swing the cleaver, longsword and scythe at a zombie (`/summon zombie ~ ~ ~3`).
- Does the swing trail run along the blade, and stop at the tip and the handle?
- Does each weapon use a fitting move set?

## 3b. Weapon abilities (10 min)
All 23 weapons now have working abilities. Try these, with a few zombies around (`/summon zombie ~ ~ ~4`):
- **Sneak + right click:** Skyreach Spear (launch up; hit something in the air to plunge), Harbinger's Railblade (1.5 s charge, then beam), Choirbreaker Gauntlets (EMP stun), Crownshard Karambits (blink between enemies).
- **Cogwright Breaker:** hit 3 to 5 times (watch the "Pressure" counter), then sneak and hit to release it.
- **Bows:** Rootstring Bow and Abyssal Longbow should draw and shoot like a normal bow (you need arrows outside creative). A full draw with the Rootstring roots enemies where it lands; the Abyssal arrow pierces and drags.
- **Epic Fight:** Rustbite Karambit: dodge an attack, then hit within 1 s (extra damage, target flinches). Wroughtnaut Bulwark: parry (guard just as the hit lands) and the attacker takes the damage back.
- Each active ability greys out on the hotbar while it cools down.

## 4. Cast animations (10 min)
```
/superpower add tt:cast_test
```
Palladium adds ability keys for the power. If the keys aren't shown, open Palladium's powers screen and look there. There are nine casts: focus, flick, slam, rise, ward, blink, weapon raise, railblade charge and gauntlet charge. Use each cast once, then again in front view (F5 twice).
- Does the body move, with the charge particles at the hands and then a burst with sound?
- Does the burst land at the peak of the motion, not before or after it?
- Does it look good, or stiff or floaty? (Compare with the preview page.)
- Try one cast in Epic Fight battle mode (R). Does it still play?

Also try Iron's built-in version: `/cast @p irons_spellbooks:fireball`. Note how it looks next to ours.

## 5. Quick health check (2 min)
`/reload` should print no red errors in chat. When you're done, close the game normally.

## Send back
- `logs/latest.log` from the new instance's `minecraft` folder (or upload it to https://mclo.gs and send the link).
- Your notes and screenshots for steps 2 to 4. Short is fine, for example "2: halberd too big, cleaver great; 4: slam burst too early".
