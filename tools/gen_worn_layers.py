"""Worn weapons: weapons that are drawn ON the player instead of held (owner, 2026-10-29: "it wraps around your hand
... like a part of your hand in all POVs", for every skin size and over armour).

For each entry in WORN this writes a Palladium render layer that is shown while the item is in the main hand:
  assets/tt/palladium/model_layers/<id>_worn[_slim].json   Bedrock geometry on the player's arm bones (wide + slim)
  assets/tt/textures/models/worn/<id>.png (+ _glow.png)     64x64 textures painted from the weapon's colours
  assets/tt/palladium/render_layers/<id>_worn[_glow].json   the layers (the glow one renders full-bright)
  data/tt/palladium/powers/<id>_worn.json                    a hidden power with the render_layer abilities
  data/tt/palladium/item_powers/<id>.json                    grants that power while the item is in the main hand
Third person: the held item model is scaled to 0 (gen_models.py WORN_DISPLAY) and the layer follows the arm bone, so
it fits slim and wide arms and sits over chestplate sleeves (inflate > 1.0, the outer armour layer). First person:
vanilla doesn't draw the arm while an item is held, so the item model itself is drawn where the hand would be.

Formats from Palladium's 1.20 source (ThreeTAG/Palladium, branch 1.20/main): ModelLayerManager reads
assets/<ns>/palladium/model_layers/*.json (Bedrock "minecraft:geometry", BedrockModelUtil), PackRenderLayer takes
model_type/model_layer/texture/render_type with {"normal", "slim"} skin-typed values, ItemPowerManager reads
data/<ns>/palladium/item_powers/*.json ({"slot", "item", "power"}). Run by build_prism.py."""
import json, os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KJ = os.path.join(ROOT, "pack", "kubejs")
WORN = ["choirbreaker_gauntlets"]


def hexc(h, f=1.0):
    h = h.lstrip("#")
    return tuple(max(0, min(255, int(int(h[i:i + 2], 16) * f))) for i in (0, 2, 4)) + (255,)


def bone(name, pivot, cubes=()):
    return {"name": name, "pivot": pivot, "cubes": list(cubes)}


def arm_cubes(x0, w, mirror):
    """Gauntlet on one arm: x0..x0+w is the arm's width (4 wide, 3 slim), the hand is at y=12, the forearm up to 18.
    Inflate above 1.0 so it covers a chestplate sleeve (outer armour layer, inflate 1.0)."""
    outer = x0 - 0.0 if not mirror else x0 + w          # outside face of the arm (-x right arm, +x left arm)
    plate_x = outer - 1.75 if not mirror else outer + 1.15
    c = [
        {"origin": [x0, 12, -2], "size": [w, 6, 4], "inflate": 1.1, "uv": [0, 0]},       # glove and cuff
        {"origin": [x0, 12, -2], "size": [w, 1.6, 4], "inflate": 1.35, "uv": [0, 16]},   # knuckle plate
        {"origin": [x0, 17.2, -2], "size": [w, 0.8, 4], "inflate": 1.4, "uv": [0, 24]},  # servo ring
        {"origin": [x0, 15.4, -2], "size": [w, 0.8, 4], "inflate": 1.4, "uv": [0, 24]},  # servo ring
        {"origin": [plate_x, 13, -1.6], "size": [0.6, 4, 3.2], "uv": [20, 0]},           # back plate
    ]
    for cube in c:
        cube["mirror"] = mirror
    return c


def emitter_cubes(x0, w, mirror):
    outer = x0 if not mirror else x0 + w
    ex = outer - 2.05 if not mirror else outer + 1.75
    return [{"origin": [ex, 14, -0.9], "size": [0.3, 1.8, 1.8], "uv": [0, 0], "mirror": mirror}]


def geometry(ident, slim, cubes_fn):
    w = 3 if slim else 4
    bones = [bone("head", [0, 24, 0]), bone("hat", [0, 24, 0]), bone("body", [0, 24, 0]),
             bone("right_arm", [-5, 22, 0], cubes_fn(-4 - w, w, False)),
             bone("left_arm", [5, 22, 0], cubes_fn(4, w, True)),
             bone("right_leg", [-1.9, 12, 0]), bone("left_leg", [1.9, 12, 0])]
    return {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": f"geometry.{ident}", "texture_width": 64, "texture_height": 64},
        "bones": bones}]}


def texture(w, path, glow=False):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if glow:
        d.rectangle([0, 0, 15, 15], fill=hexc(w["secondary"]))
        d.rectangle([2, 2, 5, 5], fill=hexc(w["secondary"], 1.35))
    else:
        d.rectangle([0, 0, 15, 9], fill=hexc(w["accent"], 1.6))          # glove: dark, with a red seam
        for y in range(0, 10, 2):
            d.line([0, y, 15, y], fill=hexc(w["accent"], 1.9))
        d.line([0, 5, 15, 5], fill=hexc(w["secondary"]))
        for y0, y1 in ((16, 21), (24, 29)):                                # chrome plates and rings
            d.rectangle([0, y0, 15, y1], fill=hexc(w["primary"], 0.85))
            d.line([0, y0, 15, y0], fill=hexc(w["primary"], 1.1))
        d.rectangle([20, 0, 27, 7], fill=hexc(w["primary"], 0.8))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main():
    weapons = {w["id"]: w for w in json.load(open(os.path.join(ROOT, "design", "weapons", "weapons.json")))["weapons"]}
    for wid in WORN:
        w = weapons[wid]
        a = os.path.join(KJ, "assets", "tt")
        for suffix, fn in (("", arm_cubes), ("_glow", emitter_cubes)):
            for slim in (False, True):
                name = f"{wid}_worn{suffix}{'_slim' if slim else ''}"
                write(os.path.join(a, "palladium", "model_layers", name + ".json"), geometry("tt_" + name, slim, fn))
            texture(w, os.path.join(a, "textures", "models", "worn", f"{wid}{suffix}.png"), glow=bool(suffix))
            layer = {"model_type": "minecraft:humanoid",
                     "model_layer": {"normal": f"tt:{wid}_worn{suffix}", "slim": f"tt:{wid}_worn{suffix}_slim"},
                     "texture": f"tt:textures/models/worn/{wid}{suffix}.png",
                     "render_type": "glow" if suffix else "solid"}
            write(os.path.join(a, "palladium", "render_layers", f"{wid}_worn{suffix}.json"), layer)
        write(os.path.join(KJ, "data", "tt", "palladium", "powers", f"{wid}_worn.json"), {
            "name": {"text": w.get("name", wid) + " (worn)"}, "icon": "tt:" + wid, "hidden": True,
            "abilities": {"layer": {"type": "palladium:render_layer", "render_layer": f"tt:{wid}_worn", "hidden": True},
                          "glow": {"type": "palladium:render_layer", "render_layer": f"tt:{wid}_worn_glow", "hidden": True}}})
        write(os.path.join(KJ, "data", "tt", "palladium", "item_powers", wid + ".json"),
              {"slot": "mainhand", "item": "tt:" + wid, "power": f"tt:{wid}_worn"})
    print(f"Worn layers: {len(WORN)} ({', '.join(WORN)})")


if __name__ == "__main__":
    main()
