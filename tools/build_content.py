#!/usr/bin/env python3
"""Generate Terrestrial Tribulations pack content from design/weapons/weapons.json.

Outputs (all under pack/kubejs/):
  startup_scripts/tt_weapons.generated.js   item + tool-tier registration
  client_scripts/tt_tooltips.generated.js   ability, lore and stat tooltips
  assets/tt/lang/en_us.json                 names coloured by rarity
  assets/tt/textures/item/<id>.png          16x16 placeholder textures in each weapon's palette
  data/tt/capabilities/weapons/<id>.json    Epic Fight weapon capabilities (moveset + trail colour)

Usage: python3 tools/build_content.py
"""
import json
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KJS = os.path.join(ROOT, "pack", "kubejs")
RARITY_COLOR = {"common": "§f", "uncommon": "§e", "rare": "§b", "epic": "§d", "legendary": "§6", "mythic": "§c"}
VANILLA_RARITY = {"common": "common", "uncommon": "uncommon", "rare": "rare", "epic": "epic", "legendary": "epic", "mythic": "epic"}
TIER_NAMES = ["", "Primitive", "Reinforced", "Adventurer", "Veteran", "Elite", "Relic", "Legendary", "Mythic"]
# Epic Fight weapon categories. Staff uses the spear moveset until Iron's Spells integration is done.
EF_TYPE = {"sword": "sword", "dagger": "dagger", "longsword": "longsword", "tachi": "tachi", "greatsword": "greatsword",
           "spear": "spear", "axe": "axe", "fist": "fist", "staff": "spear"}


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(rgb, f):
    return tuple(max(0, min(255, int(c * f))) for c in rgb)


# ---------- textures ----------
def line(a, b):
    (x0, y0), (x1, y1) = a, b
    n = max(abs(x1 - x0), abs(y1 - y0))
    return [(round(x0 + (x1 - x0) * t / n), round(y0 + (y1 - y0) * t / n)) for t in range(n + 1)] if n else [a]


def shape(family):
    """Return {(x,y): role} for a 16x16 item sprite (handle bottom-left, tip top-right). Roles: P S A L."""
    px = {}
    def put(pts, role):
        for p in pts:
            if 0 <= p[0] < 16 and 0 <= p[1] < 16:
                px[p] = role
    def blade(start, length, width, tip=True):
        for t in range(length):
            x, y = start[0] + t, start[1] - t
            put([(x, y)], "P")
            if width >= 2: put([(x + 1, y)], "L")
            if width >= 3: put([(x, y - 1)], "P")
        if tip: put([(start[0] + length, start[1] - length)], "L")
    def hilt(center, guard=2, handle=3):
        cx, cy = center
        put([(cx - i, cy - i) for i in range(1, guard + 1)] + [(cx + i, cy + i) for i in range(1, guard + 1)] + [center], "A")
        put([(cx - 1 - i, cy + 1 + i) for i in range(handle)], "S")
        put([(cx - 1 - handle, cy + 1 + handle)], "A")
    if family == "sword":
        blade((6, 9), 8, 2); hilt((5, 10))
    elif family == "longsword":
        blade((6, 9), 9, 2); hilt((5, 10), guard=3, handle=4)
    elif family == "greatsword":
        blade((6, 9), 9, 3); hilt((5, 10), guard=3, handle=3)
    elif family == "tachi":
        for t in range(9):
            x, y = 6 + t, 9 - t - (1 if 3 <= t <= 6 else 0)
            put([(x, y)], "P"); put([(x + 1, y)], "L")
        hilt((5, 10), guard=1, handle=4)
    elif family == "dagger":
        blade((7, 8), 5, 2); hilt((6, 9), guard=2, handle=2)
    elif family == "karambit":
        import math
        for a in range(200, 345, 8):  # hooked curved blade
            r = math.radians(a)
            put([(round(9 + 5 * math.cos(r)), round(9 + 5 * math.sin(r)))], "P")
            put([(round(9 + 4 * math.cos(r)), round(9 + 4 * math.sin(r)))], "L")
        put(line((12, 7), (9, 11)), "S")             # grip
        put([(8, 12), (7, 12), (7, 13), (8, 14), (9, 13)], "A")  # finger ring
    elif family == "spear":
        put(line((1, 14), (10, 5)), "S")
        put([(11, 4), (12, 3), (13, 2), (14, 1), (11, 3), (12, 4), (12, 2), (13, 3)], "P"); put([(13, 1), (14, 2)], "L")
        put([(10, 4), (11, 5)], "A")
    elif family == "hammer":
        put(line((2, 14), (9, 7)), "S")
        for x in range(8, 14):
            for y in range(2, 7):
                put([(x, y)], "P")
        put([(8, 2), (13, 6)], "L"); put([(10, 4), (11, 4), (10, 5), (11, 5)], "A")
    elif family == "axe":
        put(line((2, 14), (11, 5)), "S")
        for x, y in [(9, 3), (10, 2), (11, 2), (12, 3), (13, 4), (13, 5), (12, 6), (11, 7), (10, 6), (9, 5), (10, 3), (11, 3), (12, 4), (12, 5), (11, 6), (10, 5), (10, 4), (11, 4), (11, 5)]:
            put([(x, y)], "P")
        put([(13, 4), (13, 5)], "L"); put([(8, 6), (9, 7)], "A")
    elif family == "scythe":
        put(line((3, 15), (9, 3)), "S")
        put(line((9, 3), (14, 4)) + line((14, 4), (14, 8)), "P"); put(line((10, 4), (13, 5)), "L")
        put([(9, 2), (8, 3)], "A")
    elif family == "gauntlets":
        for x in range(4, 12):
            for y in range(5, 12):
                put([(x, y)], "P")
        put([(4, 4), (6, 4), (8, 4), (10, 4)], "L"); put(line((4, 12), (11, 12)), "S"); put([(7, 8), (8, 8), (7, 9), (8, 9)], "A")
    elif family == "bow":
        import math
        for a in range(-80, 81, 6):
            r = math.radians(a)
            put([(round(5 + 6 * math.cos(r)), round(8 + 7 * math.sin(r)))], "P")
        put(line((7, 1), (7, 15)), "A"); put([(10, 7), (10, 8), (10, 9)], "S")
    elif family == "staff":
        put(line((2, 14), (10, 6)), "S")
        put([(11, 4), (12, 3), (12, 4), (11, 3), (12, 5), (13, 4)], "A"); put([(11, 5), (10, 4), (13, 3), (11, 2)], "P")
    return px


def make_texture(w):
    p, s, a = hexrgb(w["primary"]), hexrgb(w["secondary"]), hexrgb(w["accent"])
    colors = {"P": p, "L": shade(p, 1.35) if sum(p) < 600 else shade(p, 0.85), "S": s, "A": a}
    px = shape(w["family"])
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for (x, y), role in px.items():
        img.putpixel((x, y), colors[role] + (255,))
    outline = shade(p, 0.45) if sum(p) > 150 else shade(s, 0.5)
    for x in range(16):
        for y in range(16):
            if (x, y) in px:
                continue
            if any((x + dx, y + dy) in px for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                img.putpixel((x, y), outline + (255,))
    path = os.path.join(KJS, "assets", "tt", "textures", "item", w["id"] + ".png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def make_materials():
    """Simple icons for the story materials registered in startup_scripts/tt_materials.js."""
    mats = {
        "bone_shard": ("#E8DFC8", [(6, 10), (7, 9), (8, 8), (9, 7), (10, 6), (7, 10), (9, 8), (8, 9)]),
        "hollow_fang": ("#4E4A55", [(7, 4), (7, 5), (8, 5), (7, 6), (8, 6), (8, 7), (9, 7), (8, 8), (9, 8), (9, 9), (9, 10), (10, 11)]),
        "crown_shard_fragment": ("#FFD700", [(8, 3), (7, 4), (8, 4), (9, 4), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (7, 6), (8, 6), (9, 6), (7, 7), (8, 7), (9, 7), (8, 8), (8, 9), (8, 10)]),
        "emberhold_charter": ("#F2E8D0", [(x, y) for x in range(4, 12) for y in range(4, 12)]),
    }
    for name, (col, pts) in mats.items():
        img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        c = hexrgb(col)
        for x, y in pts:
            img.putpixel((x, y), c + (255,))
        for x in range(16):
            for y in range(16):
                if (x, y) not in pts and any((x + dx, y + dy) in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    img.putpixel((x, y), shade(c, 0.4) + (255,))
        if name == "emberhold_charter":
            for x in range(5, 11):
                img.putpixel((x, 6), (163, 22, 43, 255)); img.putpixel((x, 9), (120, 100, 80, 255))
        path = os.path.join(KJS, "assets", "tt", "textures", "item", name + ".png")
        img.save(path)


# ---------- scripts ----------
def main():
    data = json.load(open(os.path.join(ROOT, "design", "weapons", "weapons.json"), encoding="utf-8"))
    weapons = data["weapons"]
    hdr = "// GENERATED by tools/build_content.py from design/weapons/weapons.json. Do not edit by hand.\n"

    tiers, items = [], []
    for w in weapons:
        make_texture(w)
        if w["family"] == "bow":
            items.append(f"  // {w['name']}: bow behaviour needs the tt_bridge mod; registered as a placeholder item for now\n"
                         f"  event.create('tt:{w['id']}').maxStackSize(1).rarity('{VANILLA_RARITY[w['rarity']]}')")
            continue
        tiers.append(f"  event.add('tt_{w['id']}', t => {{ t.uses = {w['durability']}; t.speed = 6.0; t.attackDamageBonus = 0.0; "
                     f"t.level = {min(4, max(1, w['tier'] // 2))}; t.enchantmentValue = {10 + w['tier']}; t.repairIngredient = 'minecraft:iron_ingot' }})")
        items.append(f"  event.create('tt:{w['id']}', 'sword').tier('tt_{w['id']}')"
                     f".attackDamageBaseline({w['damage'] - 1:.1f}).speedBaseline({w['speed'] - 4:.1f})"
                     f".rarity('{VANILLA_RARITY[w['rarity']]}')  // {w['damage']} dmg, {w['speed']} speed")
    write(os.path.join(KJS, "startup_scripts", "tt_weapons.generated.js"), hdr +
          "// Sword damage shown in-game = 1 + baseline (tier bonus is 0); attack speed = 4 + speedBaseline.\n"
          "ItemEvents.toolTierRegistry(event => {\n" + "\n".join(tiers) + "\n})\n\n"
          "StartupEvents.registry('item', event => {\n" + "\n".join(items) + "\n})\n")

    lang = {}
    tips = []
    for w in weapons:
        lang[f"item.tt.{w['id']}"] = RARITY_COLOR[w["rarity"]] + w["name"]
        lines = [f"§8{TIER_NAMES[w['tier']]} · {w['rarity'].capitalize()} {w['family'].capitalize()}",
                 f"§6{w['ability_name']}", f"§7{w['ability_text']}", f"§8§o\"{w['lore']}\"", f"§3{w['story']}"]
        if w["impl"] == "BRIDGE":
            lines.append("§c[Prototype] Ability arrives with the tt_bridge mod")
        elif w["impl"] == "EDP":
            lines.append("§c[Prototype] Epic Fight skill data pending")
        tips.append(f"  event.add('tt:{w['id']}', {json.dumps(lines, ensure_ascii=False)})")
    lang.update({"item.tt.bone_shard": "Bone Shard", "item.tt.hollow_fang": "Hollow Fang",
                 "item.tt.crown_shard_fragment": "§6Crown Shard Fragment", "item.tt.emberhold_charter": "§eEmberhold Charter"})
    write(os.path.join(KJS, "assets", "tt", "lang", "en_us.json"), json.dumps(lang, indent=2, ensure_ascii=False) + "\n")
    write(os.path.join(KJS, "client_scripts", "tt_tooltips.generated.js"), hdr +
          "ItemEvents.tooltip(event => {\n" + "\n".join(tips) + "\n})\n")

    for w in weapons:
        if w["family"] == "bow":
            continue
        cap = {"type": "epicfight:" + EF_TYPE[w["ef"]],
               "attributes": {"common": {"armor_negation": round(w["tier"] * 2.5, 1), "impact": round(0.4 + w["tier"] * 0.15, 2),
                                         "max_strikes": 3 if w["ef"] in ("greatsword",) else 1}},
               "_tt_trail_color": w["trail"]}
        write(os.path.join(KJS, "data", "tt", "capabilities", "weapons", w["id"] + ".json"), json.dumps(cap, indent=2) + "\n")
    make_materials()
    print(f"Generated content for {len(weapons)} weapons.")


if __name__ == "__main__":
    main()
