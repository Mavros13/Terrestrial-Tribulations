# Final release checklist

Things to do before the public release. Add to this list whenever something is parked "for the final steps".

- [x] **Release zip without test helpers** (2026-10-29): `build_prism.py` now also builds `dist/Terrestrial-Tribulations-<pack_version>-CurseForge.zip` (all stages, nothing from `tools/dev_only.txt`; checked: no test files inside). Bump `pack_version` in `modpack/curseforge-mods.json` and add a `CHANGELOG.md` entry for every release.
- [ ] **Play the release zip once on the desktop** (fresh instance from the 0.9.0 zip): main menu, new world, Chapter 1, an NPC talk.
- [x] **Karambit look as a player choice** (2026-10-29): vanilla swords stay vanilla (TT Karambits pack over Karambit Vault), only our 4 karambits use the karambit models and Punchy animations; both packs can be turned off in Options → Resource Packs and stay off. Confirm in game: vanilla iron sword looks and swings vanilla; karambits look right in hand and in the inventory.
- [x] **Default options without overwriting players' settings** (2026-10-29): `pack/options.txt` is gone (Prism and CurseForge overwrite override files on every pack update). **Default Options** (+ Balm) now switches Karambit Vault x Punchy on once per instance from `pack/config/defaultoptions-common.toml`; its journal remembers that, so a player who turns the pack off keeps it off. Confirm on the desktop: fresh import has the pack on; turn it off, update the pack, still off.
- [x] **Amendments** (Supplementaries' companion mod, avoids its startup warning): added to both mod lists, stage D (2026-10-29).
- [ ] **Side quest tabs** (2026-10-29: written, `tools/quest_side.py`, 5 tabs in the "Side Paths" group). Still to do: confirm every item ID on the next server test (selftest `quest_items`) and play through one tab on the desktop.
- [ ] **Merge PR #1** and point the install links at `main`.
