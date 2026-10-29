#!/usr/bin/env python3
"""Story NPC sites: one small structure per story NPC, generated into the world (owner, 2026-10-29: "they spawn
naturally in specific structures that don't let you in until that chapter is unlocked").

Writes, all under pack/kubejs/data/tt/ (a data pack KubeJS loads before worldgen):
  structures/npc/<site>.nbt               the building (vanilla structure-template NBT, gzip, DataVersion 3465 = 1.20.1)
  worldgen/template_pool/npc/<site>.json  a one-piece jigsaw pool
  worldgen/structure/npc/<site>.json      jigsaw structure on the surface (beard_thin terrain blending)
  worldgen/structure_set/npc/<site>.json  random_spread placement (not for the refugee camp, which is placed at spawn)
  tags/worldgen/structure/npc/<site>.json one-entry tag: explorer maps point at a tag
  tags/worldgen/structure/npc_sites.json  every site (the KubeJS script asks "is this player inside one?")
  loot_tables/npc_maps/<site>.json        an explorer map to the nearest site (Async Locator searches off-thread)
and pack/kubejs/config/tt_npc_sites.json, read by server_scripts/tt_npc_sites.js:
  - the refugee camp (Maera, Doran) is placed next to world spawn on the first load, because Chapter 1 needs Maera at once;
  - every other site is locked until its stage tt_meet_<npc>: walking in without it puts you back outside, with a line;
  - the stage and the map come from the quest just before that NPC's first talk (MEET_AFTER, added by gen_quests.py);
  - the first time a player with the stage walks in, the NPC appears on its marker block (Easy NPC preset import),
    once per world: later copies of the same site stay empty.

Formats checked against 1.20.1: StructureTemplate.save (size/palette/blocks/entities/DataVersion), JigsawStructure
CODEC (start_pool, size, start_height, project_start_to_heightmap, max_distance_from_center, terrain_adaptation),
RandomSpreadStructurePlacement (spacing, separation, salt), ExplorationMapFunction (destination = structure tag).
Data folders are 1.20.1 names: structures/, loot_tables/ (both singular from 1.21 on)."""
import gzip, io, json, os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_npcs import CAST

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "pack", "kubejs", "data", "tt")
CFG = os.path.join(ROOT, "pack", "kubejs", "config", "tt_npc_sites.json")
DATA_VERSION = 3465  # Minecraft 1.20.1


# ---------- minimal NBT writer (big-endian, named root) ----------
def _str(s):
    b = s.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def _payload(tag, v):
    if tag == 3:
        return struct.pack(">i", v)
    if tag == 8:
        return _str(v)
    if tag == 10:
        out = b""
        for k, (t, val) in v.items():
            out += bytes([t]) + _str(k) + _payload(t, val)
        return out + b"\x00"
    if tag == 9:
        et, items = v
        return bytes([et if items else 0]) + struct.pack(">i", len(items)) + b"".join(_payload(et, i) for i in items)
    raise ValueError(tag)


def nbt_file(root):
    raw = bytes([10]) + _str("") + _payload(10, root)
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as g:
        g.write(raw)
    return buf.getvalue()


def parse_state(s):
    name, props = (s.split("[", 1) + [""])[:2]
    name = name if ":" in name else "minecraft:" + name
    p = dict(kv.split("=") for kv in props.rstrip("]").split(",") if kv) if props else {}
    return name, p


# ---------- a tiny voxel canvas ----------
class Site:
    def __init__(self, w, h, d):
        self.w, self.h, self.d = w, h, d
        self.b = {(x, y, z): "air" for x in range(w) for y in range(1, h) for z in range(d)}  # clear the box above the floor

    def set(self, x, y, z, s):
        assert 0 <= x < self.w and 0 <= y < self.h and 0 <= z < self.d, (x, y, z)
        self.b[(x, y, z)] = s

    def fill(self, x0, y0, z0, x1, y1, z1, s):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, s)

    def floor(self, pattern):
        """pattern(x, z) -> block state or None (leave the ground)"""
        for x in range(self.w):
            for z in range(self.d):
                s = pattern(x, z)
                if s:
                    self.set(x, 0, z, s)

    def nbt(self):
        palette, index, blocks = [], {}, []
        for (x, y, z), s in sorted(self.b.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
            if s not in index:
                index[s] = len(palette)
                name, props = parse_state(s)
                entry = {"Name": (8, name)}
                if props:
                    entry["Properties"] = (10, {k: (8, v) for k, v in props.items()})
                palette.append(entry)
            blocks.append({"pos": (9, (3, [x, y, z])), "state": (3, index[s])})
        return nbt_file({"DataVersion": (3, DATA_VERSION), "size": (9, (3, [self.w, self.h, self.d])),
                         "palette": (9, (10, palette)), "blocks": (9, (10, blocks)), "entities": (9, (10, []))})


def tent(s, x0, z0, length, wool, along_x=True):
    """An A-frame canvas tent, 3 wide, open at both ends."""
    for i in range(length):
        for dx, y, st in ((0, 1, f"{wool}_wool"), (1, 2, f"{wool}_wool"), (2, 1, f"{wool}_wool")):
            if along_x:
                s.set(x0 + i, y, z0 + dx, st)
            else:
                s.set(x0 + dx, y, z0 + i, st)
    for i in range(length):  # bedroll inside
        if along_x:
            s.set(x0 + i, 1, z0 + 1, f"{wool}_carpet" if i % 2 else "air")
        else:
            s.set(x0 + 1, 1, z0 + i, f"{wool}_carpet" if i % 2 else "air")


# ---------- the sites ----------
def refugee_camp():
    s = Site(15, 6, 15)
    s.floor(lambda x, z: "dirt_path" if (x == 7 or z == 7) else ("coarse_dirt" if (x * 7 + z * 3) % 5 == 0 else None))
    s.set(7, 0, 7, "cobblestone"); s.set(7, 1, 7, "campfire[lit=true]")
    for x, z in ((5, 6), (9, 8), (6, 9), (8, 5)):
        s.set(x, 1, z, "spruce_log[axis=x]" if x < 7 else "spruce_log[axis=z]")
    tent(s, 1, 1, 5, "red")          # Maera's tent (Ember Accord crimson)
    tent(s, 9, 1, 5, "white")
    tent(s, 1, 10, 4, "light_gray", along_x=False)
    # Doran's open-air forge, south-east corner
    s.fill(10, 0, 10, 14, 0, 14, "stone_bricks")
    s.set(13, 1, 13, "blast_furnace[facing=west]"); s.set(13, 1, 11, "anvil[facing=north]")
    s.set(11, 1, 13, "water_cauldron[level=3]"); s.set(14, 1, 10, "smithing_table")
    s.set(14, 1, 14, "lava_cauldron"); s.set(14, 2, 14, "iron_bars")
    for y in (1, 2, 3):
        s.set(10, y, 14, "spruce_fence")
    s.set(10, 4, 14, "lantern[hanging=false]")
    s.set(12, 0, 12, "smooth_stone")  # Doran's marker
    for x, z in ((6, 1), (8, 13), (13, 6)):
        s.set(x, 1, z, "hay_block"); s.set(x, 2, z, "barrel[facing=up]")
    s.set(6, 0, 5, "red_terracotta")  # Maera's marker, by her tent and the fire
    return s, {"maera": "red_terracotta", "doran": "smooth_stone"}


def thornwatch_outpost():
    s = Site(15, 9, 15)
    s.floor(lambda x, z: "podzol" if (x + z) % 3 == 0 else "coarse_dirt")
    for i in range(15):  # palisade with a gate on the south side
        for (x, z) in ((i, 0), (i, 14), (0, i), (14, i)):
            if z == 14 and 6 <= x <= 8:
                continue
            for y in (1, 2, 3):
                s.set(x, y, z, "spruce_log[axis=y]")
            s.set(x, 4, z, "spruce_fence" if (x + z) % 2 else "air")
    # watchtower in the north-west corner
    s.fill(1, 1, 1, 3, 5, 3, "spruce_planks"); s.fill(2, 1, 2, 2, 5, 2, "air")
    s.fill(1, 6, 1, 3, 6, 3, "spruce_slab[type=bottom]")
    for y in range(1, 7):
        s.set(2, y, 2, "ladder[facing=south]")
    s.set(2, 1, 3, "air"); s.set(2, 2, 3, "air")
    for x, z in ((1, 1), (3, 1), (1, 3), (3, 3)):
        s.set(x, 7, z, "spruce_fence")
    s.set(1, 8, 1, "green_wool")  # Thornwatch colours on the corner post
    s.set(7, 0, 7, "mossy_cobblestone"); s.set(7, 1, 7, "campfire[lit=true]")
    for x in (10, 12):
        s.set(x, 1, 3, "target"); s.set(x, 1, 4, "hay_block")
    s.fill(10, 1, 10, 12, 1, 12, "spruce_planks"); s.fill(10, 2, 10, 12, 2, 12, "green_carpet")
    s.set(5, 1, 11, "barrel[facing=up]"); s.set(4, 1, 11, "grindstone[face=floor,facing=north]")
    s.set(7, 0, 12, "moss_block")  # Rhosk's marker, just inside the gate
    return s, {"rhosk": "moss_block"}


def pell_ruin():
    s = Site(13, 7, 11)
    s.floor(lambda x, z: "cobblestone" if (x * 5 + z) % 4 else "gravel")
    for x in range(13):  # broken north and west walls of an Old Engine ruin
        top = 2 + (x * 7 % 4)
        for y in range(1, top):
            s.set(x, y, 0, "cracked_stone_bricks" if (x + y) % 3 == 0 else "mossy_stone_bricks")
    for z in range(11):
        top = 1 + (z * 5 % 4)
        for y in range(1, top):
            s.set(0, y, z, "stone_bricks" if (z + y) % 2 else "mossy_stone_bricks")
    s.set(4, 1, 1, "oxidized_copper"); s.set(5, 1, 1, "weathered_cut_copper"); s.set(5, 2, 1, "lightning_rod")
    s.set(2, 1, 3, "piston[facing=up]"); s.set(2, 1, 4, "sticky_piston[facing=east]")
    tent(s, 7, 4, 4, "brown", along_x=False)  # Pell's patched tent
    s.set(11, 1, 9, "smithing_table"); s.set(10, 1, 9, "chest[facing=north]"); s.set(11, 1, 1, "barrel[facing=up]")
    s.set(6, 1, 9, "lantern[hanging=false]"); s.set(3, 1, 8, "exposed_copper"); s.set(3, 2, 8, "copper_block")
    s.set(5, 0, 6, "waxed_copper_block")  # Pell's marker
    return s, {"pell": "waxed_copper_block"}


def tamsin_grove():
    s = Site(13, 15, 13)
    s.floor(lambda x, z: "moss_block" if (x - 6) ** 2 + (z - 6) ** 2 <= 20 else None)
    s.fill(5, 0, 5, 6, 9, 6, "oak_log[axis=y]")  # the old oak: a 2x2 trunk
    for x, z, y in ((4, 5, 1), (7, 6, 1), (5, 7, 1), (6, 4, 1), (4, 6, 2), (7, 5, 2)):
        s.set(x, y, z, "oak_log[axis=y]")
    for x, z in ((3, 5), (8, 6), (5, 8), (6, 3)):
        s.set(x, 0, z, "rooted_dirt"); s.set(x, 1, z, "mangrove_roots")
    for x in range(1, 12):
        for z in range(1, 12):
            for y in range(8, 14):
                r = (x - 5.5) ** 2 + (z - 5.5) ** 2 + ((y - 10.5) * 1.6) ** 2
                if r <= 26 and not (5 <= x <= 6 and 5 <= z <= 6 and y <= 9):
                    s.set(x, y, z, "oak_leaves[persistent=true]" if (x + y + z) % 5 else "flowering_azalea_leaves[persistent=true]")
    for x, z in ((2, 6), (9, 4), (8, 9), (3, 9), (10, 7)):
        s.set(x, 1, z, "moss_carpet")
    s.set(9, 1, 8, "flowering_azalea"); s.set(3, 1, 3, "azalea")
    s.set(7, 1, 7, "lantern[hanging=false]")
    s.set(9, 0, 6, "mossy_cobblestone")  # Tamsin's marker, at the foot of the oak
    return s, {"tamsin": "mossy_cobblestone"}


def conclave_tower():
    s = Site(9, 17, 9)
    s.floor(lambda x, z: "polished_deepslate" if (x + z) % 2 else "calcite")
    for y in range(1, 13):
        for x in range(1, 8):
            for z in range(1, 8):
                edge = x in (1, 7) or z in (1, 7)
                corner = x in (1, 7) and z in (1, 7)
                if corner:
                    continue
                if edge:
                    window = y in (3, 4, 8, 9) and (x == 4 or z == 4)
                    s.set(x, y, z, "purple_stained_glass" if window else ("amethyst_block" if y % 4 == 0 else "calcite"))
    for y in (5, 10):  # two upper floors, with a ladder hole by the east wall
        s.fill(2, y, 2, 6, y, 6, "smooth_quartz")
    for y in range(1, 13):
        s.set(6, y, 3, "ladder[facing=west]")
    s.fill(4, 1, 1, 4, 2, 1, "air")  # door gap, north side
    s.fill(2, 13, 2, 6, 13, 6, "purpur_slab[type=bottom]"); s.set(4, 14, 4, "amethyst_cluster[facing=up]")
    for x, z in ((2, 2), (2, 6), (6, 2)):
        s.set(x, 1, z, "bookshelf"); s.set(x, 2, z, "bookshelf")
    s.set(2, 1, 4, "enchanting_table"); s.set(6, 6, 2, "lectern[facing=west]"); s.set(2, 6, 6, "bookshelf")
    s.set(3, 11, 3, "amethyst_cluster[facing=up]"); s.set(4, 3, 4, "end_rod[facing=up]")
    s.set(4, 0, 4, "purpur_block")  # Ilsabet's marker
    return s, {"ilsabet": "purpur_block"}


def stranger_caravan():
    s = Site(11, 6, 9)
    s.floor(lambda x, z: "dirt_path" if 3 <= z <= 5 else None)
    s.fill(2, 1, 2, 7, 1, 4, "stripped_spruce_wood[axis=x]")  # wagon bed
    for x in (2, 7):
        s.set(x, 1, 1, "dark_oak_trapdoor[facing=south,half=bottom,open=true]")
        s.set(x, 1, 5, "dark_oak_trapdoor[facing=north,half=bottom,open=true]")
    for x in range(2, 8):  # a too-clean white cover
        s.set(x, 2, 2, "white_wool"); s.set(x, 2, 4, "white_wool"); s.set(x, 3, 3, "white_wool")
    s.fill(3, 2, 3, 6, 2, 3, "light_gray_carpet")
    s.set(8, 1, 3, "spruce_fence"); s.set(9, 1, 3, "spruce_fence")
    s.set(1, 1, 7, "barrel[facing=up]"); s.set(2, 1, 7, "barrel[facing=up]"); s.set(9, 1, 7, "chest[facing=north]")
    s.set(4, 1, 7, "lantern[hanging=false]"); s.set(6, 1, 7, "white_carpet"); s.set(7, 1, 7, "white_carpet")
    s.set(5, 0, 6, "polished_andesite")  # the Stranger's marker
    return s, {"stranger": "polished_andesite"}


def wren_lookout():
    s = Site(9, 6, 9)
    s.floor(lambda x, z: "snow_block" if (x + z) % 4 else "packed_ice")
    s.fill(1, 1, 1, 1, 3, 4, "spruce_log[axis=y]")  # lean-to
    for z in range(1, 5):
        s.set(2, 3, z, "brown_wool"); s.set(3, 2, z, "brown_wool")
    s.set(2, 1, 2, "white_carpet"); s.set(2, 1, 3, "white_carpet")
    s.set(5, 0, 5, "cobblestone"); s.set(5, 1, 5, "campfire[lit=true]")
    s.set(6, 1, 2, "cartography_table"); s.set(7, 1, 2, "barrel[facing=up]")
    s.set(7, 1, 7, "spruce_fence"); s.set(7, 2, 7, "spruce_fence"); s.set(7, 3, 7, "lantern[hanging=false]")
    s.set(3, 0, 6, "blue_ice")  # Wren's marker
    return s, {"wren": "blue_ice"}


def sol_archive():
    s = Site(13, 8, 13)
    s.floor(lambda x, z: "chiseled_stone_bricks" if (x, z) == (6, 6) else ("stone_bricks" if (x + z) % 3 else "cracked_stone_bricks"))
    for i in range(13):
        for (x, z) in ((i, 0), (i, 12), (0, i), (12, i)):
            if z == 12 and 5 <= x <= 7:
                continue
            top = 3 + ((x * 3 + z * 5) % 4)
            for y in range(1, top):
                s.set(x, y, z, "stone_bricks" if (x + y + z) % 3 else "mossy_stone_bricks")
    for x in (2, 4, 8, 10):  # shelves in rows
        for z in (2, 3, 4, 8, 9):
            s.set(x, 1, z, "bookshelf"); s.set(x, 2, z, "bookshelf" if (x + z) % 2 else "air")
    s.set(6, 1, 3, "lectern[facing=south]"); s.set(3, 1, 10, "lectern[facing=east]")
    s.set(9, 1, 10, "candle[candles=3,lit=true]"); s.set(1, 1, 1, "cobweb"); s.set(11, 2, 1, "cobweb")
    s.set(6, 1, 1, "chiseled_bookshelf[facing=south]")
    s.set(6, 0, 8, "polished_granite")  # Sol's marker
    return s, {"sol": "polished_granite"}


# id: (builder, stage that unlocks it or None, quest whose completion gives the stage and the map, biome tag,
#      spacing, separation, salt, map name, locked line)
SITES = {
    "refugee_camp": (refugee_camp, None, None, None, 0, 0, 0, "Refugee Camp", ""),
    "thornwatch_outpost": (thornwatch_outpost, "tt_meet_rhosk", "c2_found", "#minecraft:has_structure/pillager_outpost",
                           32, 12, 74511201, "Thornwatch Outpost",
                           "Thornwatch sentries bar the gate. \"Captain's orders. Nobody in until Emberhold has a charter.\""),
    "pell_ruin": (pell_ruin, "tt_meet_pell", "c2_stage2", "#minecraft:has_structure/pillager_outpost",
                  32, 12, 74511202, "Ruin with a Tent",
                  "Something in the ruin ticks, then a voice: \"Not yet! Not yet. Grow your village first, then we'll talk.\""),
    "tamsin_grove": (tamsin_grove, "tt_meet_tamsin", "c3_pell", "#minecraft:is_forest",
                     28, 10, 74511203, "The Old Oak",
                     "The roots tighten. The wood isn't ready to speak with you yet."),
    "conclave_tower": (conclave_tower, "tt_meet_ilsabet", "c4_mirror", "#minecraft:has_structure/pillager_outpost",
                       36, 14, 74511204, "Lumen Conclave Tower",
                       "A ward of bent light turns you around. The Conclave only opens to someone it has heard of."),
    "stranger_caravan": (stranger_caravan, "tt_meet_stranger", "c5_town", "#minecraft:has_structure/pillager_outpost",
                         36, 14, 74511205, "A Clean Caravan",
                         "A polite voice from the wagon: \"Closed, I'm afraid. Come back when Emberhold is a town.\""),
    "wren_lookout": (wren_lookout, "tt_meet_wren", "c6_nether", "#minecraft:has_structure/igloo",
                     32, 12, 74511206, "Scout's Lookout",
                     "The camp is empty and the snow untouched. Whoever lives here is out scouting."),
    "sol_archive": (sol_archive, "tt_meet_sol", "c6_ready", "#minecraft:has_structure/pillager_outpost",
                    36, 14, 74511207, "Sunken Archive",
                    "The archive door is sealed with old Accord wax. It will open when the realms do."),
}
# Quest key -> (stage, map loot table) for gen_quests.py
MEET_AFTER = {v[2]: (v[1], f"tt:npc_maps/{k}") for k, v in SITES.items() if v[2]}


def write(path, data, binary=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if binary else "w", **({} if binary else {"encoding": "utf-8"})) as f:
        f.write(data if binary else json.dumps(data, indent=2) + "\n")


def main():
    cfg = {"_comment": "Generated by tools/gen_npc_sites.py; don't edit. Read by server_scripts/tt_npc_sites.js.",
           "camp": "tt:npc/refugee_camp", "sites": {}}
    for sid, (build, stage, after, biomes, spacing, sep, salt, title, locked) in SITES.items():
        site, markers = build()
        for npc, block in markers.items():
            assert npc in CAST, npc
            n = sum(1 for v in site.b.values() if v == block)
            assert n == 1, f"{sid}: marker {block} for {npc} appears {n} times (must be unique)"
        write(os.path.join(DATA, "structures", "npc", sid + ".nbt"), site.nbt(), binary=True)
        write(os.path.join(DATA, "worldgen", "template_pool", "npc", sid + ".json"), {
            "fallback": "minecraft:empty",
            "elements": [{"weight": 1, "element": {"element_type": "minecraft:single_pool_element",
                                                   "location": f"tt:npc/{sid}", "projection": "rigid",
                                                   "processors": "minecraft:empty"}}]})
        write(os.path.join(DATA, "worldgen", "structure", "npc", sid + ".json"), {
            "type": "minecraft:jigsaw",
            # the camp never generates on its own (an empty biome list); the script places it at spawn
            "biomes": biomes or [],
            "step": "surface_structures", "spawn_overrides": {}, "terrain_adaptation": "beard_thin",
            "start_pool": f"tt:npc/{sid}", "size": 1, "start_height": {"absolute": -1},
            "project_start_to_heightmap": "WORLD_SURFACE_WG", "max_distance_from_center": 80, "use_expansion_hack": False})
        if biomes:
            write(os.path.join(DATA, "worldgen", "structure_set", "npc", sid + ".json"), {
                "structures": [{"structure": f"tt:npc/{sid}", "weight": 1}],
                "placement": {"type": "minecraft:random_spread", "spacing": spacing, "separation": sep, "salt": salt}})
            write(os.path.join(DATA, "tags", "worldgen", "structure", "npc", sid + ".json"), {"values": [f"tt:npc/{sid}"]})
            write(os.path.join(DATA, "loot_tables", "npc_maps", sid + ".json"), {
                "type": "minecraft:chest",
                "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": "minecraft:map", "functions": [
                    {"function": "minecraft:exploration_map", "destination": f"tt:npc/{sid}", "decoration": "target_x",
                     "zoom": 2, "search_radius": 100, "skip_existing_chunks": False},
                    {"function": "minecraft:set_name", "name": {"text": title, "color": "gold", "italic": False}}]}]}]})
        cfg["sites"][f"tt:npc/{sid}"] = {
            "title": title, "stage": stage, "locked": locked,
            "npcs": {npc: {"marker": "minecraft:" + block, "preset": f"tt:easy_npc/preset/{CAST[npc][3]}/{npc}.npc.snbt"}
                     for npc, block in markers.items()}}
    write(os.path.join(DATA, "tags", "worldgen", "structure", "npc_sites.json"), {"values": [f"tt:npc/{s}" for s in SITES]})
    write(CFG, cfg)
    print(f"NPC sites: {len(SITES)} structures ({sum(len(v['npcs']) for v in cfg['sites'].values())} NPCs), "
          f"{len(MEET_AFTER)} unlocked by quests")


if __name__ == "__main__":
    main()
