# Final release checklist

Things to do before the public release. Add to this list whenever something is parked "for the final steps".

- [ ] **Release zip without test helpers:** build with `python tools/build_curseforge.py --release` (leaves out everything in `tools/dev_only.txt`: `tt_testkit.js`, the selftest, `tt:cast_test`).
- [x] **Karambit look as a player choice** (2026-10-29): vanilla swords stay vanilla (TT Karambits pack over Karambit Vault), only our 4 karambits use the karambit models and Punchy animations; both packs can be turned off in Options → Resource Packs and stay off. Confirm in game: vanilla iron sword looks and swings vanilla; karambits look right in hand and in the inventory.
- [x] **Default options without overwriting players' settings** (2026-10-29): `pack/options.txt` is gone (Prism and CurseForge overwrite override files on every pack update). **Default Options** (+ Balm) now switches Karambit Vault x Punchy on once per instance from `pack/config/defaultoptions-common.toml`; its journal remembers that, so a player who turns the pack off keeps it off. Confirm on the desktop: fresh import has the pack on; turn it off, update the pack, still off.
- [x] **Amendments** (Supplementaries' companion mod, avoids its startup warning): added to both mod lists, stage D (2026-10-29).
- [ ] **Side quest tabs** (tech, magic, world tutorials) once the mod list is final.
- [ ] **Merge PR #1** and point the install links at `main`.
