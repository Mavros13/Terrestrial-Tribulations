// Terrestrial Tribulations: one-time spawn pre-generation (hand-written).
// Terralith plus the structure mods make first-time terrain generation the pack's main stutter (docs/00-kickoff.md,
// risk R1). Once per world, a minute after it first loads, this asks Chunky to pre-generate a square around world
// spawn (kubejs/config/tt_pregen.json). Chunky works in the background and keeps going across restarts; players
// can stop it with /chunky pause or /chunky cancel.

let ttPregenCfg = null
try {
  ttPregenCfg = JsonIO.read('kubejs/config/tt_pregen.json')
} catch (e) { console.error(`[TT] could not read tt_pregen.json: ${e}`) }

ServerEvents.loaded(event => {
  const server = event.server
  if (!ttPregenCfg || !ttPregenCfg.enabled || !Platform.isLoaded('chunky')) return
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
