# Story NPC sites: how they're designed and built (2026-10-29)

Oscar asked for more detail (paths, decoration, lighting, texture), based on how other structure mods and builders do
it. This note records what we took from that research and how `tools/gen_npc_sites.py` applies it.

## Building techniques
- **Gradients, not stripes.** Order a palette from dark/rough to light/clean, and run the dark end at the base of a
  wall, fading upward with some noise. Horizontal bands ("sandwiching") and random speckle ("smallpox") look worse
  than a gradient. ([WesterosCraft: gradients](https://westeroscraft.com/docs/building/fundamentals/gradients))
- **Weather first, then gradient.** Cracks and moss gather at corners, openings, bases and wall tops, not evenly.
- **Depth and silhouette.** No flat boxes: buttresses, overhanging eaves, posts and beams, stairs and slabs on edges,
  uneven or collapsed wall tops.
- **Towers:** octagonal rather than square, a wide plinth, narrower upper storeys, a pointed roof, windows only where
  there are rooms, and those lit from inside. Dark stone below with pale stone and amethyst trim suits the Conclave.
  ([minecraft.how: wizard tower](https://minecraft.how/blog/post/build-wizard-tower-minecraft))
- **Light where people would put it:** lanterns on posts along paths, hung from tent poles, beams and tree crowns,
  candles on shelves, torches on palisade walls, and a smoking chimney on the forge.
- **Paths are worn mixes** of dirt path, coarse dirt, gravel and packed mud, wider where people gather.

## How structure mods implement it
Checked against [Lithostitched's custom structure guide](https://www.mintlify.com/Apollounknowndev/lithostitched/guides/custom-structures)
and the [processor list reference](https://wiki.ronlab.site/content/minecraftwiki_en_all_maxi_2025-11/Processor_list).
YUNG's, Towns and Towers and Dungeons and Taverns use the same vanilla pieces.
- One template pool per structure; each pool element names a **processor list**.
- **Processor lists** (`worldgen/processor_list/npc/<site>.json`) use `minecraft:rule` with `random_block_match`.
  Each copy of a site is weathered differently: stone bricks crack or grow moss, copper rusts, paths wear, and
  shelves lose books. Rules only touch blocks without states, because a rule's output replaces the whole state.
  They never produce a site's own marker block.
- **Loot chests** keep a `LootTable` in the template's block-entity NBT, using vanilla tables that fit each site:
  - weaponsmith at Doran's forge
  - fletcher at Thornwatch
  - toolsmith at Pell's
  - cartographer in the tower
  - temple at the caravan
  - igloo at Wren's
  - stronghold library at Sol's archive
- **Terrain:** the template is projected to `WORLD_SURFACE_WG`, and `beard_thin` blends the ground under and around
  it. The sites stay small (at most 19 x 26 x 19) and single-piece, which keeps worldgen cheap. Structure Layout
  Optimizer and Async Locator take care of the rest.

## The eight sites
| Site | Main features |
|---|---|
| Refugee Camp | Four A-frame tents (Maera's crimson one is biggest). A stone-ringed fire with log benches. Doran's lean-to forge with a smoking chimney. Crates, lantern posts and worn crossroads. |
| Thornwatch Outpost | Uneven sharpened palisade and a gatehouse with banners. A roofed watchtower on stilts. A green barracks tent, a training yard and a fire with benches. |
| Ruin with a Tent | Broken brick walls with a mossy base and buttresses. A fallen column. A huge copper boiler rusting green from the bottom. Pipes, scrap, and Pell's tent and workbench. |
| The Old Oak | A 3x3 trunk with buttress roots and branches, and a lumpy oak and azalea crown with lanterns. A mossy shrine with candles, flowers and stepping stones. |
| Lumen Conclave Tower | Octagonal, with a dark plinth and buttresses. Walls fade from deepslate to calcite with amethyst bands. A narrower top storey and a pointed purpur roof. Lit windows, three floors of rooms. |
| A Clean Caravan | A birch wagon with a white cover and a driver's bench. A market stall under a striped awning. A rutted road. |
| Scout's Lookout | A railed deck on stilts with a roof and ladder. A fur lean-to, a fire pit and a firewood stack in the snow. |
| Sunken Archive | Thick brick walls with collapsed sections and an arched door. Roof beams with hanging lanterns. Rows of shelves with candles, a rug and a great lectern. |

Review page: `blockbench/previews/npc-sites.html` (flat colours, built by `tools/build_site_viewer.py`).
