# Spell and power animations: how mods do it, and how we will (2026-10-28)

**Question (owner, 2026-10-28):** how do magic mods, and other mods with the same style, animate a player casting a spell or using a power? How can we use the same approach so that every power we add, especially through our own `tt_bridge` mod, plays a custom animation that looks extremely good?

**Method:** the source code of each mod was read, not just its description. Repos cloned:
- Iron's Spells 'n Spellbooks: branches `1.20.1-legacy` (Oct 2025) and `1.20.1-dragon`.
- Spell Engine and Better Combat: `1.20.1`.
- Ars Nouveau: `1.20`.
- playerAnimator: `1.20`.
- Emotecraft: `dev`.
- Epic Fight: `1.20.1`, with history checked back past our pinned 20.14.17.
- GeckoLib: `1.20.1`.
- Palladium: `1.20/main`, 4.5.4. We ship 4.5.9.
- AAA Particles: `master`, plus its wiki.

Mod pages were also checked on Modrinth, CurseForge and the official docs. Sources are listed at the end.

## 1. The short answer

A spell that "looks extremely good" in Minecraft is never one thing. It is four layers fired together, on the same tick, by one trigger:

| Layer | What the player sees | What the good mods use |
|---|---|---|
| **Body** | The player's arms, torso and legs move through a cast pose | **playerAnimator** keyframe animations. Iron's Spells, Spell Engine, Palladium, Better Combat and Emotecraft all use it. Epic Fight uses its own skeletal animations |
| **Item** | The staff, sword or gauntlet itself moves, opens, spins or glows | **GeckoLib** animated items (`GeoItem` + `triggerAnim`), glow masks, animated textures |
| **Effects** | Particles, beams, swirls, rings, trails, light | Vanilla particles, custom render layers, **Effekseer** effects (AAA Particles), **Photon** effects |
| **Feel** | Sound, screen shake, camera, hit-stop | Start, loop and release sounds; distance-falloff camera shake; Epic Fight hit-stop (Impactful) |

**What this means for us.** We already ship every core library this needs:
- playerAnimator 1.0.2-rc1
- GeckoLib 4.8.4
- Palladium 4.5.9
- Epic Fight 20.14.17
- KubeJS
- Iron's Spells

So the first, very good results need **no new mod and no Java**. Section 6 lays out three tiers: what works today with no code, what small add-ons unlock, and what `tt_bridge` adds for the top-quality version.

## 2. How the best mods do it (from their source)

### Iron's Spells 'n Spellbooks: the reference implementation
- **Animation files.** `assets/irons_spellbooks/player_animation/casting_animations.json` holds **71 animations** in the GeckoLib/Bedrock keyframe format (`format_version`, `animations`, `bones`, per-keyframe `easing`).
  - Cast animations include `instant_projectile`, `charged_throw`, `long_cast` / `long_cast_finish`, `continuous_thrust`, `continuous_overhead`, `charge_raised_hand`, `self_cast_two_hands`, `cast_t_pose`, `kneeling_prayer`, `stomp`, `touch_ground`, `summon_fiery_daggers` and `magma_throw`.
  - It also has `sword_*` and `scythe_*` combat combos.
  - Bones are `torso`, `head`, `right_arm`, `left_arm`, `right_leg`, `left_leg` and `body`.
- **Spell stages.** Every spell declares a *start* animation and a *finish* animation (`AnimationHolder`).
  - Charge-up spells hold their last frame (`HOLD_ON_LAST_FRAME`) until released, then the finish animation plays.
  - `animatesLegs` decides whether the legs are animated. It is false for most casts, so the player can still walk.
- **Smooth playback**, from `ClientSpellCastHelper.animatePlayerStart`:
  - The animation fades in over **2 ticks** with `Ease.INOUTSINE` (`replaceAnimationWithFade(AbstractFadeModifier.standardFadeIn(2, INOUTSINE), …)`).
  - It plays on its own playerAnimator layer at **priority 42**.
- **Aim follows the camera.** An `AdjustmentModifier` adds the player's pitch and head yaw to both arms every frame. A projectile spell therefore always points where you look.
- **Off-hand mirroring.** A `MirrorModifier` flips the whole animation when the spell is cast from the off-hand.
- **First person.** `FirstPersonMode.THIRD_PERSON_MODEL` renders the real animated arms and items in first person, so you see your own hands cast. A config flag lets players turn it off.
- **Networking.** The server decides that a cast started or finished. Packets (`ClientboundOnCastStarted` / `ClientboundOnCastFinished`) tell every nearby client to play the animation on that player.
- **Effects:**
  - Render layers on the caster: `ChargeSpellLayer` (energy at the hands while charging) and `EnergySwirlLayer` (a swirl around the body).
  - GeckoLib models for spell entities: hammers, tentacles, wisps, ice blocks, roots.
  - Server-synced camera shake: `CameraShakeManager` adds yaw, pitch and roll noise in `ViewportEvent.ComputeCameraAngles`, fading with distance and time.
  - 22 custom particle types.
- **`/cast <casters> <spell> [level]`** (permission 2) makes any entity cast any Iron's spell, with its full animation and effects.

### Spell Engine (Wizards and others): the same pattern, data-driven
- Spell JSON declares an animation for each **stage**: casting (charge or channel) and release. Release animations can have random variants.
- Animations are made in **Blender** (`animations/*.blend` in the repo: `one_handed_projectile_charge`, `…_release`, `one_handed_area_charge`, `dual_handed_weapon_cross`, `archery_pull` and so on) and exported to playerAnimator JSON.
- **Pitch control**, from `AbstractClientPlayerEntityMixin`:
  - In first person, the arms tilt by the full pitch.
  - In third person, the arms tilt by half the pitch and the body and legs counter-tilt by the other half, so the pose stays balanced when you aim up or down.
- Leg animation is switched off while mounted.
- Animation speed scales with casting speed.
- Sounds for cast start, cast loop, release, travel and impact. Particle "shapes" follow the caster. Beams have flow and colour. Area spells draw ground indicators. Dynamic light is supported.
- Fabric-first, and built around Better Combat, which conflicts with Epic Fight. It is **not for our pack**, but its stage model is the one to copy.

### Ars Nouveau: item-side animation instead of body animation
- No playerAnimator. The spell book, wands, spell bow and crossbow, Enchanter's Sword, shield and mirror are **GeckoLib items** (`GeoItem`), so the item in your hand animates. The body uses vanilla arm poses.
- This is the pattern for weapons that come alive in your hand.

### Palladium (our hero packs): powers with animation built in
- Palladium 4.5.x (1.20.1) abilities relevant here:
  - `player_animation`: plays any playerAnimator animation by ID.
  - `animation_timer` and `repeating_animation_timer`: smooth 0→1 progress values.
  - `aim`, `energy_beam`, `energy_blast`.
  - `particles`, `play_sound`, `shader_effect`, `trail`, `render_layer`, `gui_overlay`, `vibrate`, `size`.
  - `command`: runs commands when the power fires.
- **KubeJS animations (client):** `PalladiumEvents.registerAnimations(event => event.register(id, priority, builder => …))` writes procedural poses per body part.
  - Rotations and positions are eased with `.animate(Easing, progress)`.
  - The poses are driven by an animation timer's value (`animationUtil.getAnimationTimerAbilityValue(player, powerId, key, partialTicks)`).
  - They are first-person aware (`FirstPersonContext`).
  - The built-in `AimAnimation` is written this way.
- **Caveat** (`PlayerAnimationAbility.java`): `player_animation` is marked **experimental** and always fades in over **20 ticks** (1 second). That is too slow for a snappy cast, but fine for a channelled pose.

### Epic Fight: its own skeleton, with three no-code entry points
- Epic Fight replaces the player model in battle mode with its own armature. Its animations are skeletal JSON made in **Blender** with the Epic Fight rig and `blender-json-exporter`. The docs cover Blender 2.79 and 3.6.
- **Resource-pack animations.** Files under `assets/<ns>/animmodels/animations/` that carry a `"constructor": {"invocation_command": …}` block and `"properties"` are loaded **without code**.
  - These are `AnimationManager.readResourcepackAnimation` animations, fixed for datapacks in Dec 2025, which is before our 20.14.17.
- **In-game Datapack Editor.** Mods → Epic Fight → Config → datapack editing (`IngameConfigurationScreen` → `DatapackEditScreen`). It has:
  - an **Import Animations** screen, with a model previewer
  - attack-animation property screens
  - weapon combo and weapon type screens
  - mob combat behaviours

  It writes all of this as a datapack, which is the no-code way to build custom Epic Fight attacks.
- **KubeJS custom skills.** Epic Fight ships a KubeJS plugin (`compat/kubejs`) with skill types `basic`, `chargeable` and `passive`.
  - Hooks include `executeOnServer`, `executeOnClient`, `onInitiate`, `canExecute`, cooldown, max stacks, duration and GUI drawing.
  - Bindings include `EpicFightCapabilities`, `PlayerPatch`, `SkillSlots` and `EFUtils.requestExecuteSkill`.
  - It exists in our version: the classes moved package in Nov 2025, and the plugin predates that.
  - So **Epic Fight skills, including weapon innate skills, can be written in KubeJS** and can play any Epic Fight animation (`playerPatch.playAnimationSynchronized(…)`). That is a second route next to the EDP add-on.
- **Battle mode with playerAnimator:**
  - Epic Fight's `PlayerAnimatorCompat` (fixed Mar 2025) hands the player back to the vanilla renderer while a playerAnimator animation is active.
  - Since Jan 2026, Epic Fight's own *action* animations take priority.
  - So Iron's and Palladium cast animations show in battle mode, and a running Epic Fight attack still wins.
  - Third-party "Epic Fight x Iron's Spells (enhanced) animations" add-ons exist, which shows players want casts done in Epic Fight's own style.

### GeckoLib: animated items, armour, blocks and entities
- `GeoItem` + `GeoItemRenderer` give an item its own bones and animations in hand, in first and third person.
- The server triggers per-stack animations with `triggerAnim(player, GeoItem.getOrAssignId(stack, level), controller, anim)`, synced to all clients. Ars Nouveau and Iron's both use this.
- Animation JSON can carry **keyframe events** (`sound_effects`, `particle_effects`, `timeline`), so a sound or particle fires on an exact frame.
- `AutoGlowingGeoLayer` renders a `<texture>_glowmask.png` at full brightness, giving true emissive glow on parts of the model.
- Made in **Blockbench** with the GeckoLib plugin.

## 3. The engines side by side

| Engine | Animates | Format | Made in | Triggered by | First person | In our pack |
|---|---|---|---|---|---|---|
| playerAnimator | Player body (6 parts + body, bends with bendy-lib) | Emotecraft JSON or GeckoLib/Bedrock JSON in `assets/<ns>/player_animation/`, keyed `<ns>:<animation name>` | Blockbench + GeckoLib plugin + Emotecraft player `.bbmodel`; or Blender `emote_creator.blend` | Client code; Palladium `player_animation`; AnimationJS (KubeJS) | Yes (`THIRD_PERSON_MODEL`) | ✅ 1.0.2-rc1 |
| Epic Fight | Player and humanoid armature, weapons follow `Tool_R` | Skeletal JSON in `animmodels/animations/` | Blender (EF rig + exporter); in-game Datapack Editor to wire it up | Weapon combos and skills (data, KubeJS, EDP) | Epic Fight's own first-person | ✅ 20.14.17 |
| GeckoLib | Items, armour, blocks, entities | `.geo.json` + `.animation.json` | Blockbench + GeckoLib plugin | Code (`triggerAnim`); GeckoJS (KubeJS add-on) | Yes, for items | ✅ 4.8.4 |
| Palladium JS | Player body, procedurally | KubeJS client script | Code | Ability timers | Yes | ✅ 4.5.9 |

## 4. The effects layer

- **Effekseer through AAA Particles** (MIT). It loads `.efkefc` effects made in the free **Effekseer** editor, the tool many anime-style games use for VFX: slashes, magic circles, auras, explosions. AAA Particles is that loader, with 3.7M downloads, and the newest 1.20.1 Forge build is 2.2.3 (Jul 2026).
  - Files go in `assets/<ns>/effeks/`.
  - It ships a **KubeJS binding**: `AAAParticles.addParticle(level, new ParticleEmitterInfo('tt:fire_circle').position(…).scale(…).bindOnEntity(player))`. It also supports parameters and triggers, so an effect can react while it plays.
  - The add-on **AAA Particles Command** adds `/spawnaaaparticle <id>`, usable from Palladium's `command` ability.
  - Effects don't render under *Fabulous* graphics.
- **Photon** (by KilaBash) is a Unity-style VFX editor that runs inside the game (`/photon_editor`). It does emitters, trails, beams, timelines and shader graphs, and has 1.20.1 Forge builds up to 1.1.17 (Jan 2026). Effects play with `/photon` commands or code.
  - Its license is CC BY-NC-SA 4.0. That's fine in a free modpack; selling the pack would need permission.
- **Lodestone** (the Malum library) has a code-only particle builder, screen shake and post-processing. It's only worth adding if `tt_bridge` needs it.
- **Already in the pack:**
  - Palladium `particles`, `energy_beam`, `trail` and `shader_effect`
  - Epic Fight swing trails, which we now fit to each model
  - Impactful (hit-stop)
  - Iron's Spells' own particles
  - Animated and glowing item textures (`gen_models.py`)

## 5. What makes a cast feel great (rules taken from the source above)

1. **Split every power into stages:** *wind-up* (anticipation) → *cast* (the moment of release) → *follow-through*, plus an optional *channel* loop. Iron's and Spell Engine both do this. Release is the frame where the effect, sound and shake all fire together.
2. **Fade in fast.** Use 2 ticks with an in-out-sine ease, as Iron's does. Never cut in hard, and don't use Palladium's 20-tick fade for a quick cast.
3. **Aim follows the camera.** Add pitch and head yaw to the arms. In third person, split the pitch between arms and torso, as Spell Engine does.
4. **Mirror for the off-hand.** Leave the legs alone unless the move is a stomp, slam or kneel, and switch them off when mounted.
5. **Show it in first person** with the real third-person arms (`THIRD_PERSON_MODEL`). The player mostly sees the cast from their own eyes.
6. **Layer the sound:** a start sound, a loop while charging, and a release sound. Pitch-shift it a little at random.
7. **Shake the camera on big releases**, fading with distance and time. Keep it small (Iron's peaks at about 0.35° per axis).
8. **Light it.** Use emissive glow on hands, items and effects (glow masks, full-bright elements, Effekseer additive blending).
9. **Scale with power.** Animation speed follows cast speed, and higher tiers get bigger effects and more shake.
10. **One trigger, server-side.** The server decides that a cast happened and tells all nearby clients, so everyone sees the same thing.

## 6. Our plan: three tiers

### Tier A: works today, with no new mods and no Java
- **Reuse Iron's 71 cast animations by ID.** For example, a Palladium power can contain `{"type": "palladium:player_animation", "animation": "irons_spellbooks:charged_throw"}`. playerAnimator registers every animation under `<namespace>:<animation name>`.
- **Our own body animations.** Drop GeckoLib-format JSON into `pack/kubejs/assets/tt/player_animation/`. KubeJS serves `kubejs/assets` as a resource pack, so they become `tt:<name>`.
- **Palladium powers for story powers and heroes:** `player_animation` (channelled poses) + `particles` + `play_sound` + `energy_beam` + `command`. For snappy casts, use `PalladiumEvents.registerAnimations` with an `animation_timer`, which gives a custom easing curve and first-person support.
- **Iron's `/cast`.** Run it from a Palladium `command` ability or a KubeJS script to get a full Iron's spell (animation, effects and sound) on demand. The command needs permission level 2, so run it as the server: `execute as <player> run cast @s irons_spellbooks:fireball 3`.
- **Epic Fight weapon skills in KubeJS** (`StartupEvents.registry('epicfight:skill', e => e.create('tt:ember_hook', 'basic')…)`). Each skill can play Epic Fight animations, including ones imported with the in-game Datapack Editor.
  - This can replace KubeJS damage "riders" with real skills.
  - Registry key and builder names must be confirmed in-game first.

### Tier B: small add-ons to test at stage D
| Add-on | Gives us | Notes |
|---|---|---|
| AAA Particles (+ AAA Particles Command) | Effekseer VFX, with a KubeJS binding and a command | MIT; Forge 1.20.1 2.2.3. Not under Fabulous graphics |
| AnimationJS | `player.triggerAnimation('tt:cast_fire')` from **server** KubeJS, synced; client model and render events | GPL-3; 1.20.1 0.1.3 (Apr 2026). Needs playerAnimator, KubeJS and Lio's Player Animator API |
| GeckoJS | GeckoLib **animated items, armour and blocks from KubeJS**, so our `tt:` weapons could move in hand | LGPL-3; Forge 1.20.1; last update **Feb 2024**, so it must be tested with GeckoLib 4.8.4 and with how our weapons are registered |
| Photon | In-game VFX editor and player | CC BY-NC-SA; free modpack OK |

### Tier C: `tt_bridge` (our own mod) for the best result
Copy Iron's proven structure exactly (section 2). In MCreator this means a few custom code elements; the Player Animator API plugin only offers a bare "Play Animation" block, with no stop, fade or sync.
- **One client service, `TTCast`:**
  - its own `ModifierLayer` (priority about 1000, above Palladium and Iron's)
  - a 2-tick INOUTSINE fade
  - an `AdjustmentModifier` that adds aim pitch and yaw
  - a `MirrorModifier` for the off-hand
  - `THIRD_PERSON_MODEL` first person
  - `start(player, anim)`, `finish(player, anim)` and `stop(player)`
- **Two packets** (cast start and cast finish, with entity ID, animation ID and speed) sent to everyone tracking the player.
- **A data-driven cast definition:** `data/tt/casts/<power>.json` lists the stage animations (`windup`, `release`, `channel`), sounds, Effekseer effects and their bone or hand anchors, shake strength, and whether legs are animated. One tool runs every power, and new powers are just data.
- **GeckoLib weapons**, for the weapons that should physically move (a gauntlet that vents, a railblade that charges, a scythe whose blade unfolds).
  - Use `triggerAnim` on cast, with keyframe sound and particle events.
  - Add a glow mask. The current `gen_models.py` models stay as the base look.
- **Camera shake** through `ViewportEvent.ComputeCameraAngles`, the same as Iron's.

## 7. How we will author the animations

- **Player body animations:**
  - **Blockbench** with the GeckoLib plugin and Emotecraft's player model (`blender/model_item.bbmodel` in the Emotecraft repo, with `_bend` variants for elbow and knee bends).
  - Export as a GeckoLib animation JSON to `blockbench/animations/player/<name>.json`. The build will copy these to `pack/kubejs/assets/tt/player_animation/`.
  - Name bones `torso`, `head`, `right_arm`, `left_arm`, `right_leg`, `left_leg` and `body`.
  - Emotecraft's notes say Blockbench support is weaker before 1.21.7. If an animation looks wrong in-game, use the Blender `emote_creator.blend` rig instead (older rigs for older playerAnimator versions).
- **Epic Fight attacks:** Blender 3.6 + the Epic Fight rig + `blender-json-exporter`, then import with the in-game Datapack Editor. Save the exported datapack in the repo.
- **Effects:** the Effekseer editor (free), saving `.efkefc` to `effects/effekseer/<name>.efkefc`. The build copies them to `pack/kubejs/assets/tt/effeks/`.
- **Animated weapons:** Blockbench GeckoLib "animated item" projects in `blockbench/models/weapons/`.
- **Every cast gets a short brief before modelling,** in the style of `blockbench/specs/weapons.md`: the stages with frame counts, the release frame, the hand anchor, the effect and the sound.

## 8. Things that can go wrong

- **playerAnimator 1.0.2-rc1** is the 1.20.1 build. The library must never be shaded into `tt_bridge`; use it as a normal dependency.
- **Epic Fight battle mode** hides playerAnimator animations while an Epic Fight action animation runs. Casts must not overlap a swing, or the cast must be an Epic Fight animation itself.
- **Palladium's `player_animation`** is experimental, with a fixed 20-tick fade.
- **Iron's `/cast`** needs permission level 2. Run it from the server, not as the player.
- **Effekseer** effects don't render under Fabulous graphics.
- **GeckoJS** is stale (Feb 2024).
- **Photon** is non-commercial only.
- **KubeJS scripts** share one global scope with the hero packs, so prefix everything with `tt` (see the `kubejs-shared-scope` note).
- **Sync.** A cast animation started only on the client is invisible to other players. Every route above that syncs goes through the server.

## 9. First experiments when the PC is back

These are cheap tests that prove the pipeline before any big build.
1. `/cast @s irons_spellbooks:fireball` in a cheat world, in both normal and Epic Fight battle mode. Check that the animation shows and how first person looks.
2. A one-file Palladium test power that plays `irons_spellbooks:self_cast_two_hands` with `palladium:player_animation` and spawns particles. Judge the 20-tick fade.
3. One hand-made `tt:` player animation in `kubejs/assets/tt/player_animation/` played the same way.
4. A one-skill Epic Fight KubeJS registration (`basic`) bound to a test weapon, playing a built-in Epic Fight animation. This confirms the registry ID and builder names.
5. Stage D: add AAA Particles and play its debug effect from KubeJS on a cast.

## Sources

- Iron's Spells source: [github.com/iron431/irons-spells-n-spellbooks](https://github.com/iron431/irons-spells-n-spellbooks) (`ClientSpellCastHelper`, `ClientSetup`, `SpellAnimations`, `AnimationHolder`, `CameraShakeManager`, `CastCommand`, `player_animation/casting_animations.json`)
- playerAnimator: [github.com/KosmX/minecraftPlayerAnimator](https://github.com/KosmX/minecraftPlayerAnimator) (README, `PlayerAnimationRegistry`, `FirstPersonMode`, `GeckoLibSerializer`)
- Emotecraft tools: [github.com/KosmX/emotes/tree/dev/blender](https://github.com/KosmX/emotes)
- Spell Engine: [github.com/ZsoltMolnarrr/SpellEngine](https://github.com/ZsoltMolnarrr/SpellEngine) (README, `AbstractClientPlayerEntityMixin`, `animations/*.blend`)
- Ars Nouveau: [github.com/baileyholl/Ars-Nouveau](https://github.com/baileyholl/Ars-Nouveau)
- Palladium 1.20: [github.com/ThreeTAG/Palladium](https://github.com/ThreeTAG/Palladium) (`Abilities`, `PlayerAnimationAbility`, `RegisterAnimationsEventJS`, `AimAnimation`, `AnimationUtil`)
- Epic Fight: [github.com/Epic-Fight/epicfight](https://github.com/Epic-Fight/epicfight) (`AnimationManager`, `compat/kubejs`, `compat/PlayerAnimatorCompat`, `client/gui/datapack`); docs: [epicfight-docs.readthedocs.io](https://epicfight-docs.readthedocs.io/Guides/page1/)
- GeckoLib: [github.com/bernie-g/geckolib](https://github.com/bernie-g/geckolib) (`GeoItem`, `KeyFramesAdapter`, `AutoGlowingGeoLayer`)
- AAA Particles: [modrinth.com/mod/aaa-particles](https://modrinth.com/mod/aaa-particles), [github.com/ChloePrime/AAAParticles](https://github.com/ChloePrime/AAAParticles) (`AAAParticleKubeJSPlugin`, wiki); AAA Particles Command: [moddex.gg](https://moddex.gg/mod/aaaparticlescommand-mr-PBjbrfUN)
- Photon: [modrinth.com/project/gzevkJbM](https://modrinth.com/project/gzevkJbM)
- AnimationJS: [modrinth.com/mod/animationjs](https://modrinth.com/mod/animationjs)
- GeckoJS: [modrinth.com/mod/geckojs](https://modrinth.com/mod/geckojs)
- MCreator Player Animator API plugin: [mcreator.net/node/116267](https://mcreator.net/node/116267)
- Lodestone: [github.com/LodestarMC/Lodestone](https://www.github.com/LodestarMC/Lodestone)
- Epic Fight x Iron's Spells animation add-ons: [modrinth.com/mod/epic-fight-x-irons-spells-animation-fix](https://modrinth.com/mod/epic-fight-x-irons-spells-animation-fix)
