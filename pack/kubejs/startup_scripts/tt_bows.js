// Terrestrial Tribulations: shooting for our bows (hand-written). The bow items themselves are registered in
// tt_weapons.generated.js with a bow use animation; when the player lets go, they call global.ttShootBow.
// Works like a vanilla bow: same draw time and power curve, uses arrows from the inventory (any arrow type, none in
// creative), full draw = critical arrow. Our extras: the arrow carries the bow's id so server scripts can add the
// bow's ability (tt_active_abilities.js), plus per-bow base damage and piercing.
// DRAFT: untested in-game.

const $TT_BowItem = Java.loadClass('net.minecraft.world.item.BowItem')
const $TT_ArrowItem = Java.loadClass('net.minecraft.world.item.ArrowItem')
const $TT_Pickup = Java.loadClass('net.minecraft.world.entity.projectile.AbstractArrow$Pickup')

global.ttShootBow = (stack, level, entity, timeLeft, opts) => {
  if (level.isClientSide() || !entity.isPlayer()) return
  const power = $TT_BowItem.getPowerForTime(72000 - timeLeft)
  if (power < 0.1) return
  const creative = entity.abilities.instabuild
  const inv = entity.inventory
  let ammo = null
  for (let i = 0; i < inv.getContainerSize() && !ammo; i++) {
    const s = inv.getItem(i)
    if (!s.isEmpty() && s.item instanceof $TT_ArrowItem) ammo = s
  }
  if (!ammo && !creative) return
  const arrowItem = ammo ? ammo.item : Item.of('minecraft:arrow').item
  const arrow = arrowItem.createArrow(level, ammo ? ammo : Item.of('minecraft:arrow'), entity)
  arrow.shootFromRotation(entity, entity.getXRot(), entity.getYRot(), 0, power * 3.0, 1.0)
  arrow.setBaseDamage(opts.damage)
  if (power >= 1.0) arrow.setCritArrow(true)
  if (opts.pierce > 0) arrow.setPierceLevel(opts.pierce)
  arrow.persistentData.putString('tt_bow', opts.id)
  arrow.persistentData.putBoolean('tt_full', power >= 1.0)
  if (creative) arrow.pickup = $TT_Pickup.CREATIVE_ONLY
  level.addFreshEntity(arrow)
  level.server.runCommandSilent(`execute in ${level.dimension} run playsound minecraft:entity.arrow.shoot player @a ${entity.x} ${entity.y} ${entity.z} 1 ${1 / (Math.random() * 0.4 + 1.2) + power * 0.5}`)
  if (ammo && !creative) ammo.shrink(1)
}
