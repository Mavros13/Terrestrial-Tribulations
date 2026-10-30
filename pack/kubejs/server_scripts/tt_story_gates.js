// Terrestrial Tribulations: story gates (hand-written).
// Gated items (configured in kubejs/config/tt_story_gates.json) can't be worn or right-click used until the player
// has the gate's KubeJS stage. Quests grant stages with a command reward: /kubejs stages add @p <stage>
// Also exports every loaded item namespace (with counts) to kubejs/exported/tt_item_namespaces.json, so we can
// look up the real namespaces of the Palladium hero packs and other mods after the first launch.

let TT_GATES = []
// Server scripts share one scope with the Palladium addon packs' scripts; FSang18's Heroes (random_power.js) already declares `cfg`.
// KubeJS' Rhino also throws "redeclaration of var" for const inside try blocks, so declare outside them and only assign inside.
let ttGatesCfg = null
try {
  ttGatesCfg = JsonIO.read('kubejs/config/tt_story_gates.json')
  if (ttGatesCfg && ttGatesCfg.gates) TT_GATES = ttGatesCfg.gates
} catch (e) { console.error(`[TT] could not read tt_story_gates.json: ${e}`) }

function ttGateFor(id) {
  if (!id || id == 'minecraft:air') return null
  const ns = String(id).split(':')[0]
  for (const g of TT_GATES) {
    if ((g.items && g.items.indexOf(String(id)) >= 0) || (g.namespaces && g.namespaces.indexOf(ns) >= 0)) return g
  }
  return null
}

ServerEvents.loaded(event => {
  let counts = {}
  try {
    Ingredient.all.itemIds.forEach(id => { let ns = String(id).split(':')[0]; counts[ns] = (counts[ns] || 0) + 1 })
    JsonIO.write('kubejs/exported/tt_item_namespaces.json', counts)
    console.info(`[TT] exported ${Object.keys(counts).length} item namespaces`)
  } catch (e) { console.error(`[TT] namespace export failed: ${e}`) }
})

const TT_ARMOR_SLOTS = ['head', 'chest', 'legs', 'feet']

// "You can now..." hints: each item or dimension gate's "unlocked" line, told once per player the first time they
// hold the gate's stage (a flag in the player's persistent data, so it survives relogs).
let TT_UNLOCK_HINTS = []
try {
  let ttDims = ttGatesCfg && ttGatesCfg.dimension_gates ? ttGatesCfg.dimension_gates.gates : []
  TT_GATES.concat(ttDims || []).forEach(g => { if (g.stage && g.unlocked) TT_UNLOCK_HINTS.push(g) })
} catch (e) { console.error(`[TT] unlock hints failed: ${e}`) }

PlayerEvents.tick(event => {
  const p = event.player
  if (TT_UNLOCK_HINTS.length == 0 || TT_TICK % 40 != 7) return
  try {
    TT_UNLOCK_HINTS.forEach(g => {
      let flag = `tt_hint_${g.stage}`
      if (p.stages.has(g.stage) && !p.persistentData.getBoolean(flag)) {
        p.persistentData.putBoolean(flag, true)
        p.tell(Text.gold(g.unlocked))
        p.server.runCommandSilent(`execute at ${p.username} run playsound minecraft:ui.toast.challenge_complete player ${p.username} ~ ~ ~ 0.6 1`)
      }
    })
  } catch (e) { console.error(`[TT] unlock hint failed: ${e}`) }
})

PlayerEvents.tick(event => {
  const p = event.player
  if (TT_GATES.length == 0 || TT_TICK % 20 != 0) return
  try {
    for (let slot of TT_ARMOR_SLOTS) {
      let stack = p.getItemBySlot(slot)
      let g = ttGateFor(stack.id)
      if (g && !p.stages.has(g.stage)) {
        p.setItemSlot(slot, Item.empty)
        p.give(stack)
        p.setStatusMessage(Text.red(g.message))
      }
    }
  } catch (e) { console.error(`[TT] gate tick failed: ${e}`) }
})

ItemEvents.rightClicked(event => {
  const g = ttGateFor(event.item.id)
  if (g && !event.player.stages.has(g.stage)) {
    event.player.setStatusMessage(Text.red(g.message))
    event.cancel()
  }
})
