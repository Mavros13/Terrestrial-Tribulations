"""Builds blockbench/previews/npc-viewer.html: every story NPC skin on a 3D player model (skinview3d), with its
name, role and look, for review (owner, 2026-10-29: "show me each npc skin"). Skins are embedded, so the page is one
file. Run after gen_npc_skins.py (build_prism.py does)."""
import base64, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKINS = os.path.join(ROOT, "pack", "kubejs", "assets", "tt", "textures", "entity", "npc")
OUT = os.path.join(ROOT, "blockbench", "previews", "npc-viewer.html")

# key: (name, colour, slim, role)
NPCS = {
    "maera": ("Elder Maera", "#E0675C", True, "Keeper of Emberhold. Main quest giver, Chapters 1 and 2."),
    "doran": ("Doran", "#E8934A", False, "Emberhold's smith. Forges the Ashfang Karambit, later upgrades weapons."),
    "rhosk": ("Captain Rhosk", "#7FBF62", False, "Thornwatch captain. Guards the road and tests newcomers."),
    "pell": ("Pell", "#D9A55C", False, "Tinkerer. Brings Create to Chapter 3 and the Cogwright Breaker."),
    "tamsin": ("Tamsin Rootwarden", "#6CC27A", True, "Verdant Pact. Gives the Rootstring Bow, guides to the Twilight Shard."),
    "ilsabet": ("Ilsabet", "#B796EE", True, "Conclave lead. Gives the Prism Ward Staff, later spell upgrades."),
    "stranger": ("The Stranger", "#B5BBC2", False, "Sells rare Old Engine parts. Asks more than it answers."),
    "wren": ("Wren", "#7CC6EA", True, "Scout. Exploration quests, Frostmaw and the dimension portals."),
    "sol": ("Archivist Sol", "#E2CF8A", False, "Emberhold librarian. Realm briefings and the Regent's Words."),
}


def looks():
    out = {}
    src = os.path.join(ROOT, "design", "npcs")
    for f in sorted(os.listdir(src)):
        if not f.endswith("-dialogue.md"):
            continue
        heading = None
        for line in open(os.path.join(src, f), encoding="utf-8"):
            if line.startswith("## "):
                heading = line[3:].strip()
            m = re.match(r"\*\*Look:\*\* (.*?)\s*\*\*Voice", line)
            if m and heading:
                for key, (name, *_r) in NPCS.items():
                    if heading.startswith(name) or heading.startswith(name.split()[-1]):
                        t = m.group(1).rstrip(". ")
                        out.setdefault(key, t[:1].upper() + t[1:] + ".")
    return out


def main():
    lk = looks()
    cards = []
    for key, (name, colour, slim, role) in NPCS.items():
        data = base64.b64encode(open(os.path.join(SKINS, key + ".png"), "rb").read()).decode()
        cards.append(f'''    <article class="npc" style="--npc:{colour}">
      <canvas data-skin="data:image/png;base64,{data}" data-model="{'slim' if slim else 'default'}" aria-label="{name}, 3D skin preview"></canvas>
      <div class="meta">
        <h2>{name}</h2>
        <p class="role">{role}</p>
        <p class="look">{lk.get(key, '')}</p>
        <p class="tag">{'Slim arms' if slim else 'Wide arms'} · tt:textures/entity/npc/{key}.png</p>
      </div>
    </article>''')
    html = HTML.replace("%CARDS%", "\n".join(cards)).replace("%COUNT%", str(len(NPCS)))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Built {os.path.relpath(OUT, ROOT)} with {len(NPCS)} NPCs")


HTML = """<title>Emberhold Cast</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Pixelify+Sans:wght@500;700&family=Source+Sans+3:wght@400;600&display=swap">
<style>
/* Layout: a torch-lit gallery wall, one alcove per NPC, the model turning slowly in each. Single dark theme. */
:root {
  --bg: #17130f; --wall: #221c16; --alcove: #2c241c; --line: #3d3227;
  --fg: #efe4d2; --muted: #b5a68f; --ember: #e8934a;
  --display: "Pixelify Sans", "Courier New", monospace; --body: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  color-scheme: dark;
}
body { background: var(--bg); color: var(--fg); font: 16px/1.5 var(--body); }
.wrap { max-width: 1180px; margin: 0 auto; padding-block: 40px 56px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
header { display: grid; gap: 8px; margin-bottom: 32px; }
header .eyebrow { font: 600 13px/1 var(--body); letter-spacing: .14em; text-transform: uppercase; color: var(--ember); }
h1 { font: 700 clamp(32px, 6vw, 52px)/1.05 var(--display); margin: 0; text-wrap: balance; }
header p { margin: 0; color: var(--muted); max-width: 62ch; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.npc { background: linear-gradient(180deg, var(--alcove), var(--wall)); border: 1px solid var(--line); border-radius: 6px;
  display: grid; grid-template-rows: auto 1fr; overflow: hidden; min-width: 0; }
.npc canvas { width: 100%; height: 320px; display: block; cursor: grab;
  background: radial-gradient(ellipse at 50% 85%, color-mix(in srgb, var(--npc) 28%, transparent), transparent 62%); }
.npc canvas:active { cursor: grabbing; }
.meta { padding: 14px 18px 18px; border-top: 1px solid var(--line); display: grid; gap: 6px; align-content: start; }
h2 { font: 700 24px/1.1 var(--display); margin: 0; color: var(--npc); }
.role { margin: 0; font-weight: 600; }
.look { margin: 0; color: var(--muted); }
.tag { margin: 4px 0 0; font: 12px/1.3 ui-monospace, "Cascadia Mono", Consolas, monospace; color: var(--muted); opacity: .8; overflow-wrap: anywhere; }
.controls { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 6px; }
button { font: 600 14px/1 var(--body); color: var(--fg); background: var(--alcove); border: 1px solid var(--line);
  border-radius: 4px; padding: 10px 14px; cursor: pointer; }
button[aria-pressed="true"] { border-color: var(--ember); color: var(--ember); }
button:focus-visible { outline: 2px solid var(--ember); outline-offset: 2px; }
.fallback { padding: 24px; color: var(--muted); }
</style>

<div class="wrap">
  <header>
    <span class="eyebrow">Terrestrial Tribulations · story NPCs</span>
    <h1>Emberhold Cast</h1>
    <p>All %COUNT% story NPC skins on the player model, as Easy NPC will show them. Drag a model to turn it, scroll to zoom.</p>
    <div class="controls">
      <button id="walk" type="button" aria-pressed="true">Walking</button>
      <button id="spin" type="button" aria-pressed="true">Turning</button>
    </div>
  </header>
  <section class="grid">
%CARDS%
  </section>
</div>

<script src="https://cdn.jsdelivr.net/npm/skinview3d@3.1.0/bundles/skinview3d.bundle.js"></script>
<script>
(function () {
  const viewers = [];
  const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!window.skinview3d) {
    document.querySelectorAll(".npc canvas").forEach(c => {
      const img = document.createElement("img");
      img.src = c.dataset.skin; img.alt = "skin texture"; img.style.cssText = "image-rendering:pixelated;width:100%;padding:24px";
      c.replaceWith(img);
    });
    return;
  }
  document.querySelectorAll(".npc canvas").forEach((canvas, i) => {
    const v = new skinview3d.SkinViewer({ canvas, width: canvas.clientWidth || 300, height: 320,
      skin: canvas.dataset.skin, model: canvas.dataset.model });
    v.zoom = 0.82;
    v.fov = 40;
    v.autoRotate = !reduce;
    v.autoRotateSpeed = 0.6;
    if (!reduce) { v.animation = new skinview3d.WalkingAnimation(); v.animation.speed = 0.55; v.animation.progress = i * 0.4; }
    v.globalLight.intensity = 2.4;
    v.cameraLight.intensity = 0.7;
    viewers.push(v);
  });
  const fit = () => viewers.forEach(v => { const w = v.canvas.parentElement.clientWidth; if (w) v.setSize(w, 320); });
  window.addEventListener("resize", fit); fit();
  const walk = document.getElementById("walk"), spin = document.getElementById("spin");
  walk.addEventListener("click", () => {
    const on = walk.getAttribute("aria-pressed") !== "true";
    walk.setAttribute("aria-pressed", on); walk.textContent = on ? "Walking" : "Standing";
    viewers.forEach((v, i) => { v.animation = on ? Object.assign(new skinview3d.WalkingAnimation(), { speed: 0.55 }) : null; });
  });
  spin.addEventListener("click", () => {
    const on = spin.getAttribute("aria-pressed") !== "true";
    spin.setAttribute("aria-pressed", on); spin.textContent = on ? "Turning" : "Still";
    viewers.forEach(v => { v.autoRotate = on; });
  });
  if (reduce) { walk.setAttribute("aria-pressed", "false"); walk.textContent = "Standing";
    spin.setAttribute("aria-pressed", "false"); spin.textContent = "Still"; }
})();
</script>
"""

if __name__ == "__main__":
    main()
