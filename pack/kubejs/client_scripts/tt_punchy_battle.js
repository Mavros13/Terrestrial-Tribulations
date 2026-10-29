// Punchy only outside Epic Fight battle mode (owner, 2026-10-29: Punchy is "perfect" in normal first person, but in
// battle mode both mods draw the arms and every weapon shows twice; Epic Fight wins there).
// Punchy 2.8g: punchy.config.PunchyConfig.isModEnabled() is read every frame; snapshot() returns a copy of its config
// and applyAndSave(data) applies it and writes config/punchy/punchy_config.json, so we only call it when the mode changes.
// Epic Fight 20.14: yesman.epicfight.client.ClientEngine.getInstance().isBattleMode().
// If the game closes in battle mode, local/tt/punchy_battle.json remembers that we switched Punchy off, and it is
// switched back on at the next login. A player who turned Punchy off in its own menu is left alone.
let TT_PUNCHY = null
let TT_EF_CLIENT = null
try {
  TT_PUNCHY = Java.loadClass('punchy.config.PunchyConfig')
  TT_EF_CLIENT = Java.loadClass('yesman.epicfight.client.ClientEngine')
} catch (e) {
  console.info('[tt] Punchy battle-mode toggle off: ' + e)
}
let TT_PUNCHY_MARK = 'local/tt/punchy_battle.json'
let ttPunchyBattle = null // last battle state seen; null until the first tick in a world

function ttPunchySet(on) {
  let d = TT_PUNCHY.snapshot()
  if (d.enableMod == on) return
  d.enableMod = on
  TT_PUNCHY.applyAndSave(d)
}

function ttPunchyMarked() {
  let m = JsonIO.read(TT_PUNCHY_MARK)
  return m != null && m.disabledByTT == true
}

function ttPunchyMark(v) {
  JsonIO.write(TT_PUNCHY_MARK, { disabledByTT: v })
}

ClientEvents.tick(event => {
  if (TT_PUNCHY == null || TT_EF_CLIENT == null || Client.player == null) return
  let engine = TT_EF_CLIENT.getInstance()
  if (engine == null) return
  let battle = engine.isBattleMode() == true
  if (battle === ttPunchyBattle) return
  try {
    if (battle) {
      if (TT_PUNCHY.isModEnabled()) {
        ttPunchySet(false)
        ttPunchyMark(true)
      }
    } else if (ttPunchyMarked()) {
      ttPunchySet(true)
      ttPunchyMark(false)
    }
  } catch (e) {
    console.warn('[tt] Punchy battle-mode toggle: ' + e)
  }
  ttPunchyBattle = battle
})

ClientEvents.loggedOut(event => {
  ttPunchyBattle = null
})
