// Terrestrial Tribulations: weapon recipes (hand-written). Weapons from later tiers come from quests and bosses.
ServerEvents.recipes(event => {
  event.shaped('tt:frontier_cleaver', [' F', 'FB', 'S '], { F: 'minecraft:flint', B: 'minecraft:bone', S: 'minecraft:stick' })
  event.shaped('tt:rustbite_karambit', [' I', 'IL', 'S '], { I: 'minecraft:iron_ingot', L: 'minecraft:leather', S: 'minecraft:stick' })
  event.shapeless('tt:ashfang_karambit', ['tt:rustbite_karambit', 'tt:hollow_fang', 'tt:hollow_fang', 'minecraft:blaze_powder'])
  event.shapeless('2x tt:bone_shard', ['minecraft:bone', 'minecraft:flint'])
})
