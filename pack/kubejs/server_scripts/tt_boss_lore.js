// Terrestrial Tribulations: boss lore (hand-written).
// Gives existing mod bosses their story names (boss bar; build_content.py also renames the entity types in every other
// place through lang overrides in kubejs/assets/<mod>/lang) and speaks their story lines to nearby players, from
// kubejs/config/tt_boss_lore.json. We never change the bosses' models or fights (design/story/boss-roles.md).

let TT_LORE = {}
let ttLoreCfg = null
try {
  ttLoreCfg = JsonIO.read('kubejs/config/tt_boss_lore.json')
  if (ttLoreCfg && ttLoreCfg.bosses) TT_LORE = ttLoreCfg.bosses
} catch (e) { console.error(`[TT] could not read tt_boss_lore.json: ${e}`) }

function ttLoreSay(entity, line) {
  if (!line) return
  const msg = String(line).replace(/&([0-9a-fk-or])/g, '§$1')
  entity.level.players.forEach(p => { if (p.distanceToEntity(entity) < 96) p.tell(msg) })
}

function ttLoreName(entity, lore) {
  const fn = Text[lore.color] || Text.white
  entity.setCustomName(fn(lore.name))
}

EntityEvents.spawned(event => {
  const e = event.entity
  const lore = TT_LORE[String(e.type)]
  if (!lore) return
  try {
    if (!e.persistentData.getBoolean('tt_lore')) {
      e.persistentData.putBoolean('tt_lore', true)
      // Always on the first spawn: some mods name their bosses themselves (the Aether's generated Valkyrie names), and
      // their boss bars follow setCustomName. Again a second later, in case the mod names it after joining the world.
      ttLoreName(e, lore)
      // Wait a tick so the boss is in the world (and players are near it) before it speaks
      event.server.scheduleInTicks(20, () => { if (e.isAlive()) { ttLoreName(e, lore); ttLoreSay(e, lore.intro) } })
    }
  } catch (err) { console.error(`[TT] boss lore spawn failed: ${err}`) }
})

EntityEvents.hurt(event => {
  const e = event.entity
  const lore = TT_LORE[String(e.type)]
  if (!lore || !lore.phases) return
  try {
    let frac = (e.health - event.damage) / e.maxHealth
    let pd = e.persistentData
    lore.phases.forEach((ph, i) => {
      if (frac <= ph.at && !pd.getBoolean(`tt_lore_p${i}`)) { pd.putBoolean(`tt_lore_p${i}`, true); ttLoreSay(e, ph.line) }
    })
  } catch (err) { console.error(`[TT] boss lore phase failed: ${err}`) }
})

EntityEvents.death(event => {
  const lore = TT_LORE[String(event.entity.type)]
  if (lore) try { ttLoreSay(event.entity, lore.death) } catch (err) { console.error(`[TT] boss lore death failed: ${err}`) }
})
