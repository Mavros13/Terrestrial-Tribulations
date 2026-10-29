# Final release checklist

Things to do before the public release. Add to this list whenever something is parked "for the final steps".

- [ ] **Release zip without test helpers:** build with `python tools/build_curseforge.py --release` (leaves out everything in `tools/dev_only.txt`: `tt_testkit.js`, the selftest, `tt:cast_test`).
- [ ] **Karambit look as a player choice** (Oscar, 2026-10-29): Karambit Vault x Punchy also restyles vanilla swords. Make it switchable in game. Plan: give our 4 karambits their own copies of the needed model parents only if the licence allows (ARR, so likely not), otherwise keep the pack but make it optional: leave it in `resourcepacks/` enabled by default and document Options → Resource Packs, or add a small toggle (e.g. a keybind/command via a resource-pack-switching mod, or a separate "TT karambits only" pack that overrides the vanilla sword models back). Check how our karambits look with the pack off first.
- [ ] **Default options without overwriting players' settings:** `pack/options.txt` only sets `resourcePacks`; check that a CurseForge pack update doesn't reset players' own settings (or switch to a default-options mod).
- [x] **Amendments** (Supplementaries' companion mod, avoids its startup warning): added to both mod lists, stage D (2026-10-29).
- [ ] **Side quest tabs** (tech, magic, world tutorials) once the mod list is final.
- [ ] **Merge PR #1** and point the install links at `main`.
