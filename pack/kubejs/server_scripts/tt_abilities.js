// Terrestrial Tribulations: weapon abilities that KubeJS can do on its own (impl = KJS in weapons.json).
// Abilities marked EDP (Epic Fight skill data) or BRIDGE (tt_bridge mod) are NOT here.
// DRAFT: untested in-game. Every handler is wrapped so that one failure can't break the others.

const TT_FOOD = { 'minecraft:cow': 'minecraft:beef', 'minecraft:pig': 'minecraft:porkchop', 'minecraft:sheep': 'minecraft:mutton',
  'minecraft:chicken': 'minecraft:chicken', 'minecraft:rabbit': 'minecraft:rabbit' }

function ttSafe(name, fn) {
  try { fn() } catch (e) { console.error(`[TT] ability ${name} failed: ${e}`) }
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
      t.attack(6)
    } else d.putInt('tt_rime', stacks)
  })

  // Three Heads (Hydra's Tri-Edge): every 3rd consecutive hit (within 3s) -> 3x3 dmg + Poison II 4s
  if (held == 'tt:hydras_tri_edge') ttSafe('three_heads', () => {
    const count = (now - d.getLong('tt_hydra_last') > 60) ? 1 : d.getInt('tt_hydra') + 1
    d.putLong('tt_hydra_last', now)
    if (count >= 3) {
      d.putInt('tt_hydra', 0)
      t.attack(3); t.attack(3); t.attack(3)
      t.potionEffects.add('minecraft:poison', 80, 1)
    } else d.putInt('tt_hydra', count)
  })

  // Echo Strike (Sculkheart Dagger): after 1s, repeat 50% of the damage
  if (held == 'tt:sculkheart_dagger') ttSafe('echo_strike', () => {
    const echo = event.damage * 0.5
    event.server.scheduleInTicks(20, () => { if (t.isAlive()) t.attack(echo) })
  })

  // Harvest of Gloom (Undergloom Scythe): 3+ enemies hit by the same swing (same tick) -> heal 2 HP each, max once per 2s
  if (held == 'tt:undergloom_scythe') ttSafe('harvest_of_gloom', () => {
    const pd = p.persistentData
    const count = pd.getLong('tt_gloom_tick') == now ? pd.getInt('tt_gloom_n') + 1 : 1
    pd.putLong('tt_gloom_tick', now); pd.putInt('tt_gloom_n', count)
    if (count == 3 && now >= pd.getLong('tt_gloom_cd')) { p.heal(6); pd.putLong('tt_gloom_cd', now + 40); pd.putBoolean('tt_gloom_on', true) }
    else if (count > 3 && pd.getBoolean('tt_gloom_on') && pd.getLong('tt_gloom_cd') == now + 40) p.heal(2)
  })

  // Pack Mark (Gnawblade): mark target 8s (glowing). Rat focus-fire is added by tt_bridge once Rats is in the pack.
  if (held == 'tt:gnawblade') ttSafe('pack_mark', () => {
    t.potionEffects.add('minecraft:glowing', 160, 0)
    d.putLong('tt_pack_mark_until', now + 160)
  })
})
