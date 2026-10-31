// Terrestrial Tribulations: weapon abilities that KubeJS can do on its own (impl = KJS in weapons.json).
// Active abilities (sneak + use) and the BRIDGE abilities KubeJS can do are in tt_active_abilities.js; the rest wait for tt_bridge.
// INNATE weapons (impl in weapons.json): each one uses a built-in Epic Fight innate skill for the motion (its family's,
// or one named in a custom weapon type, see build_content.py TYPE_TEMPLATES) and the ability is added here as a "rider"
// on the hits that skill deals. Epic Fight tags those hits with the runtime damage tag epicfight:weapon_innate
// (EpicFightSkills, 1.20.1 source). See docs/research/2026-10-27-epic-fight-data-formats.md.
// DRAFT: untested in-game. Every handler is wrapped so that one failure can't break the others.

const TT_FOOD = { 'minecraft:cow': 'minecraft:beef', 'minecraft:pig': 'minecraft:porkchop', 'minecraft:sheep': 'minecraft:mutton',
  'minecraft:chicken': 'minecraft:chicken', 'minecraft:rabbit': 'minecraft:rabbit' }

// Prefixed names: all server scripts (ours and the hero packs') share one global scope.
const $TT_TagKey = Java.loadClass('net.minecraft.tags.TagKey')
const $TT_Registries = Java.loadClass('net.minecraft.core.registries.Registries')
const $TT_ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
const $TT_MobEffects = Java.loadClass('net.minecraft.world.effect.MobEffects')
const TT_INNATE = $TT_TagKey.create($TT_Registries.DAMAGE_TYPE, new $TT_ResourceLocation('epicfight', 'weapon_innate'))
// Entity IDs that count as "Hollowed" for Soul Severance: the undead Hollowed and the Hollow bosses (boss-roles.md).
const TT_HOLLOWED = ['minecraft:zombie', 'minecraft:husk', 'minecraft:drowned', 'minecraft:zombie_villager',
  'bosses_of_mass_destruction:lich', 'mowziesmobs:umvuthi', 'cataclysm:scylla']

// Time in ticks for cooldowns and timers. Level game time (the gameTime bean) reads as undefined from KubeJS on 1.20.1 (2026-10-30 desktop
// test: every cooldown write threw "Cannot convert NaN to java.lang.Long"), so this counts 50 ms wall-clock ticks. It
// keeps rising across restarts, so stored cooldowns stay valid. Shared by every server script (one global scope).
// Blink behind a target and turn to face it (Ashfang Karambit's Ember Hook, Crownshard Karambits' Shard Rend). ServerPlayer's six-argument
// teleportTo sets the view too; the three-argument one kept the old facing (2026-10-30 desktop test: facing away).
function ttBlinkBehind(p, t) {
  let x = t.x - t.lookAngle.x() * 1.2
  let z = t.z - t.lookAngle.z() * 1.2
  let dx = t.x - x, dz = t.z - z
  let dy = (t.y + t.eyeHeight * 0.8) - (t.y + p.eyeHeight)
  let yaw = Math.atan2(-dx, dz) * 180 / Math.PI
  let pitch = -Math.atan2(dy, Math.max(0.1, Math.sqrt(dx * dx + dz * dz))) * 180 / Math.PI
  p.teleportTo(p.level, x, t.y, z, yaw, pitch)
}

function ttNow() {
  return Math.floor(Date.now() / 50)
}

// Server ticks since start, for "every N ticks" checks inside per-player tick handlers (same value for every player in
// one tick, never skips a tick the way wall-clock time can under lag).
let TT_TICK = 0
ServerEvents.tick(event => { TT_TICK++ })

function ttSafe(name, fn) {
  try { fn() } catch (e) { console.error(`[TT] ability ${name} failed: ${e}`) }
}

// Extra damage on top of a hit. Damage dealt inside the hurt event is swallowed by the target's invulnerability frames
// (vanilla sets them before the event fires), so it lands one tick later with the frames cleared.
function ttBonus(server, target, amount) {
  server.scheduleInTicks(1, () => {
    if (!target.isAlive()) return
    target.invulnerableTime = 0
    target.attack(amount)
  })
}

// A line on the ground from the player along their horizontal facing, `len` blocks long.
// step 20: the whole line at once, pulsing once a second for `seconds`. Smaller step: a wave that lights one more block
// every `step` ticks and hits each enemy once. onHit runs for each enemy standing on a lit part (enemies as in
// ttEnemiesNear, tt_active_abilities.js: living, not the player, not other players, not the player's pets).
function ttGroundLine(p, len, seconds, particle, step, onHit) {
  const level = p.level, server = p.level.server
  const yaw = p.getYRot() * Math.PI / 180
  const dx = -Math.sin(yaw), dz = Math.cos(yaw)
  const sx = p.x, sy = p.y, sz = p.z
  const wave = step < 20
  const hitOnce = {}
  // a function per pulse, so each closure keeps its own k (Rhino's for-let doesn't make one binding per loop)
  const pulse = k => () => ttSafe('ground_line', () => {
    const from = wave ? k + 0.5 : 0.5, to = wave ? k + 1.5 : len + 0.5
    for (let d = from; d < to; d += 0.5) ttParticle(level, particle, sx + dx * d, sy + 0.15, sz + dz * d, 0.15, wave ? 4 : 2)
    ttEnemiesNear(p, sx + dx * (from + to) / 2, sy + 1, sz + dz * (from + to) / 2, (to - from) / 2 + 1).forEach(e => {
      // where the enemy is along the line and how far off it
      const ex = e.x - sx, ez = e.z - sz
      const along = ex * dx + ez * dz, across = Math.abs(ex * dz - ez * dx)
      if (along < from - 0.5 || along > to || across > e.bbWidth / 2 + 0.7 || Math.abs(e.y - sy) > 2) return
      if (wave) { let id = String(e.uuid); if (hitOnce[id]) return; hitOnce[id] = true }
      onHit(e)
    })
  })
  for (let k = 0; k < (wave ? len : seconds); k++) server.scheduleInTicks(k * (wave ? step : 20), pulse(k))
}

// Scavenger's Edge (Frontier Cleaver)
// Thorn displays left behind if the server stopped while a Briar Line was up
ServerEvents.loaded(event => event.server.runCommandSilent('kill @e[type=minecraft:block_display,tag=tt_briar]'))

EntityEvents.death(event => ttSafe('scavengers_edge', () => {
  const p = event.source.player
  if (!p || p.mainHandItem.id != 'tt:frontier_cleaver') return
  const e = event.entity
  const food = TT_FOOD[e.type]
  if (food) e.block.popItem(food)
  else if (e.isMonster() && Math.random() < 0.10) e.block.popItem('tt:bone_shard')
}))

EntityEvents.hurt(event => {
  const p = event.source.player
  if (!p) return
  const t = event.entity
  const held = p.mainHandItem.id
  const now = ttNow()
  const d = t.persistentData

  // Rime Mark (Frostmaw Fang): 5 stacks -> freeze 1.5s + 6 dmg; 10s per-target cooldown
  if (held == 'tt:frostmaw_fang') ttSafe('rime_mark', () => {
    if (now < d.getLong('tt_rime_cd')) return
    const stacks = d.getInt('tt_rime') + 1
    if (stacks >= 5) {
      d.putInt('tt_rime', 0)
      d.putLong('tt_rime_cd', now + 200)
      t.potionEffects.add('minecraft:slowness', 30, 9)
      t.potionEffects.add('minecraft:weakness', 30, 2)
      ttBonus(event.server, t, 6)
    } else d.putInt('tt_rime', stacks)
  })

  // Three Heads (Hydra's Tri-Edge): every 3rd consecutive hit (within 3s) -> 3x3 dmg + Poison II 4s
  if (held == 'tt:hydras_tri_edge') ttSafe('three_heads', () => {
    const count = (now - d.getLong('tt_hydra_last') > 60) ? 1 : d.getInt('tt_hydra') + 1
    d.putLong('tt_hydra_last', now)
    if (count >= 3) {
      d.putInt('tt_hydra', 0)
      ttBonus(event.server, t, 9)
      t.potionEffects.add('minecraft:poison', 80, 1)
    } else d.putInt('tt_hydra', count)
  })

  // Echo Strike (Sculkheart Dagger): after 1s, repeat 50% of the damage
  if (held == 'tt:sculkheart_dagger') ttSafe('echo_strike', () => {
    const echo = event.damage * 0.5
    event.server.scheduleInTicks(19, () => ttBonus(event.server, t, echo))
  })

  // Harvest of Gloom (Undergloom Scythe): 3+ enemies hit by the same swing (same tick) -> heal 2 HP each, max once per 2s
  if (held == 'tt:undergloom_scythe') ttSafe('harvest_of_gloom', () => {
    const pd = p.persistentData
    const count = pd.getLong('tt_gloom_tick') == now ? pd.getInt('tt_gloom_n') + 1 : 1
    pd.putLong('tt_gloom_tick', now); pd.putInt('tt_gloom_n', count)
    if (count == 3 && now >= pd.getLong('tt_gloom_cd')) { p.heal(6); pd.putLong('tt_gloom_cd', now + 40); pd.putBoolean('tt_gloom_on', true) }
    else if (count > 3 && pd.getBoolean('tt_gloom_on') && pd.getLong('tt_gloom_cd') == now + 40) p.heal(2)
  })

  // ----- INNATE riders: only on hits dealt by the weapon's Epic Fight innate skill -----
  const innate = event.source.is(TT_INNATE)

  // Ember Hook (Ashfang Karambit, Eviscerate): the first skill hit hooks you behind the target and sets it on fire for
  // 3 s; your next normal hit within 2 s deals +50% (the "crit").
  if (held == 'tt:ashfang_karambit') ttSafe('ember_hook', () => {
    const pd = p.persistentData
    if (innate) {
      t.setSecondsOnFire(3)
      if (now > pd.getLong('tt_ember_until')) event.server.scheduleInTicks(2, () => ttSafe('ember_hook_move', () => {
        if (!p.isAlive() || !t.isAlive()) return
        ttParticle(p.level, 'minecraft:flame', p.x, p.y + 1, p.z, 0.3, 12)
        ttBlinkBehind(p, t)
        ttSound(p.level, 'minecraft:item.firecharge.use', t.x, t.y, t.z, 1.4)
      }))
      pd.putLong('tt_ember_until', now + 40)
    }
    else if (now <= pd.getLong('tt_ember_until')) { pd.putLong('tt_ember_until', 0); ttBonus(event.server, t, event.damage * 0.5) }
  })

  // Rallying Strike (Accord Longsword, The Guillotine; Sharp Stab with a shield): Strength I + Resistance I 6s to you,
  // players, tamed animals and the citizens and guards of your own MineColonies colony (ttColony, tt_active_abilities.js)
  // within 8 blocks. Once per second so multi-hit skills don't stack.
  if (held == 'tt:accord_longsword' && innate) ttSafe('rallying_strike', () => {
    const pd = p.persistentData
    if (now < pd.getLong('tt_rally_cd')) return
    pd.putLong('tt_rally_cd', now + 20)
    const colony = ttColony(p)
    p.level.getEntitiesWithin(p.boundingBox.inflate(8)).forEach(a => {
      const citizen = colony && String(a.type) == 'minecolonies:citizen' && colony.isCoordInColony(a.level, a.blockPosition())
      if (a.isLiving() && (a == p || a.isPlayer() || (a.owner && a.owner == p) || citizen)) {
        a.potionEffects.add('minecraft:strength', 120, 0)
        a.potionEffects.add('minecraft:resistance', 120, 0)
      }
    })
    ttSound(p.level, 'minecraft:event.raid.horn', p.x, p.y, p.z, 1.6)
  })

  // Briar Line (Thornwatch Halberd, Grasping Spire / Heartpiercer): the target is slowed (Slowness II 5 s), and the first
  // skill hit plants a 6-block thorn line along your facing for 5 s: 2 damage per second and Slowness II to enemies on it.
  if (held == 'tt:thornwatch_halberd' && innate) ttSafe('briar_line', () => {
    t.potionEffects.add('minecraft:slowness', 100, 1)
    const pd = p.persistentData
    if (now < pd.getLong('tt_briar_cd')) return
    pd.putLong('tt_briar_cd', now + 40)
    ttGroundLine(p, 6, 5, 'minecraft:composter', 20, e => {
      e.invulnerableTime = 0
      e.attack(2)
      e.potionEffects.add('minecraft:slowness', 30, 1)
    })
    ttSound(p.level, 'minecraft:block.sweet_berry_bush.place', p.x, p.y, p.z, 0.7)
    // Visible thorns (2026-10-30 desktop test: the particles alone were too faint to notice): a berry-bush display
    // entity on each block of the line, removed when the line ends. Display entities have no hitbox and drop nothing.
    const yaw = p.getYRot() * Math.PI / 180, tag = `tt_briar_${now}`
    for (let k = 1; k <= 6; k++) {
      const bx = p.x - Math.sin(yaw) * k, bz = p.z + Math.cos(yaw) * k
      p.level.server.runCommandSilent(`execute in ${p.level.dimension} run summon minecraft:block_display ${bx} ${Math.floor(p.y)} ${bz} `
        + `{block_state:{Name:"minecraft:sweet_berry_bush",Properties:{age:"3"}},Tags:["tt_briar","${tag}"],`
        + `transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-0.5f,0f,-0.5f],scale:[1f,1f,1f]}}`)
    }
    p.level.server.scheduleInTicks(100, () => p.level.server.runCommandSilent(`kill @e[type=minecraft:block_display,tag=${tag}]`))
  })

  // Soul Severance (Hollowbane Tachi, Rushing Tempo): strip invisibility; +100% vs entities in TT_HOLLOWED.
  if (held == 'tt:hollowbane_tachi' && innate) ttSafe('soul_severance', () => {
    t.removeEffect($TT_MobEffects.INVISIBILITY)
    if (TT_HOLLOWED.includes(String(t.type))) ttBonus(event.server, t, event.damage)
  })

  // Flame Wake (Cinder Crown, Steel Whirlwind): every enemy the skill hits burns 5 s, and the first hit sends a 10-block
  // wave of erupting flame along your facing: 4 damage and 5 s of fire to each enemy it reaches. No fire blocks placed.
  if (held == 'tt:cinder_crown' && innate) ttSafe('flame_wake', () => {
    t.setSecondsOnFire(5)
    const pd = p.persistentData
    if (now < pd.getLong('tt_wake_cd')) return
    pd.putLong('tt_wake_cd', now + 60)
    ttGroundLine(p, 10, 1, 'minecraft:flame', 2, e => {
      e.invulnerableTime = 0
      e.attack(4)
      e.setSecondsOnFire(5)
    })
    ttSound(p.level, 'minecraft:item.firecharge.use', p.x, p.y, p.z, 0.6)
  })

  // Pack Mark (Gnawblade): mark target 8s (glowing). Rat focus-fire is added by tt_bridge once Rats is in the pack.
  if (held == 'tt:gnawblade') ttSafe('pack_mark', () => {
    t.potionEffects.add('minecraft:glowing', 160, 0)
    d.putLong('tt_pack_mark_until', now + 160)
  })
})
