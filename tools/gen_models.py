#!/usr/bin/env python3
"""Generate our own 3D held models for the custom weapons (owner's choice, 2026-10-28: build our own models).

For every weapon with a shape in SHAPES below, this writes:
  blockbench/exports/weapons/<id>.json      Java Block/Item model (opens in Blockbench for hand-tuning)
  blockbench/textures/weapons/<id>.png      texture atlas, one frame per animation step (+ .mcmeta when animated)
  blockbench/textures/weapons/<id>_icon.png 32x32 inventory icon rendered from the model
  blockbench/previews/<id>.png              textured preview renders (not shipped; for review)
  blockbench/previews/_sheet.png            every preview on one sheet
build_content.py then installs the exports into the pack (3D in hand, flat icon in inventories).

Conventions (see blockbench/specs/weapons.md):
- Weapons are modelled upright along +Y with the grip on x=8, z=8 and the hand at y~1. The display transforms are
  vanilla item/handheld with -45 degrees added to every Z rotation. ItemTransform applies rotationXYZ (Rx*Ry*Rz), so
  that is the same as tilting the model -45 degrees about Z into the sprite's bottom-left to top-right diagonal,
  where vanilla handheld display already works. This leaves each element free to use its own 22.5-degree tilts.
- Elements named glow* get full brightness from build_content.py (Forge forge_data).
- Texture: every face gets its own patch of the atlas at DENSITY px per model unit (16 per block, i.e. a 64x
  resource-pack density), cut from a per-material sheet at the face's position so patterns run on across
  neighbouring elements, then bevelled (light top-left rim, dark bottom-right rim). Materials with a glow or veins
  pattern make the texture animated: energy flows along the blade and pulses over ANIM_FRAMES frames.
- Java item limits are respected: coordinates in [-16, 32], one rotation axis per element, angles in 22.5 steps.

A hand-made export of the same name replaces a generated one: delete the weapon's entry in SHAPES and drop the
Blockbench export in place.

Usage: python3 tools/gen_models.py
"""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BB = os.path.join(ROOT, "blockbench")
DENSITY = 4          # texture px per model unit
SHEET = 48 * DENSITY # material sheet covers the whole [-16, 32] model range
ANIM_FRAMES = 8      # frames for animated materials
FRAMETIME = 3        # game ticks per frame (8 x 3 = 1.2 s loop)


# ---------- colour helpers ----------
def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def lit(c, f):
    return tuple(max(0, min(255, int(round(x * f)))) for x in c)


# ---------- noise ----------
def value_noise(seed, cells_x, cells_y, size=SHEET):
    """Smooth noise in [0, 1]: a random grid upscaled bicubically."""
    rng = np.random.default_rng(seed)
    g = (rng.random((cells_y + 1, cells_x + 1)) * 255).astype(np.uint8)
    img = Image.fromarray(g, "L").resize((size, size), Image.BICUBIC)
    return np.asarray(img, dtype=np.float32) / 255.0


def fbm(seed, base=6, octaves=4):
    out, amp, tot = np.zeros((SHEET, SHEET), np.float32), 1.0, 0.0
    for o in range(octaves):
        c = base * 2 ** o
        out += amp * value_noise(seed * 31 + o, c, c)
        tot += amp
        amp *= 0.5
    return out / tot


def col(c):
    return np.array(rgb(c) if isinstance(c, str) else c, np.float32)


def lerp(a, b, t):
    t = np.clip(t, 0, 1)[..., None]
    return a * (1 - t) + b * t


# ---------- materials (sheets) ----------
ANIMATED_KINDS = ("glow", "veins")


def paint_sheet(mat, seed, frame=0, frames=1):
    """One SHEET x SHEET RGB array for a material. Y grows downward (= down the weapon)."""
    kind, c1, c2 = mat
    a, b = col(c1), col(c2 or c1)
    white = col((255, 255, 255))
    Y, X = np.mgrid[0:SHEET, 0:SHEET].astype(np.float32)
    n = fbm(seed)
    fine = value_noise(seed + 7, SHEET // 2, SHEET // 2)
    ph = 2 * math.pi * frame / max(1, frames)                     # animation phase, loops over the frames
    if kind == "metal":          # brushed metal: streaks along the length, soft sheen bands
        streak = value_noise(seed + 3, SHEET // 2, 3)                   # stretched along Y
        sheen = 0.5 + 0.5 * np.sin(Y / SHEET * 2 * math.pi * 3 + n * 4)
        f = 0.82 + 0.22 * streak + 0.12 * sheen + 0.06 * fine
        out = a * f[..., None]
        band = np.abs(((X * 0.7 - Y) % 56) - 28) < 3.5                 # polished highlight running across the parts
        out[band] = lerp(out[band], white * np.ones_like(out[band]), np.full(int(band.sum()), 0.28))
        scratch = (value_noise(seed + 9, 40, 40) > 0.86) & (fine > 0.6)
        out[scratch] = a * 1.35
    elif kind == "hammered":     # forged steel: bright planished metal pocked with dark hammer marks
        pits = value_noise(seed + 13, SHEET // 2, SHEET // 2)
        pits2 = value_noise(seed + 17, SHEET // 5, SHEET // 5)
        depth = np.clip((pits * 0.65 + pits2 * 0.35 - 0.6) * 6, 0, 1)
        out = lerp(a * (0.92 + 0.12 * fine)[..., None], b, depth * 0.9)
        out[(depth < 0.05) & (fine > 0.8)] = lerp(a, white, np.full(1, 0.35))[0]
    elif kind == "edge":         # honed edge: near-white with a faint ripple
        out = lerp(a, white, 0.45 + 0.3 * fine + 0.1 * np.sin(Y * 0.8))
    elif kind == "dark":         # lacquer / obsidian: deep, cloudy, with sparse glints of the second colour
        out = a * (0.8 + 0.4 * n)[..., None]
        glint = fine > 0.93
        out[glint] = lerp(a, b, np.full(glint.sum(), 0.6)) * 1.4
    elif kind == "wood":         # wavy grain along the length
        g = np.sin((X + 9 * n) * 0.55) * 0.5 + 0.5
        out = lerp(a, b, g * 0.75) * (0.92 + 0.12 * fine)[..., None]
    elif kind == "wrap":         # diagonal leather / cloth bands with dark seams
        band = ((X + Y) % 10)
        f = np.where(band < 1.2, 0.55, 0.9 + 0.12 * np.sin(band / 10 * math.pi))
        out = a * (f * (0.94 + 0.12 * fine))[..., None]
    elif kind == "bone":         # mottled ivory with pores
        out = lerp(a, b, n * 0.8) * (0.95 + 0.08 * fine)[..., None]
        pores = value_noise(seed + 5, 64, 64) > 0.82
        out[pores] *= 0.82
    elif kind == "gem":          # faceted crystal: bands of facets with bright sparkles
        facet = (np.floor(X / 6) + np.floor(Y / 6)) % 3
        out = lerp(a * 0.7, lerp(a, white, np.full(X.shape, 0.5)), facet / 2 * 0.8 + 0.2 * fine)
        out[fine > 0.9] = white
    elif kind == "glow":         # flowing energy: bright filaments drifting along the blade, pulsing
        flow = (np.sin(Y * 2 * math.pi / 48 * 2 - ph + n * 6) * 0.5 + 0.5)
        flow2 = (np.sin(Y * 2 * math.pi / 48 * 5 + ph * 2 + X * 0.3 + n * 9) * 0.5 + 0.5)
        e = 0.45 * flow + 0.35 * flow2 + 0.2 * fine
        pulse = 0.85 + 0.15 * math.sin(ph)
        out = lerp(b, a, e * 1.3) * pulse
        out = lerp(out, lerp(a, white, np.full(X.shape, 0.6)), np.clip(e - 0.62, 0, 1) * 2.6)
    elif kind == "veins":        # dark stone with branching cracks that glow and pulse
        r = np.abs(fbm(seed + 11, 9, 3) - 0.5)                    # thin branching cracks
        crack = np.clip(1 - r / 0.028, 0, 1) ** 1.5
        heat = 0.75 + 0.25 * np.sin(ph + n * 5)
        out = a * (0.75 + 0.35 * n)[..., None]
        out = lerp(out, lerp(b, white, np.full(X.shape, 0.25)) * heat[..., None], crack)
    elif kind == "scale":        # overlapping scales in offset rows
        row = np.floor(Y / 5)
        cx = (X + (row % 2) * 3) % 6 - 3
        cy = Y % 5
        d = np.sqrt(cx ** 2 + (cy * 1.2) ** 2) / 4
        out = a * (1.15 - 0.45 * np.clip(d, 0, 1) + 0.08 * fine)[..., None]
        out[cy < 0.8] *= 0.7
    elif kind == "feather":      # barbs angled away from the shaft
        barb = np.sin((np.abs(X % 16 - 8) + Y) * 1.1) * 0.5 + 0.5
        out = lerp(a, b, np.abs(X % 16 - 8) / 8 * 0.8 + 0.2 * barb)
        out[np.abs(X % 16 - 8) < 0.8] = b * 1.1
    else:                        # flat
        out = a * (0.94 + 0.1 * n)[..., None]
    return np.clip(out, 0, 255)


def bevel(patch, face):
    """Two-step rim light (top/left bright, bottom/right dark) plus light falling off down each side face, so
    every cube reads as a rounded, lit object rather than a flat colour."""
    h, w = patch.shape[:2]
    if face in ("north", "south", "east", "west") and h > 2:
        patch *= np.linspace(1.07, 0.9, h, dtype=np.float32)[:, None, None]
    elif face == "up":
        patch *= 1.05
    if w >= 3 and h >= 3:
        patch[0, :] *= 1.2
        patch[:, 0] *= 1.12
        patch[-1, :] *= 0.7
        patch[:, -1] *= 0.8
    if w >= 8 and h >= 8:
        patch[1, 1:-1] *= 1.08
        patch[1:-1, 1] *= 1.05
        patch[-2, 1:-1] *= 0.88
        patch[1:-1, -2] *= 0.92
    return np.clip(patch, 0, 255)


# ---------- geometry builder ----------
class Model:
    def __init__(self, wid):
        self.wid = wid
        self.mats = []       # list of (kind, c1, c2)
        self.els = []

    def mat(self, kind, c1, c2=None):
        m = (kind, c1, c2)
        if m not in self.mats:
            assert len(self.mats) < 16, f"{self.wid}: more than 16 materials"
            self.mats.append(m)
        return self.mats.index(m)

    def box(self, name, frm, to, m, rot=None):
        # Shapes are written with blades, axe heads and hooks on +X; in game that side faces back toward the
        # holder (Oscar, 2026-10-29 test: cleaver and halberd "backwards"), so every element is mirrored to -X.
        frm, to = [16 - to[0], frm[1], frm[2]], [16 - frm[0], to[1], to[2]]
        if rot:
            axis, angle, origin = rot
            rot = (axis, angle if axis == "x" else -angle, [16 - origin[0], origin[1], origin[2]])
        frm = [round(v, 3) for v in frm]
        to = [round(v, 3) for v in to]
        for v in frm + to:
            assert -16 <= v <= 32, f"{self.wid}/{name}: coordinate {v} outside [-16, 32]"
        el = {"name": name, "from": frm, "to": to, "m": m}
        if rot:
            axis, angle, origin = rot
            assert angle in (-45, -22.5, 0, 22.5, 45), f"{self.wid}/{name}: angle {angle}"
            el["rotation"] = {"angle": angle, "axis": axis, "origin": [round(v, 3) for v in origin]}
        self.els.append(el)

    # Centered helpers: x/z centered on 8, y explicit.
    def c(self, name, y0, y1, w, d, m, dx=0.0, dz=0.0, rot=None):
        self.box(name, [8 - w / 2 + dx, y0, 8 - d / 2 + dz], [8 + w / 2 + dx, y1, 8 + d / 2 + dz], m, rot)

    def taper(self, name, y0, y1, w0, w1, d, m, steps, dx0=0.0, dx1=0.0, edge=None, edge_w=0.35, ridge=True, ridge_f=0.28):
        """Blade from width w0 at y0 to w1 at y1, optionally drifting sideways (curve), with bright edge strips on
        both sides and a raised central ridge (ridge: True = same material, a material index, or False). Short
        steps keep curves and tapers smooth."""
        steps = max(steps, int(round((y1 - y0) / 1.4)))
        h = (y1 - y0) / steps
        for i in range(steps):
            t = (i + 0.5) / steps
            w = w0 + (w1 - w0) * t
            dx = dx0 + (dx1 - dx0) * (t * t)
            ya, yb = y0 + i * h, y0 + (i + 1) * h + 0.01
            self.c(f"{name}_{i}", ya, yb, w, d, m, dx=dx)
            if edge is not None and w > 2 * edge_w + 0.2:
                self.c(f"{name}_edgeL_{i}", ya, yb, edge_w, d + 0.1, edge, dx=dx - w / 2 + edge_w / 2)
                self.c(f"{name}_edgeR_{i}", ya, yb, edge_w, d + 0.1, edge, dx=dx + w / 2 - edge_w / 2)
            if ridge is not False and w > 1.1 and d >= 0.5:
                rm = m if ridge is True else ridge
                rn = ("glow_" if self.mats[rm][0] == "glow" else "") + f"{name}_ridge_{i}"
                self.c(rn, ya, yb, max(0.25, w * ridge_f), d + 0.24, rm, dx=dx)

    def grip(self, y0, y1, r, m_wrap, m_cap=None):
        self.c("grip", y0, y1, r, r, m_wrap)
        y = y0 + 0.7
        while y < y1 - 0.5:                                         # raised wrap ribs
            self.c(f"grip_rib_{round(y, 1)}", y, y + 0.35, r + 0.22, r + 0.22, m_wrap)
            y += 1.3
        if m_cap is not None:
            self.c("grip_cap", y0 - 1.2, y0, r + 0.8, r + 0.8, m_cap)
            self.c("grip_knob", y0 - 1.7, y0 - 1.2, r + 0.2, r + 0.2, m_cap)


# ---------- display (vanilla item/handheld with Z - 45) ----------
DISPLAY = {
    "thirdperson_righthand": {"rotation": [0, -90, 10], "translation": [0, 4, 0.5], "scale": [0.85, 0.85, 0.85]},
    "thirdperson_lefthand": {"rotation": [0, 90, -100], "translation": [0, 4, 0.5], "scale": [0.85, 0.85, 0.85]},
    "firstperson_righthand": {"rotation": [0, -90, -20], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
    "firstperson_lefthand": {"rotation": [0, 90, -70], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
    "ground": {"rotation": [0, 0, -45], "translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
    "gui": {"rotation": [0, 0, -45], "translation": [0, 0, 0], "scale": [1, 1, 1]},
    "head": {"rotation": [0, 180, -45], "translation": [0, 13, 7], "scale": [1, 1, 1]},
    "fixed": {"rotation": [0, 180, -45], "translation": [0, 0, 0], "scale": [1, 1, 1]},
}


def scaled_display(s):
    """Display for long weapons: the model is built at a manageable size and scaled up in hand."""
    d = json.loads(json.dumps(DISPLAY))
    for k in ("thirdperson_righthand", "thirdperson_lefthand", "firstperson_righthand", "firstperson_lefthand", "ground"):
        d[k]["scale"] = [round(v * s, 3) for v in d[k]["scale"]]
    return d


def worn_display():
    """Worn weapons (owner, 2026-10-29: "wraps around your hand ... like a part of your hand in all POVs"): the held
    model is placed over the fist and forearm instead of in the grip. Built fist-up (+y = knuckles, -z = back of the
    hand); vanilla's third-person hand pose (ItemInHandLayer: X -90, Y 180, translate 1/16, 2/16, -10/16) puts the
    item origin at the front of the hand, so rotation [-90, 180, 0] lays the model along the arm, knuckles past the
    hand and back plate on the front. Scale is wider than the arm (covers chestplate sleeves, any skin width) and
    shorter along it. Epic Fight draws held items on its animated hand joint with this same third-person transform,
    so the gauntlet follows battle-mode animations (a Palladium arm layer did not)."""
    d = scaled_display(1.0)
    tp = {"rotation": [-90, 180, 0], "translation": [0, -2, -2.95], "scale": [1.5, 0.9, 1.5]}
    d["thirdperson_righthand"] = dict(tp)
    d["thirdperson_lefthand"] = dict(tp)
    d["firstperson_righthand"] = {"rotation": [-60, 0, 0], "translation": [1.13, 4.5, -3], "scale": [0.8, 0.8, 0.8]}
    d["firstperson_lefthand"] = {"rotation": [-60, 0, 0], "translation": [1.13, 4.5, -3], "scale": [0.8, 0.8, 0.8]}
    return d


# ---------- the weapons ----------
STEEL = "#B8C0C8"
DARK_STEEL = "#4A4F57"


def limb_chain(m, name, x, y, segs, wid, dep, mat, sign, glow=None):
    """Bow limb from (x, y) as a chain of straight segments, each tilted away from the string (toward -x).
    segs = [(length, angle)]; sign 1 = upper limb, -1 = lower limb. Returns the tip (x, y)."""
    for i, (L, ang) in enumerate(segs):
        y0, y1 = (y, y + L) if sign > 0 else (y - L, y)
        rot = ("z", ang * sign, [x, y, 8]) if ang else None
        m.box(f"{name}_{i}", [x - wid / 2, y0, 8 - dep / 2], [x + wid / 2, y1, 8 + dep / 2], mat, rot)
        if glow is not None:
            m.box(f"glow_{name}_{i}", [x - 0.18, y0 + 0.3 * sign * 0 + 0.3, 8 - dep / 2 - 0.05],
                  [x + 0.18, y1 - 0.3, 8 + dep / 2 + 0.05], glow, rot)
        r = math.radians(ang)
        x, y = x - L * math.sin(r), y + sign * L * math.cos(r)
    return x, y


def disc(m, name, cx, cy, size, depth, mat, dz=0.0):
    """Round boss facing +z/-z: a square and a 45-degree square overlap into an octagon."""
    h = size / 2
    m.box(name, [cx - h, cy - h, 8 - depth / 2 + dz], [cx + h, cy + h, 8 + depth / 2 + dz], mat)
    k = h * 0.82
    m.box(name + "_r", [cx - k, cy - k, 8 - depth / 2 + dz + 0.01], [cx + k, cy + k, 8 + depth / 2 + dz - 0.01], mat,
          ("z", 45, [cx, cy, 8]))


def frontier_cleaver(m, p, s, a):
    steel, wood = m.mat("hammered", p, "#34312D"), m.mat("wood", s, "#5E4128")
    edge, iron = m.mat("edge", "#F4F1E8"), m.mat("metal", a)
    copper, sinew = m.mat("metal", "#B5653A"), m.mat("wrap", "#7A5A3A")
    # handle: a flat, slightly swelling wooden slab with copper rivets and an iron butt cap
    m.c("butt_cap", -7.2, -6.2, 2.0, 1.6, iron)
    m.c("handle_low", -6.2, -2.0, 1.8, 1.35, wood)
    m.c("handle_mid", -2.0, 1.6, 1.95, 1.45, wood)
    m.c("handle_high", 1.6, 4.0, 1.8, 1.35, wood)
    for y in (-4.6, 0.6):
        m.c(f"rivet_{y}", y, y + 0.7, 0.7, 1.7, copper)
    m.c("lashing", 3.0, 4.0, 2.05, 1.55, sinew)
    m.c("bolster", 4.0, 5.0, 2.1, 1.6, iron)
    # the blade: a broad rectangle hung off the spine side, with a real hanging hole near the top corner
    m.box("blade", [6.9, 5.0, 7.62], [14.6, 16.6, 8.38], steel)
    m.box("blade_top_spine", [6.9, 16.6, 7.62], [7.8, 18.4, 8.38], steel)
    m.box("blade_top_main", [9.2, 16.6, 7.62], [14.6, 18.4, 8.38], steel)
    m.box("blade_top_bar", [7.8, 17.8, 7.62], [9.2, 18.4, 8.38], steel)
    m.box("spine", [6.7, 5.0, 7.55], [7.3, 18.4, 8.45], iron)
    m.box("spine_top", [6.7, 18.4, 7.55], [14.6, 18.9, 8.45], iron)
    m.box("bevel", [13.6, 4.7, 7.68], [14.6, 18.4, 8.32], edge)
    m.box("edge", [14.6, 4.7, 7.74], [15.2, 18.6, 8.26], edge)
    m.box("heel", [6.9, 4.4, 7.62], [15.2, 5.0, 8.38], iron)
    return scaled_display(1.0)


def accord_longsword(m, p, s, a):
    steel, edge, brass = m.mat("metal", STEEL), m.mat("edge", "#D8DEE4"), m.mat("metal", s)
    crimson, leather, fuller = m.mat("gem", p), m.mat("wrap", p), m.mat("metal", "#7E858D")
    # wheel pommel with a crimson gem at its heart
    disc(m, "pommel", 8, -8.4, 2.8, 1.1, brass)
    m.c("pommel_gem", -9.0, -7.8, 0.8, 1.3, crimson)
    m.c("pommel_neck", -7.0, -6.4, 1.0, 1.0, brass)
    # long two-handed grip: crimson leather with brass ferrules and a mid riser
    m.c("ferrule_low", -6.4, -5.8, 1.6, 1.6, brass)
    m.grip(-5.8, 2.0, 1.35, leather)
    m.c("riser", -2.2, -1.7, 1.55, 1.55, brass)
    m.c("ferrule_high", 2.0, 2.6, 1.6, 1.6, brass)
    # straight cross-guard with flared ends and a langet block
    m.c("cross", 2.6, 3.3, 9.4, 0.9, brass)
    m.c("cross_end_L", 2.3, 3.6, 0.6, 1.1, brass, dx=-4.9)
    m.c("cross_end_R", 2.3, 3.6, 0.6, 1.1, brass, dx=4.9)
    m.c("quillon_block", 2.4, 4.0, 1.8, 1.4, brass)
    m.c("quillon_gem", 2.9, 3.6, 0.6, 1.5, crimson)
    # long, slim blade with a dark fuller running two thirds of its length
    m.taper("blade", 4.0, 28.4, 2.3, 0.9, 0.6, steel, 12, edge=edge, edge_w=0.3, ridge=False)
    m.c("fuller", 4.4, 20.5, 0.55, 0.68, fuller)
    m.c("tip", 28.4, 29.6, 0.6, 0.5, edge)
    m.c("tip_point", 29.6, 30.4, 0.3, 0.4, edge)
    return scaled_display(0.82)


def gnawblade(m, p, s, a):
    blade, edge = m.mat("metal", p), m.mat("edge", "#C9C2B6")
    wrap, bone, tail = m.mat("wrap", s), m.mat("bone", "#E6DECB", "#B8AE98"), m.mat("flat", a)
    m.c("skull", -3.6, -1.2, 2.6, 2.6, bone)
    m.c("skull_snout", -2.8, -1.8, 1.2, 1.4, bone, dz=1.6)
    m.c("ear_L", -1.4, -0.6, 0.7, 0.7, bone, dx=-1.0)
    m.c("ear_R", -1.4, -0.6, 0.7, 0.7, bone, dx=1.0)
    m.c("eye_L", -2.4, -2.0, 0.5, 0.2, tail, dx=-0.6, dz=1.31)
    m.c("eye_R", -2.4, -2.0, 0.5, 0.2, tail, dx=0.6, dz=1.31)
    m.c("tail_loop", -6, -3.6, 0.4, 0.4, tail, dx=1.2, rot=("z", 22.5, [9.2, -3.6, 8]))
    m.grip(-1.2, 3, 1.5, wrap)
    m.c("guard", 3, 3.8, 4.2, 1.4, blade)
    m.c("guard_tooth_L", 3.4, 4.6, 0.6, 0.8, edge, dx=-2.0)
    m.c("guard_tooth_R", 3.4, 4.6, 0.6, 0.8, edge, dx=2.0)
    m.taper("blade", 3.8, 14, 2.8, 1.4, 0.8, blade, 5, edge=edge)
    m.c("tip", 14, 15.2, 0.8, 0.6, edge)
    for i, y in enumerate((5.5, 7.5, 9.5, 11.5)):                       # rat-tooth serrations on the spine
        m.c(f"tooth_{i}", y, y + 1.0, 0.7, 0.7, edge, dx=-1.6 + 0.12 * i)
    return DISPLAY


def rootstring_bow(m, p, s, a):
    bark, leaf, moss = m.mat("wood", s, "#3E2C1B"), m.mat("feather", p, a), m.mat("wrap", a)
    vine = m.mat("flat", p)
    m.c("grip", 5.6, 10.4, 1.7, 1.7, moss)
    segs = [(3.0, 0), (3.2, 22.5), (3.0, 22.5), (2.6, 45)]
    tips = []
    for side, sign, y in (("up", 1, 10.4), ("down", -1, 5.6)):
        tx, ty = limb_chain(m, f"limb_{side}", 8, y, segs, 1.25, 1.15, bark, sign)
        tips.append((tx, ty))
        m.box(f"leaf_{side}", [tx - 1.6, ty - 0.6, 7.95], [tx + 0.4, ty + 0.6, 8.05], leaf, ("z", 22.5 * sign, [tx, ty, 8]))
        m.c(f"nock_{side}", ty - 0.5, ty + 0.5, 0.9, 0.9, moss, dx=tx - 8)
    for i, y in enumerate((11.8, 13.6, 3.8, 2.0)):                   # vine knots winding round the limbs
        m.c(f"vine_{i}", y, y + 0.7, 1.6, 1.6, vine, dx=-0.15 * (i % 2))
    (tx, ty), (bx, by) = tips
    m.box("string", [tx - 0.1, by, 7.9], [tx + 0.1, ty, 8.1], moss)
    return DISPLAY


def thornwatch_halberd(m, p, s, a):
    shaft, bronze, head = m.mat("wood", "#5A4128", "#3B2A18"), m.mat("metal", s), m.mat("metal", p)
    thorn, edge = m.mat("flat", a), m.mat("edge", "#9FB8A6")
    m.c("ferrule", -14, -12, 1.6, 1.6, bronze)
    m.c("shaft", -12, 23, 1.2, 1.2, shaft)
    m.c("grip_band", -2, 2, 1.45, 1.45, bronze)
    for i in range(5):                                             # thorn vine winding up the shaft
        y = 7 + i * 2.2
        m.c(f"vine_{i}", y, y + 1.4, 1.8, 0.5, head, dz=0.6 if i % 2 else -0.6, rot=("z", 22.5 if i % 2 else -22.5, [8, y, 8]))
        m.c(f"thorn_{i}", y + 0.4, y + 0.9, 0.5, 0.5, thorn, dx=1.1 if i % 2 else -1.1)
    m.c("collar_low", 17, 18.2, 2.0, 2.0, bronze)
    m.c("socket", 18.2, 24.5, 1.7, 1.5, head)
    m.c("collar_high", 24.5, 25.5, 2.2, 2.2, bronze)
    # axe blade on +x: a broad plate whose cutting edge flares into upper and lower horns
    m.box("axe_neck", [8.8, 19.4, 7.65], [11, 23.2, 8.35], head)
    m.box("axe_plate", [11, 17.6, 7.7], [14.4, 25, 8.3], head)
    m.box("axe_edge", [14.4, 17.2, 7.75], [15.1, 25.4, 8.25], edge)
    m.box("axe_horn_up", [13.2, 25, 7.75], [15.1, 27.2, 8.25], edge, ("z", -22.5, [15.1, 25, 8]))
    m.box("axe_horn_down", [13.2, 15.2, 7.75], [15.1, 17.4, 8.25], edge, ("z", 22.5, [15.1, 17.4, 8]))
    m.box("axe_vein", [11.4, 20.6, 7.6], [14.0, 21.8, 8.4], thorn)
    # back spike on -x, curving down like a thorn
    m.box("spike_base", [5.6, 20.4, 7.6], [7.2, 22.4, 8.4], head)
    m.box("spike", [2.4, 20.8, 7.7], [5.6, 22.0, 8.3], thorn, ("z", 22.5, [5.6, 21.4, 8]))
    m.taper("spear", 25.5, 31.8, 1.8, 0.4, 0.7, head, 4, edge=edge)
    return scaled_display(1.1)


def cogwright_breaker(m, p, s, a):
    copper, brass, glass = m.mat("metal", p), m.mat("metal", s), m.mat("glow", a, "#1A6F78")
    handle = m.mat("wood", "#4B3524", "#2E2016")
    m.c("pommel", -6, -4.6, 2.2, 2.2, brass)
    m.c("handle", -4.6, 16, 1.4, 1.4, handle)
    for y in (0, 4, 8):
        m.c(f"band_{y}", y, y + 0.8, 1.9, 1.9, brass)
    m.c("head", 16, 22, 9, 4.2, copper)
    m.c("face_L", 16.5, 21.5, 1.2, 4.6, brass, dx=-5)
    m.c("face_R", 16.5, 21.5, 1.2, 4.6, brass, dx=5)
    m.c("piston_rod", 18.3, 19.7, 13.5, 1.0, brass)
    for side in (-1, 1):                                           # exposed gears: two crossed discs per side
        m.c(f"gear_a_{side}", 17, 21, 3.6, 0.6, brass, dz=2.4 * side)
        m.c(f"gear_b_{side}", 17, 21, 3.6, 0.6, brass, dz=2.4 * side, rot=("z", 45, [8, 19, 8 + 2.4 * side]))
    for i in range(5):                                             # five pressure gauges on top
        m.c(f"glow_gauge_{i + 1}", 22, 22.8, 0.9, 0.9, glass, dx=-3.2 + i * 1.6)
    return scaled_display(0.95)


def prism_ward_staff(m, p, s, a):
    ivory, gold, prism = m.mat("bone", p, "#D9D0B8"), m.mat("metal", s), m.mat("gem", a)
    glowp = m.mat("glow", a, "#2346B8")
    m.c("foot_spike", -15.4, -14, 0.8, 0.8, gold)
    m.c("foot", -14, -12.6, 1.8, 1.8, gold)
    m.c("shaft", -12.6, 21, 1.4, 1.4, ivory)
    for y in (-8, -1, 6, 13):                                      # gold bands with tiny inset gems
        m.c(f"band_{y}", y, y + 0.7, 1.8, 1.8, gold)
        m.c(f"glow_band_gem_{y}", y + 0.15, y + 0.55, 0.5, 1.9, glowp)
    m.grip(0, 4, 1.5, m.mat("wrap", "#3B3F7A"))
    m.c("collar", 21, 22.4, 2.6, 2.6, gold)
    m.c("collar_lip", 22.4, 22.9, 3.2, 3.2, gold)
    for i, (dx, dz) in enumerate(((-2.4, 0), (2.4, 0), (0, -2.4), (0, 2.4))):   # four bowed cage bars
        m.c(f"bar_low_{i}", 22.9, 25, 0.55, 0.55, gold, dx=dx * 0.7, dz=dz * 0.7)
        m.c(f"bar_mid_{i}", 25, 28.4, 0.55, 0.55, gold, dx=dx, dz=dz)
        m.c(f"bar_top_{i}", 28.4, 30.4, 0.55, 0.55, gold, dx=dx * 0.7, dz=dz * 0.7)
        m.c(f"bar_gem_{i}", 26.3, 27.1, 0.8, 0.8, prism, dx=dx * 1.08, dz=dz * 1.08)
    m.c("crown", 30.4, 31.2, 3.0, 3.0, gold)
    m.c("crown_spike", 31.2, 32, 0.8, 0.8, gold)
    m.c("prism", 24.4, 28.8, 2.0, 2.0, prism, rot=("y", 45, [8, 26.6, 8]))
    m.c("prism_cap_low", 23.8, 24.4, 1.0, 1.0, prism, rot=("y", 45, [8, 26.6, 8]))
    m.c("prism_cap_high", 28.8, 29.4, 1.0, 1.0, prism, rot=("y", 45, [8, 26.6, 8]))
    m.c("glow_prism", 25.0, 28.2, 1.2, 1.2, glowp, rot=("y", 45, [8, 26.6, 8]))
    return scaled_display(1.05)


def hollowbane_tachi(m, p, s, a):
    lacquer, hamon, silver = m.mat("dark", p, s), m.mat("glow", s, "#3B1677"), m.mat("metal", a)
    wrap = m.mat("wrap", "#2A2530")
    m.grip(-7, 3, 1.4, wrap, silver)
    for y in (-5, -2, 1):                                               # menuki diamonds on the wrap
        m.c(f"menuki_{y}", y, y + 0.8, 0.6, 1.6, silver)
    m.c("tsuba", 3, 3.7, 3.6, 3.6, silver)
    m.c("tsuba_rim", 3.05, 3.65, 3.9, 0.6, lacquer)
    m.c("habaki", 3.7, 4.8, 1.6, 1.2, silver)
    m.taper("blade", 4.8, 29, 1.7, 1.2, 0.6, lacquer, 8, dx0=0, dx1=-2.6)   # curved single edge
    for i in range(6):                                                  # hamon along the edge, following the curve
        t0, t1 = i / 6, (i + 1) / 6
        y0, y1 = 4.8 + 24.2 * t0, 4.8 + 24.2 * t1
        dx = -2.6 * ((t0 + t1) / 2) ** 2
        m.c(f"glow_hamon_{i + 1}", y0, y1 + 0.01, 0.35, 0.65, hamon, dx=dx + 0.55)
    m.c("kissaki_1", 29, 30, 1.0, 0.55, lacquer, dx=-2.75)
    m.c("kissaki_2", 30, 30.8, 0.5, 0.5, lacquer, dx=-3.0)
    m.c("glow_kissaki", 29, 30.4, 0.3, 0.6, hamon, dx=-2.3)
    return scaled_display(0.8)


def cinder_crown(m, p, s, a):
    obsidian, veins, magma = m.mat("dark", p, s), m.mat("veins", p, s), m.mat("glow", a, s)
    grip = m.mat("wrap", "#2B1A1F")
    m.c("pommel", -7, -5.4, 2.4, 2.4, obsidian)
    m.grip(-5.4, 3, 1.7, grip)
    m.c("guard", 3, 4.8, 8, 2.4, obsidian)
    for i, dx in enumerate((-3.2, -1.6, 0, 1.6, 3.2)):             # crown of five spikes
        m.c(f"spike_{i}", 4.8, 7 + (1.2 if dx == 0 else 0), 0.9, 0.9, magma, dx=dx)
    m.taper("blade", 4.8, 26, 6.2, 5.4, 1.4, obsidian, 4, ridge=False)
    m.c("glow_cracks_F", 6, 25, 5.4, 0.02, veins, dz=0.72)
    m.c("glow_cracks_B", 6, 25, 5.4, 0.02, veins, dz=-0.72)
    m.c("tip", 26, 27.4, 4.4, 1.2, obsidian)
    m.c("tip_2", 27.4, 28.6, 2.6, 1.1, obsidian)
    m.c("tip_3", 28.6, 29.6, 1.0, 1.0, magma)
    for i in range(6):                                             # jagged, ember-tipped teeth along both edges
        y = 7 + i * 3.2
        hw = 3.1 - 0.4 * (y - 4.8) / 21.2
        for side in (-1, 1):
            x = 8 + side * hw
            m.box(f"tooth_{i}_{side}", [x - 0.6, y, 7.45], [x + 0.6, y + 1.6, 8.55], obsidian, ("z", -22.5 * side, [x, y, 8]))
            m.box(f"glow_ember_{i}_{side}", [x - 0.3, y + 1.0, 7.4], [x + 0.3, y + 1.6, 8.6], magma, ("z", -22.5 * side, [x, y, 8]))
    return scaled_display(1.0)


def wroughtnaut_bulwark(m, p, s, a):
    iron, rust, rivet = m.mat("metal", p), m.mat("dark", s, "#C46A4E"), m.mat("metal", a)
    edge, handle = m.mat("edge", "#A9AEB3"), m.mat("wood", "#3B2E25", "#251C16")
    m.c("haft", -8, 23, 1.5, 1.5, handle)
    m.c("pommel", -9.6, -8, 2.2, 2.2, iron)
    m.c("pommel_spike", -10.6, -9.6, 1.0, 1.0, rivet)
    m.grip(-7, -1, 1.65, m.mat("wrap", "#4A3A2C"))
    for y in (2, 7):
        m.c(f"strap_{y}", y, y + 0.8, 1.9, 1.9, rivet)
    # great slab blade on +x: straight top, bearded lower edge
    m.box("plate", [8.6, 12, 7.35], [15.4, 23.4, 8.65], iron)
    m.box("beard_1", [10.4, 10.4, 7.4], [15.4, 12, 8.6], iron)
    m.box("beard_2", [12.4, 9.0, 7.45], [15.4, 10.4, 8.55], iron)
    m.box("edge", [15.4, 9.0, 7.5], [16.2, 23.4, 8.5], edge)
    m.box("edge_tip", [15.4, 23.4, 7.55], [16.0, 24.2, 8.45], edge)
    m.box("rust_streak_a", [10.6, 13, 7.32], [12.2, 21.5, 8.68], rust)
    m.box("rust_streak_b", [13.2, 10.6, 7.32], [14.0, 16, 8.68], rust)
    for r in range(3):
        for c in range(3):
            y = 14 + r * 3.2
            m.box(f"rivet_{r}_{c}", [9.4 + c * 2.0, y, 7.1], [10.2 + c * 2.0, y + 0.8, 8.9], rivet)
    m.box("spine", [8.4, 23.4, 7.25], [15.6, 24.4, 8.75], rivet)
    # back hammer poll on -x
    m.box("poll_neck", [5.8, 16.5, 7.4], [8.6, 19.5, 8.6], iron)
    m.box("poll", [3.6, 15.6, 6.9], [5.8, 20.4, 9.1], iron)
    m.box("poll_face", [3.2, 16.0, 7.1], [3.6, 20.0, 8.9], rivet)
    m.c("cap", 23, 24.8, 2.2, 2.2, iron)
    m.c("cap_spike", 24.8, 26, 0.9, 0.9, rivet)
    return scaled_display(0.95)


def skyreach_spear(m, p, s, a):
    shaft, gold, vane, white = m.mat("metal", s), m.mat("metal", "#E8D27A"), m.mat("feather", p, a), m.mat("edge", a)
    glowtip, sky = m.mat("glow", p, "#2A7FC0"), m.mat("metal", p)
    m.c("butt_spike", -15.8, -14.6, 0.6, 0.6, gold)
    m.c("butt", -14.6, -13.4, 1.4, 1.4, gold)
    m.c("shaft", -13.4, 20, 1.1, 1.1, shaft)
    m.grip(-2, 4, 1.3, m.mat("wrap", "#5B8FC4"))
    for y in (-9, 9, 15):
        m.c(f"ring_{y}", y, y + 0.6, 1.4, 1.4, gold)
    m.c("collar", 18.6, 20.4, 1.9, 1.9, gold)
    m.c("socket", 20.4, 22.2, 1.5, 1.5, sky)
    for sign in (-1, 1):                                           # swept wings of three stepped feathers each
        for k, (L, y) in enumerate(((4.2, 20.6), (3.4, 19.8), (2.6, 19.0))):
            x0 = 8 + 0.7 * sign
            x1 = x0 + L * sign
            m.box(f"wing_{sign}_{k}", [min(x0, x1), y, 7.95], [max(x0, x1), y + 1.0, 8.05], vane,
                  ("z", 22.5 * sign, [x0, y, 8]))
    m.taper("tip", 22.2, 31.2, 1.9, 0.3, 0.7, sky, 6, edge=white, edge_w=0.3, ridge=glowtip)
    m.c("tip_point", 31.2, 32, 0.3, 0.3, white)
    return scaled_display(1.15)


def hydras_tri_edge(m, p, s, a):
    scale, venom, black = m.mat("scale", p), m.mat("glow", s, "#2E7F12"), m.mat("dark", a, p)
    edge, fang = m.mat("edge", "#9FE0BE"), m.mat("bone", "#EDE8D5", "#C9C2A8")
    m.grip(-4, 3, 1.5, black, scale)
    m.c("guard", 3, 4.4, 6, 1.8, scale)
    m.c("glow_guard_eye", 3.3, 4.1, 1.2, 1.9, venom)
    m.taper("root", 4.4, 9, 3.2, 2.6, 0.9, scale, 2)
    for i, (rot, dx) in enumerate(((-22.5, 1.2), (0, 0), (22.5, -1.2))):   # three serpent-headed prongs
        org = [8 + dx, 9, 8]
        y1 = 22 if rot == 0 else 19
        r = ("z", rot, org) if rot else None
        m.c(f"prong_{i}", 9, y1, 1.3, 0.8, scale, dx=dx, rot=r)
        m.c(f"prong_edge_{i}", 9.5, y1 - 0.3, 0.3, 0.85, edge, dx=dx + 0.5, rot=r)
        m.c(f"neck_{i}", y1 - 1.2, y1, 1.6, 1.1, scale, dx=dx, rot=r)
        m.c(f"skull_{i}", y1, y1 + 1.4, 1.9, 1.6, black, dx=dx, rot=r)
        m.c(f"snout_{i}", y1 + 1.4, y1 + 2.6, 1.3, 1.2, black, dx=dx, dz=0.1, rot=r)
        m.c(f"jaw_{i}", y1 + 0.4, y1 + 2.2, 1.1, 0.4, black, dx=dx, dz=-0.9, rot=r)
        m.c(f"fang_L_{i}", y1 + 1.8, y1 + 2.5, 0.25, 0.25, fang, dx=dx - 0.4, dz=-0.55, rot=r)
        m.c(f"fang_R_{i}", y1 + 1.8, y1 + 2.5, 0.25, 0.25, fang, dx=dx + 0.4, dz=-0.55, rot=r)
        m.c(f"glow_eyes_{i + 1}", y1 + 0.7, y1 + 1.15, 2.0, 0.35, venom, dx=dx, dz=0.45, rot=r)
        m.c(f"crest_{i}", y1 + 0.2, y1 + 1.2, 0.4, 1.0, edge, dx=dx, dz=0.9, rot=r)
    return DISPLAY


def undergloom_scythe(m, p, s, a):
    blade, bone, cord = m.mat("metal", p), m.mat("bone", s, "#B5AC93"), m.mat("wrap", a)
    edge = m.mat("glow", "#BFF5EC", p)                             # soul-light edge, animated
    spine = m.mat("dark", a, p)
    m.c("haft", -15, 24, 1.2, 1.2, bone)
    m.c("foot", -15.6, -14, 1.5, 1.5, cord)
    m.c("side_grip", 6, 7.2, 3.4, 0.9, cord, dx=1.4)
    for y in (-10, -2, 14):
        m.c(f"cord_{y}", y, y + 0.9, 1.5, 1.5, cord)
    m.c("socket", 22.4, 25.6, 2.2, 2.2, spine)
    m.c("socket_spike", 25.6, 27.4, 0.8, 0.8, spine)
    x, y = 7.0, 25.2                                               # crescent blade sweeping out over -x and down
    for i, (L, b, ang) in enumerate(((3.6, 2.6, 0), (3.6, 2.4, 22.5), (3.2, 2.0, 22.5), (2.8, 1.5, 45), (2.2, 0.9, 45))):
        rot = ("z", ang, [x, y, 8]) if ang else None
        m.box(f"blade_{i}", [x - L, y - b, 7.65], [x, y, 8.35], blade, rot)
        m.box(f"spine_{i}", [x - L, y - 0.35, 7.55], [x, y + 0.15, 8.45], spine, rot)
        m.box(f"glow_edge_{i}", [x - L, y - b - 0.4, 7.7], [x, y - b, 8.3], edge, rot)
        r = math.radians(ang)
        x, y = x - L * math.cos(r), y - L * math.sin(r)
    return scaled_display(1.05)


def sculkheart_dagger(m, p, s, a):
    blade, core, black = m.mat("dark", p, s), m.mat("glow", s, "#0E6E77"), m.mat("dark", a, p)
    edge, horn = m.mat("edge", "#6FB8BE"), m.mat("metal", "#1E5A60")
    # flared, fan-shaped pommel (two splayed wings) like a khanjar's
    m.box("pommel_wing_L", [6.2, -5.3, 7.4], [8.0, -4.3, 8.6], black, ("z", -22.5, [8, -4.3, 8]))
    m.box("pommel_wing_R", [8.0, -5.3, 7.4], [9.8, -4.3, 8.6], black, ("z", 22.5, [8, -4.3, 8]))
    m.c("pommel_cap", -4.6, -3.6, 2.0, 1.4, black)
    # waisted grip with two glowing sculk bosses
    m.c("grip_low", -3.6, -0.4, 1.35, 1.2, black)
    m.c("grip_waist", -0.4, 1.0, 1.1, 1.05, black)
    m.c("grip_high", 1.0, 3.0, 1.4, 1.2, black)
    disc(m, "boss_low", 8, -2.0, 1.5, 1.5, horn)
    disc(m, "glow_boss_low", 8, -2.0, 0.8, 1.62, core)
    disc(m, "boss_high", 8, 1.8, 1.5, 1.5, horn)
    disc(m, "glow_boss_high", 8, 1.8, 0.8, 1.62, core)
    m.c("collar", 3.0, 3.9, 2.2, 1.6, horn)
    # broad J-curved blade sweeping toward -x, glowing sculk vein down its spine
    m.taper("blade", 3.9, 13.0, 2.8, 1.0, 0.8, blade, 8, dx0=0.0, dx1=-3.2, edge=edge, edge_w=0.22, ridge=core, ridge_f=0.12)
    x, y = 8 - 3.2, 13.0
    m.box("hook_1", [x - 0.5, y - 0.1, 7.65], [x + 0.5, y + 1.8, 8.35], blade, ("z", 45, [x, y, 8]))
    m.box("hook_edge", [x + 0.2, y - 0.1, 7.6], [x + 0.5, y + 1.8, 8.4], edge, ("z", 45, [x, y, 8]))
    m.box("hook_tip", [x - 0.2, y + 1.7, 7.75], [x + 0.25, y + 2.6, 8.25], edge, ("z", 45, [x, y, 8]))
    return DISPLAY


def choirbreaker_gauntlets(m, p, s, a):
    chrome, red, black = m.mat("metal", p), m.mat("glow", s, "#6E0B18"), m.mat("dark", a, "#3A3A3A")
    m.c("cuff", -5, 0.6, 4.0, 4.0, black)
    for i, y in enumerate((-4.4, -2.6, -0.8)):                          # chrome servo rings around the cuff
        m.c(f"servo_{i}", y, y + 0.7, 4.4, 4.4, chrome)
    m.c("glow_cuff_line", -4, 0.2, 0.4, 4.1, red, dx=1.6)
    m.c("palm", 0.6, 5, 4.4, 3.2, black)
    m.c("back_plate", 1, 5.2, 4.6, 0.8, chrome, dz=-1.9)
    m.c("glow_emitter", 2.2, 4.0, 1.8, 0.3, red, dz=-2.4)                # sonic emitter on the back of the hand
    for i in range(4):
        x = -1.65 + i * 1.1
        m.c(f"knuckle_{i}", 5, 6.4, 0.95, 3.4, chrome, dx=x)
        m.c(f"finger_{i}", 3.6, 6.0, 0.9, 1.3, black, dx=x, dz=2.2)    # fingers curled into a fist
        m.c(f"glow_knuckle_{i}", 5.6, 6.0, 0.6, 0.2, red, dx=x, dz=-1.75)
    m.c("thumb", 2.4, 4.4, 1.0, 2.6, chrome, dx=2.6, dz=0.8)
    return worn_display()


def harbingers_railblade(m, p, s, a):
    gun, neon, hazard = m.mat("metal", p), m.mat("glow", s, "#127A06"), m.mat("wrap", a)
    dark = m.mat("dark", "#15191B", s)
    m.grip(-6, 2.5, 1.6, gun, gun)
    m.c("trigger_guard", -1, 2, 0.5, 1.2, gun, dx=1.3)
    m.c("housing", 2.5, 6, 4.6, 2.8, gun)
    m.c("battery", 2.9, 5.6, 1.4, 3.2, dark, dx=-1.0)
    m.c("glow_battery_cell", 3.3, 5.2, 0.8, 3.3, neon, dx=-1.0)
    for i in range(3):                                             # cooling vents
        m.c(f"vent_{i}", 3.1 + i * 0.9, 3.5 + i * 0.9, 1.6, 2.9, dark, dx=1.1)
    m.c("emitter_L", 6, 7, 1.3, 2.2, hazard, dx=-1.7)
    m.c("emitter_R", 6, 7, 1.3, 2.2, hazard, dx=1.7)
    m.c("rail_L", 6, 27.6, 0.9, 1.3, gun, dx=-1.35)
    m.c("rail_R", 6, 27.6, 0.9, 1.3, gun, dx=1.35)
    m.c("rail_edge_L", 6.5, 27, 0.25, 1.35, dark, dx=-1.9)
    m.c("rail_edge_R", 6.5, 27, 0.25, 1.35, dark, dx=1.9)
    m.c("glow_channel", 6.4, 27.2, 1.8, 0.5, neon)
    for y in (10, 15, 20, 24.5):                                   # hazard coils
        m.c(f"coil_{y}", y, y + 1.2, 4.0, 1.7, hazard)
        m.c(f"coil_core_{y}", y + 0.3, y + 0.9, 4.2, 1.8, dark)
    m.c("prong_L", 27.6, 30, 0.9, 1.2, gun, dx=-1.35)
    m.c("prong_R", 27.6, 30, 0.9, 1.2, gun, dx=1.35)
    m.c("glow_muzzle", 27.4, 28.6, 1.8, 0.7, neon)
    return scaled_display(0.82)


def abyssal_longbow(m, p, s, a):
    limb, veins, pearl = m.mat("dark", p, s), m.mat("glow", s, "#3D1170"), m.mat("bone", a, "#CFC4B6")
    m.c("grip", 5.6, 10.4, 1.9, 1.9, pearl)
    m.c("riser_up", 10.4, 11.6, 1.6, 1.4, limb)
    m.c("riser_down", 4.4, 5.6, 1.6, 1.4, limb)
    segs = [(3.0, 0), (3.2, 22.5), (3.2, 45), (2.4, 22.5), (1.8, -22.5)]   # recurve: flips forward at the tip
    tips = []
    for side, sign, y in (("up", 1, 11.6), ("down", -1, 4.4)):
        tx, ty = limb_chain(m, f"limb_{side}", 8, y, segs, 1.3, 1.1, limb, sign, glow=veins)
        tips.append((tx, ty))
        m.c(f"tip_{side}", ty - 0.6, ty + 0.6, 1.0, 1.0, pearl, dx=tx - 8)
    (tx, ty), (bx, by) = tips
    m.box("string", [tx - 0.1, by, 7.9], [tx + 0.1, ty, 8.1], pearl)
    return DISPLAY


def thornecutter(m, p, s, a):
    void, gold, grey = m.mat("dark", "#1C1924", s), m.mat("glow", s, "#4A3A10"), m.mat("metal", a)
    wrap, black = m.mat("wrap", "#1C1A22"), m.mat("dark", p, a)
    m.c("ring", -8, -6, 2.6, 2.6, gold)
    m.grip(-6, 3, 1.7, wrap, black)
    m.c("guard", 3, 4.6, 7.4, 2.0, black)
    m.c("guard_gem", 3.2, 4.4, 1.4, 2.2, gold)
    m.taper("blade", 4.6, 27, 4.6, 1.6, 1.2, void, 7, edge=grey, edge_w=0.4, ridge=gold)
    for side in (-1, 1):                                           # gold seams running up both faces
        m.c(f"glow_seam_F{side}", 5.4, 24, 0.3, 1.3, gold, dx=0.9 * side)
    m.c("chips", 12, 20, 0.45, 1.25, grey, dx=2.05)
    m.c("tip", 27, 29.4, 0.9, 0.9, grey)
    return scaled_display(1.0)


def emberhold_oathblade(m, p, s, a):
    white, crimson, flame, edge = m.mat("metal", p), m.mat("metal", s), m.mat("glow", a, s), m.mat("edge", "#FFFFFF")
    m.c("pommel", -5, -3.6, 2, 2, crimson)
    m.c("glow_pommel_gem", -4.6, -4.0, 0.8, 2.1, flame)
    m.grip(-3.6, 3, 1.5, m.mat("wrap", s))
    m.c("guard", 3, 4.3, 6.6, 1.8, crimson)
    m.c("guard_tip_L", 3.4, 5.0, 0.9, 1.4, crimson, dx=-3.4)
    m.c("guard_tip_R", 3.4, 5.0, 0.9, 1.4, crimson, dx=3.4)
    m.c("crest", 2.4, 5, 2.4, 2.2, crimson)
    m.taper("blade", 4.3, 22, 2.6, 1.8, 0.8, white, 5, edge=edge, ridge=flame)          # glowing fuller
    m.c("tip", 22, 24, 1.0, 0.7, white)
    for i, (y, h) in enumerate(((7, 3.6), (12, 4.2), (17, 3.0))):       # flame tongues licking off the edge
        x = 8.7                                                         # rooted inside the edge
        m.box(f"glow_flame_{i + 1}a", [x, y, 7.75], [x + 0.8, y + h, 8.25], flame, ("z", -22.5, [x, y, 8]))
        m.box(f"glow_flame_{i + 1}b", [x + 0.3, y + 0.6, 7.8], [x + 0.9, y + h * 0.65, 8.2], flame, ("z", -45, [x, y, 8]))
    return DISPLAY


SHAPES = {
    "frontier_cleaver": frontier_cleaver, "accord_longsword": accord_longsword, "gnawblade": gnawblade,
    "rootstring_bow": rootstring_bow, "thornwatch_halberd": thornwatch_halberd, "cogwright_breaker": cogwright_breaker,
    "prism_ward_staff": prism_ward_staff, "hollowbane_tachi": hollowbane_tachi, "cinder_crown": cinder_crown,
    "wroughtnaut_bulwark": wroughtnaut_bulwark, "skyreach_spear": skyreach_spear, "hydras_tri_edge": hydras_tri_edge,
    "undergloom_scythe": undergloom_scythe, "sculkheart_dagger": sculkheart_dagger,
    "choirbreaker_gauntlets": choirbreaker_gauntlets, "harbingers_railblade": harbingers_railblade,
    "abyssal_longbow": abyssal_longbow, "thornecutter": thornecutter, "emberhold_oathblade": emberhold_oathblade,
}


# ---------- output ----------
FACES = ("north", "east", "south", "west", "up", "down")


def face_rect(el, face):
    """(u0, v0, width, height) in model units of the face, on the material sheet (origin at -16, top at 32)."""
    (x0, y0, z0), (x1, y1, z1) = el["from"], el["to"]
    if face in ("north", "south"):
        return x0 + 16, 32 - y1, x1 - x0, y1 - y0
    if face in ("east", "west"):
        return z0 + 16, 32 - y1, z1 - z0, y1 - y0
    return x0 + 16, z0 + 16, x1 - x0, z1 - z0


def pack(sizes, side):
    """Shelf-pack (w, h) rects with 1 px padding into side x side. Returns positions or None."""
    order = sorted(range(len(sizes)), key=lambda i: -sizes[i][1])
    pos, x, y, shelf = [None] * len(sizes), 1, 1, 0
    for i in order:
        w, h = sizes[i]
        if x + w + 1 > side:
            x, y, shelf = 1, y + shelf + 2, 0
        if y + h + 1 > side:
            return None
        pos[i] = (x, y)
        x += w + 2
        shelf = max(shelf, h)
    return pos


def build(w):
    m = Model(w["id"])
    display = SHAPES[w["id"]](m, w["primary"], w["secondary"], w["accent"])
    animated = any(k in ANIMATED_KINDS for k, _, _ in m.mats)
    frames = ANIM_FRAMES if animated else 1
    seed = sum(ord(ch) for ch in w["id"])
    sheets = [[paint_sheet(mat, seed + 101 * i, f if mat[0] in ANIMATED_KINDS else 0, frames)
               for f in range(frames)] for i, mat in enumerate(m.mats)]

    faces = []                                                      # (element index, face, sheet rect px, size px)
    for ei, el in enumerate(m.els):
        for f in FACES:
            u, v, du, dv = face_rect(el, f)
            pw, ph = max(1, int(round(du * DENSITY))), max(1, int(round(dv * DENSITY)))
            sx = int(min(max(0, round(u * DENSITY)), SHEET - pw))
            sy = int(min(max(0, round(v * DENSITY)), SHEET - ph))
            faces.append((ei, f, sx, sy, pw, ph))
    side = 64
    while (pos := pack([(fc[4], fc[5]) for fc in faces], side)) is None:
        side *= 2
    tex = np.zeros((side * frames, side, 4), np.float32)
    for fr in range(frames):
        for (ei, f, sx, sy, pw, ph), (ax, ay) in zip(faces, pos):
            patch = sheets[m.els[ei]["m"]][fr][sy:sy + ph, sx:sx + pw].copy()
            if not m.els[ei]["name"].startswith("glow"):
                patch = bevel(patch, f)
            oy = fr * side
            tex[oy + ay:oy + ay + ph, ax:ax + pw, :3] = patch
            # 1 px bleed border so mipmaps and filtering never pick up a neighbour
            tex[oy + ay - 1, ax:ax + pw, :3] = patch[0]
            tex[oy + ay + ph, ax:ax + pw, :3] = patch[-1]
            tex[oy + ay - 1:oy + ay + ph + 1, ax - 1, :3] = tex[oy + ay - 1:oy + ay + ph + 1, ax, :3]
            tex[oy + ay - 1:oy + ay + ph + 1, ax + pw, :3] = tex[oy + ay - 1:oy + ay + ph + 1, ax + pw - 1, :3]
            tex[oy + ay - 1:oy + ay + ph + 1, ax - 1:ax + pw + 1, 3] = 255
    img = Image.fromarray(tex.astype(np.uint8), "RGBA")

    unit = side / 16.0                                              # px per UV unit
    elements = [{"name": el["name"], "from": el["from"], "to": el["to"], "faces": {}} for el in m.els]
    for (ei, f, sx, sy, pw, ph), (ax, ay) in zip(faces, pos):
        elements[ei]["faces"][f] = {"uv": [round(ax / unit, 4), round(ay / unit, 4), round((ax + pw) / unit, 4),
                                           round((ay + ph) / unit, 4)], "texture": "#0"}
    for e, el in zip(elements, m.els):
        if "rotation" in el:
            e["rotation"] = el["rotation"]
    model = {"credit": "Generated by tools/gen_models.py (Terrestrial Tribulations)", "texture_size": [side, side],
             "textures": {"0": "tt:item/" + w["id"] + "_3d", "particle": "tt:item/" + w["id"] + "_3d"},
             "elements": elements, "display": display}
    return m, model, img, frames, side


def write_outputs(w, model, tex, frames):
    os.makedirs(os.path.join(BB, "exports", "weapons"), exist_ok=True)
    os.makedirs(os.path.join(BB, "textures", "weapons"), exist_ok=True)
    with open(os.path.join(BB, "exports", "weapons", w["id"] + ".json"), "w", encoding="utf-8") as fh:
        json.dump(model, fh, indent=1)
        fh.write("\n")
    png = os.path.join(BB, "textures", "weapons", w["id"] + ".png")
    tex.save(png, optimize=True)
    meta = png + ".mcmeta"
    if frames > 1:
        with open(meta, "w", encoding="utf-8") as fh:
            json.dump({"animation": {"frametime": FRAMETIME, "interpolate": True}}, fh)
            fh.write("\n")
    elif os.path.exists(meta):
        os.remove(meta)


# ---------- preview renderer (orthographic, textured, painter's algorithm) ----------
def rot_point(pt, rotation):
    if not rotation:
        return pt
    ang = math.radians(rotation["angle"])
    ox, oy, oz = rotation["origin"]
    x, y, z = pt[0] - ox, pt[1] - oy, pt[2] - oz
    ca, sa = math.cos(ang), math.sin(ang)
    if rotation["axis"] == "x":
        y, z = y * ca - z * sa, y * sa + z * ca
    elif rotation["axis"] == "y":
        x, z = x * ca + z * sa, -x * sa + z * ca
    else:
        x, y = x * ca - y * sa, x * sa + y * ca
    return (x + ox, y + oy, z + oz)


def face_corners(el, f):
    """World corners matching UV (u0,v0), (u1,v0), (u0,v1), (u1,v1) the way Minecraft maps them."""
    (x0, y0, z0), (x1, y1, z1) = el["from"], el["to"]
    return {"south": [(x0, y1, z1), (x1, y1, z1), (x0, y0, z1), (x1, y0, z1)],
            "north": [(x1, y1, z0), (x0, y1, z0), (x1, y0, z0), (x0, y0, z0)],
            "east": [(x1, y1, z1), (x1, y1, z0), (x1, y0, z1), (x1, y0, z0)],
            "west": [(x0, y1, z0), (x0, y1, z1), (x0, y0, z0), (x0, y0, z1)],
            "up": [(x0, y1, z0), (x1, y1, z0), (x0, y1, z1), (x1, y1, z1)],
            "down": [(x0, y0, z1), (x1, y0, z1), (x0, y0, z0), (x1, y0, z0)]}[f]


SHADE = {"up": 1.0, "south": 0.9, "north": 0.7, "east": 0.78, "west": 0.62, "down": 0.5}


def render(model, tex, yaw, w=300, h=560, pitch=12, tilt=0, pad=15, bg=(34, 38, 46)):
    """Z-buffered render of frame 0: yaw in degrees around Y (0 = looking at the south face), then tilt about the
    view axis (-45 lays the weapon on the inventory diagonal). bg None gives a transparent background."""
    side = model["texture_size"][0]
    texa = np.asarray(tex.convert("RGB"), np.float32)[:side]
    unit = side / 16.0
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))

    def view(p):
        x, y, z = p[0] - 8, p[1] - 8, p[2] - 8
        x, z = x * cy + z * sy, -x * sy + z * cy
        y, z = y * cp - z * sp, y * sp + z * cp
        return x * ct - y * st, x * st + y * ct, z

    vs = [view(rot_point(p, el.get("rotation"))) for el in model["elements"] for f in FACES for p in face_corners(el, f)]
    xmin, xmax = min(v[0] for v in vs), max(v[0] for v in vs)
    ymin, ymax = min(v[1] for v in vs), max(v[1] for v in vs)
    sc = min((w - 2 * pad) / (xmax - xmin), (h - 2 * pad) / (ymax - ymin))
    xc, yc = (xmax + xmin) / 2, (ymax + ymin) / 2

    def proj(p):
        x, y, z = view(p)
        return np.array((w / 2 + (x - xc) * sc, h / 2 - (y - yc) * sc, z))

    img = np.zeros((h, w, 4), np.float32)
    img[:] = (bg or (0, 0, 0)) + (255 if bg else 0,)
    zbuf = np.full((h, w), -1e9, np.float32)
    for el in model["elements"]:
        glow = el["name"].startswith("glow")
        for f, fd in el["faces"].items():
            a, b, c, _ = [proj(rot_point(p, el.get("rotation"))) for p in face_corners(el, f)]
            e1, e2 = b - a, c - a
            det = e1[0] * e2[1] - e2[0] * e1[1]
            if abs(det) < 1e-3:
                continue
            xs = [a[0], b[0], c[0], b[0] + e2[0]]
            yv = [a[1], b[1], c[1], b[1] + e2[1]]
            x0, x1 = max(0, int(min(xs))), min(w - 1, int(max(xs)) + 1)
            y0, y1 = max(0, int(min(yv))), min(h - 1, int(max(yv)) + 1)
            if x0 > x1 or y0 > y1:
                continue
            Y, X = np.mgrid[y0:y1 + 1, x0:x1 + 1].astype(np.float32) + 0.5
            dx, dy = X - a[0], Y - a[1]
            s_ = (dx * e2[1] - dy * e2[0]) / det
            t_ = (e1[0] * dy - e1[1] * dx) / det
            inside = (s_ >= 0) & (s_ <= 1) & (t_ >= 0) & (t_ <= 1)
            z = a[2] + s_ * e1[2] + t_ * e2[2]
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            vis = inside & (z > sub)
            if not vis.any():
                continue
            u0, v0, u1, v1 = [q * unit for q in fd["uv"]]
            tu = np.clip((u0 + s_ * (u1 - u0)).astype(int), 0, side - 1)
            tv = np.clip((v0 + t_ * (v1 - v0)).astype(int), 0, side - 1)
            shade = 1.0 if glow else SHADE[f]
            sub[vis] = z[vis]
            img[y0:y1 + 1, x0:x1 + 1][vis] = np.concatenate(
                [texa[tv[vis], tu[vis]] * shade, np.full((int(vis.sum()), 1), 255, np.float32)], axis=1)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA")


def render_icon(model, tex, size=32):
    """Inventory icon: the 3D model on the sprite diagonal, supersampled, with a dark outline like vanilla items."""
    big = render(model, tex, 25, w=size * 4, h=size * 4, pitch=20, tilt=-45, pad=6, bg=None)
    small = big.resize((size, size), Image.BOX)
    a = np.asarray(small, np.float32).copy()
    solid = a[..., 3] > 110
    a[..., 3] = np.where(solid, 255, 0)
    near = np.zeros_like(solid)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        near |= np.roll(solid, (dy, dx), axis=(0, 1))
    edge = near & ~solid
    a[edge] = (24, 20, 28, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def main():
    data = json.load(open(os.path.join(ROOT, "design", "weapons", "weapons.json"), encoding="utf-8"))
    os.makedirs(os.path.join(BB, "previews"), exist_ok=True)
    tiles = []
    for w in data["weapons"]:
        if w["id"] not in SHAPES:
            continue
        m, model, tex, frames, side = build(w)
        write_outputs(w, model, tex, frames)
        icon = render_icon(model, tex)
        icon.save(os.path.join(BB, "textures", "weapons", w["id"] + "_icon.png"))
        pv = Image.new("RGBA", (600, 590), (28, 31, 38, 255))
        pv.paste(render(model, tex, 0), (0, 0))
        pv.paste(render(model, tex, 40), (300, 0))
        pv.paste(icon.resize((96, 96), Image.NEAREST), (496, 8), icon.resize((96, 96), Image.NEAREST))
        ImageDraw.Draw(pv).text((8, 568), f"{w['name']}  ({len(model['elements'])} elements, {side}px"
                                f"{', animated' if frames > 1 else ''})", fill=(230, 230, 230, 255))
        pv.save(os.path.join(BB, "previews", w["id"] + ".png"))
        tiles.append(pv.resize((300, 295), Image.LANCZOS))
        print(f"{w['id']}: {len(model['elements'])} elements, {len(m.mats)} materials, {side}px"
              f"{', animated' if frames > 1 else ''}")
    cols = 5
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGBA", (300 * cols, 295 * rows), (28, 31, 38, 255))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * 300, (i // cols) * 295))
    sheet.save(os.path.join(BB, "previews", "_sheet.png"))


if __name__ == "__main__":
    main()
