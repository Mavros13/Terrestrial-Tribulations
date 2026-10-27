// Terrestrial Tribulations: custom weapon registration (KubeJS 2001, MC 1.20.1 Forge)
// DRAFT, untested: check the builder methods against the installed KubeJS version before relying on this.
StartupEvents.registry('item', event => {
  event.create('tt:ashfang_karambit', 'sword')
    .tier('iron')
    .attackDamageBaseline(2.0)   // final damage depends on the tier bonus; tune in game to reach 5
    .speedBaseline(-1.8)         // ~2.2 attack speed
    .maxDamage(600)
    .rarity('uncommon')
    .displayName('Ashfang Karambit')
})
