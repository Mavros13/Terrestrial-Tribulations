// Terrestrial Tribulations: the weapon abilities first planned for tt_bridge, done in KubeJS instead.
// Active abilities trigger on SNEAK + USE (right click while sneaking), because plain right click is Epic Fight's guard
// in battle mode. Each one puts the weapon on a real item cooldown, so the hotbar shows when it's ready.
// Other mods are reached through their Java APIs: Epic Fight's player event listener (dodge, parry; names checked
// against its 1.20.1 source), MineColonies' colony manager, and Iron's spell event (startup_scripts/tt_forge_events.js).
// Bows shoot through startup_scripts/tt_bows.js, which tags each arrow with its bow.
// Uses ttSafe and ttBonus from tt_abilities.js (all server scripts share one scope, so every name here starts with tt).
// DRAFT: untested in-game.

const $TT_AABB = Java.loadClass('net.minecraft.world.phys.AABB')
const $TT_BuiltInRegistries = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries')
const TT_BOSSES = $TT_TagKey.create($TT_Registries.ENTITY_TYPE, new $TT_ResourceLocation('forge', 'bosses'))

function ttParticle(level, type, x, y, z, spread, count) {
  level.server.runCommandSilent(`execute in ${level.dimension} run particle ${type} ${x} ${y} ${z} ${spread} ${spread} ${spread} 0.02 ${count} force`)
}

function ttSound(level, sound, x, y, z, pitch) {
  level.server.runCommandSilent(`execute in ${level.dimension} run playsound ${sound} player @a ${x} ${y} ${z} 1 ${pitch}`)
}

// Living, hostile-to-us entities near a point (not the player, not their pets, not other players)
function ttEnemiesNear(p, x, y, z, r) {
  const box = new $TT_AABB(x - r, y - r, z - r, x + r, y + r, z + r)
  const out = []  // a plain JS array, so callers can sort and slice
  p.level.getEntitiesWithin(box).forEach(e => {
    if (e.isLiving() && e != p && !e.isPlayer() && !(e.owner && e.owner == p) && e.isAlive()) out.push(e)
  })
  return out
}

function ttIsBoss(e) {
  return $TT_BuiltInRegistries.ENTITY_TYPE.get(new $TT_ResourceLocation(String(e.type))).is(TT_BOSSES)
}

function ttReady(event, ticks) {
  const p = event.player
  const item = p.mainHandItem.item
  if (p.cooldowns.isOnCooldown(item)) return false
  p.cooldowns.addCooldown(item, ticks)
  return true
}

ItemEvents.rightClicked(event => {
  const p = event.player
  if (String(event.hand) != 'MAIN_HAND' || !p.isShiftKeyDown()) return
  const held = event.item.id
  const level = p.level
  const server = event.server

  // Gale Vault (Skyreach Spear): launch about 8 blocks up. A hit while airborne turns into a plunge (see hurt below);
  // landing from a plunge slams everything within 4 blocks. No fall damage until you land.
  if (held == 'tt:skyreach_spear') ttSafe('gale_vault', () => {
    if (!ttReady(event, 280)) return
    p.push(0, 1.6, 0)
    p.hurtMarked = true
    p.persistentData.putBoolean('tt_vault', true)
    p.persistentData.putLong('tt_vault_at', level.gameTime)
    ttParticle(level, 'minecraft:cloud', p.x, p.y + 0.2, p.z, 0.6, 30)
    ttSound(level, 'minecraft:entity.phantom.flap', p.x, p.y, p.z, 0.8)
    ttSound(level, 'minecraft:item.trident.riptide_1', p.x, p.y, p.z, 1.2)
  })

  // Rail Lance (Harbinger's Railblade): 1.5 s charge with sparks at the blade, then a 20-block piercing beam, 12 damage
  // to everything on the line. Stops at the first solid block. Cancels if you switch items during the charge.
  if (held == 'tt:harbingers_railblade') ttSafe('rail_lance', () => {
    if (!ttReady(event, 360)) return
    ttSound(level, 'minecraft:block.beacon.power_select', p.x, p.y, p.z, 1.6)
    for (let i = 0; i < 30; i += 3) server.scheduleInTicks(i, () => {
      if (p.mainHandItem.id == 'tt:harbingers_railblade') ttParticle(level, 'minecraft:electric_spark', p.x, p.y + 1.1, p.z, 0.4, 6)
    })
    server.scheduleInTicks(30, () => ttSafe('rail_lance_fire', () => {
      if (!p.isAlive() || p.mainHandItem.id != 'tt:harbingers_railblade') return
      const look = p.lookAngle
      const sx = p.x, sy = p.eyeY - 0.2, sz = p.z
      let len = 20
      for (let d = 1; d <= 20; d++) {
        const b = level.getBlock(Math.floor(sx + look.x() * d), Math.floor(sy + look.y() * d), Math.floor(sz + look.z() * d))
        if (!b.blockState.getCollisionShape(level, b.pos).isEmpty()) { len = d; break }
      }
      for (let d = 0.5; d <= len; d += 0.5) ttParticle(level, 'minecraft:end_rod', sx + look.x() * d, sy + look.y() * d, sz + look.z() * d, 0.02, 1)
      const ex = sx + look.x() * len, ey = sy + look.y() * len, ez = sz + look.z() * len
      const box = new $TT_AABB(Math.min(sx, ex), Math.min(sy, ey), Math.min(sz, ez), Math.max(sx, ex), Math.max(sy, ey), Math.max(sz, ez)).inflate(1.5)
      level.getEntitiesWithin(box).forEach(e => {
        if (!e.isLiving() || e == p || e.isPlayer() || (e.owner && e.owner == p)) return
        // distance from the entity's centre to the beam line
        const cx = e.x - sx, cy = e.y + e.bbHeight / 2 - sy, cz = e.z - sz
        const t = Math.max(0, Math.min(len, cx * look.x() + cy * look.y() + cz * look.z()))
        const dx = cx - look.x() * t, dy = cy - look.y() * t, dz = cz - look.z() * t
        if (Math.sqrt(dx * dx + dy * dy + dz * dz) <= e.bbWidth / 2 + 0.6) {
          e.invulnerableTime = 0
          e.attack(12)
        }
      })
      ttSound(level, 'minecraft:item.trident.thunder', p.x, p.y, p.z, 1.4)
      ttParticle(level, 'minecraft:flash', ex, ey, ez, 0, 1)
    }))
  })

  // Overload Punch (Choirbreaker Gauntlets): 1 s wind-up, then an EMP ring that stuns enemies within 6 blocks for 3 s
  // (Slowness 255, Weakness, Mining Fatigue). Iron Choir and machine targets will be tagged once the boss roles are final.
  if (held == 'tt:choirbreaker_gauntlets') ttSafe('overload_punch', () => {
    if (!ttReady(event, 400)) return
    ttSound(level, 'minecraft:block.respawn_anchor.charge', p.x, p.y, p.z, 0.8)
    for (let i = 0; i < 20; i += 4) server.scheduleInTicks(i, () => ttParticle(level, 'minecraft:electric_spark', p.x, p.y + 1, p.z, 0.3, 8))
    server.scheduleInTicks(20, () => ttSafe('overload_punch_release', () => {
      if (!p.isAlive()) return
      ttEnemiesNear(p, p.x, p.y + 1, p.z, 6).forEach(e => {
        e.potionEffects.add('minecraft:slowness', 60, 254)
        e.potionEffects.add('minecraft:weakness', 60, 2)
        e.potionEffects.add('minecraft:mining_fatigue', 60, 2)
        ttParticle(level, 'minecraft:electric_spark', e.x, e.y + e.bbHeight / 2, e.z, 0.3, 10)
      })
      ttParticle(level, 'minecraft:sonic_boom', p.x, p.y + 1, p.z, 0, 1)
      ttSound(level, 'minecraft:entity.warden.sonic_boom', p.x, p.y, p.z, 1.6)
    }))
  })

  // Shard Rend (Crownshard Karambits): blink to up to 3 enemies within 10 blocks, 8 damage each, untouchable while
  // blinking (Resistance 255 for the duration).
  if (held == 'tt:crownshard_karambits') ttSafe('shard_rend', () => {
    const targets = ttEnemiesNear(p, p.x, p.y + 1, p.z, 10).filter(e => e.isMonster() || e.target == p)
      .sort((a, b) => p.distanceTo(a) - p.distanceTo(b)).slice(0, 3)
    if (targets.length == 0) { p.setStatusMessage('No enemies in reach'); return }
    if (!ttReady(event, 440)) return
    p.potionEffects.add('minecraft:resistance', 6 * targets.length + 4, 254)
    targets.forEach((e, i) => server.scheduleInTicks(i * 6, () => ttSafe('shard_rend_hit', () => {
      if (!p.isAlive() || !e.isAlive()) return
      ttParticle(level, 'minecraft:reverse_portal', p.x, p.y + 1, p.z, 0.3, 15)
      p.teleportTo(e.x - e.lookAngle.x() * 1.2, e.y, e.z - e.lookAngle.z() * 1.2)
      e.invulnerableTime = 0
      e.attack(8)
      ttParticle(level, 'minecraft:sweep_attack', e.x, e.y + 1, e.z, 0.2, 1)
      ttSound(level, 'minecraft:entity.enderman.teleport', e.x, e.y, e.z, 1.5)
    })))
  })
})

EntityEvents.hurt(event => {
  const t = event.entity

  // No fall damage during Gale Vault, or just after landing from it
  if (t.isPlayer() && event.source.type == 'fall' &&
      (t.persistentData.getBoolean('tt_vault') || t.level.gameTime <= t.persistentData.getLong('tt_nofall_until'))) {
    event.cancel()
    return
  }

  // Prism Ward: the barrier reflects the next projectile back at whoever fired it. event.cancel() ends the handler
  // (KubeJS throws to stop it), so it is called outside ttSafe.
  let ttReflected = false
  if (t.isPlayer() && t.level.gameTime <= t.persistentData.getLong('tt_prism_until')) ttSafe('prism_reflect', () => {
    const direct = event.source.immediate, shooter = event.source.actual
    if (!direct || !shooter || direct == shooter || !shooter.isLiving()) return
    t.persistentData.putLong('tt_prism_until', 0)
    direct.discard()
    ttBonus(event.server, shooter, event.damage)
    ttParticle(t.level, 'minecraft:end_rod', t.x, t.y + 1, t.z, 0.4, 25)
    ttSound(t.level, 'minecraft:block.amethyst_cluster.break', t.x, t.y, t.z, 1.2)
    ttReflected = true
  })
  if (ttReflected) {
    event.cancel()
    return
  }

  // Bow abilities: the arrow carries its bow's id (tt_bows.js). Use KubeJS's immediate/actual/type: Rhino can't see
  // DamageSource.getDirectEntity()/getEntity()/getMsgId() on a server (found by the 2026-10-28 server test).
  const arrow = event.source.immediate
  if (arrow && arrow.persistentData.contains('tt_bow')) ttSafe('bow_hit', () => {
    const bow = arrow.persistentData.getString('tt_bow')
    const owner = arrow.owner
    if (!arrow.persistentData.getBoolean('tt_full') || !owner) return
    // Undertow Arrow: each enemy hit is dragged on along the arrow's path, about 4 blocks
    if (bow == 'tt:abyssal_longbow') {
      const v = arrow.deltaMovement, len = Math.max(0.01, v.length())
      t.push(v.x() / len * 1.1, 0.25, v.z() / len * 1.1)
      t.hurtMarked = true
      ttParticle(t.level, 'minecraft:bubble_column_up', t.x, t.y + 1, t.z, 0.3, 15)
    }
    if (bow == 'tt:rootstring_bow') ttSeedshot(owner, t.x, t.y, t.z)
    arrow.persistentData.putBoolean('tt_full', false)
  })

  const p = event.source.player
  if (!p) return
  const held = p.mainHandItem.id
  const now = t.level.gameTime
  const pd = p.persistentData

  // Gale Vault plunge: hitting while airborne drives you down
  if (held == 'tt:skyreach_spear' && pd.getBoolean('tt_vault') && !p.onGround()) ttSafe('gale_plunge', () => {
    p.setDeltaMovement(p.deltaMovement.x(), -2.2, p.deltaMovement.z())
    p.hurtMarked = true
    pd.putBoolean('tt_plunge', true)
  })

  // Pressure Release (Cogwright Breaker): each hit stores pressure (max 5); a sneak attack releases it as a knock-up
  // slam, 2 damage per pressure to everything within 4 blocks.
  if (held == 'tt:cogwright_breaker') ttSafe('pressure_release', () => {
    const pressure = pd.getInt('tt_pressure')
    if (p.isShiftKeyDown() && pressure > 0) {
      pd.putInt('tt_pressure', 0)
      ttEnemiesNear(p, t.x, t.y, t.z, 4).forEach(e => {
        ttBonus(event.server, e, 2 * pressure)
        e.push(0, 0.5 + 0.1 * pressure, 0)
        e.hurtMarked = true
      })
      ttParticle(t.level, 'minecraft:explosion', t.x, t.y + 0.5, t.z, 0.5, 2)
      ttSound(t.level, 'minecraft:block.piston.extend', t.x, t.y, t.z, 0.6)
      ttSound(t.level, 'minecraft:entity.generic.explode', t.x, t.y, t.z, 1.3)
      p.setStatusMessage('Pressure released!')
    } else if (!p.isShiftKeyDown()) {
      const next = Math.min(5, pressure + 1)
      pd.putInt('tt_pressure', next)
      p.setStatusMessage(`Pressure ${next}/5`)
      ttParticle(t.level, 'minecraft:poof', p.x, p.y + 1, p.z, 0.2, 3)
    }
  })

  // Sunder the Regent (Thornecutter): up to +40% damage against bosses (#forge:bosses) as their health drops; at most
  // once per 25 s a hit also strips one beneficial effect from the boss.
  if (held == 'tt:thornecutter') ttSafe('sunder_the_regent', () => {
    if (!ttIsBoss(t)) return
    const missing = 1 - t.health / t.maxHealth
    if (missing > 0) ttBonus(event.server, t, event.damage * 0.4 * missing)
    if (now >= pd.getLong('tt_sunder_cd')) {
      let buff = null
      t.activeEffects.forEach(fx => { if (!buff && fx.effect.isBeneficial()) buff = fx })
      if (buff) {
        t.removeEffect(buff.effect)
        pd.putLong('tt_sunder_cd', now + 500)
        ttParticle(t.level, 'minecraft:crit', t.x, t.y + t.bbHeight / 2, t.z, 0.5, 20)
        ttSound(t.level, 'minecraft:item.shield.break', t.x, t.y, t.z, 0.7)
      }
    }
  })
})

// Gale Vault landing: a plunge ends in an AoE slam; any landing ends the vault (and its fall-damage protection).
PlayerEvents.tick(event => {
  const p = event.player
  const pd = p.persistentData
  if (!pd.getBoolean('tt_vault') || !p.onGround()) return
  const now = p.level.gameTime
  if (now < pd.getLong('tt_vault_at') + 6) return  // still on the ground on the launch tick
  ttSafe('gale_landing', () => {
    pd.putBoolean('tt_vault', false)
    pd.putLong('tt_nofall_until', now + 10)
    if (pd.getBoolean('tt_plunge')) {
      ttEnemiesNear(p, p.x, p.y, p.z, 4).forEach(e => {
        ttBonus(event.server, e, 8)
        e.push((e.x - p.x) * 0.3, 0.4, (e.z - p.z) * 0.3)
        e.hurtMarked = true
      })
      ttParticle(p.level, 'minecraft:explosion', p.x, p.y + 0.2, p.z, 1.2, 4)
      ttParticle(p.level, 'minecraft:cloud', p.x, p.y + 0.2, p.z, 1.5, 30)
      ttSound(p.level, 'minecraft:block.anvil.land', p.x, p.y, p.z, 0.6)
      ttSound(p.level, 'minecraft:entity.generic.explode', p.x, p.y, p.z, 0.9)
      pd.putBoolean('tt_plunge', false)
    }
  })
})

// Seedshot (Rootstring Bow): a fully drawn arrow plants a 3x3 briar patch where it lands (entity or ground). Enemies in
// it are rooted for 4 s. 8 s cooldown per player. No blocks are placed, so nothing is griefed.
function ttSeedshot(owner, x, y, z) {
  const pd = owner.persistentData
  const now = owner.level.gameTime
  if (now < pd.getLong('tt_seed_cd')) return
  pd.putLong('tt_seed_cd', now + 160)
  const level = owner.level
  ttEnemiesNear(owner, x, y + 0.5, z, 1.8).forEach(e => {
    e.potionEffects.add('minecraft:slowness', 80, 254)
    e.potionEffects.add('minecraft:weakness', 80, 0)
  })
  for (let i = 0; i < 80; i += 10) owner.server.scheduleInTicks(i, () => {
    ttParticle(level, 'minecraft:composter', x, y + 0.3, z, 1.0, 12)
    ttParticle(level, 'minecraft:spore_blossom_air', x, y + 0.6, z, 1.0, 4)
  })
  ttSound(level, 'minecraft:block.sweet_berry_bush.place', x, y, z, 0.7)
  ttSound(level, 'minecraft:block.azalea_leaves.break', x, y, z, 0.8)
}

// Arrows that hit the ground: watch tagged, fully drawn Rootstring arrows until they stop, then plant the patch.
EntityEvents.spawned(event => {
  const a = event.entity
  if (!a.persistentData.getBoolean('tt_full') || a.persistentData.getString('tt_bow') != 'tt:rootstring_bow') return
  const watch = n => event.server.scheduleInTicks(2, () => ttSafe('seedshot_watch', () => {
    if (a.isRemoved() || !a.persistentData.getBoolean('tt_full') || n > 100) return
    if (a.deltaMovement.lengthSqr() < 0.0001 && a.owner) {
      a.persistentData.putBoolean('tt_full', false)
      ttSeedshot(a.owner, a.x, a.y, a.z)
      return
    }
    watch(n + 1)
  }))
  watch(0)
})

// Oath of the Capital (Emberhold Oathblade): +1 damage per Town Hall level of the colony you own (max +5); kills
// inside your colony heal citizens and guards within 12 blocks. MineColonies classes are loaded if present.
let $TT_Colonies = null
try { $TT_Colonies = Java.loadClass('com.minecolonies.api.colony.IColonyManager') } catch (e) { console.warn('[TT] MineColonies API not found; Oath of the Capital is off') }

function ttColony(p) {
  if (!$TT_Colonies) return null
  return $TT_Colonies.getInstance().getIColonyByOwner(p.level, p)
}

EntityEvents.hurt(event => {
  const p = event.source.player
  if (!p || p.mainHandItem.id != 'tt:emberhold_oathblade') return
  ttSafe('oath_damage', () => {
    const colony = ttColony(p)
    if (!colony) return
    const hall = colony.getBuildingManager().getTownHall()
    const lvl = hall ? Math.min(5, hall.getBuildingLevel()) : 0
    if (lvl > 0) ttBonus(event.server, event.entity, lvl)
  })
})

EntityEvents.death(event => {
  const p = event.source.player
  if (!p || p.mainHandItem.id != 'tt:emberhold_oathblade') return
  ttSafe('oath_heal', () => {
    const colony = ttColony(p)
    const e = event.entity
    if (!colony || !colony.isCoordInColony(e.level, e.blockPosition())) return
    const box = new $TT_AABB(e.x - 12, e.y - 6, e.z - 12, e.x + 12, e.y + 6, e.z + 12)
    e.level.getEntitiesWithin(box).forEach(c => {
      if (String(c.type) == 'minecolonies:citizen') {
        c.heal(4)
        ttParticle(e.level, 'minecraft:heart', c.x, c.y + 2, c.z, 0.3, 2)
      }
    })
  })
})

// Epic Fight hooks: Reversal Cut (Rustbite Karambit) after a successful dodge, Iron Recoil (Wroughtnaut Bulwark) on a
// parry. Listeners live on the player's Epic Fight patch, so they are added at login and again after respawn.
let $TT_EF = null, $TT_EFEvent = null
try {
  $TT_EF = Java.loadClass('yesman.epicfight.world.capabilities.EpicFightCapabilities')
  $TT_EFEvent = Java.loadClass('yesman.epicfight.world.entity.eventlistener.PlayerEventListener$EventType')
} catch (e) { console.warn('[TT] Epic Fight API not found; Reversal Cut and Iron Recoil are off') }
const TT_EF_UUID = Java.loadClass('java.util.UUID').fromString('6f1d2c4e-7a3b-4f0e-9d1a-2b7c5e8f9a01')

function ttHookEpicFight(p, server) {
  if (!$TT_EF) return
  server.scheduleInTicks(20, () => ttSafe('ef_hooks', () => {
    const patch = $TT_EF.getPlayerPatch(p)
    if (!patch) return
    const listener = patch.getEventListener()
    // priority -1: runs after Epic Fight's own guard and dodge handlers, even when they cancel the event
    listener.addEventListener($TT_EFEvent.DODGE_SUCCESS_EVENT, TT_EF_UUID, ev => ttSafe('reversal_cut_ready', () => {
      if (p.mainHandItem.id != 'tt:rustbite_karambit') return
      p.persistentData.putLong('tt_reversal_until', p.level.gameTime + 20)
      ttParticle(p.level, 'minecraft:crit', p.x, p.y + 1, p.z, 0.4, 8)
    }), -1)
    listener.addEventListener($TT_EFEvent.TAKE_DAMAGE_EVENT_ATTACK, TT_EF_UUID, ev => ttSafe('iron_recoil', () => {
      if (!ev.isParried() || p.mainHandItem.id != 'tt:wroughtnaut_bulwark') return
      const src = ev.getDamageSource(), attacker = src.actual
      if (!attacker || attacker != src.immediate || !attacker.isLiving()) return  // melee only
      ttBonus(server, attacker, ev.getDamage())
      attacker.potionEffects.add('minecraft:slowness', 20, 254)
      attacker.potionEffects.add('minecraft:weakness', 20, 2)
      ttParticle(p.level, 'minecraft:crit', attacker.x, attacker.y + 1, attacker.z, 0.4, 15)
      ttSound(p.level, 'minecraft:block.anvil.land', p.x, p.y, p.z, 1.6)
    }), -1)
  }))
}

PlayerEvents.loggedIn(event => ttHookEpicFight(event.player, event.server))
PlayerEvents.respawned(event => ttHookEpicFight(event.player, event.server))

// Reversal Cut payoff: the next hit within 1 s of a dodge deals +2 and makes the target flinch
EntityEvents.hurt(event => {
  const p = event.source.player
  if (!p || p.mainHandItem.id != 'tt:rustbite_karambit') return
  ttSafe('reversal_cut', () => {
    const now = p.level.gameTime
    if (now > p.persistentData.getLong('tt_reversal_until')) return
    p.persistentData.putLong('tt_reversal_until', 0)
    const t = event.entity
    ttBonus(event.server, t, 2)
    t.potionEffects.add('minecraft:slowness', 15, 254)
    ttParticle(t.level, 'minecraft:sweep_attack', t.x, t.y + 1, t.z, 0.1, 1)
  })
})
