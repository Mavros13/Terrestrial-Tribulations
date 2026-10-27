// Terrestrial Tribulations: custom weapon registration (KubeJS 2001, MC 1.20.1 Forge)
// DRAFT, untested. Check the builder methods against the installed KubeJS version.
// Sword damage formula: tier bonus + attackDamageBaseline + 1 (iron tier bonus = 2).
// Attack speed formula: 4 + speedBaseline.
// Full specs: design/weapons/ROSTER.md
StartupEvents.registry('item', event => {
  // Base karambit: 6 damage (= iron sword), 1.8 speed (iron sword 1.6)
  event.create('tt:rustbite_karambit', 'sword')
    .tier('iron')
    .attackDamageBaseline(3.0)   // 2 + 3 + 1 = 6
    .speedBaseline(-2.2)         // 4 - 2.2 = 1.8
    .maxDamage(250)
    .displayName('Rustbite Karambit')

  event.create('tt:ashfang_karambit', 'sword')
    .tier('iron')
    .attackDamageBaseline(4.0)   // 7
    .speedBaseline(-2.0)         // 2.0
    .maxDamage(600)
    .rarity('uncommon')
    .displayName('Ashfang Karambit')
})
