# Test Build 1: install list (compatibility baseline)

> **Superseded for installation by docs/06-testing-guide.md (Prism import).** The stage list and checklist below still apply.

**Goal:** prove that the pack's core systems load **together** on your PC before we add content. Everything here is still CANDIDATE. This build is how mods become CONFIRMED.

**Target:** Minecraft **1.20.1** · **Forge 47.4.x** (latest 47.4 build; **never 47.2.0**, it breaks Origins) · **Java 17** (the launcher provides it).

---

## 0. Launcher setup (one time)
**Recommended: the CurseForge app.** It installs each mod's required dependencies automatically, which removes most of the risk of a version mismatch.

1. Install the CurseForge app, then go to **Minecraft → Create Custom Profile**.
2. Name: `TT Test Build 1` · Game version: **1.20.1** · Mod loader: **Forge**. Choose the **newest 47.4.x** build listed.
3. Profile options (⋯) → **Profile Options** → turn **off** "Use system memory settings" → set memory to **8192 MB** for now.
4. The JVM arguments field (in CurseForge: Settings → Minecraft → Java Settings) can stay at the default for this test.

(Prism Launcher also works. If you use it, you'll need to add dependencies manually.)

## 1. Install in three stages. Launch after each stage.
Adding mods in stages tells us *which group* breaks if something fails, so we don't have to guess.

For every mod: search it in the profile's **Add Content** tab, pick the **newest file marked 1.20.1 + Forge**, and accept any dependencies the app offers.

### Stage A: the risky core (animation and player-model mods together)
| # | Mod | Why it's here | Version seen in research |
|---|---|---|---|
| 1 | **Epic Fight** | Combat animations | 20.14.x (newest 1.20.1 Forge) |
| 2 | **Palladium** | Superheroes | 4.5.9 |
| 3 | **Iron's Spells 'n Spellbooks** | Magic #1 | 3.15.6 |
| 4 | **Origins (Forge)** | Origins + Fates | 1.10.0.9 |
| 5 | **Passive Skill Tree** | Talent tree | newest 1.20.1 Forge |
| 6 | **KubeJS** | Scripting | 2001.6.x |
| 7 | **PassiveSTJS** | Custom skills | 1.20.1-0.2.2 |
| 8 | **JEI** | Recipe viewer, for checking items exist | newest |
| 9 | **Spark** | Performance profiler | newest |

Dependencies the app will add (expect roughly these): Architectury API, Rhino, GeckoLib, Curios API, playerAnimator, Caelus API and possibly others. **Accept them all.**

➡️ **Launch. Create a new Creative world. Do the Stage A checks (§3).**

### Stage B: story, city and quests
| # | Mod | Why |
|---|---|---|
| 10 | **FTB Quests** | Quest book (adds FTB Library and FTB Teams) |
| 11 | **Easy NPC** (the *bundle* file) | Story NPCs and dialogue |
| 12 | **MineColonies** | The capital city (adds Structurize, MultiPiston, BlockUI and Domum Ornamentum) |
| 13 | **Champions Unofficial** | Elite mobs |
| 14 | **Jade** | Shows what you're looking at |

➡️ **Launch. Use a NEW world. Do the Stage B checks.**

### Stage C: combat polish and performance
| # | Mod | Why |
|---|---|---|
| 15 | **Epic Fight - Impactful** | Hit-stop and screen shake |
| 16 | **NEpicloob NeonSword** | Glowing swing trails (compatibility unknown on Epic Fight 20.14; **remove it first if Stage C crashes**) |
| 17 | **Afterswing** | **Only if** its Files tab has a 1.20.1 Forge file; otherwise skip it and tell me |
| 18 | **Embeddium** | Rendering speed |
| 19 | **ModernFix** | Startup and memory |
| 20 | **FerriteCore** | Memory |

Not in this build yet: worldgen, dimensions, Create, AE2, boss mods, Oculus shaders. They come in Test Build 2, once this baseline works.

## 2. Things to write down while you install
- The **exact Forge version** and the **exact file name** of every mod (CurseForge shows it on the mod's row). Paste them to me. That list becomes our first CONFIRMED manifest.

## 3. Checks after each stage
**All stages:**
- [ ] The game reaches the main menu with no crash.
- [ ] A new world loads and you can walk around for 2 minutes.
- [ ] Quit and reload the world. It still works.
- [ ] Note the startup time (roughly, in minutes).

**Stage A:**
- [ ] Epic Fight: press **R** (the default key) to switch to battle mode, attack with a sword, and try a dodge. Animations play.
- [ ] Iron's Spells: in Creative, take a spell book and a scroll, then cast a spell. The casting animation plays.
- [ ] Palladium: open the Palladium creative tab and equip any suit or power item. The power works and nothing renders broken.
- [ ] **Together:** in Epic Fight battle mode, cast a spell and use a Palladium power. Note any frozen or doubled arms, T-posing, or a missing animation.
- [ ] Origins: the origin selection screen appears in a new world.
- [ ] Passive Skill Tree: open it (check Controls for its key). The tree screen appears.
- [ ] Type `/kubejs reload server_scripts` in chat. There is no error message.

**Stage B:**
- [ ] The FTB Quests book opens (the empty book is fine).
- [ ] Spawn an Easy NPC (from its creative tab) and open its dialogue editor.
- [ ] Place a MineColonies Supply Camp, then a Town Hall. The colony is created.
- [ ] A few hostile mobs spawn with Champions elite name tags (Survival, at night).

**Stage C:**
- [ ] Sword swings show trails, and hits show impact effects.
- [ ] Press **F3** in an open area at **12 chunks render distance** and write down the FPS.
- [ ] Type `/spark profiler start`, play for 60 seconds, then type `/spark profiler stop` and send me the link it prints.

## 4. What to send back
1. ✅ or ❌ for each check above.
2. The mod file-name list (§2).
3. If anything crashed: the **crash report** (`crash-reports/` folder in the profile) and **`logs/latest.log`**. In the CurseForge app: right-click the profile → **Open Folder**.
4. The FPS figure and the Spark link.

You can paste logs into https://mclo.gs and send me the link. I'll read them and find the first real error rather than guessing.

## 5. If it crashes
- Don't remove mods at random. Send the crash report and log first.
- Quick isolation, if you want to try it yourself: remove *only the last stage's* mods and relaunch. If it works, the problem is in that stage.

## Acceptance: Test Build 1 passes when
- All three stages launch and a world loads and reloads with no crash.
- Epic Fight, Iron's Spells and Palladium animations work together without visual breakage. Minor issues get logged rather than blocking.
- Origins, Passive Skill Tree, FTB Quests, Easy NPC and MineColonies each open and function.
- FPS without shaders at 12 chunks is recorded (target 60+).
