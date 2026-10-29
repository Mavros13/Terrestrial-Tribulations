#!/usr/bin/env python3
"""Builds blockbench/previews/npc-holsters.html: each story NPC in the looks from tools/gen_npcs.py LOOKS (skin,
pose, held items) with the holstered weapon placed exactly as server_scripts/tt_npc_sites.js places it in game
(owner, 2026-10-29: "can you show me an example"). Review page only; run by build_prism.py.

The maths follows Minecraft 1.20.1:
- player model: 1/16-block pixels, facing +z, right arm at -x; ModelPart rotations are rotationZYX in model space
  (y down, front -z), which in this y-up, front +z world is Euler(x, -y, -z, "ZYX");
- item_display: entity yaw -> transformation (translation, left_rotation, scale, right_rotation) -> a 180-degree
  turn about y (ItemDisplayRenderer) -> the item's "fixed" display transform (translate/16, rotationXYZ in degrees,
  scale) -> the model, shifted by -0.5 blocks so it turns about its centre.
Karambits use Karambit Vault's models in game, which aren't in this repo, so they show as a flat stand-in blade."""
import base64, json, os

from gen_npcs import CAST, LOOKS, HOLSTERS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BB = os.path.join(ROOT, "blockbench")
SKINS = os.path.join(ROOT, "pack", "kubejs", "assets", "tt", "textures", "entity", "npc")
OUT = os.path.join(BB, "previews", "npc-holsters.html")


def b64(path):
    return "data:image/png;base64," + base64.b64encode(open(path, "rb").read()).decode()


def weapon(item_id):
    wid = item_id.split(":")[1]
    exp = os.path.join(BB, "exports", "weapons", wid + ".json")
    png = os.path.join(BB, "textures", "weapons", wid + ".png")
    if not item_id.startswith("tt:") or not (os.path.exists(exp) and os.path.exists(png)):
        return {"id": item_id, "flat": True}
    m = json.load(open(exp, encoding="utf-8"))
    return {"id": item_id, "size": m["texture_size"][0], "tex": b64(png),
            "fixed": m.get("display", {}).get("fixed", {}),
            "elements": [{k: e[k] for k in ("name", "from", "to", "faces", "rotation") if k in e} for e in m["elements"]]}


def main():
    weapons, npcs = {}, []
    for key, looks in LOOKS.items():
        names, display, color, model, _variant = CAST[key]
        for lk in looks:
            if len(lk) > 3:
                weapons.setdefault(lk[3][1], weapon(lk[3][1]))
                npcs.append({"key": key, "name": display, "color": color, "slim": model == "humanoid_slim",
                             "skin": b64(os.path.join(SKINS, key + ".png")), "pose": lk[2] or {},
                             "at": lk[3][0], "item": lk[3][1]})
    data = {"npcs": npcs, "weapons": weapons, "holsters": HOLSTERS}
    html = TEMPLATE.replace("__DATA__", json.dumps(data, separators=(",", ":")))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Holster preview: {len(npcs)} NPCs -> {os.path.relpath(OUT, ROOT)}")


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NPC Holsters</title>
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
#view{width:100%;height:min(66vh,600px);border:1px solid var(--line);border-radius:12px;background:var(--panel);touch-action:none;display:block}
#info{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
#info h2{margin:0 0 4px;font-size:17px}#info p{margin:2px 0;color:var(--muted);font-size:13px}
</style></head><body>
<header><h1>Holstered weapons</h1><p>Each NPC in their off-duty look, with the weapon placed the way the game places it. Drag to turn, scroll or pinch to zoom.</p></header>
<nav id="tabs"></nav>
<main><canvas id="view"></canvas><section id="info"></section></main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
const DATA = __DATA__;
const PX = 1 / 16;
const canvas = document.getElementById('view');
const renderer = new THREE.WebGLRenderer({canvas, antialias: true, alpha: true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 0.05, 50);
const controls = new THREE.OrbitControls(camera, canvas);
controls.enableDamping = true; controls.target.set(0, 0.95, 0);
camera.position.set(-2.0, 1.7, -3.4);
scene.add(new THREE.AmbientLight(0xffffff, 0.7));
const sun = new THREE.DirectionalLight(0xffffff, 0.55); sun.position.set(-3, 5, -2); scene.add(sun);
const fill = new THREE.DirectionalLight(0xffffff, 0.3); fill.position.set(3, 2, 4); scene.add(fill);
const ground = new THREE.Mesh(new THREE.CircleGeometry(1.4, 40), new THREE.MeshLambertMaterial({color: 0x8c8274}));
ground.rotation.x = -Math.PI / 2; scene.add(ground);

function texture(src) {
  const t = new THREE.TextureLoader().load(src);
  t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.generateMipmaps = false;
  return t;
}

// A skin box: size w,h,d pixels, texture origin u,v on the 64x64 skin; faces as Minecraft maps them.
function skinBox(tex, w, h, d, u, v, inflate) {
  const g = new THREE.BufferGeometry(), pos = [], uv = [], idx = [];
  const x0 = -w / 2 - inflate, x1 = w / 2 + inflate, y0 = -h / 2 - inflate, y1 = h / 2 + inflate, z0 = -d / 2 - inflate, z1 = d / 2 + inflate;
  const S = 64;
  const face = (c, r) => {  // c: 4 corners [tl,tr,bl,br]; r: texture rect [u,v,w,h]
    const n = pos.length / 3;
    c.forEach(p => pos.push(...p));
    const [a, b, cw, ch] = r;
    uv.push(a / S, 1 - b / S, (a + cw) / S, 1 - b / S, a / S, 1 - (b + ch) / S, (a + cw) / S, 1 - (b + ch) / S);
    idx.push(n, n + 2, n + 1, n + 1, n + 2, n + 3);
  };
  face([[x0, y1, z1], [x1, y1, z1], [x0, y0, z1], [x1, y0, z1]], [u + d, v + d, w, h]);            // front (+z)
  face([[x1, y1, z0], [x0, y1, z0], [x1, y0, z0], [x0, y0, z0]], [u + 2 * d + w, v + d, w, h]);    // back (-z)
  face([[x0, y1, z0], [x0, y1, z1], [x0, y0, z0], [x0, y0, z1]], [u, v + d, d, h]);                // right side (-x)
  face([[x1, y1, z1], [x1, y1, z0], [x1, y0, z1], [x1, y0, z0]], [u + d + w, v + d, d, h]);        // left side (+x)
  face([[x0, y1, z0], [x1, y1, z0], [x0, y1, z1], [x1, y1, z1]], [u + d, v, w, d]);                // top
  face([[x0, y0, z1], [x1, y0, z1], [x0, y0, z0], [x1, y0, z0]], [u + d + w, v, w, d]);            // bottom
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos.map(p => p * PX), 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx); g.computeVertexNormals();
  return new THREE.Mesh(g, new THREE.MeshLambertMaterial({map: tex, transparent: true, alphaTest: 0.1, side: THREE.DoubleSide}));
}

// A model part: pivot (pixels, y up from the feet), box offset from the pivot, inner + outer layer.
function part(tex, pivot, offset, size, base, over, rot) {
  const g = new THREE.Group();
  g.position.set(pivot[0] * PX, pivot[1] * PX, pivot[2] * PX);
  for (const [uvo, inf] of [[base, 0], [over, 0.25 + (size[1] == 8 ? 0.25 : 0)]]) {
    const m = skinBox(tex, size[0], size[1], size[2], uvo[0], uvo[1], inf);
    m.position.set(offset[0] * PX, offset[1] * PX, offset[2] * PX);
    g.add(m);
  }
  if (rot) g.rotation.set(rot[0], -rot[1], -rot[2], 'ZYX');
  return g;
}

function npcModel(n) {
  const tex = texture(n.skin), p = n.pose, aw = n.slim ? 3 : 4;
  const root = new THREE.Group();
  root.add(part(tex, [0, 24, 0], [0, 4, 0], [8, 8, 8], [0, 0], [32, 0], p.Head));
  root.add(part(tex, [0, 24, 0], [0, -6, 0], [8, 12, 4], [16, 16], [16, 32], p.Body));
  root.add(part(tex, [-5, 22, 0], [-(aw / 2 - 1), -4, 0], [aw, 12, 4], [40, 16], [40, 32], p.RightArm));
  root.add(part(tex, [5, 22, 0], [aw / 2 - 1, -4, 0], [aw, 12, 4], [32, 48], [48, 48], p.LeftArm));
  root.add(part(tex, [-1.9, 12, 0], [0, -6, 0], [4, 12, 4], [0, 16], [0, 32], p.RightLeg));
  root.add(part(tex, [1.9, 12, 0], [0, -6, 0], [4, 12, 4], [16, 48], [0, 48], p.LeftLeg));
  root.scale.setScalar(0.9375);  // humanoid renderers scale players by 15/16
  return root;
}

// ---------- weapons, built as Minecraft renders an item_display with the "fixed" item transform ----------
const CORNERS = {
  south: ([x0, y0, z0], [x1, y1, z1]) => [[x0, y1, z1], [x1, y1, z1], [x0, y0, z1], [x1, y0, z1]],
  north: ([x0, y0, z0], [x1, y1, z1]) => [[x1, y1, z0], [x0, y1, z0], [x1, y0, z0], [x0, y0, z0]],
  east:  ([x0, y0, z0], [x1, y1, z1]) => [[x1, y1, z1], [x1, y1, z0], [x1, y0, z1], [x1, y0, z0]],
  west:  ([x0, y0, z0], [x1, y1, z1]) => [[x0, y1, z0], [x0, y1, z1], [x0, y0, z0], [x0, y0, z1]],
  up:    ([x0, y0, z0], [x1, y1, z1]) => [[x0, y1, z0], [x1, y1, z0], [x0, y1, z1], [x1, y1, z1]],
  down:  ([x0, y0, z0], [x1, y1, z1]) => [[x0, y0, z1], [x1, y0, z1], [x0, y0, z0], [x1, y0, z0]],
};
function rotate(p, r) {
  if (!r) return p;
  const a = r.angle * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
  let [x, y, z] = [p[0] - r.origin[0], p[1] - r.origin[1], p[2] - r.origin[2]];
  if (r.axis === 'x') [y, z] = [y * c - z * s, y * s + z * c];
  else if (r.axis === 'y') [x, z] = [x * c + z * s, -x * s + z * c];
  else [x, y] = [x * c - y * s, x * s + y * c];
  return [x + r.origin[0], y + r.origin[1], z + r.origin[2]];
}
function weaponModel(w) {
  const g = new THREE.Group();
  if (w.flat) {  // stand-in for Karambit Vault's model: a flat curved blade on a grip
    const shape = new THREE.Shape();
    shape.moveTo(0, 0); shape.quadraticCurveTo(4, 6, 1, 12); shape.lineTo(-0.5, 11); shape.quadraticCurveTo(1.5, 6, -1.5, 1); shape.lineTo(0, 0);
    const blade = new THREE.Mesh(new THREE.ShapeGeometry(shape), new THREE.MeshLambertMaterial({color: 0xb8b8c0, side: THREE.DoubleSide}));
    blade.position.set(-1 + 8, 4, 8);
    const grip = new THREE.Mesh(new THREE.BoxGeometry(1.5, 5, 1.5), new THREE.MeshLambertMaterial({color: 0x5a3a24}));
    grip.position.set(7.5, 1.5, 8);
    const holder = new THREE.Group(); holder.add(blade, grip); holder.scale.setScalar(PX);
    g.add(holder);
  } else {
    const tex = texture(w.tex);
    tex.repeat.set(1, w.frameScale || 1);
    const pos = [], uv = [];
    w.elements.forEach(el => {
      for (const [f, fd] of Object.entries(el.faces)) {
        const c = CORNERS[f](el.from, el.to).map(p => rotate(p, el.rotation));
        const [u0, v0, u1, v1] = fd.uv.map(t => t / 16);
        const q = [[u0, 1 - v0], [u1, 1 - v0], [u0, 1 - v1], [u1, 1 - v1]];
        for (const i of [0, 2, 1, 1, 2, 3]) { pos.push(...c[i].map(t => t * PX)); uv.push(...q[i]); }
      }
    });
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    geo.computeVertexNormals();
    const img = new Image();
    img.onload = () => { const n = Math.max(1, Math.round(img.height / img.width)); tex.repeat.set(1, 1 / n); tex.offset.set(0, 1 - 1 / n); };
    img.src = w.tex;
    g.add(new THREE.Mesh(geo, new THREE.MeshLambertMaterial({map: tex, transparent: true, alphaTest: 0.1, side: THREE.DoubleSide})));
  }
  // ItemRenderer: translate(-0.5) after the display transform; ItemTransform.apply: translate, rotationXYZ, scale
  g.position.set(-0.5, -0.5, -0.5);
  const fx = new THREE.Group(); fx.add(g);
  const f = w.fixed || {}, r = (f.rotation || [0, 0, 0]).map(d => d * Math.PI / 180), t = (f.translation || [0, 0, 0]), sc = f.scale || [1, 1, 1];
  const disp = new THREE.Group(); disp.add(fx);
  fx.rotation.set(r[0], r[1], r[2], 'XYZ'); fx.scale.set(sc[0], sc[1], sc[2]);
  disp.position.set(t[0] * PX, t[1] * PX, t[2] * PX);
  const flip = new THREE.Group(); flip.add(disp); flip.rotation.y = Math.PI;  // ItemDisplayRenderer
  return flip;
}
function holster(item, h) {
  // item_display transformation = translation * left_rotation * scale * right_rotation
  const inner = new THREE.Group(); inner.add(weaponModel(DATA.weapons[item]));
  inner.quaternion.set(...h.right_rotation);
  const scaled = new THREE.Group(); scaled.add(inner); scaled.scale.set(...h.scale);
  const outer = new THREE.Group(); outer.add(scaled);
  outer.quaternion.set(...h.left_rotation); outer.position.set(...h.translation);
  return outer;  // entity yaw 0: display space = world, +z = the NPC's front
}

let shown = null;
function show(i) {
  const n = DATA.npcs[i];
  if (shown) scene.remove(shown);
  shown = new THREE.Group();
  shown.add(npcModel(n));
  shown.add(holster(n.item, DATA.holsters[n.at]));
  scene.add(shown);
  document.querySelectorAll('#tabs button').forEach((b, j) => b.setAttribute('aria-pressed', j === i));
  const label = n.item.split(':')[1].replace(/_/g, ' ');
  document.getElementById('info').innerHTML = `<h2>${n.name}</h2><p>${label} on the ${n.at}.</p>` +
    (DATA.weapons[n.item].flat ? '<p>Karambits use Karambit Vault’s model in game; this flat blade only marks where it sits.</p>' : '');
}
DATA.npcs.forEach((n, i) => { const b = document.createElement('button'); b.textContent = n.name; b.onclick = () => show(i); document.getElementById('tabs').appendChild(b); });
function resize() { const w = canvas.clientWidth, h = canvas.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
addEventListener('resize', resize); resize(); show(0);
(function loop() { controls.update(); renderer.render(scene, camera); requestAnimationFrame(loop); })();
</script></body></html>
"""

if __name__ == "__main__":
    main()
