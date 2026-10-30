#!/usr/bin/env python3
"""Switch off third-party data that can never load, so real errors stand out in the log.

CoreWithStuff (a library in stage C) ships recipes and block loot tables for blocks it doesn't register in our
setup (the Chromatix colours, the moon stone sets and ores, and a few machines). Each one logs an error at every
start and every /reload: 200 recipes twice each, plus loot tables (2026-10-29 server test, IDs listed in the report
by tools/server_test.ps1). This writes overrides into our KubeJS data pack, which loads above mod jars:
  data/corewithstuff/recipes/<id>.json          a Forge "forge:false" condition, so the recipe is skipped quietly
  data/corewithstuff/loot_tables/blocks/<id>.json  an empty block loot table
If a CoreWithStuff update ever registers these blocks, delete the matching family here.

FSang18's Heroes ships four functions that fail to parse at every start and /reload (2026-10-29 server test:
block_freeze uses an empty block id, shieldkill a sort option with no value, webs/kill_lead a decimal where an
integer goes, mjolnir_summon a block that doesn't exist). They never load as they are, so empty versions in
data/fsang/functions/ change nothing in play and stop the errors. Remove one here if an fsang update fixes it.
"""
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "pack", "kubejs", "data", "corewithstuff")
FSANG = os.path.join(ROOT, "pack", "kubejs", "data", "fsang", "functions")
FSANG_BROKEN = ["block_freeze", "shieldkill", "webs/kill_lead", "mjolnir_summon"]

COLOURS = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray", "cyan",
           "purple", "blue", "brown", "green", "red", "black"]
MOONS = ["moon", "pale_moon", "dark_moon"]
SET = ["stone", "stone_slab", "stone_stairs", "stone_bricks", "stone_brick_slab", "stone_brick_stairs",
       "stone_tiles", "stone_tile_slab", "stone_tile_stairs"]
ORES = ["coal", "iron", "gold", "copper", "lead", "emerald", "lapis", "redstone", "diamond", "mythril"]
MACHINES = ["block_mixer", "elevator_block", "fabricator", "oxygen_generator", "player_sensor", "plushie", "quizia"]
SANDS = ["moon_sand", "moon_sandstone", "moon_smooth_sandstone", "moon_cut_sandstone", "moon_chiseled_sandstone"]


def recipes():
    ids = [f"{c}_chromatix_{v}" for c in COLOURS for v in
           ("block_base", "block_bulk", "block_single", "slab_bulk", "slab_from_block", "slab_single",
            "stairs_bulk", "stairs_from_block", "stairs_single")]
    ids += [f"reset_chromatix_{v}" for v in ("block", "slab", "stairs")]
    for m in MOONS:
        ids += [f"{m}_{s}" for s in SET]
        cob = "cobbled_moon_stone" if m == "moon" else f"{m.split('_')[0]}_cobbled_moon_stone"
        ids += [f"{cob}_slab", f"{cob}_stairs", f"chiseled_{m}_stone", f"cracked_{m}_stone_bricks"]
    ids += SANDS[1:] + MACHINES + ["quizia_new", "mythril_ingot_smelting", "mythril_ingot_blasting"]
    return ids


def loot_tables():
    ids = [f"{c}_chromatix_{v}" for c in COLOURS for v in ("block", "slab", "stairs")]
    for m in MOONS:
        ids += [f"{m}_{s}" for s in SET] + [f"{m}_{o}_ore" for o in ORES]
        cob = "cobbled_moon_stone" if m == "moon" else f"{m.split('_')[0]}_cobbled_moon_stone"
        ids += [cob, f"{cob}_slab", f"{cob}_stairs"]
        # the mod names these both ways round (recipes: cracked_dark_..., loot: dark_cracked_...)
        ids += [f"chiseled_{m}_stone", f"cracked_{m}_stone_bricks"]
        if m != "moon":
            p = m.split("_")[0]
            ids += [f"{p}_chiseled_moon_stone", f"{p}_cracked_moon_stone_bricks"]
    return ids + SANDS + MACHINES


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def main():
    shutil.rmtree(DATA, ignore_errors=True)
    rec, loot = sorted(set(recipes())), sorted(set(loot_tables()))
    for r in rec:
        write(os.path.join(DATA, "recipes", r + ".json"),
              {"conditions": [{"type": "forge:false"}], "type": "minecraft:crafting_shapeless",
               "ingredients": [{"item": "minecraft:barrier"}], "result": {"item": "minecraft:barrier"}})
    for t in loot:
        write(os.path.join(DATA, "loot_tables", "blocks", t + ".json"), {"type": "minecraft:block", "pools": []})
    shutil.rmtree(FSANG, ignore_errors=True)
    for fn in FSANG_BROKEN:
        os.makedirs(os.path.dirname(os.path.join(FSANG, fn)), exist_ok=True)
        with open(os.path.join(FSANG, fn + ".mcfunction"), "w", encoding="utf-8") as f:
            f.write("# Terrestrial Tribulations: emptied, the original fails to parse (tools/gen_quiet_data.py)\n")
    print(f"Quiet data: {len(rec)} CoreWithStuff recipes and {len(loot)} loot tables switched off, "
          f"{len(FSANG_BROKEN)} broken fsang functions emptied")


if __name__ == "__main__":
    main()
