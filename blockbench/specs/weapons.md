# Blockbench modelling briefs: the 23 custom weapons (v1, 2026-10-27)

Source of truth for names, colours and abilities: `design/weapons/ROSTER.md` and `design/weapons/weapons.json`. This file only covers **how each weapon looks in 3D** and how to get a model into the pack. Nothing here has been modelled or tested yet.

## 1. Pipeline (same for every weapon)

1. **New project:** Blockbench → *Java Block/Item* (not GeckoLib). Epic Fight draws the held item with the normal item model, so a plain Java item model works with every moveset and needs no code.
2. **Save the source** as `blockbench/models/weapons/<id>.bbmodel`.
3. **One texture per weapon**, saved as `blockbench/textures/weapons/<id>.png`. Use only that weapon's four registry colours plus darker and lighter shades of them. Leave no stray hues, because rule 1 of the roster says the colours must stay unique.
4. **Export** with *File → Export → Export Block/Item Model* to `blockbench/exports/weapons/<id>.json`.
5. **Optional hand-drawn inventory icon:** 16×16, saved as `blockbench/textures/weapons/<id>_icon.png`. Without it, the generated placeholder icon stays.
6. **Run `python3 tools/build_prism.py`.** `build_content.py` picks the model up and does the rest:
   - It points the textures at `tt:item/<id>_3d`.
   - It gives every element whose name starts with `glow` full brightness, using Forge's `forge_data`.
   - It wraps the model in Forge's `separate_transforms` loader, so the 3D model shows in hand and on the ground, and the flat icon shows in inventories and item frames.
   - Deleting a source removes its outputs on the next build.
7. **Test in game:** check the model in vanilla first person, in Epic Fight battle mode (third person, with a few attacks), in an inventory, and on the ground. Then commit the `.bbmodel`, the PNG and the export.

### Hard limits of the Java item format
- Each element can rotate on **one axis only**, in 22.5° steps (−45, −22.5, 0, 22.5, 45). Curves such as karambit hooks, scythe crescents and recurve limbs are built from short stepped cubes.
- Coordinates must stay between −16 and 32 on every axis, so a model is at most 3 blocks long. Longer weapons are modelled at a smaller size and enlarged with the Display `scale`.
- Semi-transparent pixels work for items, so ice and crystal blades can use alpha of roughly 60–80%.
- Animated textures work: a vertical strip plus a `<id>.png.mcmeta` beside the PNG. Only Crownshard uses one.

### Orientation and display
- Model the weapon **upright along +Y**, with the grip centred on X = 8, Z = 8 and the hand point at about Y = 4.
- In the Display tab, start every slot from Blockbench's *handheld* preset. Then adjust only `thirdperson_righthand` (Epic Fight uses it), `firstperson_righthand` and `ground`.
- **Left hand:** leave it on mirror, except for karambits (see §2).
- Record the final Display values in each brief's *Display* line once tested, so the next weapon in that family can start from them.
- **Swing trail:** Epic Fight draws it from the hand joint using the family's preset length (`TRAIL_POS` in `tools/build_content.py`). If a finished model is much longer or shorter than its family, note the new blade length in its brief so the trail's `end_pos` can be changed to match.

### Budgets
| Tier | Elements (cubes) | Texture | Glow elements |
|---|---|---|---|
| 1–3 | ≤ 24 | 32×32 | ≤ 2 |
| 4–6 | ≤ 40 | 64×64 | ≤ 4 |
| 7–8 | ≤ 64 | 64×64 (Crownshard: 64×256 strip) | ≤ 8 |

These keep the GTX 1660 Super comfortable with several players holding weapons, as set in `docs/02-toolchain.md`.

### Length targets (Blockbench units, 16 = 1 block, before Display scale)
| Family | Length | Notes |
|---|---|---|
| Karambit | 10–14 | Blade hooks *forward* (toward −X when held), and the finger ring sits below the grip |
| Dagger | 10–13 | Straight |
| Sword | 22–26 | |
| Longsword / Tachi | 28–32 | Tachi has a visible curve, built from 3–4 stepped blade segments |
| Greatsword | 36–44 | Model at about 30 and use Display scale 1.3–1.5 |
| Spear / Halberd | 40–46 | Model at about 32 and use Display scale 1.4 |
| Scythe | 40 handle | The crescent extends sideways about 14 |
| Hammer / Axe | 28–32 | The head carries the mass, so keep the handle thin (2×2) |
| Staff | 36–40 | |
| Bow | about 30 tall | Static model for now (no pull frames, see §2) |
| Gauntlets | about 8 | A knuckle plate that wraps the fist, see #18 |

## 2. Family notes
- **Silhouette rule (roster rule 1):** within a family no two weapons may share a silhouette. Each brief names the feature that keeps it apart.
- **Karambits** (#2, #3, #12, #21): Epic Fight's dagger moveset holds them blade-forward. The hook must read from the side, because that's the view players see in third person. Check the left-hand display separately, since dual-wielding is planned for #21.
- **Bows** (#6, #20): they're placeholder items until `tt_bridge` gives them bow behaviour, so there's no `pulling` predicate yet. Model the *rest* pose only. Draw the string as a single 1-pixel-wide element so pull frames can be added later as `<id>_pulling_0..2` models.
- **Gauntlets** (#18): Epic Fight's fist moveset shows the held item at the fist. Model a plate around a 4×4×4 fist volume at the origin, and leave the fist area itself open (no cube).

## 3. Briefs

Each line gives the colour roles as P (primary), S (secondary), A (accent) and T (trail), with hex values from the registry. "Glow" lists the elements to name `glow…`.

### Tier 1–3

**1. Frontier Cleaver** (`frontier_cleaver`, sword, 24 long)
- *Shape:* a wide, crude cleaver blade of knapped bone with 3 notches knocked out of the edge. A flint wedge is lashed where a guard would be, and the grip is wrapped in sinew.
- *Colours:* blade P `#E8DFC8` with darker chips; lashing and grip S `#A67B4F`; flint A `#5A5A5A`.
- *Silhouette key:* the only sword with a blade wider at the tip than at the base.
- *Glow:* none. Budget: 24 / 32×32.

**2. Rustbite Karambit** (`rustbite_karambit`, karambit, 11 long) ★ the base karambit
- *Shape:* a plain hooked blade (3 stepped segments), a round finger ring at the pommel, and a leather-wrapped grip.
- *Colours:* blade P `#9AA3A8` with scratch lines; wrap S `#6B4A2E`; rust patches A `#B5562B` on the spine and ring.
- *Silhouette key:* the smallest and simplest karambit. Every later karambit should look like an upgrade of this one.
- *Glow:* none. Budget: 18 / 32×32.

**3. Ashfang Karambit** (`ashfang_karambit`, karambit, 14 long)
- *Shape:* a longer, fang-shaped hook with 4 serration teeth on the inner curve. An ember seam runs along the blade's centre line.
- *Colours:* blade P `#2B2B2B`; seam S `#F26B1D`; ash-grey edge highlights A `#8C8C8C`.
- *Silhouette key:* serrated inner curve and the longest hook of the T1–3 karambits.
- *Glow:* `glow_seam` (1 px wide, the full blade length). Budget: 24 / 32×32.

**4. Accord Longsword** (`accord_longsword`, longsword, 30 long)
- *Shape:* a straight, narrow blade, and a brass crossguard whose two arms curl upward like flame tongues. A crimson tabard ribbon hangs from the guard: 2 thin offset cubes, rotated 22.5°.
- *Colours:* blade P `#A3162B` fuller stripe on a steel-shaded blade (use P shades only); guard S `#C9A243`; ribbon and grip cloth A `#F2E8D0`.
- *Silhouette key:* the hanging ribbon and flame-arm guard.
- *Glow:* none. Budget: 24 / 32×32.

**5. Gnawblade** (`gnawblade`, dagger, 11 long)
- *Shape:* a short chisel blade with 3 square "teeth" cut into the edge, a cheese-yellow wrapped grip, and a tiny rat skull (3×3×3) as the pommel.
- *Colours:* blade P `#7D7468`; wrap S `#F2C230`; a pink tail-cord loop A `#E3A0A6` hanging from the skull.
- *Silhouette key:* the skull pommel plus tail loop.
- *Glow:* none. Budget: 20 / 32×32.

**6. Rootstring Bow** (`rootstring_bow`, bow, 30 tall)
- *Shape:* two living-wood limbs in stepped curves, with 3–4 leaf tufts sprouting from them (flat 0-thickness planes) and a vine string.
- *Colours:* leaves P `#3F8F3A`; limbs S `#5C4128`; moss and vine A `#8DB255`. Trail T `#7BD36A` belongs to the arrow particles, not the model.
- *Silhouette key:* leaf tufts break the outline.
- *Glow:* none. Budget: 24 / 32×32.

### Tier 4–6

**7. Thornwatch Halberd** (`thornwatch_halberd`, spear, 44 long)
- *Shape:* a long shaft, an axe-head on one side with a back-spike, and a spear tip. Thorn vines wind 2 turns around the upper shaft, and there's a bronze ferrule at the butt.
- *Colours:* head and vines P `#1F4D2B`; ferrule and head rim S `#A0703A`; thorn tips A `#7A1E1E`.
- *Silhouette key:* the only spear-family weapon with an axe-head.
- *Glow:* none. Budget: 36 / 64×64.

**8. Cogwright Breaker** (`cogwright_breaker`, hammer, 30 long)
- *Shape:* a boxy hammer head with a piston rod running through it, and 2 exposed gears on the sides (thin discs built from 2 cubes at 0° and 45°). There are 5 small gauge lights in a row on the head's top face.
- *Colours:* head P `#B87333`; gears and rivets S `#D4AF37`; gauge lights A `#3FD0E0`.
- *Silhouette key:* the protruding piston rod.
- *Glow:* `glow_gauge_1` to `glow_gauge_5`, kept as 5 separate elements so `tt_bridge` can later show 0–5 pressure with model overrides.
- *Budget:* 40 / 64×64. This is over the glow limit, so treat the 5 gauges as one.

**9. Prism Ward Staff** (`prism_ward_staff`, staff, 38 long)
- *Shape:* an ivory shaft with a pale-gold filigree cage at the top: 4 thin bars bowing outward, built from stepped cubes. A blue prism sits inside, rotated 45° on Y and not touching the bars.
- *Colours:* shaft P `#F5F0E1`; cage S `#E6CF8B`; prism A `#4A7BFF` with white facets.
- *Silhouette key:* the open cage head.
- *Glow:* `glow_prism`. Budget: 30 / 64×64.

**10. Hollowbane Tachi** (`hollowbane_tachi`, tachi, 32 long)
- *Shape:* a curved, single-edged black blade in 4 stepped segments, with a small round tsuba and a long two-hand grip. A violet hamon line follows the edge.
- *Colours:* blade P `#111014`; hamon S `#8A3FFC`; tsuba and habaki A `#C0C0C8`.
- *Silhouette key:* the only curved blade among longswords.
- *Glow:* `glow_hamon` (one element per blade segment, so up to 4, named `glow_hamon_1..4`). Budget: 32 / 64×64.

**11. Cinder Crown** (`cinder_crown`, greatsword, 30 long, Display scale 1.4)
- *Shape:* a slab blade, very wide and squared off, with molten cracks painted across it. The guard is a ring of 5 short upward spikes, like a crown.
- *Colours:* blade P `#1A0E1F`; cracks S `#E0301E` fading to A `#FFB000` at the crack centres.
- *Silhouette key:* the crown-spike guard.
- *Glow:* `glow_cracks`, a thin overlay element 0.01 px in front of each blade face carrying only the crack pixels (transparent elsewhere). Budget: 34 / 64×64.

**12. Frostmaw Fang** (`frostmaw_fang`, karambit, 15 long)
- *Shape:* a large tusk-shaped hook, thick at the base and tapering, with a snow-fur grip (a fuzzy, slightly oversized cube).
- *Colours:* blade P `#7FC8F8` at about 75% alpha, with S `#F4FBFF` frost on the edge and A `#B8F1FF` highlights.
- *Silhouette key:* a translucent, tusk-thick hook and the biggest karambit before Mythic.
- *Glow:* none (the translucency carries it). Budget: 30 / 64×64.

**13. Wroughtnaut Bulwark** (`wroughtnaut_bulwark`, axe, 32 long)
- *Shape:* a tall tower-shield plate fixed to the haft, with its outer edge sharpened into a blade. There's a 3×3 grid of rivets on the plate.
- *Colours:* plate P `#3A3D40`; rust streaks S `#8E3B2E`; rivets A `#B08D3C`.
- *Silhouette key:* the slab-shield profile, unlike any other axe.
- *Glow:* none. Budget: 36 / 64×64.

**14. Skyreach Spear** (`skyreach_spear`, spear, 40 long)
- *Shape:* a slender white-gold lance, with a long, needle-thin tip. Two pairs of sky-blue feather vanes (flat planes) sit below the tip.
- *Colours:* vanes P `#6EC6FF`; shaft and tip S `#FFF3C4`; cloud-white wraps A `#FFFFFF`.
- *Silhouette key:* the thinnest spear, and the feather vanes.
- *Glow:* `glow_tip` (a faint shine on the tip). Budget: 26 / 64×64.

**15. Hydra's Tri-Edge** (`hydras_tri_edge`, sword, 26 long)
- *Shape:* the blade splits into 3 prongs above the guard (one straight, two angled out at 22.5°). Each prong ends in a small serpent head (2–3 cubes), and the blade is scale-patterned.
- *Colours:* blade P `#0F8A5F`; venom drips and eyes S `#7CFC00`; scale lines and grip A `#16241C`.
- *Silhouette key:* the three prongs.
- *Glow:* `glow_eyes` (the 6 eye pixels on one element per head, so `glow_eyes_1..3`). Budget: 38 / 64×64.

**16. Undergloom Scythe** (`undergloom_scythe`, scythe, 40 handle)
- *Shape:* a long bone-white handle, slightly crooked (2 segments at 22.5°), with a side grip halfway down. A muted-teal crescent blade is built from 5 stepped cubes. Gloom mist comes from particles, not the model.
- *Colours:* blade P `#3E6B66`; handle S `#D9D2BC`; binding cords A `#4B3B5C`.
- *Silhouette key:* the only scythe.
- *Glow:* none. Budget: 34 / 64×64.

**17. Sculkheart Dagger** (`sculkheart_dagger`, dagger, 12 long)
- *Shape:* a straight blade at about 65% alpha, with an opaque cyan core running through it (a separate inner element). The crossguard looks like sculk tendrils (4 thin cubes).
- *Colours:* blade P `#0B3B3F`; core S `#29DFEB`; guard and grip A `#050A0C`.
- *Silhouette key:* the see-through blade with a visible core.
- *Glow:* `glow_core`. A pulsing core would need an animated texture, which only Crownshard gets, so it stays static. Budget: 22 / 64×64.

### Tier 7–8

**18. Choirbreaker Gauntlets** (`choirbreaker_gauntlets`, gauntlets, about 8)
- *Shape:* a chrome knuckle plate across the front of the fist with 4 raised knuckle ridges. Two round signal-red emitter cores sit on the back of the hand, and matte-black servo segments cover the wrist (3 stacked rings).
- *Colours:* plates P `#DCE3EA`; emitters S `#E01E37`; servos A `#1C1C1C`.
- *Silhouette key:* the only fist weapon.
- *Glow:* `glow_emitter_1`, `glow_emitter_2`. Budget: 36 / 64×64. See the gauntlet note in §2.

**19. Harbinger's Railblade** (`harbingers_railblade`, longsword, 32 long)
- *Shape:* the blade is an open rail frame: two parallel gunmetal rails with a gap between them. A neon-green energy channel fills the gap, and there are 3 hazard-yellow coil bands around the rails. The guard is blocky, like an emitter housing.
- *Colours:* frame P `#2C3539`; channel S `#39FF14`; coils A `#FFD300` with black hazard stripes.
- *Silhouette key:* the open, two-rail blade.
- *Glow:* `glow_channel`. Budget: 40 / 64×64.

**20. Abyssal Longbow** (`abyssal_longbow`, bow, 34 tall)
- *Shape:* a deep recurve: limbs bend back, then forward at the tips (stepped). Bioluminescent veins are painted along the limbs, with pearl tips and a pearl grip inlay.
- *Colours:* limbs P `#0B1640`; veins S `#B04DFF`; tips A `#EAE0D5`.
- *Silhouette key:* the recurve tips; Rootstring is a simple arc.
- *Glow:* `glow_veins` (an overlay element per limb, transparent except for the vein pixels). Budget: 40 / 64×64.

**21. Crownshard Karambits** (`crownshard_karambits`, karambit, 14 long, one blade)
- *Shape:* a crystalline hooked blade of faceted shards set into a crown-gold spine, with a crown-gold finger ring whose rim has 3 small points.
- *Colours:* shards P `#F8F8FF` tinted by an animated hue cycle; settings S `#FFD700`; the static shard tint is A `#C9A0FF`.
- *Animated texture:* a 64×256 strip (4 frames, each shifting the shard tint around the hue wheel) and `crownshard_karambits.png.mcmeta` with `{"animation": {"frametime": 4, "interpolate": true}}`.
- *Silhouette key:* the crystal facets and the pointed ring.
- *Glow:* `glow_shard_1..4`. Budget: 48 / 64×256.
- *Open question:* "wielded as a dual pair" is the `tt_bridge` mod's job (an off-hand copy, or one item that renders twice). The model is one blade, and it must look right in **both** hands.

**22. Thornecutter** (`thornecutter`, greatsword, 34 long, Display scale 1.4)
- *Shape:* a long, tapered void-black blade (narrower than Cinder Crown's slab) cracked with gold seams that branch like a broken crown. The guard is a plain, heavy black bar, and a cracked gold ring forms the pommel.
- *Colours:* blade P `#07060A`; seams S `#C8A951`; hollow-grey chips at the crack edges A `#4E4A55`.
- *Silhouette key:* the tapering point and plain guard, against Cinder Crown's square slab and spiked guard.
- *Glow:* `glow_seams` (an overlay element, as on Cinder Crown). Budget: 40 / 64×64.

**23. Emberhold Oathblade** (`emberhold_oathblade`, sword, 26 long)
- *Shape:* a royal white blade with a crimson-gold guard bearing the Emberhold crest (a 5×5 flat plate). A white flame runs along the edge: 3 flickering tongue elements at different heights, rotated 22.5° outward.
- *Colours:* blade P `#FBF7EE`; fittings S `#B8323F`; flame A `#FFF6E0` at about 85% alpha.
- *Silhouette key:* the flame tongues breaking the edge line.
- *Glow:* `glow_flame_1..3`. Budget: 44 / 64×64.

## 4. Suggested order
1. **Rustbite Karambit:** the simplest model. It sets the karambit Display values everyone reuses.
2. **Frontier Cleaver:** the first weapon a player gets. It sets the sword Display values.
3. **Ashfang Karambit:** the first test of the `glow` pipeline.
4. After that, go in tier order. Give priority to weapons whose testing stage arrives first (Test Build 1 covers chapters 1–3).
