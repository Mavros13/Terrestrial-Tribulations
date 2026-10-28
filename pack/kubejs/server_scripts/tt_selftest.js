// Terrestrial Tribulations: self-test (hand-written). Run from the server console or in game (op):
//   /kubejs custom_command tt_selftest
// Checks that our content really loaded: every tt: weapon item exists, our Epic Fight weapon capabilities apply,
// our Palladium powers, origins and origin layers are registered, and every dimension-gate dimension exists (when its
// mod is installed). The expected lists come from kubejs/config/tt_selftest.json (tools/gen_selftest.py).
// Prints "[TT] selftest ..." lines to the log and writes kubejs/exported/tt_selftest.json. tools/server_test.ps1 runs
// it on the headless test server. Mod APIs checked against source: Epic Fight 1.20.1
// (EpicFightCapabilities.getItemStackCapability, CapabilityItem.isEmpty), Palladium 1.20/main
// (PowerManager.getInstance(Level).getPower(ResourceLocation)), Origins Forge (OriginsAPI.getOriginsRegistry/
// getLayersRegistry(MinecraftServer)).

function ttSelfTest(server) {
  let results = {}
  let total = { pass: 0, fail: 0 }
  let cfg = null
  try { cfg = JsonIO.read('kubejs/config/tt_selftest.json') } catch (e) { cfg = null }
  if (!cfg) {
    console.error('[TT] selftest FAIL could not read kubejs/config/tt_selftest.json')
    return
  }
  let RL = Java.loadClass('net.minecraft.resources.ResourceLocation')

  // name: section; list: ids; check(id) returns true, false, or a string (skip reason)
  function section(name, list, check) {
    let r = { pass: [], fail: [], skip: [] }
    let ids = []
    if (list) list.forEach(id => ids.push(String(id)))
    ids.forEach(id => {
      let ok = false
      try { ok = check(id) } catch (e) { ok = `error: ${e}` }
      if (ok === true) r.pass.push(id)
      else if (ok === false) r.fail.push(id)
      else r.skip.push(`${id} (${ok})`)
    })
    results[name] = r
    total.pass += r.pass.length
    total.fail += r.fail.length
    let line = `[TT] selftest ${r.fail.length ? 'FAIL' : 'PASS'} ${name}: ${r.pass.length}/${ids.length}`
    if (r.fail.length) line += ` missing: ${r.fail.join(', ')}`
    if (r.skip.length) line += ` skipped: ${r.skip.join('; ')}`
    if (r.fail.length) console.error(line)
    else console.info(line)
  }

  section('items', cfg.items, id => !Item.of(id).isEmpty())

  if (Platform.isLoaded('epicfight')) {
    let EFC = Java.loadClass('yesman.epicfight.world.capabilities.EpicFightCapabilities')
    section('epic_fight_weapons', cfg.ef_weapons, id => {
      let stack = Item.of(id)
      if (stack.isEmpty()) return 'item missing'
      return !EFC.getItemStackCapability(stack).isEmpty()
    })
  }

  if (Platform.isLoaded('palladium')) {
    let PM = Java.loadClass('net.threetag.palladium.power.PowerManager')
    section('palladium_powers', cfg.powers, id => PM.getInstance(server.getLevel('minecraft:overworld')).getPower(new RL(id)) != null)
  }

  if (Platform.isLoaded('origins')) {
    let OAPI = Java.loadClass('io.github.edwinmindcraft.origins.api.OriginsAPI')
    section('origins', cfg.origins, id => OAPI.getOriginsRegistry(server).containsKey(new RL(id)))
    section('origin_layers', cfg.layers, id => OAPI.getLayersRegistry(server).containsKey(new RL(id)))
  }

  section('gated_dimensions', cfg.dimensions, id => {
    let ns = id.split(':')[0]
    if (!Platform.isLoaded(ns)) return `mod ${ns} not installed`
    return server.getLevel(id) != null
  })

  console.info(`[TT] selftest done: ${total.pass} passed, ${total.fail} failed`)
  try {
    JsonIO.write('kubejs/exported/tt_selftest.json', { passed: total.pass, failed: total.fail, results: results })
  } catch (e) { console.error(`[TT] selftest could not write its report: ${e}`) }
}

ServerEvents.customCommand('tt_selftest', event => {
  try {
    ttSelfTest(event.server)
  } catch (e) {
    console.error(`[TT] selftest crashed: ${e}`)
  }
})
