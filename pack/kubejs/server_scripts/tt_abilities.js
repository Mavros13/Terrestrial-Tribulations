// Terrestrial Tribulations: weapon abilities that KubeJS can do on its own (impl = KJS in weapons.json).
// Active abilities (sneak + use) and the BRIDGE abilities KubeJS can do are in tt_active_abilities.js; the rest wait for tt_bridge.
// EDP weapons: Epic Fight data can only assign its built-in innate skills (no new skills), so each EDP weapon keeps
// its family's built-in innate skill and the custom effect is added here as a "rider" on hits that skill deals.
// Epic Fight tags those hits with the runtime damage tag epicfight:weapon_innate (EpicFightDamageSource.is, 1.20.1
// source). See docs/research/2026-10-27-epic-fight-data-formats.md.
// DRAFT: untested in-game. Every handler is wrapped so that one failure can't break the others.

const TT_FOOD = { 'minecraft:cow': 'minecraft:beef', 'minecraft:pig': 'minecraft:porkchop', 'minecraft:sheep': 'minecraft:mutton',
  'minecraft:chicken': 'minecraft:chicken', 'minecraft:rabbit': 'minecraft:rabbit' }

// Prefixed names: all server scripts (ours and the hero packs') share one global scope.
const $TT_TagKey = Java.loadClass('net.minecraft.tags.TagKey')
const $TT_Registries = Java.loadClass('net.minecraft.core.registries.Registries')
const $TT_ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
const $TT_MobEffects = Java.loadClass('net.minecraft.world.effect.MobEffects')
const TT_INNATE = $TT_TagKey.create($TT_Registries.DAMAGE_TYPE, new $TT_ResourceLocation('epicfight', 'weapon_innate'))
// Entity IDs that count as "Hollowed" for Soul Severance: the undead Hollowed and the Hollow bosses (boss-roles.md).
const TT_HOLLOWED = ['minecraft:zombie', 'minecraft:husk', 'minecraft:drowned', 'minecraft:zombie_villager',
  'bosses_of_mass_destruction:lich', 'mowziesmobs:umvuthi', 'cataclysm:scylla']

function ttSafe(name, fn) {
  try { fn() } catch (e) { console.error(`[TT] ability ${name} failed: ${e}`) }
}

// Extra damage on top of a hit. Damage dealt inside the hurt event is swallowed by the target's invulnerability frames
// (vanilla sets them before the event fires), so it lands one tick later with the frames cleared.
function ttBonus(server, target, amount) {
  server.scheduleInTicks(1, () => {
    if (!target.isAlive()) return
    target.invulnerableTime = 0
    target.attack(amount)
  })
}

// Scavenger's Edge (Frontier Cleaver)
EntityEvents.death(event => ttSafe('scavengers_edge', () => {
  const p = event.source.player
  if (!p || p.mainHandItem.id != 'tt:frontier_cleaver') return
  const e = event.entity
  const food = TT_FOOD[e.type]
  if (food) e.block.popItem(food)
  else if (e.isMonster() && Math.random() < 0.10) e.block.popItem('tt:bone_shard')
}))

EntityEvents.hurt(event => {
  const p = event.source.player
  if (!p) return
  const t = event.entity
  const held = p.mainHandItem.id
  const now = t.level.gameTime
  const d = t.persistentData

  // Rime Mark (Frostmaw Fang): 5 stacks -> freeze 1.5s + 6 dmg; 10s per-target cooldown
  if (held == 'tt:frostmaw_fang') ttSafe('rime_mark', () => {
    if (now < d.getLong('tt_rime_cd')) return
    const stacks = d.getInt('tt_rime') + 1
    if (stacks >= 5) {
      d.putInt('tt_rime', 0)
      d.putLong('tt_rime_cd', now + 200)
      t.potionEffects.add('minecraft:slowness', 30, 9)
      t.potionEffects.add('minecraft:weakness', 30, 2)
      ttBonus(event.server, t, 6)
    } else d.putInt('tt_rime', stacks)
  })

  // Three Heads (Hydra's Tri-Edge): every 3rd consecutive hit (within 3s) -> 3x3 dmg + Poison II 4s
  if (held == 'tt:hydras_tri_edge') ttSafe('three_heads', () => {
    const count = (now - d.getLong('tt_hydra_last') > 60) ? 1 : d.getInt('tt_hydra') + 1
    d.putLong('tt_hydra_last', now)
    if (count >= 3) {
      d.putInt('tt_hydra', 0)
      ttBonus(event.server, t, 9)
      t.potionEffects.add('minecraft:poison', 80, 1)
    } else d.putInt('tt_hydra', count)
  })

  // Echo Strike (Sculkheart Dagger): after 1s, repeat 50% of the damage
  if (held == 'tt:sculkheart_dagger') ttSafe('echo_strike', () => {
    const echo = event.damage * 0.5
    event.server.scheduleInTicks(19, () => ttBonus(event.server, t, echo))
  })

  // Harvest of Gloom (Undergloom Scythe): 3+ enemies hit by the same swing (same tick) -> heal 2 HP each, max once per 2s
  if (held == 'tt:undergloom_scythe') ttSafe('harvest_of_gloom', () => {
    const pd = p.persistentData
    const count = pd.getLong('tt_gloom_tick') == now ? pd.getInt('tt_gloom_n') + 1 : 1
    pd.putLong('tt_gloom_tick', now); pd.putInt('tt_gloom_n', count)
    if (count == 3 && now >= pd.getLong('tt_gloom_cd')) { p.heal(6); pd.putLong('tt_gloom_cd', now + 40); pd.putBoolean('tt_gloom_on', true) }
    else if (count > 3 && pd.getBoolean('tt_gloom_on') && pd.getLong('tt_gloom_cd') == now + 40) p.heal(2)
  })

  // ----- EDP riders: only on hits dealt by the weapon's Epic Fight innate skill -----
  const innate = event.source.is(TT_INNATE)

  // Ember Hook (Ashfang Karambit, innate = Eviscerate): fire 3s; the next normal hit within 2s deals +50% (the "crit")
  if (held == 'tt:ashfang_karambit') ttSafe('ember_hook', () => {
    const pd = p.persistentData
    if (innate) { t.setSecondsOnFire(3); pd.putLong('tt_ember_until', now + 40) }
    else if (now <= pd.getLong('tt_ember_until')) { pd.putLong('tt_ember_until', 0); ttBonus(event.server, t, event.damage * 0.5) }
  })

  // Rallying Strike (Accord Longsword, innate = Sharp Stab / Liechtenauer): Strength I + Resistance I 6s to you, players
  // and tamed animals within 8 blocks. Once per second so multi-hit skills don't stack. MineColonies guards: tt_bridge.
  if (held == 'tt:accord_longsword' && innate) ttSafe('rallying_strike', () => {
    const pd = p.persistentData
    if (now < pd.getLong('tt_rally_cd')) return
    pd.putLong('tt_rally_cd', now + 20)
    p.level.getEntitiesWithin(p.boundingBox.inflate(8)).forEach(a => {
      if (a.isLiving() && (a == p || a.isPlayer() || (a.owner && a.owner == p))) {
        a.potionEffects.add('minecraft:strength', 120, 0)
        a.potionEffects.add('minecraft:resistance', 120, 0)
      }
    })
  })

  // Briar Line (Thornwatch Halberd, innate = Heartpiercer / Grasping Spire): Slowness II 5s + 2 damage per second for 5s.
  // The persistent 6-block thorn line on the ground needs tt_bridge.
  if (held == 'tt:thornwatch_halberd' && innate) ttSafe('briar_line', () => {
    t.potionEffects.add('minecraft:slowness', 100, 1)
    for (let i = 1; i <= 5; i++) event.server.scheduleInTicks(20 * i - 1, () => ttBonus(event.server, t, 2))
  })

  // Soul Severance (Hollowbane Tachi, innate = Rushing Tempo): strip invisibility; +100% vs entities in TT_HOLLOWED.
  if (held == 'tt:hollowbane_tachi' && innate) ttSafe('soul_severance', () => {
    t.removeEffect($TT_MobEffects.INVISIBILITY)
    if (TT_HOLLOWED.includes(String(t.type))) ttBonus(event.server, t, event.damage)
  })

  // Flame Wake (Cinder Crown, innate = Steel Whirlwind): every enemy the skill hits burns 5s. The 10-block flame line
  // on the ground needs tt_bridge.
  if (held == 'tt:cinder_crown' && innate) ttSafe('flame_wake', () => t.setSecondsOnFire(5))

  // Pack Mark (Gnawblade): mark target 8s (glowing). Rat focus-fire is added by tt_bridge once Rats is in the pack.
  if (held == 'tt:gnawblade') ttSafe('pack_mark', () => {
    t.potionEffects.add('minecraft:glowing', 160, 0)
    d.putLong('tt_pack_mark_until', now + 160)
  })
})
