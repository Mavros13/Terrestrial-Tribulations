"""Builds blockbench/previews/npc-sites.html: a 3D review page for the story NPC sites from tools/gen_npc_sites.py.

Each block is drawn as a flat-coloured box (thin for carpets, slabs and trapdoors), so the page shows layout and colour,
not textures. Each NPC's marker block glows, so you can see where they will stand. Run by build_prism.py.
"""
import json
import os

import gen_npc_sites as g

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "blockbench", "previews", "npc-sites.html")

COLORS = {
    "amethyst_block": "#8561c5", "amethyst_cluster": "#a77fe0", "anvil": "#444444", "azalea": "#6b8a2e",
    "barrel": "#8b6a3e", "blast_furnace": "#5c5c5e", "blue_ice": "#74a8f5", "bookshelf": "#7a5a33",
    "brown_carpet": "#724728", "brown_wool": "#724728", "calcite": "#dfe0dc", "campfire": "#e0802a",
    "candle": "#e8d6a8", "cartography_table": "#6b5236", "chest": "#a2722c", "chiseled_bookshelf": "#7a5a33",
    "chiseled_stone_bricks": "#777777", "coarse_dirt": "#77553b", "cobblestone": "#7f7f7f", "cobweb": "#dddddd",
    "copper_block": "#c06b4f", "cracked_stone_bricks": "#727272", "dark_oak_trapdoor": "#4a3218",
    "dirt_path": "#94793f", "enchanting_table": "#3a2b4f", "end_rod": "#f2ecd9", "exposed_copper": "#a1806b",
    "flowering_azalea": "#7a8f3a", "flowering_azalea_leaves": "#6a8a3a", "gravel": "#857f7e",
    "green_carpet": "#546d1b", "green_wool": "#546d1b", "grindstone": "#8e8e8e", "hay_block": "#b5970f",
    "iron_bars": "#9a9a9a", "ladder": "#9c7c48", "lantern": "#f0b94a", "lava_cauldron": "#d8561a",
    "lectern": "#a0794a", "light_gray_carpet": "#8e8e86", "light_gray_wool": "#8e8e86", "lightning_rod": "#c27354",
    "mangrove_roots": "#4b3b26", "moss_block": "#596e2d", "moss_carpet": "#596e2d", "mossy_cobblestone": "#6e7a5e",
    "mossy_stone_bricks": "#73796a", "oak_leaves": "#4f7a28", "oak_log": "#6b5434", "oxidized_copper": "#52a284", "packed_ice": "#8db4f0",
    "piston": "#9e8a63", "podzol": "#5b3f1d", "polished_andesite": "#848686", "polished_deepslate": "#48484a",
    "polished_granite": "#9a6a57", "purple_stained_glass": "#7f3fb2", "purpur_block": "#a97ea9",
    "purpur_slab": "#a97ea9", "red_carpet": "#a02722", "red_terracotta": "#8f3d2e", "red_wool": "#a02722",
    "rooted_dirt": "#906a4c", "smithing_table": "#3f3f4a", "smooth_quartz": "#ebe5de", "smooth_stone": "#9e9e9e",
    "snow_block": "#f4fafa", "spruce_fence": "#5f4a2b", "spruce_log": "#3b2a16", "spruce_planks": "#725434",
    "spruce_slab": "#725434", "sticky_piston": "#8a9c63", "stone_bricks": "#7a7a7a",
    "stripped_spruce_wood": "#74593a", "target": "#e4c9a6", "water_cauldron": "#3f76e4",
    "waxed_copper_block": "#c06b4f", "weathered_cut_copper": "#6c9a77", "white_carpet": "#e9ecec",
    "white_wool": "#e9ecec",
}
SEE_THROUGH = {"purple_stained_glass", "iron_bars", "cobweb", "spruce_fence", "oak_leaves", "flowering_azalea_leaves"}


def shape(name, props):
    """(height, inset) of the box: carpets and trapdoors are thin, bottom slabs half, small props inset."""
    if name.endswith("_carpet"):
        return 0.07, 0
    if name.endswith("_trapdoor"):
        return 0.19, 0
    if name.endswith("_slab"):
        return (1, 0) if props.get("type") == "double" else (0.5, 0)
    if name in ("candle", "lantern", "end_rod", "lightning_rod", "amethyst_cluster", "campfire", "azalea",
                "flowering_azalea", "spruce_fence", "iron_bars", "ladder", "cobweb"):
        return (0.45 if name == "campfire" else 0.8), 0.3
    return 1, 0


def main():
    sites = []
    for sid, (build, stage, after, biomes, *_rest) in g.SITES.items():
        title = _rest[-2]
        site, markers = build()
        marker_blocks = {b: npc for npc, b in markers.items()}
        blocks = []
        for (x, y, z), s in site.b.items():
            if s == "air":
                continue
            name, props = g.parse_state(s)
            short = name.split(":")[1]
            h, inset = shape(short, props)
            blocks.append([x, y, z, COLORS.get(short, "#ff00ff"), h, inset,
                           1 if short in SEE_THROUGH else 0, marker_blocks.get(s, "")])
        missing = {g.parse_state(s)[0] for s in site.b.values() if s != "air"} - {"minecraft:" + k for k in COLORS}
        assert not missing, f"no preview colour for {sorted(missing)}"
        sites.append({"id": sid, "title": title, "size": [site.w, site.h, site.d], "stage": stage or "",
                      "after": after or "", "npcs": [g.CAST[n][1] for n in markers], "blocks": blocks})
    html = TEMPLATE.replace("__DATA__", json.dumps(sites, separators=(",", ":")))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"NPC site viewer: {len(sites)} sites -> {os.path.relpath(OUT, ROOT)}")


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NPC Sites</title>
<style>
:root{--bg:#f4f1ea;--panel:#fffdf8;--ink:#2a2620;--muted:#6e665a;--line:#ddd5c6;--accent:#b5651d}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#17150f;--panel:#211e17;--ink:#ece6da;--muted:#a59c8c;--line:#3a352b;--accent:#e08a3c}}
:root[data-theme="dark"]{--bg:#17150f;--panel:#211e17;--ink:#ece6da;--muted:#a59c8c;--line:#3a352b;--accent:#e08a3c}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,sans-serif}
header{padding:16px 16px 8px}h1{margin:0;font-size:20px}header p{margin:4px 0 0;color:var(--muted);font-size:13px}
nav{display:flex;flex-wrap:wrap;gap:6px;padding:8px 16px}
nav button{border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:999px;padding:6px 12px;font:inherit;font-size:13px;cursor:pointer}
nav button[aria-pressed="true"]{border-color:var(--accent);color:var(--accent);font-weight:600}
main{padding:0 16px 16px;display:grid;gap:12px}
#view{width:100%;height:min(62vh,560px);border:1px solid var(--line);border-radius:12px;background:var(--panel);touch-action:none}
#info{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
#info h2{margin:0 0 4px;font-size:17px}#info p{margin:2px 0;color:var(--muted);font-size:13px}
code{font-size:12px}
</style></head><body>
<header><h1>Story NPC sites</h1><p>Generated by tools/gen_npc_sites.py. Flat colours, not textures. The glowing block is where the NPC appears. Drag to turn, pinch or scroll to zoom.</p></header>
<nav id="tabs"></nav>
<main><canvas id="view"></canvas><section id="info"></section></main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
const SITES = __DATA__;
const canvas = document.getElementById('view');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 500);
const controls = new THREE.OrbitControls(camera, canvas);
controls.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xffffff, 0x554433, 0.75));
const sun = new THREE.DirectionalLight(0xffffff, 0.7); sun.position.set(30, 50, 20); scene.add(sun);
let group = null;
function show(i){
  const s = SITES[i];
  if (group) scene.remove(group);
  group = new THREE.Group();
  const geo = new THREE.BoxGeometry(1,1,1);
  const mats = {};
  for (const [x,y,z,col,h,inset,clear,npc] of s.blocks){
    const key = col+clear+npc;
    mats[key] = mats[key] || new THREE.MeshLambertMaterial({color:col, transparent:!!clear, opacity:clear?0.55:1,
      emissive: npc ? new THREE.Color(col) : new THREE.Color(0), emissiveIntensity: npc ? 0.8 : 0});
    const m = new THREE.Mesh(geo, mats[key]);
    const w = 1 - inset;
    m.scale.set(w, h, w);
    m.position.set(x + 0.5 - s.size[0]/2, y + h/2, z + 0.5 - s.size[2]/2);
    group.add(m);
  }
  scene.add(group);
  const r = Math.max(...s.size);
  controls.target.set(0, s.size[1]/3, 0);
  camera.position.set(r*1.3, r*1.0, r*1.3);
  controls.update();
  document.querySelectorAll('#tabs button').forEach((b,j)=>b.setAttribute('aria-pressed', j===i));
  document.getElementById('info').innerHTML = `<h2>${s.title}</h2><p>NPCs: ${s.npcs.join(', ')}</p>`+
    `<p>${s.stage ? `Locked until <code>${s.stage}</code>, given by quest <code>${s.after}</code> with a map.` : 'Placed beside world spawn on first load; always open.'}</p>`+
    `<p>${s.size.join(' × ')} blocks · <code>/place structure tt:npc/${s.id}</code></p>`;
}
SITES.forEach((s,i)=>{const b=document.createElement('button'); b.textContent=s.title; b.onclick=()=>show(i); document.getElementById('tabs').appendChild(b);});
function resize(){const w=canvas.clientWidth,h=canvas.clientHeight; renderer.setSize(w,h,false); camera.aspect=w/h; camera.updateProjectionMatrix();}
addEventListener('resize', resize);
resize(); show(0);
(function loop(){controls.update(); renderer.render(scene, camera); requestAnimationFrame(loop);})();
</script></body></html>
"""

if __name__ == "__main__":
    main()
