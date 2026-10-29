# Risk register
| ID | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| R1 | Worldgen stutter/conflicts | High | High | One terrain mod (Terralith), incremental structures, Chunky pregen of spawn once per world (tt_pregen.js, 2026-10-29) | Arch | Mitigated, measure in game |
| R2 | Combat framework conflicts | Med | High | Better Combat only | Arch | Open |
| R3 | Custom-mod scope creep | High | High | Vertical slices, data-driven | Dev | Open |
| R4 | Superhero power creep | Med | Med | KubeJS + core flags gating | Design | Open |
| R5 | Entity load | Med | High | Caps, culling, Spark profiling | Dev | Open |
| R6 | Redistribution licences | Med | High | Manifest-only distribution | Release | Open |
| R7 | Rats / Elytra Trims / Wakes unavailable on Forge 1.20.1 | Low (builds found) | Low | Alternatives or CUSTOM | Arch | Open |
