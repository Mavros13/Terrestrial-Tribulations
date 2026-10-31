// Terrestrial Tribulations: other mods' Forge events (hand-written). ForgeEvents only works in startup scripts; each
// handler just leaves a mark on the player that server scripts (tt_active_abilities.js) act on.
// DRAFT: untested in-game.

// Prism Ward (Prism Ward Staff): casting any Iron's spell with the staff in either hand raises a 3 s barrier that
// reflects the next projectile (10 s cooldown). Event and getters checked against Iron's 1.20.1 source
// (io.redspace.ironsspellbooks.api.events.SpellOnCastEvent, posted on the Forge bus by AbstractSpell).
ForgeEvents.onEvent('io.redspace.ironsspellbooks.api.events.SpellOnCastEvent', event => {
  try {
    let p = event.getEntity()
    if (!p || p.level.isClientSide()) return
    if (p.mainHandItem.id != 'tt:prism_ward_staff' && p.offHandItem.id != 'tt:prism_ward_staff') return
    let pd = p.persistentData
    let now = Math.floor(Date.now() / 50)
    if (now < pd.getLong('tt_prism_cd')) return
    pd.putLong('tt_prism_until', now + 60)
    pd.putLong('tt_prism_cd', now + 200)
    p.level.server.runCommandSilent(`execute in ${p.level.dimension} run particle minecraft:end_rod ${p.x} ${p.y + 1} ${p.z} 0.6 0.9 0.6 0.01 40 force`)
    p.level.server.runCommandSilent(`execute in ${p.level.dimension} run playsound minecraft:block.amethyst_block.resonate player @a ${p.x} ${p.y} ${p.z} 1 1.4`)
  } catch (e) {
    console.error(`[TT] prism_ward failed: ${e}`)
  }
})
