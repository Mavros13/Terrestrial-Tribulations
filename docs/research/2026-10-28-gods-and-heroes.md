# Gods and Heroes (Palladium edition): what's inside (2026-10-28)

**Status: DROPPED 2026-10-31.** Historical research only. The pack no longer ships or requires this mod; Origins Heritage + Fate cover that layer; FSang/Satsu remain. Do not re-add to ModSync or CurseForge lists.

Read from the newest Forge 1.20.1 jar on Modrinth (`gods-and-heroes-palladium`, v1.4, `Gods-And-Heroes-PE-1.4.jar`, 227 KB, 2025-04-27) on the owner's laptop, as data only (opened as a zip, never run; deleted afterwards). Was **All Rights Reserved** / Modrinth-only.

- **Mod id `ghmorak`**, a data-only jar (`modLoader = 'lowcodefml'`). mods.toml says 1.2.1, pack.mcmeta says 1.4.
- **Namespaces:** `ghmorak` (items, Palladium powers, functions), `super_powers` (origins, origin powers, functions, tags); it also writes into `origins` and `minecraft` (a load tag runs `ghmorak:load`).
- **Palladium addon pack:** yes (`"id": "ghmorak"`, pack_format 15, needs Palladium >= 4.0.0). Items (8): `ghmorak:kryptonian_essence`, `jumper_essence`, `speedster_essence`, `white_essence`, `syringe`, `syringe_jumper`, `syringe_kryptonian`, `syringe_speedster`. Powers (9): `ghmorak:builder`, `engineer`, `speed`, `speed_key`, `jumper`, `ars_magic`, `krypto`, `size_shifter`, `iron_mage`.
- **Origin layer:** `origins:super_powers/origin` ("Super Power", `replace: true`, `allow_random: true`), separate from `origins:origin` and our `tt:fate`.
  Origins (10): `super_powers:humano`, `speedster`, `speedster_key`, `kryptonian`, `ars_magic`, `iron_mage`, `builder`, `engineer`, `jumper`, `size_shifter`. Each origin's `give_*_sp` power adds its Palladium power (e.g. speedster runs `superpower add ghmorak:speed @s`, and removes it when lost).
- **Dependencies:** mods.toml: Minecraft >= 1.20, Palladium, Pehkui. Modrinth: required Palladium, Origins (Forge), Origins, KubeJS, Pehkui; optional Ars Nouveau, Create, Iron's Spells; incompatible GH-Powers. `ars_magic` and `iron_mage` presumably need the optional mods.

## How the pack used it (before drop)
- The Super Power layer was hidden at character creation and quests granted Speedster → Jumper → Kryptonian via `/origin set`. That wiring was removed 2026-10-31 along with the ModSync entry and the `ghmorak` story-gate namespace.
