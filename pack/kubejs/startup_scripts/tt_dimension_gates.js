// Terrestrial Tribulations: dimension gates (hand-written). Players without a gate's KubeJS stage can't travel into
// its dimensions; the portal simply doesn't fire and they get the gate's message on the action bar. Gates live in
// kubejs/config/tt_story_gates.json ("dimension_gates"). ForgeEvents only works in startup scripts.
// Event checked against Forge 1.20.1: net.minecraftforge.event.entity.EntityTravelToDimensionEvent is cancelable and
// is posted from Entity/ServerPlayer.changeDimension (ForgeHooks.onTravelToDimension), which every portal mod uses.
// DRAFT: untested in-game.

let ttDimGates = null
function ttLoadDimGates() {
  ttDimGates = []
  try {
    let cfg = JsonIO.read('kubejs/config/tt_story_gates.json')
    let dg = cfg ? cfg.dimension_gates : null
    if (dg && dg.enabled && dg.gates) ttDimGates = dg.gates
  } catch (e) {
    console.error(`[TT] could not read dimension gates: ${e}`)
  }
}

ForgeEvents.onEvent('net.minecraftforge.event.entity.EntityTravelToDimensionEvent', event => {
  let gate = null
  try {
    let p = event.getEntity()
    if (!p || !p.isPlayer() || p.isCreative() || p.isSpectator()) return
    if (ttDimGates == null) ttLoadDimGates()
    let dim = String(event.getDimension().location())
    for (let g of ttDimGates) {
      if (g.dimensions.indexOf(dim) >= 0 && !p.stages.has(g.stage)) { gate = g; break }
    }
    if (gate) {
      let now = Math.floor(Date.now() / 50)
      if (now >= p.persistentData.getLong('tt_dimgate_msg')) {
        p.setStatusMessage(Text.of(gate.message).gold())
        p.persistentData.putLong('tt_dimgate_msg', now + 60)
      }
    }
  } catch (e) {
    console.error(`[TT] dimension gate failed: ${e}`)
  }
  if (gate) event.setCanceled(true)
})
