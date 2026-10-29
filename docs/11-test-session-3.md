# Test session 3: everything since 2026-10-29 morning (about 40 minutes)

The desktop test after merging PR #1 into `main` (2026-10-29). Do the steps in order. If something is wrong, write down the step number and what you saw, or take a screenshot, and keep going.

## 0. Get the builds (5 min)
Import **both** into Prism (**Add Instance** → **Import**, set memory to 8 GB in Edit → Settings → Java):
- Test build (has the test commands): `https://github.com/Mavros13/Terrestrial-Tribulations/raw/main/dist/Terrestrial-Tribulations-TestBuild2-CurseForge.zip`
- Release build (what players get): `https://github.com/Mavros13/Terrestrial-Tribulations/raw/main/dist/Terrestrial-Tribulations-0.9.0-CurseForge.zip`

Steps 1–6 use the **test build**. Step 7 uses the release build.

## 1. Window and settings (2 min)
Launch the test build.
- The loading screen is dark with an orange bar. The window title reads "Terrestrial Tribulations 0.9.0", with the broken-crown icon.
- Options → Resource Packs: **Karambit Vault x Punchy** and **TT Karambits** are both on, with TT Karambits above it.

## 2. Karambits and vanilla swords (8 min)
New world: **Creative**, cheats **on**. Then:
```
/give @p minecraft:iron_sword
/give @p tt:rustbite_karambit
/give @p tt:ashfang_karambit
/give @p tt:frostmaw_fang
/give @p tt:crownshard_karambits
```
- **Iron sword:** looks like a normal iron sword in the inventory and in hand, swings normally, and is named "Iron Sword".
- **Each karambit:** the inventory icon is the 3D karambit, matching what's in your hand. Outside battle mode, the karambit animations play: idle, swing and **Y** to inspect.
- Battle mode (**R**): Epic Fight's arms only, no doubled weapon.

## 2b. Weapon skills (5 min)
Survival is easier for this (skills charge by hitting things): `/gamemode survival`, `/kubejs custom_command tt_mobs` for targets, then in battle mode (**R**) hit until the skill gauge is full and press the weapon skill key.
```
/give @p tt:accord_longsword
/give @p tt:thornwatch_halberd
/give @p tt:cinder_crown
```
- **Accord Longsword:** the skill is an overhead leap-strike (The Guillotine), and you get Strength and Resistance. Normal swings are the usual longsword ones.
- **Thornwatch Halberd:** after the skill hits, a line of green specks stays on the ground ahead of you for 5 s, and mobs standing on it take damage and slow down.
- **Cinder Crown:** the first skill hit sends a wave of flame 10 blocks ahead of you, setting mobs on it alight.
- **Ashfang Karambit** (from step 2): the skill hit moves you behind the target.

## 3. NPCs: talk quests and shops (10 min)
```
/kubejs custom_command tt_story
/kubejs custom_command tt_npcs
```
- First mark the two quests before them as done, so the talk quests can complete:
  `/ftbquests change_progress @p complete BC7B140352112BF4` (Plant the Charter) and
  `/ftbquests change_progress @p complete DE3F8A37795E0699` (A Town).
- Open the quest book, then talk to **the Stranger** and go through "A Kind Word" to the end. The quest **"A Kind Word"** (Chapter 6) ticks itself off.
- Talk to **Captain Rhosk** and press Goodbye. **"The Thornwatch Visits"** (Chapter 2) ticks.
- Open **Doran's** shop (Trade): the offers are there, and buying one works.
- Choose "Not for sale." with the Stranger: the talk ends there, with no "That's all I ask." line after it.

### 3b. NPC sites (5 min, use a **new world**)
- Within a few seconds of the first load, a small camp stands about 24 blocks east of spawn, with **Elder Maera** and **Doran** in it once you walk in.
- In survival, `/place structure tt:npc/thornwatch_outpost ~10 ~ ~` then walk into it: you're put back outside with a gold line.
- `/kubejs custom_command tt_story` (gives every stage), walk in again: **Captain Rhosk** appears on the outpost. Placing a second outpost and walking in gives no second Rhosk.
- Complete "Plant the Charter" (`c2_found`) in a fresh survival world: an explorer map to the outpost lands in your inventory.
- **Moving in:** in creative, place a Town Hall and paste a Blacksmith's Hut with the build tool's Paste button.
  `/kubejs custom_command tt_story`, then `/kubejs custom_command tt_sites` and walk into the camp. Doran's menu
  shows **Come to Emberhold**; press it and he appears inside the Blacksmith, at its anvil and facing it (or the Town
  Hall if the pasted hut doesn't count as built). Talk to him there: the button is gone. Fly 200 blocks away and back: he may now stand at another spot. Near him,
  he swings his pickaxe now and then with an anvil sound and sparks.
- **Looks and holsters:** `/kubejs custom_command tt_sites`, then fly 200 blocks away and back a few times. Each NPC
  changes what it holds and how it stands. Rhosk, Pell, Tamsin and Ilsabet sometimes carry their big weapon on their
  back instead: it sits flat between the shoulders and turns with them. Note any weapon that floats, clips into the
  body or sits too high (`docs/09-story-npcs.md`, Holsters).
- **Pre-generation:** about a minute after the new world first loads, a grey chat line says the land around spawn
  is being generated. Leave the game running: a second line, "The land around spawn is ready", follows when Chunky
  finishes (several minutes or more).
- **Weapon feel:** while testing weapons, keep `docs/research/2026-10-29-weapon-balance.md` open and note any that
  feel too strong or weak.

## 4. Side Paths (5 min)
- The quest book has a **Side Paths** group with 5 tabs.
- Open **Cogwright Workshop**: its first quest opens after Pell's story quest, so mark that done first: `/ftbquests change_progress @p complete 14680D94DDB8FE4E` (The Ticking Hand). Then give yourself 16 Andesite Alloy (`/give @p create:andesite_alloy 16`): the quest completes.

## 5. Pre-generation (3 min)
- About a minute after the world first loads, a grey chat line says it's pre-generating around spawn. Play goes on, maybe with a little stutter.
- `/chunky pause` stops it.

## 6. Settings survive an update (3 min)
- Turn **Karambit Vault x Punchy** off in Options → Resource Packs and quit.
- Prism → the test instance → **Edit** → **Version**/**Modpack** → update, or re-import over it. Launch: the pack is still off.

## 7. Release build smoke test (5 min)
Launch the 0.9.0 instance, make a **Survival** world with cheats **on**, and play the first few Chapter 1 quests.
- Nothing crashes, the quest book opens, and Chapter 1 progresses.
- `/kubejs custom_command tt_kit` should **fail**: the release has no test commands.

## Send back
Step numbers with problems (and screenshots), plus `logs/latest.log` from the test instance if anything crashed.
