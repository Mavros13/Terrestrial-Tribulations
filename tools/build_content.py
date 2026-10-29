#!/usr/bin/env python3
"""Generate Terrestrial Tribulations pack content from design/weapons/weapons.json.

Outputs (all under pack/kubejs/):
  startup_scripts/tt_weapons.generated.js   item + tool-tier registration
  client_scripts/tt_tooltips.generated.js   ability, lore and stat tooltips
  assets/tt/lang/en_us.json                 names coloured by rarity
  assets/tt/textures/item/<id>.png          16x16 placeholder textures in each weapon's palette
  data/tt/capabilities/weapons/<id>.json    Epic Fight weapon capabilities (moveset preset + attributes)
  assets/tt/item_skins/<id>.json            Epic Fight swing trail (colour, length along the blade)
  assets/tt/models/item/<id>.json, <id>_3d.json, textures/item/<id>_3d.png
                                            only once a Blockbench model exists (see install_models below)

Hand-made art (briefs in blockbench/specs/weapons.md) is picked up automatically:
  blockbench/textures/weapons/<id>_icon.png   replaces the 16x16 placeholder inventory icon
  blockbench/exports/weapons/<id>.json        Blockbench "Java Block/Item" export (the 3D held model)
  blockbench/textures/weapons/<id>.png        its single texture (+ optional .png.mcmeta for animation)
  "model_parent" in weapons.json              otherwise, borrow a 3D model by resource location from a resource pack
                                              (karambits: Karambit Vault x Punchy, which the player must have enabled)

Usage: python3 tools/build_content.py
"""
import json
import os
import shutil
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KJS = os.path.join(ROOT, "pack", "kubejs")
BB = os.path.join(ROOT, "blockbench")
RARITY_COLOR = {"common": "§f", "uncommon": "§e", "rare": "§b", "epic": "§d", "legendary": "§6", "mythic": "§c"}
VANILLA_RARITY = {"common": "common", "uncommon": "uncommon", "rare": "rare", "epic": "epic", "legendary": "epic", "mythic": "epic"}
# Epic Fight's built-in innate skill for each preset (WeaponCapabilityPresets, 1.20.1): one-hand / two-hand style.
INNATE = {"sword": "Sweeping Edge", "dagger": "Eviscerate", "longsword": "Sharp Stab", "tachi": "Rushing Tempo",
          "greatsword": "Steel Whirlwind", "spear": "Heartpiercer", "axe": "The Guillotine", "fist": "Relentless Combo",
          "staff": "Heartpiercer"}
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
    icon = os.path.join(BB, "textures", "weapons", w["id"] + "_icon.png")
    if os.path.exists(icon):
        shutil.copyfile(icon, os.path.join(KJS, "assets", "tt", "textures", "item", w["id"] + ".png"))
        return
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
        "crown_shard": ("#B98CFF", [(8, 2), (7, 3), (8, 3), (9, 3), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (11, 5), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (7, 7), (8, 7), (9, 7), (7, 8), (8, 8), (9, 8), (8, 9), (8, 10), (8, 11), (8, 12)]),
        "old_engine_core": ("#B5732E", [(x, y) for x in range(5, 11) for y in range(5, 11) if (x - 7.5) ** 2 + (y - 7.5) ** 2 <= 9]),
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


# Epic Fight trail positions in the Tool_R joint (blocks; -Z runs along the blade), copied from Epic Fight's own
# item_skins for each preset (assets/epicfight/item_skins/iron_*.json and minecraft/item_skins/iron_sword|iron_axe.json,
# 1.20.1 branch, 20.14.15.1-20.15.1). "fist" has no Epic Fight reference and is a guess.
TRAIL_POS = {"sword": ([0.0, 0.1, -0.1], [0.0, -0.05, -0.95]), "dagger": ([0.0, 0.0, -0.2], [0.0, 0.1, -0.7]),
             "longsword": ([0.0, 0.0, -0.2], [0.0, 0.2, -1.5]), "tachi": ([0.0, 0.0, -0.2], [0.0, 0.4, -1.75]),
             "greatsword": ([0.0, 0.0, -0.2], [0.0, -0.24, -1.8]), "spear": ([0.0, 0.2, -0.9], [0.0, 0.25, -2.0]),
             "axe": ([0.0, -0.15, -0.35], [0.0, -0.15, -0.7]), "fist": ([0.0, 0.0, 0.0], [0.0, 0.0, -0.3])}


# Model units -> Epic Fight trail blocks, calibrated so a vanilla sword sprite (tip ~15.6 units from the grip at
# display scale 0.85) lands on Epic Fight's own iron_sword trail end (-0.95).
TRAIL_K = 0.95 / (15.6 * 0.85 / 16)
GRIP_Y = 1.0  # where the hand holds our upright models (tools/gen_models.py convention)


def model_trail(w, begin, end):
    """Fit the trail to the weapon's 3D model: from the bottom of the striking part to the tip, along -Z. Keeps the
    preset's sideways and vertical offsets. Returns the preset unchanged when there is no model."""
    exp = os.path.join(BB, "exports", "weapons", w["id"] + ".json")
    if not os.path.exists(exp) or w["ef"] in ("bow", "crossbow", "fist", "shield"):
        return begin, end
    m = json.load(open(exp, encoding="utf-8"))
    tip = max(e["to"][1] for e in m["elements"])
    strike = min((e["from"][1] for e in m["elements"] if e["from"][1] >= GRIP_Y + 2.5
                  and not e["name"].startswith(("grip", "shaft", "haft", "handle", "band", "ring", "cord", "vine", "thorn_", "wrap", "strap", "side_grip"))),
                 default=GRIP_Y + 3)
    scale = m.get("display", {}).get("thirdperson_righthand", {}).get("scale", [0.85])[0]
    to_blocks = lambda y: round(-(y - GRIP_Y) * scale / 16 * TRAIL_K, 2)
    return [begin[0], begin[1], to_blocks(strike)], [end[0], end[1], to_blocks(tip)]


def item_skin(w):
    """Epic Fight item skin (client resource, read by ItemSkinsReloadListener from assets/<ns>/item_skins/<item>.json).
    Trails of Elite (tier 5) and up are drawn at full brightness. Weapons with a 3D model get a trail fitted to it."""
    begin, end = TRAIL_POS[w["ef"] if w["ef"] in TRAIL_POS else EF_TYPE[w["ef"]]]
    begin, end = model_trail(w, begin, end)
    trail = {"color": list(hexrgb(w["trail"])), "begin_pos": begin, "end_pos": end, "lifetime": 4, "interpolations": 5,
             "texture_path": "epicfight:textures/particle/swing_trail.png", "particle_type": "epicfight:swing_trail"}
    if w["tier"] >= 5:
        trail.update({"block_light": 15, "sky_light": 15})
    return {"trail": trail}


# ---------- 3D held models ----------
def install_models(weapons):
    """Wrap each finished Blockbench export in Forge's separate_transforms loader: 3D model in hand and on the
    ground, the flat icon in inventories and item frames. Elements named glow* get full brightness through
    Forge's per-element forge_data (verify in the first test). Removes stale outputs when a source is deleted."""
    models = os.path.join(KJS, "assets", "tt", "models", "item")
    textures = os.path.join(KJS, "assets", "tt", "textures", "item")
    count = 0
    for w in weapons:
        i = w["id"]
        src = os.path.join(BB, "exports", "weapons", i + ".json")
        tex = os.path.join(BB, "textures", "weapons", i + ".png")
        outs = [os.path.join(models, i + ".json"), os.path.join(models, i + "_3d.json"),
                os.path.join(textures, i + "_3d.png"), os.path.join(textures, i + "_3d.png.mcmeta")]
        flat = {"parent": "minecraft:item/handheld", "textures": {"layer0": "tt:item/" + i}}
        if not (os.path.exists(src) and os.path.exists(tex)):
            for o in outs:
                if os.path.exists(o):
                    os.remove(o)
            if w.get("model_parent"):
                # Borrowed 3D model from a resource pack the player installs (e.g. Karambit Vault x Punchy, ARR, so
                # nothing of it is copied): we only point at its model by resource location, optionally swapping its
                # texture variables ("model_textures") to pick another material from the same pack.
                # Every perspective, the inventory included, is the pack's own (owner, 2026-10-29: the flat icons
                # "aren't at all what they look like in hand"). First person is built for the Punchy mod's hand
                # animation, which runs outside Epic Fight battle mode (client_scripts/tt_punchy_battle.js).
                model = {"parent": w["model_parent"]}
                if w.get("model_textures"):
                    model["textures"] = w["model_textures"]
                write(outs[0], json.dumps(model, indent=2) + "\n")
                count += 1
            continue
        m = json.load(open(src, encoding="utf-8"))
        m.pop("credit", None)
        m["textures"] = {k: "tt:item/" + i + "_3d" for k in (m.get("textures") or {"0": None})}
        m["textures"]["particle"] = "tt:item/" + i + "_3d"
        for e in m.get("elements", []):
            if str(e.get("name", "")).lower().startswith("glow"):
                e["forge_data"] = {"block_light": 15, "sky_light": 15}
        write(outs[1], json.dumps(m, indent=1) + "\n")
        shutil.copyfile(tex, outs[2])
        if os.path.exists(tex + ".mcmeta"):
            shutil.copyfile(tex + ".mcmeta", outs[3])
        write(outs[0], json.dumps({"loader": "forge:separate_transforms", "base": {"parent": "tt:item/" + i + "_3d"},
                                   "perspectives": {"gui": flat, "fixed": flat}}, indent=2) + "\n")
        count += 1
    return count



# ---------- TT Karambits resource pack ----------
KARAMBIT_PACK = os.path.join(ROOT, "pack", "resourcepacks", "TT Karambits")
VANILLA_SWORDS = {"wooden": "Wooden", "stone": "Stone", "iron": "Iron", "golden": "Golden", "diamond": "Diamond",
                  "netherite": "Netherite"}


def make_karambit_pack(weapons):
    """Karambit Vault x Punchy turns every vanilla sword into a karambit (models at minecraft:item/<tier>_sword, a
    Punchy compat file for item.SWORD, renamed lang). Owner, 2026-10-29: keep vanilla swords vanilla and give the
    karambit look and animations to our karambit items only. This pack sits above Karambit Vault
    (config/defaultoptions-common.toml) and puts back vanilla's own sword models (vanilla's JSON, nothing copied from
    the ARR pack), sword names and an empty Punchy sword compat; our karambits parent the pack's skins/* models,
    which share the karambit geometry (checked in the pack, 2026-10-29), and the Punchy animations are tied to our
    item IDs in kubejs/assets/minecraft/punchy/compat/tt_karambits.json."""
    if os.path.isdir(KARAMBIT_PACK):
        shutil.rmtree(KARAMBIT_PACK)
    write(os.path.join(KARAMBIT_PACK, "pack.mcmeta"), json.dumps({"pack": {
        "pack_format": 15, "description": "§6Terrestrial Tribulations§7: karambit look for our karambits only"}}, indent=2) + "\n")
    for tier in VANILLA_SWORDS:
        write(os.path.join(KARAMBIT_PACK, "assets", "minecraft", "models", "item", f"{tier}_sword.json"),
              json.dumps({"parent": "minecraft:item/handheld", "textures": {"layer0": f"minecraft:item/{tier}_sword"}}, indent=2) + "\n")
    write(os.path.join(KARAMBIT_PACK, "assets", "minecraft", "lang", "en_us.json"),
          json.dumps({f"item.minecraft.{t}_sword": f"{n} Sword" for t, n in VANILLA_SWORDS.items()}, indent=2) + "\n")
    write(os.path.join(KARAMBIT_PACK, "assets", "minecraft", "punchy", "compat", "karambit.json"),
          json.dumps({"itemSpecific": {}}, indent=2) + "\n")
    # Punchy animations from Karambit Vault, for our karambit items only (same entry the pack gives vanilla swords)
    compat = os.path.join(KJS, "assets", "minecraft", "punchy", "compat", "tt_karambits.json")
    entry = next(iter(json.load(open(compat, encoding="utf-8"))["itemSpecific"].values()))
    write(compat, json.dumps({"itemSpecific": {"tt:" + w["id"]: entry for w in weapons if w["family"] == "karambit"}},
                             indent=2) + "\n")
    bad = [w["id"] for w in weapons if (w.get("model_parent") or "").startswith("minecraft:item/") and
           w["model_parent"].split("/")[-1].removesuffix("_sword") in VANILLA_SWORDS]
    assert not bad, f"{bad}: a vanilla sword model path is vanilla again under TT Karambits; parent a skins/* model"


# ---------- scripts ----------
def main():
    data = json.load(open(os.path.join(ROOT, "design", "weapons", "weapons.json"), encoding="utf-8"))
    weapons = data["weapons"]
    hdr = "// GENERATED by tools/build_content.py from design/weapons/weapons.json. Do not edit by hand.\n"

    tiers, items = [], []
    for w in weapons:
        make_texture(w)
        if w["family"] == "bow":
            # Shooting lives in startup_scripts/tt_bows.js; base arrow damage grows with tier (vanilla bow = 2.0).
            opts = {"id": "tt:" + w["id"], "damage": round(2.0 + w["tier"] * 0.25, 2), "pierce": w.get("pierce", 0)}
            items.append(f"  event.create('tt:{w['id']}').maxStackSize(1).rarity('{VANILLA_RARITY[w['rarity']]}')"
                         f".useAnimation('bow').useDuration(s => 72000).use((level, player, hand) => true)\n"
                         f"    .releaseUsing((stack, level, entity, timeLeft) => global.ttShootBow(stack, level, entity, timeLeft, {json.dumps(opts)}))")
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
                 f"§6{w['ability_name']}" + (f" §e[{w['trigger']}]" if w.get("trigger") else ""), f"§7{w['ability_text']}", f"§8§o\"{w['lore']}\"", f"§3{w['story']}"]
        if w["impl"] == "BRIDGE":
            lines.append("§c[Prototype] Ability arrives with the tt_bridge mod")
        elif w["impl"] == "EDP":
            lines.append("§c[Prototype] Ability rides on the " + INNATE[w["ef"]] + " innate skill until its own EDP skill exists")
        tips.append(f"  event.add('tt:{w['id']}', {json.dumps(lines, ensure_ascii=False)})")
    lang.update({"item.tt.bone_shard": "Bone Shard", "item.tt.hollow_fang": "Hollow Fang",
                 "item.tt.crown_shard_fragment": "§6Crown Shard Fragment", "item.tt.emberhold_charter": "§eEmberhold Charter",
                 "item.tt.crown_shard": "§dCrown Shard", "item.tt.old_engine_core": "§6Old Engine Core"})
    write(os.path.join(KJS, "assets", "tt", "lang", "en_us.json"), json.dumps(lang, indent=2, ensure_ascii=False) + "\n")
    write(os.path.join(KJS, "client_scripts", "tt_tooltips.generated.js"), hdr +
          "ItemEvents.tooltip(event => {\n" + "\n".join(tips) + "\n})\n")

    for w in weapons:
        if w["family"] == "bow":
            continue
        cap = {"type": "epicfight:" + EF_TYPE[w["ef"]],
               "attributes": {"common": {"armor_negation": round(w["tier"] * 2.5, 1), "impact": round(0.4 + w["tier"] * 0.15, 2),
                                         "max_strikes": 3 if w["ef"] in ("greatsword",) else 1}}}
        write(os.path.join(KJS, "data", "tt", "capabilities", "weapons", w["id"] + ".json"), json.dumps(cap, indent=2) + "\n")
        write(os.path.join(KJS, "assets", "tt", "item_skins", w["id"] + ".json"), json.dumps(item_skin(w), indent=2) + "\n")
    make_materials()
    make_karambit_pack(weapons)
    n = install_models(weapons)
    print(f"Generated content for {len(weapons)} weapons ({n} with 3D models).")


if __name__ == "__main__":
    main()
