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

PlayerEvents.tick(event => {
  const p = event.player
  if (TT_GATES.length == 0 || p.level.gameTime % 20 != 0) return
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
