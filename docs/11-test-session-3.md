# Test session 3: everything since 2026-10-29 morning, before merging (about 40 minutes)

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

## 4. Side Paths (5 min)
- The quest book has a **Side Paths** group with 5 tabs.
- Open **Cogwright Workshop**: the first quest needs Andesite Alloy. Give yourself 16 (`/give @p create:andesite_alloy 16`) and it completes.

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
