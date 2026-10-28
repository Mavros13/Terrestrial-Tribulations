#!/usr/bin/env python3
"""Build blockbench/previews/weapon-viewer.html: a self-contained 3D viewer for the generated weapon models.

It embeds every export in blockbench/exports/weapons/ with its texture (and .mcmeta animation), plus the weapon's
stats from design/weapons/weapons.json, and renders them with three.js the way Minecraft does: per-face UVs,
element rotations, nearest-neighbour pixels, unlit glow* elements and interpolated texture animation.
Not shipped in the pack; it is for reviewing models. Run after tools/gen_models.py.

Usage: python3 tools/build_model_viewer.py
"""
import base64
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BB = os.path.join(ROOT, "blockbench")
OUT = os.path.join(BB, "previews", "weapon-viewer.html")


def main():
    data = json.load(open(os.path.join(ROOT, "design", "weapons", "weapons.json"), encoding="utf-8"))
    items = []
    for w in data["weapons"]:
        exp = os.path.join(BB, "exports", "weapons", w["id"] + ".json")
        png = os.path.join(BB, "textures", "weapons", w["id"] + ".png")
        if not (os.path.exists(exp) and os.path.exists(png)):
            continue
        model = json.load(open(exp, encoding="utf-8"))
        meta = png + ".mcmeta"
        anim = json.load(open(meta, encoding="utf-8"))["animation"] if os.path.exists(meta) else None
        icon = os.path.join(BB, "textures", "weapons", w["id"] + "_icon.png")
        items.append({
            "id": w["id"], "name": w["name"], "tier": w["tier"], "rarity": w["rarity"], "family": w["family"],
            "damage": w["damage"], "speed": w["speed"], "colors": [w["primary"], w["secondary"], w["accent"]],
            "ability": w.get("ability_name", ""), "abilityText": w.get("ability_text", ""), "story": w.get("story", ""),
            "lore": w.get("lore", ""), "size": model["texture_size"][0], "anim": anim,
            "elements": [{k: e[k] for k in ("name", "from", "to", "faces", "rotation") if k in e} for e in model["elements"]],
            "tex": "data:image/png;base64," + base64.b64encode(open(png, "rb").read()).decode(),
            "icon": ("data:image/png;base64," + base64.b64encode(open(icon, "rb").read()).decode()) if os.path.exists(icon) else "",
        })
    template = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_viewer_template.html"), encoding="utf-8").read()
    html = template.replace("/*__DATA__*/[]", json.dumps(items, separators=(",", ":")))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Built {OUT} with {len(items)} weapons, {len(html) // 1024} KB")


if __name__ == "__main__":
    main()
