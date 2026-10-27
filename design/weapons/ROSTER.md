# Weapon roster, v1 (23 weapons, Tiers 1–8)

Every weapon is a **new item** (`tt:` namespace), registered in KubeJS, modelled in Blockbench, given a moveset by Epic Fight, and given an ability through Epic Fight EDP, KubeJS or the `tt_bridge` mod. Status: **design spec, nothing implemented or tested yet.**

## Mandatory rules
1. **Visual uniqueness.** Every weapon has its own colour scheme (primary / secondary / accent) and **its own swing-trail colour**. No two weapons may share both primary and secondary colours, and no two may share a trail colour. The registry table below is the source of truth; check it before adding a weapon. The silhouette must also differ within a family (blade curve, guard shape, size).
2. **Ability uniqueness.** Every weapon has a mechanically distinct ability. Reusing a mechanic (pull, freeze, lifesteal, beam and so on) on a second weapon is not allowed, and neither is renaming a "+X% damage" effect.
3. **Story integration.** Every weapon names its chapter, source (NPC, boss, faction or location) and a lore line, and is unlocked by a quest or boss flag.
4. **Implementation path** is stated per weapon: `EDP` (Epic Fight data-driven skill), `KJS` (KubeJS event script) or `BRIDGE` (MCreator `tt_bridge` code). BRIDGE is used only when the other two can't do it.

## Stat baselines (vanilla reference: iron sword = 6 damage, 1.6 attack speed)
| Family | Epic Fight category | Damage vs a same-tier sword | Speed |
|---|---|---|---|
| Sword | sword | 100% | 1.6 |
| Karambit | dagger | ~100% at T2, then ~90% | 1.8–2.2 |
| Dagger | dagger | 85% | 2.0 |
| Longsword / Tachi | longsword / tachi | 110% | 1.4 |
| Greatsword | greatsword | 140% | 0.9 |
| Spear / Halberd | spear | 105% | 1.2 |
| Hammer | axe (mace moveset) | 130% | 1.0 |
| Scythe | greatsword (sweep) | 120% | 1.1 |
| Gauntlets | fist | 80% | 2.4 |
| Staff | (Iron's Spells staff, melee secondary) | 60% | 1.2 |
| Bow | bow | n/a | n/a |

## Colour and trail registry
| # | Weapon | Primary | Secondary | Accent | Trail |
|---|---|---|---|---|---|
| 1 | Frontier Cleaver | Bone white `#E8DFC8` | Sinew tan `#A67B4F` | Flint grey `#5A5A5A` | Dusty beige `#CDBFA0` |
| 2 | **Rustbite Karambit** | Worn steel `#9AA3A8` | Leather brown `#6B4A2E` | Rust orange `#B5562B` | Pale steel `#D7DEE2` |
| 3 | Ashfang Karambit | Charcoal `#2B2B2B` | Ember orange `#F26B1D` | Ash grey `#8C8C8C` | Ember `#FF7A1A` |
| 4 | Accord Longsword | Crimson `#A3162B` | Brass `#C9A243` | Cream cloth `#F2E8D0` | Crimson `#D42A45` |
| 5 | Gnawblade | Rat grey `#7D7468` | Cheese yellow `#F2C230` | Pink tail `#E3A0A6` | Yellow `#FFD94A` |
| 6 | Rootstring Bow | Living green `#3F8F3A` | Bark brown `#5C4128` | Moss `#8DB255` | Leaf green (arrow trail) `#7BD36A` |
| 7 | Thornwatch Halberd | Forest green `#1F4D2B` | Bronze `#A0703A` | Thorn red `#7A1E1E` | Deep green `#2E8B57` |
| 8 | Cogwright Breaker | Copper `#B87333` | Brass `#D4AF37` | Gauge cyan `#3FD0E0` | Cyan `#45E6F5` |
| 9 | Prism Ward Staff | Ivory `#F5F0E1` | Pale gold `#E6CF8B` | Arcane blue `#4A7BFF` | Prismatic white `#FFFFFF` |
| 10 | Hollowbane Tachi | Black lacquer `#111014` | Violet edge `#8A3FFC` | Silver `#C0C0C8` | Violet `#9B5CFF` |
| 11 | Cinder Crown | Obsidian `#1A0E1F` | Molten red `#E0301E` | Magma yellow `#FFB000` | Magma `#FF4A1C` |
| 12 | Frostmaw Fang | Glacier blue `#7FC8F8` | Snow white `#F4FBFF` | Ice cyan `#B8F1FF` | Ice blue `#A6E4FF` |
| 13 | Wroughtnaut Bulwark | Dark iron `#3A3D40` | Rust red `#8E3B2E` | Rivet gold `#B08D3C` | Iron grey `#6E7377` |
| 14 | Skyreach Spear | Sky blue `#6EC6FF` | White-gold `#FFF3C4` | Cloud white `#FFFFFF` | Golden white `#FFF1A8` |
| 15 | Hydra's Tri-Edge | Emerald `#0F8A5F` | Venom green `#7CFC00` | Scale black `#16241C` | Venom `#8CFF3A` |
| 16 | Undergloom Scythe | Muted teal `#3E6B66` | Bone `#D9D2BC` | Gloom purple `#4B3B5C` | Murky teal `#5FA39A` |
| 17 | Sculkheart Dagger | Deep teal `#0B3B3F` | Sculk cyan `#29DFEB` | Black `#050A0C` | Sculk pulse `#1FFFF0` |
| 18 | Choirbreaker Gauntlets | Chrome `#DCE3EA` | Signal red `#E01E37` | Matte black `#1C1C1C` | Red `#FF2A44` |
| 19 | Harbinger's Railblade | Gunmetal `#2C3539` | Neon green `#39FF14` | Hazard yellow `#FFD300` | Neon green `#4DFF4D` |
| 20 | Abyssal Longbow | Deep navy `#0B1640` | Bioluminescent purple `#B04DFF` | Pearl `#EAE0D5` | Abyss violet (arrow trail) `#C77DFF` |
| 21 | Crownshard Karambits | Prismatic white `#F8F8FF` | Crown gold `#FFD700` | Shifting shard (animated hue) | Rainbow cycle |
| 22 | Thornecutter | Void black `#07060A` | Cracked gold `#C8A951` | Hollow grey `#4E4A55` | Black-gold `#B8963A` |
| 23 | Emberhold Oathblade | Royal white `#FBF7EE` | Crimson gold `#B8323F` | White flame `#FFF6E0` | White flame `#FFF8EA` |

Duplicate check: primary/secondary pairs are all distinct. Trails are distinct hex values; similar hues (crimson vs. magma, cyan vs. sculk) are kept apart by brightness and by particle style (see each spec).

---

## Tier 1 · Primitive

### 1. Frontier Cleaver: `tt:frontier_cleaver`
- **Family:** Sword (crude, notched bone-and-flint blade) · **Rarity:** Common
- **Stats:** 4.5 damage · 1.6 speed · 120 durability
- **Ability: Scavenger's Edge** (passive, KJS): killing a passive animal drops +1 extra food item; killing a hostile mob has a 10% chance to drop 1 Bone Shard (a Tier 2 crafting material).
- **Story:** Ch1 *The Broken Frontier*, Q1.3 "Something Sharp". The first weapon the Shard-Born makes in the ash fields. *"Ugly. Effective. Like everything out here."*
- **Acquisition:** crafted: 2 flint + 1 bone + 1 stick (available from the start).
- **Fate synergy:** none (starter).

## Tier 2 · Reinforced

### 2. Rustbite Karambit: `tt:rustbite_karambit` ★ BASE KARAMBIT
- **Family:** Karambit (plain hooked blade, finger ring, leather-wrapped grip; scratched and slightly rusted) · **Rarity:** Common
- **Stats:** **6 damage (same as an iron sword) · 1.8 speed (iron sword is 1.6)** · 250 durability (iron sword: 250)
  - This is the **starter karambit**. Every later karambit is balanced against it.
- **Ability: Reversal Cut** (EDP + KJS): after a successful Epic Fight dodge, your next hit within 1 s deals +2 damage and makes the target flinch. No cooldown, but it needs a dodge.
- **Story:** Ch1 finale, Q1.8 "Teeth for the Night". Elder Maera gives you the plans: *"Ember scouts carried these. Small enough to hide, cruel enough to matter."* It introduces the Karambit family and Epic Fight dodging.
- **Acquisition:** crafted: 2 iron ingots + 1 leather + 1 stick (recipe unlocks after Q1.8).
- **Fate synergy:** Duelist, Ranger (as a sidearm).

### 3. Frontier tier filler
Vanilla iron and copper gear fills the rest of Tier 2 (re-themed with lore tooltips only).

## Tier 3 · Adventurer

### 3. Ashfang Karambit: `tt:ashfang_karambit`
- **Family:** Karambit (longer, serrated, fang-shaped curve; charcoal blade with a glowing ember seam) · **Rarity:** Uncommon
- **Stats:** 7 damage · 2.0 speed · 600 durability
- **Ability: Ember Hook** (EDP innate, 12 s cooldown): a hooking slash that drags you behind the target. Your next hit within 2 s is a guaranteed critical and sets the target on fire for 3 s.
- **Story:** Ch2 *The First Settlement*. After the outpost defence, Doran forges it from a Hollow Alpha fang. *"Curved like the ash dunes. Bites twice."*
- **Acquisition:** Ch2 finale quest reward. Re-craftable later at Doran's anvil: 2 Hollow Fang + Rustbite Karambit + 1 blaze powder.
- **Fate synergy:** Duelist, Reaper.

### 4. Accord Longsword: `tt:accord_longsword`
- **Family:** Longsword (straight blade, brass crossguard shaped like a flame, crimson tabard ribbon) · **Rarity:** Uncommon
- **Stats:** 8 damage · 1.4 speed · 750 durability
- **Ability: Rallying Strike** (EDP innate, 20 s cooldown): an overhead strike that gives you and every ally within 8 blocks Strength I and Resistance I for 6 s. Allies include players, MineColonies guards and tamed pets.
- **Story:** Ch2. Captain of the Ember Accord militia (Rhosk's predecessor). It's awarded when Emberhold reaches City Stage 2 (Town Hall level 2). *"Raised over the first wall we built."*
- **Acquisition:** quest reward (Town Hall level 2 + Ch2 complete).
- **Fate synergy:** Vanguard, Warden.

### 5. Gnawblade: `tt:gnawblade`
- **Family:** Dagger (short, chisel-toothed edge, cheese-yellow wrapped grip, a tiny rat skull pommel) · **Rarity:** Uncommon
- **Stats:** 5.5 damage · 2.0 speed · 500 durability
- **Ability: Pack Mark** (KJS): hitting an enemy marks it for 8 s. Your tamed rats (Rats mod) within 16 blocks switch to attacking the marked target, and deal +25% damage to it.
- **Story:** Rats side line. Nib the rat-catcher gives it once you've tamed and fed your first three rats. *"They know the smell of what you've cut. They'll finish it."*
- **Acquisition:** Rats tutorial chapter reward.
- **Fate synergy:** Summoner.

### 6. Rootstring Bow: `tt:rootstring_bow`
- **Family:** Bow (living-wood limbs with sprouting leaves, a vine string) · **Rarity:** Uncommon
- **Stats:** 1.1× vanilla bow damage, 400 durability
- **Ability: Seedshot** (KJS): fully charged arrows plant a briar patch where they land (3×3, 4 s) that roots enemies in place (Slowness V). 8 s cooldown.
- **Story:** Verdant Pact introduction (Ch3 side line). Given by the Pact's warden after you clear a corrupted grove. *"Every arrow you loose, the forest remembers."*
- **Acquisition:** quest reward.
- **Fate synergy:** Ranger, Spellweaver.

## Tier 4 · Veteran

### 7. Thornwatch Halberd: `tt:thornwatch_halberd`
- **Family:** Spear/halberd (axe-head with thorn-vine engraving, bronze ferrule) · **Rarity:** Rare
- **Stats:** 9.5 damage · 1.2 speed · 1100 durability · +1 reach
- **Ability: Briar Line** (EDP innate, 15 s cooldown): a wide sweep that leaves a 6-block line of thorns for 5 s. Enemies crossing it take 2 damage per second and are slowed.
- **Story:** Ch5 *Kingdoms in Conflict*. Captain Rhosk's reward for defending the Thornwatch siege line. *"The Thornwatch never retreats. It plants."*
- **Acquisition:** Thornwatch faction reward (Ch5 siege).
- **Fate synergy:** Vanguard, Warden.

### 8. Cogwright Breaker: `tt:cogwright_breaker`
- **Family:** Hammer (a piston-driven head with exposed gears and cyan pressure-gauge lights) · **Rarity:** Rare
- **Stats:** 11.5 damage · 1.0 speed · 1400 durability
- **Ability: Pressure Release** (BRIDGE): each hit stores 1 pressure (5 maximum, shown on the gauge texture). Sneak and attack to release it all as a slam that knocks enemies up, dealing 2 damage per stored pressure in a 4-block radius.
- **Story:** Ch3 to Ch5, Cogwright Guild line. Pell builds it once you've completed the first Create factory quest. *"Steam remembers every blow. Let it answer."*
- **Acquisition:** crafted on a Create mechanical crafter (recipe unlocks from the Create chapter): andesite alloy, brass, precision mechanism.
- **Fate synergy:** Artificer, Vanguard.

### 9. Prism Ward Staff: `tt:prism_ward_staff`
- **Family:** Staff (ivory shaft, pale-gold filigree cage around a floating blue prism) · **Rarity:** Rare
- **Stats:** Iron's Spells staff, +15% spell power, +100 max mana, 5 melee damage
- **Ability: Prism Ward** (KJS + Iron's Spells): while you hold it and cast any spell, you gain a 3 s barrier that reflects the next projectile back at its shooter. 10 s cooldown.
- **Story:** Ch5, Lumen Conclave line. Ilsabet gives it when you side with (or aid) the Conclave. *"Light bends. So should every arrow aimed at you."*
- **Acquisition:** Conclave faction reward.
- **Fate synergy:** Arcanist, Spellweaver.

## Tier 5 · Elite

### 10. Hollowbane Tachi: `tt:hollowbane_tachi`
- **Family:** Tachi (black lacquered single-edge blade with a violet glowing hamon line) · **Rarity:** Epic
- **Stats:** 11 damage · 1.4 speed · 1800 durability
- **Ability: Soul Severance** (EDP innate, 18 s cooldown): an iaijutsu draw-cut through a line. It deals +100% damage to Hollowed enemies, and strips invisibility and Hollow shields from everything hit.
- **Story:** Ch4 *The Awakening*. It drops from your Hollow self after the mirror duel. *"It was always yours. You just hadn't faced the one holding it."*
- **Acquisition:** Ch4 boss drop (guaranteed).
- **Fate synergy:** Duelist, Ascendant.

### 11. Cinder Crown: `tt:cinder_crown`
- **Family:** Greatsword (obsidian slab blade cracked with molten veins, a crown-like guard) · **Rarity:** Epic
- **Stats:** 15 damage · 0.9 speed · 2000 durability · fire immune as a dropped item
- **Ability: Flame Wake** (EDP innate, 16 s cooldown): a dragging ground slash that sends a 10-block line of erupting flame forward.
- **Story:** Ch6. Forged from the core of **Ignis** (L_Ender's Cataclysm) in the Nether arc. *"A king of fire fell. His crown did not go out."*
- **Acquisition:** crafted at the Artifact Forge: Ignis core + netherite + 4 magma blocks.
- **Fate synergy:** Vanguard, Reaper.

### 12. Frostmaw Fang: `tt:frostmaw_fang`
- **Family:** Karambit (a large tusk-shaped ice blade, translucent, with a snowfur grip) · **Rarity:** Epic
- **Stats:** 10 damage · 2.0 speed · 1600 durability
- **Ability: Rime Mark** (KJS): each hit adds a frost stack. At 5 stacks the target freezes solid for 1.5 s and takes 6 bonus damage. Each target can be frozen once every 10 s.
- **Story:** Ch6 side line. It drops from **Frostmaw** (Mowzie's Mobs) in the frozen north. Wren the scout points you to it. *"Cold enough to stop a heartbeat, curved enough to find it."*
- **Acquisition:** boss drop + Ashfang Karambit upgrade at Doran's forge.
- **Fate synergy:** Duelist, Spellweaver.

### 13. Wroughtnaut Bulwark: `tt:wroughtnaut_bulwark`
- **Family:** Axe (a riveted iron shield-axe, half-tower-shield, half-blade) · **Rarity:** Epic
- **Stats:** 12 damage · 1.0 speed · 2600 durability · can guard
- **Ability: Iron Recoil** (EDP passive): a perfectly timed Epic Fight guard reflects 100% of the blocked melee damage, and staggers the attacker for 1 s.
- **Story:** Ch5–6. It drops from the **Ferrous Wroughtnaut** (Mowzie's Mobs) in Thornwatch ruins. *"It guarded an empty hall for a hundred years. Now it guards you."*
- **Acquisition:** boss drop.
- **Fate synergy:** Warden.

## Tier 6 · Relic

### 14. Skyreach Spear: `tt:skyreach_spear`
- **Family:** Spear (a slender white-gold lance with sky-blue feather vanes) · **Rarity:** Epic
- **Stats:** 13 damage · 1.2 speed · 2200 durability · +1.5 reach
- **Ability: Gale Vault** (BRIDGE, 14 s cooldown): launches you 8 blocks up. Attacking in mid-air dives you down in a plunging strike that deals area damage and no fall damage.
- **Story:** Ch7 *The Shattered Realms*, Aether Shard. Granted by the **Valkyrie Queen** after her trial. *"The sky does not fall. It descends — on purpose."*
- **Acquisition:** Aether chapter reward.
- **Fate synergy:** Ranger, Duelist.

### 15. Hydra's Tri-Edge: `tt:hydras_tri_edge`
- **Family:** Sword (a three-pronged blade, one head per prong, emerald scales) · **Rarity:** Epic
- **Stats:** 12.5 damage · 1.6 speed · 2400 durability
- **Ability: Three Heads** (KJS): every third consecutive hit on the same target triggers a triple slash (3 × 3 damage) and applies Poison II for 4 s.
- **Story:** Ch7, Twilight Shard. Forged from **Hydra** (Twilight Forest) trophies. *"Cut one head, two grow. Cut three, it's over."*
- **Acquisition:** crafted from 3 Hydra blood + a fiery ingot + a Tier 5 sword.
- **Fate synergy:** Duelist, Reaper.

### 16. Undergloom Scythe: `tt:undergloom_scythe`
- **Family:** Scythe (a long bone-white handle with a muted-teal crescent blade, gloom mist curling off it) · **Rarity:** Epic
- **Stats:** 14 damage · 1.1 speed · 2300 durability
- **Ability: Harvest of Gloom** (KJS): a sweeping hit that strikes 3 or more enemies heals you 2 HP per enemy hit. Heals at most once every 2 s.
- **Story:** Ch7, Undergarden Shard. Found in the forgotten guardian's vault. *"Down here, nothing dies alone. It's harvested."*
- **Acquisition:** dungeon loot (guaranteed, once per player).
- **Fate synergy:** Reaper.

### 17. Sculkheart Dagger: `tt:sculkheart_dagger`
- **Family:** Dagger (a translucent teal blade with a sculk-cyan core that pulses) · **Rarity:** Epic
- **Stats:** 10.5 damage · 2.0 speed · 1900 durability
- **Ability: Echo Strike** (KJS): 1 s after each hit, a silent sonic echo repeats 50% of that hit's damage. Kills with this dagger make no sound and don't alert nearby wardens or sculk.
- **Story:** Ch7, Otherside Shard (Deeper and Darker). Taken from the Warden's dimension. *"It cuts once. The dark cuts again."*
- **Acquisition:** crafted from 2 echo shards, a sculk heart and a Tier 5 dagger or karambit.
- **Fate synergy:** Duelist, Ranger.

## Tier 7 · Legendary

### 18. Choirbreaker Gauntlets: `tt:choirbreaker_gauntlets`
- **Family:** Gauntlets (chrome knuckle plates with signal-red emitter cores, matte-black wrist servos) · **Rarity:** Legendary
- **Stats:** 12 damage · 2.4 speed · 3000 durability
- **Ability: Overload Punch** (BRIDGE, 20 s cooldown): a charged punch that releases an EMP shockwave (5-block radius). It stuns Iron Choir villains and mechanical enemies for 3 s, and interrupts Palladium-powered enemies' active abilities (if the Palladium API allows it, otherwise it deals double damage to them).
- **Story:** Ch8 *The Rise of Heroes*. Pell and the Cogwrights reverse-engineer a defeated Choir Herald's suit. *"They sing in machine-code. Teach them silence."*
- **Acquisition:** crafted after the Choir Herald defeat: Herald core + Palladium suit components.
- **Fate synergy:** Artificer, Vanguard.

### 19. Harbinger's Railblade: `tt:harbingers_railblade`
- **Family:** Longsword (a gunmetal rail-frame blade with a neon-green energy channel and hazard-yellow coils) · **Rarity:** Legendary
- **Stats:** 15 damage · 1.4 speed · 3200 durability
- **Ability: Rail Lance** (BRIDGE, 18 s cooldown): charge for 1.5 s, then fire a piercing energy beam (20 blocks) that hits everything in its line for 12 damage.
- **Story:** Ch9 *War of the Realms*. Salvaged from **The Harbinger** (L_Ender's Cataclysm). *"Built to herald the end. Repurposed to postpone it."*
- **Acquisition:** Harbinger drop + Artifact Forge.
- **Fate synergy:** Artificer, Ranger.

### 20. Abyssal Longbow: `tt:abyssal_longbow`
- **Family:** Bow (deep-navy recurve with bioluminescent purple veins and pearl tips) · **Rarity:** Legendary
- **Stats:** 1.6× vanilla bow damage, 3000 durability
- **Ability: Undertow Arrow** (KJS): fully charged arrows pierce up to 3 enemies, and pull every enemy they pierce 4 blocks back toward where the arrow landed.
- **Story:** Ch9. Forged from **The Leviathan** (Cataclysm) in the sunken city. *"The deep always takes back what it's owed."*
- **Acquisition:** Leviathan drop + Artifact Forge.
- **Fate synergy:** Ranger.

## Tier 8 · Mythic

### 21. Crownshard Karambits: `tt:crownshard_karambits`
- **Family:** Karambit, wielded as a dual pair (crystalline prismatic blades set in crown gold; animated, shifting shard colours) · **Rarity:** Mythic
- **Stats:** 17 damage · 2.2 speed · unbreakable
- **Ability: Shard Rend** (BRIDGE, 22 s cooldown): blink between up to 3 enemies within 10 blocks, slashing each one (3 × 8 damage). You're untargetable during the blinks.
- **Story:** Ch10 *The Mythic Crucible*. The culmination of the karambit line: Rustbite → Ashfang → Frostmaw Fang → Crownshard, fused with Crown Shard fragments. *"Seven shards. Two blades. One heartbeat."*
- **Acquisition:** Artifact Forge: Frostmaw Fang + 3 Crown Shard fragments + Mythic Crucible tier I clear.
- **Fate synergy:** Duelist, Ascendant.

### 22. Thornecutter: `tt:thornecutter`
- **Family:** Greatsword (void-black blade with cracked gold seams, like the Crown itself fractured) · **Rarity:** Mythic
- **Stats:** 22 damage · 0.9 speed · unbreakable
- **Ability: Sunder the Regent** (KJS + BRIDGE): against bosses, damage increases by up to +40% as the boss's missing health rises. Its innate skill (25 s cooldown) is a cleaving arc that removes one active buff or phase shield from a boss.
- **Story:** Ch11 *The Final Convergence*. Forged to kill **Malric, the Hollow Regent**, from the shattered fragments of Ysolde's last blade. *"Made for one neck. It will not be sheathed until it finds it."*
- **Acquisition:** Ch11 main quest: Archivist Sol's ritual + all 7 Crown Shards.
- **Fate synergy:** Vanguard, Ascendant.

### 23. Emberhold Oathblade: `tt:emberhold_oathblade`
- **Family:** Sword (royal white blade with crimson-gold fittings, a white flame that burns along the edge) · **Rarity:** Mythic
- **Stats:** 19 damage · 1.6 speed · unbreakable
- **Ability: Oath of the Capital** (BRIDGE): gains +1 damage per Emberhold Town Hall level (up to +5), and while you're inside your colony's borders, each kill heals all nearby citizens and guards.
- **Story:** Ch12 *Beyond the Throne*. Forged when Emberhold becomes a Legendary Kingdom (Town Hall level 5). The Accord Longsword reborn. *"The first wall. The last oath."*
- **Acquisition:** Ch12 reward: Accord Longsword + Town Hall 5 + the postgame ceremony quest.
- **Fate synergy:** Vanguard, Warden.

---

## Family progressions (upgrade paths)
- **Karambit:** Rustbite (T2) → Ashfang (T3) → Frostmaw Fang (T5) → Crownshard Karambits (T8)
- **Ember Accord sword:** Accord Longsword (T3) → Emberhold Oathblade (T8)
- **Story-climax weapons:** Hollowbane Tachi (Ch4) → Thornecutter (Ch11)

## Ability uniqueness check
Scavenge drops · post-dodge bonus · hook-behind + forced crit · ally buff aura · rat focus mark · rooting briar arrow · thorn damage line · stored-pressure slam · projectile reflect · anti-Hollow line cut + reveal · flame line eruption · stacking freeze · perfect-guard reflect · vertical vault + dive · every-3rd-hit triple slash · multi-hit heal · delayed echo + silence · EMP stun + ability interrupt · charged piercing beam · pierce + pull arrows · multi-target blink · scaling with boss missing health + shield strip · colony-scaling + citizen heal. All **23 mechanics are distinct**.
