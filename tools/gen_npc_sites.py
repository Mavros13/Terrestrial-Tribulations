#!/usr/bin/env python3
"""Story NPC sites: one small structure per story NPC, generated into the world (owner, 2026-10-29: "they spawn
naturally in specific structures that don't let you in until that chapter is unlocked").

Writes, all under pack/kubejs/data/tt/ (a data pack KubeJS loads before worldgen):
  structures/npc/<site>.nbt               the building (vanilla structure-template NBT, gzip, DataVersion 3465 = 1.20.1)
  worldgen/template_pool/npc/<site>.json  a one-piece jigsaw pool
  worldgen/processor_list/npc/<site>.json random weathering, so no two copies look the same
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
from gen_npcs import CAST, MOVES, WORK

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
        self.loot = {}  # (x, y, z) -> (block entity id, loot table) for chests and barrels

    def set(self, x, y, z, s):
        assert 0 <= x < self.w and 0 <= y < self.h and 0 <= z < self.d, (x, y, z)
        self.b[(x, y, z)] = s

    def put(self, x, y, z, s):
        """Set a block only where nothing is placed yet (air, or ground the site leaves to the world)."""
        if self.b.get((x, y, z), "air") == "air":
            self.set(x, y, z, s)

    def marker(self, x, y, z, s):
        """An NPC's marker block, with two blocks of headroom kept clear above it."""
        self.set(x, y, z, s)
        for dy in (1, 2):
            self.set(x, y + dy, z, "air")

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
            block = {"pos": (9, (3, [x, y, z])), "state": (3, index[s])}
            if (x, y, z) in self.loot:
                be, table = self.loot[(x, y, z)]
                block["nbt"] = (10, {"id": (8, be), "LootTable": (8, table)})
            blocks.append(block)
        return nbt_file({"DataVersion": (3, DATA_VERSION), "size": (9, (3, [self.w, self.h, self.d])),
                         "palette": (9, (10, palette)), "blocks": (9, (10, blocks)), "entities": (9, (10, []))})


# ---------- building helpers ----------
# Design notes (research 2026-10-29, docs/research/2026-10-29-structure-design.md): no flat boxes; walls get a dark,
# rough base fading to a cleaner top (gradient, not stripes), weathering gathers at corners, openings and bases;
# timber frames and stairs/slabs break up edges; light comes from where people would put it; paths are worn, mixed
# blocks. Per-copy variation comes from each site's processor list (PROCESSORS), not from the template.
def roll(x, z, salt=0, y=0):
    """A fixed 0-99 'random' number per cell, so every build of a site is identical."""
    return ((x * 73856093) ^ (z * 19349663) ^ (y * 2654435761) ^ (salt * 83492791)) % 100


def grad(pal, t, x, y, z, salt=0, spread=0.9):
    """Pick from a palette ordered dark/rough -> light/clean: t (0..1) is where the cell sits, plus some noise."""
    i = t * (len(pal) - 1) + (roll(x, z, salt, y) - 50) / 50 * spread
    return pal[max(0, min(len(pal) - 1, round(i)))]


def path_block(x, z, salt=0):
    """A worn path: mostly dirt path, with coarse dirt, gravel and packed mud worked in."""
    r = roll(x, z, salt)
    return "dirt_path" if r < 55 else "coarse_dirt" if r < 75 else "gravel" if r < 90 else "packed_mud"


def lay_path(s, cells, salt=0, maker=path_block):
    for x, z in cells:
        s.set(x, 0, z, maker(x, z, salt))


def lamp_post(s, x, z, height=2, top="lantern[hanging=false]", post="spruce_fence"):
    for y in range(1, height + 1):
        s.put(x, y, z, post)
    s.put(x, height + 1, z, top)


def plants(s, cells, salt, chance=35, kinds=("grass", "grass", "fern", "poppy", "dandelion", "oxeye_daisy",
                                              "pink_petals[flower_amount=3,facing=north]")):
    """Ground cover on cells whose ground the site leaves to the world (or that it lists itself)."""
    for x, z in cells:
        r = roll(x, z, salt)
        if r < chance:
            s.put(x, 1, z, kinds[r % len(kinds)])


def open_ground(s):
    return [(x, z) for x in range(s.w) for z in range(s.d) if (x, 0, z) not in s.b]


def tent(s, x0, z0, length, cloth, trim, along_x=True, front_lamp=True):
    """A 5-wide A-frame tent: solid sloping cloth sides with a few trim patches, a 1-wide aisle with a bedroll, a
    closed back with a pole, and a ridge pole sticking out at the open front (i = 0) with a lantern under it."""
    def at(i, d, y, st):
        if along_x:
            s.set(x0 + i, y, z0 + d, st)
        else:
            s.set(x0 + d, y, z0 + i, st)
    axis = "x" if along_x else "z"
    for i in range(length):
        for d, y in ((0, 1), (1, 1), (1, 2), (2, 3), (3, 2), (3, 1), (4, 1)):
            at(i, d, y, f"{trim}_wool" if roll(i + x0, d + z0, 31, y) < 15 else f"{cloth}_wool")
    at(length - 1, 2, 1, "spruce_fence"); at(length - 1, 2, 2, "spruce_fence")  # back pole
    for i in range(1, length - 1):
        at(i, 2, 1, f"{trim}_carpet" if i % 2 else f"{cloth}_carpet")
    if front_lamp and (x0 if along_x else z0) >= 1:
        at(-1, 2, 3, f"stripped_spruce_log[axis={axis}]")
        at(-1, 2, 2, "lantern[hanging=true]")


def lean_to(s, x0, z0, x1, z1, high, low, roof="spruce_stairs", facing="south"):
    """A roof on log posts, sloping down towards `facing` (stairs), open on all sides."""
    for x, z in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
        top = high if (facing == "south" and z == z0) or (facing == "north" and z == z1) else low
        for y in range(1, top):
            s.set(x, y, z, "spruce_log[axis=y]")
    depth = z1 - z0
    for z in range(z0, z1 + 1):
        k = (z - z0) if facing == "south" else (z1 - z)
        y = high - round(k * (high - low) / max(1, depth))
        for x in range(x0 - 1, x1 + 2):
            if 0 <= x < s.w:
                s.set(x, y, z, f"{roof}[facing={'north' if facing == 'south' else 'south'},half=bottom]")


def logs(s, x, z, n, axis="x", y=1):
    """A short pile of logs lying down."""
    for i in range(n):
        xx, zz = (x + i, z) if axis == "x" else (x, z + i)
        s.put(xx, y, zz, f"stripped_spruce_log[axis={axis}]" if roll(xx, zz, 33) < 40 else f"spruce_log[axis={axis}]")


STONE = ["cobblestone", "mossy_cobblestone", "andesite", "stone", "stone_bricks"]  # dark/rough -> clean
BRICK = ["mossy_stone_bricks", "cracked_stone_bricks", "stone_bricks", "stone_bricks", "polished_andesite"]


# ---------- the sites ----------
def refugee_camp():
    """Survivors' camp beside world spawn: Maera's big crimson tent, three smaller ones, a ringed fire with log
    benches, Doran's lean-to forge with a smoking chimney, supply crates and worn paths."""
    s = Site(17, 7, 17)
    c = 8
    lay_path(s, [(x, z) for x in range(17) for z in range(17)
                 if abs(x - c) + abs(z - c) <= 3 or (x == c and z > 10) or (z == c and x < 6)
                 or (x == c - 1 and z > 12) or (z == c + 1 and x < 3)], 1)
    for x, z in ((c - 1, c - 2), (c + 1, c - 2), (c - 2, c - 1), (c + 2, c - 1), (c - 2, c + 1), (c + 2, c + 1),
                 (c - 1, c + 2), (c + 1, c + 2), (c, c - 2), (c, c + 2), (c - 2, c), (c + 2, c)):
        s.set(x, 0, z, "cobblestone" if roll(x, z, 2) < 50 else "mossy_cobblestone")  # stone ring round the pit
    s.set(c, 0, c, "cobblestone")
    s.set(c, 1, c, "campfire[lit=true]")
    for x, z, st in ((c - 2, c - 2, "x"), (c + 2, c + 2, "x"), (c + 2, c - 2, "z"), (c - 2, c + 2, "z")):
        s.set(x, 1, z, f"stripped_spruce_log[axis={st}]")  # log benches on the diagonals
    tent(s, 2, 1, 6, "red", "brown")                 # Maera's tent, opening east towards the fire
    tent(s, 10, 1, 5, "white", "light_gray")
    tent(s, 1, 11, 4, "light_gray", "brown", along_x=False)
    tent(s, 5, 12, 4, "green", "brown", along_x=False)
    s.set(1, 1, 6, "red_banner[rotation=4]"); s.set(1, 1, 0, "red_banner[rotation=4]")
    # Doran's forge: a stone pad under a lean-to roof, chimney with a smoking campfire on top
    s.fill(11, 0, 11, 16, 0, 16, "polished_andesite")
    for x in range(11, 17):
        for z in range(11, 17):
            if roll(x, z, 3) < 35:
                s.set(x, 0, z, "cobblestone" if roll(x, z, 4) < 50 else "stone")
    lean_to(s, 12, 12, 15, 15, 5, 3, "spruce_stairs", "south")
    s.set(15, 1, 13, "blast_furnace[facing=west]"); s.set(13, 1, 12, "anvil[facing=east]")
    s.set(12, 1, 15, "water_cauldron[level=3]"); s.set(15, 1, 15, "smithing_table"); s.set(16, 1, 12, "grindstone[face=floor,facing=west]")
    for y in range(1, 6):
        s.set(16, y, 14, "cobblestone" if y < 3 else "cobblestone_wall")
    s.set(16, 6, 14, "campfire[lit=true]")
    s.set(14, 3, 13, "lantern[hanging=true]")
    s.set(11, 1, 16, "barrel[facing=up]"); s.set(11, 2, 16, "barrel[facing=up]"); s.set(12, 1, 16, "chest[facing=north]")
    s.loot[(12, 1, 16)] = ("minecraft:chest", "minecraft:chests/village/village_weaponsmith")
    # supplies: crates, hay, a cart's worth of barrels; lantern posts along the paths
    for x, z, h in ((6, 6, 2), (7, 6, 1), (6, 7, 1), (14, 7, 2), (15, 7, 1), (15, 8, 1)):
        for y in range(1, h + 1):
            s.put(x, y, z, "barrel[facing=up]" if (x + y) % 2 else "hay_block")
    for x, z in ((c + 1, 11), (5, c - 1), (12, c - 1), (c + 1, 4)):
        lamp_post(s, x, z)
    s.put(1, 1, 9, "composter[level=5]"); s.put(4, 1, 9, "crafting_table"); s.put(3, 1, 9, "loom[facing=north]")
    s.put(10, 1, 6, "decorated_pot[facing=west]"); s.put(9, 1, 1, "decorated_pot[facing=south]")
    s.put(9, 1, 6, "chest[facing=west]"); s.loot[(9, 1, 6)] = ("minecraft:chest", "minecraft:chests/village/village_plains_house")
    logs(s, 13, 9, 3, "x"); logs(s, 9, 15, 3, "x")
    plants(s, open_ground(s), 5)
    s.marker(13, 0, 14, "smooth_stone")  # Doran's marker, at the anvil under the forge roof
    s.marker(7, 0, 5, "red_terracotta")  # Maera's marker, at her tent's door, facing the fire
    return s, {"maera": "red_terracotta", "doran": "smooth_stone"}


def thornwatch_outpost():
    """A Thornwatch palisade fort: uneven sharpened log walls, a gatehouse with banners, a roofed watchtower on
    stilts, a green barracks tent, a training yard and a fire."""
    s = Site(19, 12, 19)
    n = 18
    s.floor(lambda x, z: "podzol" if roll(x, z, 6) < 35 else "coarse_dirt" if roll(x, z, 7) < 60 else "rooted_dirt")
    for i in range(n + 1):  # palisade: heights 3-5, pointed tops, gate in the south wall
        for x, z in ((i, 0), (i, n), (0, i), (n, i)):
            if z == n and 8 <= x <= 10:
                continue
            top = 3 + roll(x, z, 8) % 3 if not (x in (0, n) and z in (0, n)) else 6
            for y in range(1, top + 1):
                s.set(x, y, z, "spruce_log[axis=y]" if roll(x, z, 9, y) < 80 else "stripped_spruce_log[axis=y]")
            s.set(x, top + 1, z, "spruce_fence")
    for x in (7, 11):  # gate posts, a lintel, banners and lanterns
        for y in range(1, 7):
            s.set(x, y, n, "stripped_spruce_log[axis=y]")
        s.set(x, 7, n, "lantern[hanging=false]")
        s.set(x, 3, n - 1, "green_wall_banner[facing=north]")
    s.fill(7, 6, n, 11, 6, n, "stripped_spruce_log[axis=x]")
    s.fill(8, 5, n, 10, 5, n, "spruce_trapdoor[facing=south,half=top,open=false]")
    lay_path(s, [(x, z) for x in range(7, 12) for z in range(10, n + 1) if abs(x - 9) <= 1 or roll(x, z, 10) < 40], 11)
    lay_path(s, [(x, z) for x in range(5, 14) for z in range(6, 11) if abs(x - 9) + abs(z - 8) <= 3], 12)
    # watchtower, north-west: four log stilts, a plank deck with railings, a stair roof, a ladder up
    for x, z in ((2, 2), (6, 2), (2, 6), (6, 6)):
        for y in range(1, 9):
            s.set(x, y, z, "spruce_log[axis=y]")
    s.fill(2, 5, 2, 6, 5, 6, "spruce_planks"); s.set(5, 5, 5, "spruce_trapdoor[facing=north,half=top,open=false]")
    for i in range(2, 7):
        for x, z in ((i, 2), (i, 6), (2, i), (6, i)):
            if s.b[(x, 6, z)] == "air":
                s.set(x, 6, z, "spruce_fence")
    for y in range(1, 6):
        s.set(5, y, 7, "ladder[facing=south]")
    for ring, y in ((0, 9), (1, 10)):
        for x in range(1 + ring, 8 - ring):
            for z in range(1 + ring, 8 - ring):
                edge = x in (1 + ring, 7 - ring) or z in (1 + ring, 7 - ring)
                if edge:
                    f = "north" if z == 1 + ring else "south" if z == 7 - ring else "west" if x == 1 + ring else "east"
                    s.set(x, y, z, f"spruce_stairs[facing={'south' if f == 'north' else 'north' if f == 'south' else 'east' if f == 'west' else 'west'},half=bottom]")
    s.fill(3, 10, 3, 5, 10, 5, "spruce_slab[type=bottom]"); s.set(4, 11, 4, "green_wool")
    s.set(4, 9, 4, "spruce_planks")
    s.set(4, 8, 4, "lantern[hanging=true]")
    s.set(3, 6, 3, "barrel[facing=up]"); s.set(4, 6, 3, "target")
    # barracks tent and training yard
    tent(s, 12, 2, 5, "green", "brown", front_lamp=False)
    for x in (13, 15):
        s.set(x, 1, 9, "hay_block"); s.set(x, 2, 9, "target")
    s.set(17, 1, 8, "spruce_fence"); s.set(17, 2, 8, "carved_pumpkin[facing=west]")
    s.set(16, 1, 11, "grindstone[face=floor,facing=west]"); s.set(17, 1, 11, "smithing_table")
    s.set(17, 1, 12, "barrel[facing=up]"); s.set(17, 1, 13, "chest[facing=west]")
    s.loot[(17, 1, 13)] = ("minecraft:chest", "minecraft:chests/village/village_fletcher")
    # the fire, with stair benches
    s.set(9, 0, 8, "cobblestone"); s.set(9, 1, 8, "campfire[lit=true]")
    s.set(7, 1, 8, "spruce_stairs[facing=west,half=bottom]"); s.set(11, 1, 8, "spruce_stairs[facing=east,half=bottom]")
    s.set(9, 1, 6, "spruce_stairs[facing=north,half=bottom]")
    for x, z, f in ((1, 9, "east"), (1, 14, "east"), (n - 1, 15, "west"), (8, 1, "south"), (14, 17, "north")):
        s.put(x, 2, z, f"wall_torch[facing={f}]")
    logs(s, 2, 12, 3, "z"); s.put(3, 1, 12, "stripped_spruce_log[axis=z]")
    s.put(2, 1, 16, "composter[level=6]"); s.put(4, 1, 16, "barrel[facing=up]"); s.put(3, 1, 16, "crafting_table")
    plants(s, [(x, z) for x in range(1, n) for z in range(1, n)], 13, 18, ("grass", "fern", "fern", "dead_bush"))
    s.marker(9, 0, 12, "moss_block")  # Rhosk's marker, on the gate road
    return s, {"rhosk": "moss_block"}


def pell_ruin():
    """An Old Engine ruin: broken brick walls with a dark, mossy base, a fallen column, a huge rusting boiler going
    green, pipes and scrap, and Pell's patched tent and workbench in the lee of the wall."""
    s = Site(17, 10, 15)
    s.floor(lambda x, z: grad(["gravel", "cobblestone", "mossy_cobblestone", "stone_bricks", "cracked_stone_bricks"],
                               0.6, x, 0, z, 14, 1.4) if roll(x, z, 15) < 85 else None)
    for x in range(17):  # north wall: tall at the east end, broken down to the west; window gaps
        top = 2 + (x * 5 % 4) + (3 if x > 10 else 0)
        for y in range(1, min(top, 9)):
            if y in (3, 4) and x in (12, 14):
                continue
            s.set(x, y, 0, grad(BRICK, y / 7, x, y, 0, 16))
    for z in range(15):  # west wall, low and broken
        top = 1 + (z * 7 % 4)
        for y in range(1, top):
            s.set(0, y, z, grad(BRICK, y / 5, 0, y, z, 17))
    for x in (4, 9, 15):  # buttresses on the north wall
        s.set(x, 1, 1, "stone_brick_stairs[facing=north,half=bottom]")
        s.set(x, 2, 1, "stone_brick_slab[type=bottom]") if x == 15 else None
    for x in range(2, 7):  # a fallen column
        s.set(x, 1, 11, "stone_bricks" if x % 2 else "chiseled_stone_bricks")
    s.set(7, 1, 11, "stone_brick_stairs[facing=east,half=bottom]")
    # the boiler: a 3-wide copper drum lying along x, oxidising from the bottom up
    for x in range(9, 15):
        for y, z in ((1, 4), (1, 5), (1, 6), (2, 3), (2, 7), (3, 3), (3, 7), (4, 4), (4, 5), (4, 6), (2, 4), (2, 6), (3, 4), (3, 6), (2, 5), (3, 5)):
            s.set(x, y, z, grad(["oxidized_copper", "weathered_copper", "exposed_copper", "copper_block"], (y - 1) / 3, x, y, z, 18, 1.2))
    for z in (4, 6):
        for x in (8, 15):
            s.set(x, 1, z, "polished_andesite") if x == 8 else s.set(x, 1, z, "polished_andesite")
    s.set(15, 2, 5, "iron_bars"); s.set(15, 3, 5, "iron_bars"); s.set(8, 3, 5, "cut_copper_stairs[facing=east,half=bottom]")
    for y in range(5, 9):
        s.set(11, y, 5, "weathered_cut_copper" if y < 8 else "lightning_rod[facing=up]")
    s.set(13, 5, 5, "exposed_cut_copper_slab[type=bottom]")
    for x in range(1, 4):
        s.set(x, 3, 1, "chain[axis=x]")
    s.set(1, 2, 1, "lantern[hanging=true]")
    # Pell's tent against the west wall, workbench, scrap heaps
    tent(s, 1, 2, 5, "brown", "light_gray", along_x=False, front_lamp=False)
    s.set(6, 1, 13, "crafting_table"); s.set(7, 1, 13, "smithing_table"); s.set(8, 1, 13, "grindstone[face=floor,facing=north]")
    s.set(5, 1, 13, "chest[facing=north]"); s.loot[(5, 1, 13)] = ("minecraft:chest", "minecraft:chests/village/village_toolsmith")
    s.set(9, 1, 13, "lantern[hanging=false]")
    for x, y, z, b in ((2, 1, 8, "cut_copper_stairs[facing=east,half=bottom]"), (3, 1, 8, "exposed_cut_copper"),
                       (3, 2, 8, "chain[axis=x]"), (6, 1, 3, "weathered_copper"), (7, 1, 3, "iron_bars"),
                       (6, 1, 2, "chipped_anvil[facing=east]"), (7, 1, 2, "exposed_cut_copper_slab[type=bottom]"),
                       (10, 1, 9, "decorated_pot[facing=north]"), (12, 1, 9, "cauldron"), (1, 1, 1, "cobweb"),
                       (16, 1, 9, "piston[facing=up]"), (16, 1, 10, "sticky_piston[facing=west]"), (16, 1, 11, "observer[facing=up]"),
                       (5, 0, 7, "cobblestone")):
        s.put(x, y, z, b)
    s.set(5, 1, 8, "campfire[lit=true]")
    s.put(10, 3, 1, "wall_torch[facing=south]")
    s.put(15, 4, 1, "wall_torch[facing=south]")
    for x in range(17):  # moss creeping over the wall tops
        top = min(2 + (x * 5 % 4) + (3 if x > 10 else 0), 9)
        if roll(x, 0, 19) < 45 and s.b.get((x, top, 0)) == "air":
            s.set(x, top, 0, "moss_carpet")
    plants(s, open_ground(s), 20, 40, ("grass", "dead_bush", "brown_mushroom", "fern"))
    s.marker(7, 0, 8, "waxed_copper_block")  # Pell's marker, between the fire and the bench
    return s, {"pell": "waxed_copper_block"}


def tamsin_grove():
    """An ancient oak: a 3x3 trunk with buttress roots, branches and an uneven crown of oak and azalea leaves;
    lanterns hung in the crown, a mossy stone shrine with candles, flowers and stepping stones in."""
    s = Site(17, 19, 17)
    c = 8
    s.floor(lambda x, z: ("moss_block" if roll(x, z, 21) < 70 else "rooted_dirt") if (x - c) ** 2 + (z - c) ** 2 <= 30 else None)
    s.fill(c - 1, 0, c - 1, c + 1, 11, c + 1, "oak_log[axis=y]")
    for x, z in ((c - 1, c - 1), (c + 1, c + 1)):  # trim two corners up high so the trunk isn't a square post
        for y in range(9, 12):
            s.set(x, y, z, "air")
    for dx, dz in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, 1), (2, -1)):  # buttress roots
        ax = "x" if dx else "z"
        s.set(c + dx, 1, c + dz, f"oak_log[axis={ax}]"); s.set(c + dx, 0, c + dz, "rooted_dirt")
        s.set(c + dx * 3 // 2, 0, c + dz * 3 // 2, "rooted_dirt"); s.put(c + dx * 3 // 2, 1, c + dz * 3 // 2, "mangrove_roots")
    for (dx, dz), y in (((1, 0), 9), ((-1, 0), 10), ((0, 1), 8), ((0, -1), 11)):  # branches
        for k in range(2, 6):
            s.set(c + dx * k, y + (k > 3), c + dz * k, f"oak_log[axis={'x' if dx else 'z'}]")
    blobs = ((c, 14, c, 4.2), (c + 4, 11, c, 3.0), (c - 4, 12, c, 3.0), (c, 11, c + 4, 2.8), (c, 13, c - 4, 3.0))
    for x in range(17):
        for z in range(17):
            for y in range(7, 19):
                if s.b.get((x, y, z), "air") != "air":
                    continue
                for bx, by, bz, r in blobs:
                    if (x - bx) ** 2 + ((y - by) * 1.4) ** 2 + (z - bz) ** 2 <= r * r + (roll(x, z, 22, y) - 50) / 30:
                        k = roll(x, z, 23, y)
                        s.set(x, y, z, "oak_leaves[persistent=true]" if k < 70 else
                              "azalea_leaves[persistent=true]" if k < 88 else "flowering_azalea_leaves[persistent=true]")
                        break
    for x, y, z in ((c + 3, 8, c + 1), (c - 3, 9, c - 1), (c + 1, 8, c + 3), (c - 1, 10, c - 3), (c + 5, 9, c - 1)):
        if s.b.get((x, y + 1, z), "air") != "air" and s.b.get((x, y, z)) == "air":
            s.set(x, y, z, "lantern[hanging=true]")
    # shrine: a ring of mossy brick walls with candles, a seat, a pot of flowers
    for x, z in ((3, 12), (2, 13), (3, 14), (4, 15), (5, 14)):
        s.set(x, 1, z, "mossy_stone_brick_wall"); s.set(x, 2, z, "candle[candles=3,lit=true]" if (x + z) % 2 else "candle[candles=1,lit=true]")
    s.set(4, 0, 13, "mossy_stone_bricks"); s.set(4, 1, 13, "mossy_stone_brick_slab[type=bottom]")
    s.set(3, 1, 13, "decorated_pot[facing=east]")
    s.set(5, 1, 12, "mossy_stone_brick_stairs[facing=south,half=bottom]")
    for z in range(13, 17):  # stepping stones in from the south
        for x in (c, c + 1):
            if roll(x, z, 24) < 60:
                s.set(x, 0, z, "mossy_stone_bricks" if roll(x, z, 25) < 50 else "stone")
    flowers = ("pink_petals[flower_amount=4,facing=east]", "lily_of_the_valley", "fern", "grass", "azure_bluet",
               "pink_petals[flower_amount=2,facing=south]", "allium", "red_mushroom", "brown_mushroom")
    plants(s, [(x, z) for x in range(17) for z in range(17) if (x - c) ** 2 + (z - c) ** 2 <= 40], 26, 50, flowers)
    for x, z in ((1, 2), (15, 14), (14, 1)):  # old stumps with moss
        s.put(x, 1, z, "oak_log[axis=y]"); s.put(x, 2, z, "moss_carpet")
    s.marker(c + 3, 0, c + 1, "mossy_cobblestone")  # Tamsin's marker, at the foot of the oak
    return s, {"tamsin": "mossy_cobblestone"}


def conclave_tower():
    """A Lumen Conclave tower: octagonal, on a dark plinth with buttresses, walls fading from dark deepslate to
    pale calcite, amethyst trim, a narrower top storey and a pointed roof; lit windows only where rooms are."""
    s = Site(15, 26, 15)
    c = 7

    def octo(x, z, r):
        dx, dz = abs(x - c), abs(z - c)
        return dx <= r and dz <= r and dx + dz <= r + r // 2

    def ring(r):
        return [(x, z) for x in range(15) for z in range(15) if octo(x, z, r) and not octo(x, z, r - 1)]
    s.floor(lambda x, z: grad(["polished_deepslate", "deepslate_tiles", "polished_blackstone_bricks", "calcite"],
                               0.5, x, 0, z, 27, 1.3) if octo(x, z, 7) else None)
    for y in range(3, 15):  # main walls, r=4 above the plinth
        for x, z in ring(4):
            t = (y - 3) / 11
            s.set(x, y, z, "amethyst_block" if y in (8, 14) else grad(["deepslate_bricks", "polished_deepslate", "tuff", "calcite", "calcite"], t, x, y, z, 28))
    for x, z in ring(5):  # plinth
        s.set(x, 1, z, "polished_deepslate"); s.set(x, 2, z, "polished_deepslate")
    for y in range(1, 3):  # interior of the plinth is the ground-floor room
        for x, z in ring(4):
            s.set(x, y, z, "deepslate_bricks")
    for y in range(15, 21):  # upper storey, narrower
        for x, z in ring(3):
            s.set(x, y, z, "amethyst_block" if y == 20 else grad(["tuff", "calcite", "calcite", "smooth_quartz"], (y - 15) / 5, x, y, z, 29))
    for x, z in ring(4):  # ledge where it steps in
        s.set(x, 15, z, "polished_deepslate_slab[type=bottom]")
    for r, y in ((3, 21), (2, 22), (1, 23)):  # pointed roof
        for x, z in ring(r):
            s.set(x, y, z, "purpur_pillar[axis=y]" if r > 1 else "amethyst_block")
        for x, z in ring(r + 1):
            if y == 21:
                s.put(x, y, z, "purpur_slab[type=bottom]")
    s.set(c, 22, c, "purpur_pillar[axis=y]"); s.set(c, 23, c, "amethyst_block"); s.set(c, 24, c, "end_rod[facing=up]")
    for x, z in ((c - 5, c - 2), (c - 5, c + 2), (c + 5, c - 2), (c + 5, c + 2), (c - 2, c - 5), (c + 2, c - 5), (c - 2, c + 5), (c + 2, c + 5)):
        for y in range(1, 6):  # buttresses
            s.set(x, y, z, "polished_deepslate_wall" if y > 2 else "polished_deepslate")
        s.set(x, 6, z, "amethyst_cluster[facing=up]")
    for y in (7, 13):  # floors
        for x in range(15):
            for z in range(15):
                if octo(x, z, 3):
                    s.set(x, y, z, "dark_oak_planks" if y == 7 else "smooth_quartz")
    for y in range(1, 20):  # ladder by the east wall
        s.set(c + 3, y, c, "ladder[facing=west]")
    for y in (7, 13):
        s.set(c + 3, y, c, "ladder[facing=west]")
    # windows: a few tall ones where the rooms are, glowing from inside
    for (x, z), ys in (((c, c - 4), (4, 5)), ((c - 4, c), (9, 10, 11)), ((c, c + 4), (9, 10)), ((c + 3, c - 3), (4,)),
                        ((c - 3, c + 3), (16, 17)), ((c + 3, c + 3), (17,)), ((c, c - 3), (17, 18))):
        for y in ys:
            if 0 <= x < 15 and 0 <= z < 15:
                s.set(x, y, z, "purple_stained_glass")
    # door, south side: an arch with soul lanterns, steps up through the plinth
    for y in range(1, 5):
        s.set(c, y, c + 4, "air"); s.set(c, y, c + 5, "air") if y < 3 else None
    for x in (c - 1, c + 1):
        s.set(x, 1, c + 5, "polished_deepslate"); s.set(x, 2, c + 5, "polished_deepslate")
    s.set(c - 1, 5, c + 4, "deepslate_brick_stairs[facing=east,half=top]"); s.set(c + 1, 5, c + 4, "deepslate_brick_stairs[facing=west,half=top]")
    for x in (c - 2, c + 2):
        s.put(x, 1, c + 6, "polished_deepslate_wall"); s.put(x, 2, c + 6, "soul_lantern[hanging=false]")
    s.set(c, 0, c + 6, "polished_deepslate"); s.set(c, 0, c + 7, "deepslate_tiles")
    # rooms
    s.set(c - 2, 1, c - 2, "bookshelf"); s.set(c - 2, 2, c - 2, "bookshelf"); s.set(c - 1, 1, c - 3, "bookshelf")
    s.set(c + 2, 1, c - 2, "enchanting_table"); s.set(c + 2, 2, c - 2, "air")
    s.set(c - 3, 1, c, "chiseled_bookshelf[facing=east,slot_0_occupied=true,slot_2_occupied=true,slot_3_occupied=true]")
    s.set(c - 2, 1, c + 2, "lectern[facing=north]")
    s.set(c, 6, c, "chain[axis=y]"); s.set(c, 5, c, "soul_lantern[hanging=true]")
    s.set(c - 2, 8, c - 2, "brewing_stand"); s.set(c - 2, 8, c + 2, "cauldron"); s.set(c + 1, 8, c - 2, "bookshelf")
    s.set(c - 3, 8, c, "bookshelf"); s.set(c - 3, 9, c, "purple_candle[candles=3,lit=true]")
    s.set(c, 8, c, "purple_carpet"); s.set(c - 1, 8, c, "purple_carpet"); s.set(c, 8, c - 1, "purple_carpet")
    s.set(c + 1, 8, c + 2, "chest[facing=north]"); s.loot[(c + 1, 8, c + 2)] = ("minecraft:chest", "minecraft:chests/village/village_cartographer")
    s.set(c, 12, c, "chain[axis=y]"); s.set(c, 11, c, "soul_lantern[hanging=true]")
    s.set(c, 14, c, "amethyst_cluster[facing=up]"); s.set(c - 2, 14, c, "end_rod[facing=up]"); s.set(c + 1, 14, c - 2, "lectern[facing=south]")
    s.set(c, 20, c, "chain[axis=y]")
    s.set(c, 19, c, "soul_lantern[hanging=true]")
    for x, z in ((c - 6, c - 1), (c - 6, c + 1), (c + 6, c - 1), (c + 6, c + 1), (c - 1, c - 6), (c + 1, c - 6)):
        s.put(x, 1, z, "allium" if (x + z) % 2 else "azure_bluet")
    s.marker(c, 0, c, "purpur_block")  # Ilsabet's marker, centre of the ground floor
    return s, {"ilsabet": "purpur_block"}


def stranger_caravan():
    """A too-clean covered wagon and a little market stall under a striped awning, on a rutted road."""
    s = Site(15, 7, 13)
    for x in range(15):  # wheel ruts either side of a grassy crown
        for z in (4, 6):
            r = roll(x, z, 34)
            s.set(x, 0, z, "coarse_dirt" if r < 45 else "gravel" if r < 75 else "dirt_path")
        s.set(x, 0, 5, "dirt_path" if roll(x, 5, 35) < 45 else "grass_block")
    # wagon: plank bed on trapdoor wheels, fence hoops, a white cover, a driver's bench, a hitch
    s.fill(3, 1, 3, 9, 1, 7, "stripped_birch_wood[axis=x]")
    for x in (4, 8):
        s.set(x, 1, 2, "spruce_trapdoor[facing=north,half=bottom,open=true]")
        s.set(x, 1, 8, "spruce_trapdoor[facing=south,half=bottom,open=true]")
    for x in range(3, 10):
        cover = "white_wool" if x not in (3, 9) else "air"
        for z, y in ((3, 2), (7, 2), (3, 3), (7, 3), (4, 4), (6, 4), (5, 4)):
            if x in (3, 9):
                if x == 3 and (z, y) in ((3, 2), (7, 2)):
                    s.set(x, y, z, "birch_fence")
                continue
            s.set(x, y, z, "white_wool" if roll(x, z, 36, y) < 85 else "light_gray_wool")
    s.set(9, 2, 4, "white_wool"); s.set(9, 2, 6, "white_wool"); s.set(9, 3, 5, "white_wool")  # closed back
    s.set(2, 2, 5, "birch_stairs[facing=east,half=bottom]")
    s.set(1, 1, 5, "birch_fence"); s.set(0, 1, 5, "birch_fence")
    s.set(9, 4, 5, "white_wool"); s.set(10, 4, 5, "stripped_birch_log[axis=x]"); s.set(10, 3, 5, "lantern[hanging=true]")
    s.fill(4, 2, 4, 8, 2, 6, "light_gray_carpet"); s.set(7, 2, 5, "chest[facing=west]")
    s.loot[(7, 2, 5)] = ("minecraft:chest", "minecraft:chests/village/village_temple")
    # market stall: counter, striped awning on posts, goods
    for x in (3, 9):
        for y in range(1, 4):
            s.set(x, y, 11, "birch_fence"); s.set(x, y, 9, "birch_fence") if y < 3 else None
    for x in range(2, 11):
        s.set(x, 4, 11, "white_wool" if x % 2 else "light_gray_wool")
        s.set(x, 3, 9, f"{'white' if x % 2 else 'light_gray'}_wool")
    for x in range(4, 9):
        s.set(x, 1, 10, "birch_trapdoor[facing=north,half=top,open=false]" if x % 2 else "barrel[facing=up]")
    s.set(4, 2, 10, "potted_white_tulip"); s.set(5, 2, 10, "white_candle[candles=3,lit=true]")
    s.set(6, 2, 10, "decorated_pot[facing=north]"); s.set(7, 2, 10, "white_candle[candles=2,lit=true]"); s.set(8, 2, 10, "potted_lily_of_the_valley")
    s.set(6, 1, 12, "white_carpet"); s.set(7, 1, 12, "white_carpet"); s.set(5, 1, 12, "white_carpet")
    lamp_post(s, 12, 9, 2, "lantern[hanging=false]", "birch_fence"); lamp_post(s, 1, 9, 2, "lantern[hanging=false]", "birch_fence")
    s.set(13, 1, 2, "white_banner[rotation=4]"); s.set(12, 1, 2, "hay_block"); s.set(11, 1, 2, "hay_block")
    s.set(14, 1, 9, "barrel[facing=up]")
    plants(s, [(x, z) for x in range(15) for z in (0, 1, 2, 8, 9, 10, 11, 12)], 37, 25, ("grass", "dandelion", "oxeye_daisy", "white_tulip", "grass"))
    s.marker(10, 0, 11, "polished_andesite")  # the Stranger's marker, at the stall
    return s, {"stranger": "polished_andesite"}


def wren_lookout():
    """A scout's lookout on stilts above the snow: a railed deck with a stair roof and a ladder, a fur lean-to, a
    fire pit and a firewood stack below."""
    s = Site(13, 11, 13)
    s.floor(lambda x, z: "snow_block" if roll(x, z, 38) < 70 or roll(x, z, 39) >= 60 else "packed_ice")
    for x, z in ((6, 2), (10, 2), (6, 6), (10, 6)):  # stilts, taller at the back to carry the roof
        for y in range(1, 9 if z == 2 else 7):
            s.set(x, y, z, "spruce_log[axis=y]" if y < 5 else "stripped_spruce_log[axis=y]")
    s.fill(6, 5, 2, 10, 5, 6, "spruce_planks")
    for i in range(6, 11):
        for x, z in ((i, 2), (i, 6)):
            if s.b[(x, 6, z)] == "air":
                s.set(x, 6, z, "spruce_fence")
    for i in range(3, 6):
        for x in (6, 10):
            if s.b[(x, 6, i)] == "air" and not (x == 6 and i == 4):
                s.set(x, 6, i, "spruce_fence")
    for z in range(2, 7):  # roof sloping down to the south
        for x in range(5, 12):
            s.set(x, 9 - (z - 2) // 2, z, "spruce_stairs[facing=north,half=bottom]")
    for y in range(1, 6):
        s.set(5, y, 4, "ladder[facing=west]")
    s.set(8, 6, 3, "cartography_table"); s.set(9, 6, 3, "barrel[facing=up]"); s.set(8, 8, 3, "lantern[hanging=true]")
    s.set(9, 6, 5, "chest[facing=north]"); s.loot[(9, 6, 5)] = ("minecraft:chest", "minecraft:chests/igloo_chest")
    s.set(10, 10, 2, "light_blue_banner[rotation=8]")
    # fur lean-to and fire below
    s.fill(1, 1, 7, 1, 3, 11, "spruce_log[axis=y]")
    for z in range(7, 12):
        s.set(2, 3, z, "brown_wool" if roll(2, z, 40) < 70 else "white_wool"); s.set(3, 2, z, "brown_wool" if roll(3, z, 41) < 60 else "white_wool")
    s.set(2, 1, 8, "white_carpet"); s.set(2, 1, 9, "brown_carpet"); s.set(2, 1, 10, "white_carpet")
    s.set(2, 2, 7, "lantern[hanging=true]") if s.b[(2, 3, 7)] != "air" else None
    s.set(6, 0, 9, "cobblestone"); s.set(6, 1, 9, "campfire[lit=true]")
    s.set(5, 1, 11, "spruce_stairs[facing=south,half=bottom]"); s.set(8, 1, 9, "spruce_stairs[facing=east,half=bottom]")
    logs(s, 9, 11, 3, "x"); s.put(9, 2, 11, "spruce_log[axis=x]"); s.put(10, 2, 11, "stripped_spruce_log[axis=x]")
    lamp_post(s, 11, 8)
    s.set(12, 1, 1, "spruce_fence"); s.set(12, 2, 1, "spruce_fence"); s.set(12, 3, 1, "lantern[hanging=false]")
    for x in range(13):
        for z in range(13):
            if roll(x, z, 42) < 35:
                s.put(x, 1, z, "snow[layers=2]" if roll(x, z, 43) < 60 else "snow[layers=1]")
    s.marker(4, 0, 9, "blue_ice")  # Wren's marker, by the fire
    return s, {"wren": "blue_ice"}


def sol_archive():
    """A half-buried Accord archive: thick brick walls on a dark rubble base, buttresses, a broken arch door,
    roof beams with hanging lanterns, rows of shelves (some still full), a reading rug and a great lectern."""
    s = Site(17, 11, 17)
    n = 16
    s.floor(lambda x, z: grad(["mossy_stone_bricks", "cracked_stone_bricks", "stone_bricks", "polished_andesite"],
                               0.55, x, 0, z, 44, 1.3))
    for i in range(n + 1):
        for x, z in ((i, 0), (i, n), (0, i), (n, i)):
            if z == n and 7 <= x <= 9:
                continue
            top = 4 + (x * 3 + z * 5) % 4 + (2 if (x in (0, n) and z in (0, n)) else 0)
            if (z == 0 and 10 <= x <= 13) or (x == n and 4 <= z <= 6):
                top = 2  # collapsed sections
            for y in range(1, top):
                s.set(x, y, z, grad(BRICK, (y - 1) / 6, x, y, z, 45))
    for x, z, f in ((4, -1, "north"), (12, -1, "north"), (-1, 4, "west"), (-1, 12, "west"), (n + 1, 12, "east")):
        pass  # (buttresses would sit outside the box; the corner columns do this job)
    for x in (6, 10):  # door arch
        for y in range(1, 6):
            s.set(x, y, n, "chiseled_stone_bricks" if y == 3 else "stone_bricks")
    s.set(7, 5, n, "stone_brick_stairs[facing=east,half=top]"); s.set(9, 5, n, "stone_brick_stairs[facing=west,half=top]")
    s.set(8, 5, n, "chiseled_stone_bricks")
    for x in range(1, n):  # roof beams, two of them broken
        for z in (5, 11):
            if not (z == 5 and 9 <= x <= 12):
                s.set(x, 7, z, "stripped_dark_oak_log[axis=x]") if s.b.get((x, 7, z)) == "air" else None
    for x, z in ((4, 5), (12, 11), (4, 11)):
        s.set(x, 6, z, "chain[axis=y]"); s.set(x, 5, z, "lantern[hanging=true]")
    for x in (3, 5, 11, 13):  # shelf rows
        for z in (2, 3, 4, 7, 8, 9):
            full = roll(x, z, 46) < 40
            s.set(x, 1, z, "bookshelf"); s.set(x, 2, z, "bookshelf" if roll(x, z, 47) < 70 else "air")
            if full and s.b[(x, 2, z)] == "bookshelf":
                s.set(x, 3, z, "candle[candles=2,lit=true]" if roll(x, z, 48) < 75 else "skeleton_skull[rotation=8]")
    s.set(8, 1, 3, "lectern[facing=south]"); s.set(8, 0, 3, "chiseled_stone_bricks")
    s.set(7, 1, 2, "candle[candles=4,lit=true]"); s.set(9, 1, 2, "candle[candles=3,lit=true]")
    s.set(8, 1, 1, "chiseled_bookshelf[facing=south,slot_0_occupied=true,slot_1_occupied=true,slot_4_occupied=true]")
    s.set(1, 1, 8, "chiseled_bookshelf[facing=east,slot_2_occupied=true,slot_5_occupied=true]")
    for x in range(6, 11):
        for z in range(6, 10):
            s.set(x, 1, z, "brown_carpet" if (x in (6, 10) or z in (6, 9)) else "red_carpet")
    s.set(14, 1, 14, "chest[facing=west]"); s.loot[(14, 1, 14)] = ("minecraft:chest", "minecraft:chests/stronghold_library")
    for x, z in ((1, 1), (15, 1), (1, 15), (2, 1)):
        s.put(x, 1, z, "cobweb")
    for x, z in ((14, 5), (15, 5), (14, 4), (12, 1), (11, 1)):  # rubble where the walls fell in
        s.put(x, 1, z, "cobblestone" if roll(x, z, 49) < 40 else "stone_brick_slab[type=bottom]" if roll(x, z, 50) < 70 else "gravel")
    for x, z in ((5, 13), (11, 13)):
        s.put(x, 1, z, "decorated_pot[facing=north]")
    lamp_post(s, 2, 13, 1, "lantern[hanging=false]", "stone_brick_wall"); lamp_post(s, 14, 9, 1, "lantern[hanging=false]", "stone_brick_wall")
    for i in range(n + 1):  # moss on the broken wall tops
        for x, z in ((i, 0), (0, i), (n, i), (i, n)):
            for y in range(9, 0, -1):
                if s.b.get((x, y, z), "air") != "air":
                    if roll(x, z, 51) < 40 and y + 1 < s.h:
                        s.set(x, y + 1, z, "moss_carpet")
                    break
    s.marker(8, 0, 11, "polished_granite")  # Sol's marker, in the aisle facing the lectern
    return s, {"sol": "polished_granite"}


# Per-site weathering so no two copies match (vanilla processor lists, rule + random_block_match). Only blocks
# without states (a rule's output replaces the whole state). Never output a site's own marker block.
PROCESSORS = {
    "refugee_camp": [("dirt_path", "coarse_dirt", 0.12), ("cobblestone", "mossy_cobblestone", 0.2)],
    "thornwatch_outpost": [("coarse_dirt", "podzol", 0.15)],
    "pell_ruin": [("stone_bricks", "cracked_stone_bricks", 0.2), ("stone_bricks", "mossy_stone_bricks", 0.15),
                  ("copper_block", "exposed_copper", 0.25), ("exposed_copper", "weathered_copper", 0.2),
                  ("cobblestone", "gravel", 0.1)],
    "tamsin_grove": [("moss_block", "rooted_dirt", 0.1)],
    "conclave_tower": [("calcite", "diorite", 0.06), ("deepslate_bricks", "cracked_deepslate_bricks", 0.15)],
    "stranger_caravan": [("grass_block", "dirt_path", 0.2)],
    "wren_lookout": [("packed_ice", "snow_block", 0.25)],
    "sol_archive": [("stone_bricks", "cracked_stone_bricks", 0.25), ("stone_bricks", "mossy_stone_bricks", 0.2),
                    ("bookshelf", "air", 0.08), ("polished_andesite", "andesite", 0.2)],
}

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
            (mx, my, mz), = [k for k, v in site.b.items() if v == block]
            assert all(site.b.get((mx, my + dy, mz), "air") == "air" for dy in (1, 2)), f"{sid}: {npc} has no headroom"
        write(os.path.join(DATA, "structures", "npc", sid + ".nbt"), site.nbt(), binary=True)
        write(os.path.join(DATA, "worldgen", "template_pool", "npc", sid + ".json"), {
            "fallback": "minecraft:empty",
            "elements": [{"weight": 1, "element": {"element_type": "minecraft:single_pool_element",
                                                   "location": f"tt:npc/{sid}", "projection": "rigid",
                                                   "processors": f"tt:npc/{sid}"}}]})
        for _, out, _p in PROCESSORS[sid]:
            assert out not in markers.values(), f"{sid}: weathering must not make marker blocks ({out})"
        write(os.path.join(DATA, "worldgen", "processor_list", "npc", sid + ".json"), {"processors": [
            {"processor_type": "minecraft:rule", "rules": [
                {"input_predicate": {"predicate_type": "minecraft:random_block_match", "block": "minecraft:" + a,
                                     "probability": prob},
                 "location_predicate": {"predicate_type": "minecraft:always_true"},
                 "output_state": {"Name": "minecraft:" + out}} for a, out, prob in PROCESSORS[sid]]}]})
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
    cfg["moves"] = {npc: {"stage": st, "buildings": ["minecolonies:" + b for b in blds], "spots": spots,
                          "name": CAST[npc][1], "line": line}
                    for npc, (st, blds, spots, line) in MOVES.items()}
    cfg["work"] = {CAST[npc][1]: {"swing": bool(w.get("swing")), "sound": w.get("sound"), "particle": w.get("particle")}
                   for npc, w in WORK.items() if w.get("swing") or w.get("sound") or w.get("particle")}
    write(os.path.join(DATA, "tags", "worldgen", "structure", "npc_sites.json"), {"values": [f"tt:npc/{s}" for s in SITES]})
    write(CFG, cfg)
    print(f"NPC sites: {len(SITES)} structures ({sum(len(v['npcs']) for v in cfg['sites'].values())} NPCs), "
          f"{len(MEET_AFTER)} unlocked by quests")


if __name__ == "__main__":
    main()
