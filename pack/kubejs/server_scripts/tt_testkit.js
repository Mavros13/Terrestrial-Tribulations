// Terrestrial Tribulations: in-game test shortcuts (hand-written). Cheats/operator only (KubeJS custom commands need op).
// Test-only: listed in tools/dev_only.txt, so the release build (build_curseforge.py --release) leaves it out.
//   /kubejs custom_command tt_kit    every tt weapon + arrows, unlocks the hero and realm stages, daytime
//   /kubejs custom_command tt_npcs   places the 9 story NPCs in a row in front of you (docs/09-story-npcs.md),
//                                    replacing story NPCs already within 64 blocks
//   /kubejs custom_command tt_story  unlocks every chapter's NPC conversations (adds the tt_ch2..12_done stages) and opens every NPC site (tt_meet_*)
//   /kubejs custom_command tt_mobs   6 zombies and 2 skeletons around you, for weapon and ability tests
//   /kubejs custom_command tt_boss   the Wither (boss lore test: "Echo of the Sundering")
//   /kubejs custom_command tt_clear  removes the test mobs and bosses within 64 blocks
// The weapon list is the self-test's (kubejs/config/tt_selftest.json, generated from design/weapons/weapons.json).

const TT_KIT_NPCS = ['humanoid_slim/maera', 'humanoid/doran', 'humanoid/rhosk', 'humanoid/pell', 'humanoid_slim/tamsin',
  'humanoid_slim/ilsabet', 'humanoid/stranger', 'humanoid_slim/wren', 'humanoid/sol']

function ttKitPlayer(event) {
  let p = null
  try { p = event.player } catch (e) { p = null }
  if (!p) p = event.server.players.length ? event.server.players[0] : null
  return p
}

function ttKitRun(event, name, fn) {
  let p = ttKitPlayer(event)
  if (!p) { console.warn(`[TT] ${name}: no player`); return }
  try { fn(p, (cmd) => event.server.runCommandSilent(cmd)); p.tell(`§a[TT] ${name} done`) }
  catch (e) { console.error(`[TT] ${name} failed: ${e}`); p.tell(`§c[TT] ${name} failed: ${e}`) }
}

ServerEvents.customCommand('tt_kit', event => ttKitRun(event, 'tt_kit', (p, run) => {
  let cfg = JsonIO.read('kubejs/config/tt_selftest.json')
  cfg.items.forEach(id => p.give(Item.of(String(id))))
  p.give(Item.of('minecraft:arrow', 64))
  ;['tt_ch7_realms', 'tt_ch8_heroes', 'tt_ch9_marks', 'tt_ch10_echoes'].forEach(s => p.stages.add(s))
  run('time set day')
  run('weather clear')
}))

ServerEvents.customCommand('tt_npcs', event => ttKitRun(event, 'tt_npcs', (p, run) => {
  let x = Math.floor(p.x), y = Math.floor(p.y), z = Math.floor(p.z) + 5
  ;['humanoid', 'humanoid_slim'].forEach(t => run(`execute as ${p.username} at @s run kill @e[type=easy_npc:${t},distance=..64]`))
  TT_KIT_NPCS.forEach((n, i) => run(`easy_npc preset import_new data tt:easy_npc/preset/${n}.npc.snbt ${x - 8 + i * 2} ${y} ${z}`))
}))

ServerEvents.customCommand('tt_mobs', event => ttKitRun(event, 'tt_mobs', (p, run) => {
  let x = Math.floor(p.x), y = Math.floor(p.y), z = Math.floor(p.z)
  ;[[6, 0], [-6, 0], [0, 6], [0, -6], [5, 5], [-5, -5]].forEach(o => run(`summon minecraft:zombie ${x + o[0]} ${y} ${z + o[1]}`))
  ;[[7, -4], [-7, 4]].forEach(o => run(`summon minecraft:skeleton ${x + o[0]} ${y} ${z + o[1]}`))
}))

ServerEvents.customCommand('tt_boss', event => ttKitRun(event, 'tt_boss', (p, run) => {
  run(`summon minecraft:wither ${Math.floor(p.x)} ${Math.floor(p.y) + 3} ${Math.floor(p.z) + 12}`)
}))

ServerEvents.customCommand('tt_story', event => ttKitRun(event, 'tt_story', (p, run) => {
  for (let n = 2; n <= 12; n++) p.stages.add('tt_ch' + n + '_done')
  ;['rhosk', 'pell', 'tamsin', 'ilsabet', 'stranger', 'wren', 'sol'].forEach(n => p.stages.add('tt_meet_' + n))
}))

ServerEvents.customCommand('tt_clear', event => ttKitRun(event, 'tt_clear', (p, run) => {
  ;['zombie', 'skeleton', 'wither', 'wither_skull'].forEach(t =>
    run(`execute as ${p.username} at @s run kill @e[type=minecraft:${t},distance=..64]`))
}))
