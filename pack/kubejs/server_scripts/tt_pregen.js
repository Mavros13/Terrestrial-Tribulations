// Terrestrial Tribulations: one-time spawn pre-generation (hand-written).
// Terralith plus the structure mods make first-time terrain generation the pack's main stutter (docs/00-kickoff.md,
// risk R1). Once per world, a minute after it first loads, this asks Chunky to pre-generate a square around world
// spawn (kubejs/config/tt_pregen.json). Chunky works in the background and keeps going across restarts; players
// can stop it with /chunky pause or /chunky cancel.

let ttPregenCfg = null
try {
  ttPregenCfg = JsonIO.read('kubejs/config/tt_pregen.json')
} catch (e) { console.error(`[TT] could not read tt_pregen.json: ${e}`) }

// Tells players and the log when Chunky's run finishes. Chunky's API (ChunkyAPI.onGenerationComplete) fires on its own
// thread, so the work is handed to the server thread. A /reload subscribes again; the done flag keeps it to one message.
function ttPregenWatch(server) {
  try {
    let chunky = Java.loadClass('org.popcraft.chunky.ChunkyProvider').get()
    chunky.getApi().onGenerationComplete(ev => server.execute(() => {
      if (server.persistentData.getBoolean('tt_pregen_done') || String(ev.world()) != 'minecraft:overworld') return
      server.persistentData.putBoolean('tt_pregen_done', true)
      server.tell(Text.gray('[Terrestrial Tribulations] The land around spawn is ready. Exploring nearby should be smooth now.'))
      console.info('[TT] pre-generation finished')
    }))
  } catch (e) { console.warn(`[TT] can't watch Chunky for the end of pre-generation: ${e}`) }
}

ServerEvents.loaded(event => {
  const server = event.server
  if (!ttPregenCfg || !ttPregenCfg.enabled || !Platform.isLoaded('chunky')) return
  // Chunky's API only exists once Chunky has started with the server, a moment after this event (2026-10-29 test)
  if (!server.persistentData.getBoolean('tt_pregen_done')) server.scheduleInTicks(100, () => ttPregenWatch(server))
  if (server.persistentData.getBoolean('tt_pregen_started')) return
  const radius = Math.max(128, Math.floor(ttPregenCfg.radius || 768))
  server.scheduleInTicks(20 * Math.max(5, Math.floor(ttPregenCfg.delay_seconds || 60)), () => {
    server.persistentData.putBoolean('tt_pregen_started', true)
    server.runCommandSilent('chunky world minecraft:overworld')
    server.runCommandSilent('chunky spawn')
    server.runCommandSilent(`chunky radius ${radius}`)
    server.runCommandSilent('chunky quiet 60')
    server.runCommandSilent('chunky start')
    server.tell(Text.gray(`[Terrestrial Tribulations] Pre-generating the land around spawn (${radius} blocks) in the background. `
      + 'It may stutter for a few minutes. /chunky pause stops it.'))
    console.info(`[TT] pre-generation started: radius ${radius} around spawn`)
  })
})
