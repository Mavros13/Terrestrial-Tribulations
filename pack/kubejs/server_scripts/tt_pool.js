// Terrestrial Tribulations: Pool and Billiards support (hand-written). The data pack itself lives in kubejs/data/
// (app, math, pool; imported by tools/import_pool.py). Its author recommends a longer command chain for the ball
// physics, so each world gets it once on first load. Players open the pool menu with /trigger swPool__trigger set 1.
ServerEvents.loaded(event => {
  const server = event.server
  if (server.persistentData.getBoolean('tt_pool_gamerule')) return
  server.persistentData.putBoolean('tt_pool_gamerule', true)
  server.runCommandSilent('gamerule maxCommandChainLength 131072')
  console.info('[TT] pool: maxCommandChainLength set to 131072')
})
