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
        scratch = (value_noise(seed + 9, 40, 40) > 0.86) & (fine > 0.6)
        out[scratch] = a * 1.35
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
        r = np.abs(fbm(seed + 11, 4, 4) - 0.5)
        crack = np.clip(1 - r / 0.045, 0, 1)
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


def bevel(patch):
    """Light the top/left rim and shade the bottom/right rim of a face patch."""
    h, w = patch.shape[:2]
    if w >= 3 and h >= 3:
        patch[0, :] *= 1.18
        patch[:, 0] *= 1.12
        patch[-1, :] *= 0.72
        patch[:, -1] *= 0.8
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

    def taper(self, name, y0, y1, w0, w1, d, m, steps, dx0=0.0, dx1=0.0, edge=None, edge_w=0.35):
        """Blade from width w0 at y0 to w1 at y1 in `steps` boxes, optionally drifting sideways (curve) and with
        bright edge strips on both sides."""
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

    def grip(self, y0, y1, r, m_wrap, m_cap=None):
        self.c("grip", y0, y1, r, r, m_wrap)
        if m_cap is not None:
            self.c("grip_cap", y0 - 1.2, y0, r + 0.8, r + 0.8, m_cap)


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


def frontier_cleaver(m, p, s, a):
    bone, sinew, flint = m.mat("bone", p, "#BFAF8F"), m.mat("wrap", s), m.mat("dark", a, "#9A9A9A")
    m.grip(-3, 3, 1.6, sinew, flint)
    m.c("lash", 2.6, 4.2, 3.2, 2.2, sinew)
    m.c("flint_wedge", 3, 5, 4.6, 1.6, flint)
    m.taper("blade", 5, 17, 3.2, 5.6, 1.1, bone, 6)               # wider at the tip than the base
    for i, y in enumerate((8.5, 11.5, 14.5)):                      # three knocked-out notches: dark chips on the edge
        m.c(f"notch_{i}", y, y + 0.9, 0.7, 1.2, flint, dx=2.6 + 0.35 * i)
    m.c("tip", 17, 18.2, 4.2, 1.0, bone, dx=0.6, rot=("z", 22.5, [8, 17, 8]))
    return DISPLAY


def accord_longsword(m, p, s, a):
    steel, edge, brass = m.mat("metal", STEEL), m.mat("edge", "#D8DEE4"), m.mat("metal", s)
    crimson, cloth = m.mat("flat", p), m.mat("wrap", a)
    m.grip(-5, 3, 1.5, cloth, brass)
    m.c("guard", 3, 4.4, 7, 1.8, brass)
    m.c("flame_L", 4.4, 7, 1.2, 1.2, brass, dx=-3.2, rot=("z", 22.5, [4.8, 4.4, 8]))
    m.c("flame_R", 4.4, 7, 1.2, 1.2, brass, dx=3.2, rot=("z", -22.5, [11.2, 4.4, 8]))
    m.taper("blade", 4.4, 27, 2.6, 1.8, 0.8, steel, 6, edge=edge)
    m.c("fuller", 5, 22, 0.6, 0.9, crimson)
    m.c("tip", 27, 29, 1.0, 0.7, edge)
    m.c("ribbon_a", -1, 3, 0.8, 0.3, crimson, dx=1.4, dz=1.0, rot=("z", 22.5, [9.4, 3, 9]))
    m.c("ribbon_b", -3.5, -0.5, 0.8, 0.3, crimson, dx=2.5, dz=1.0, rot=("z", 22.5, [10.5, -0.5, 9]))
    return scaled_display(0.85)


def gnawblade(m, p, s, a):
    blade, edge = m.mat("metal", p), m.mat("edge", "#C9C2B6")
    wrap, bone, tail = m.mat("wrap", s), m.mat("bone", "#E6DECB", "#B8AE98"), m.mat("flat", a)
    m.c("skull", -3.6, -1.2, 2.6, 2.6, bone)
    m.c("skull_snout", -2.8, -1.8, 1.2, 1.4, bone, dz=1.6)
    m.c("eye_L", -2.4, -2.0, 0.5, 0.2, tail, dx=-0.6, dz=1.31)
    m.c("eye_R", -2.4, -2.0, 0.5, 0.2, tail, dx=0.6, dz=1.31)
    m.c("tail_loop", -6, -3.6, 0.4, 0.4, tail, dx=1.2, rot=("z", 22.5, [9.2, -3.6, 8]))
    m.grip(-1.2, 3, 1.5, wrap)
    m.c("guard", 3, 3.8, 3.2, 1.4, blade)
    m.taper("blade", 3.8, 11.5, 2.4, 1.6, 0.8, blade, 4, edge=edge)
    for i, y in enumerate((6, 8, 10)):                             # chisel teeth
        m.c(f"tooth_{i}", y, y + 0.9, 0.8, 0.8, edge, dx=1.5)
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
    m.c("foot", -14, -12.6, 1.6, 1.6, gold)
    m.c("shaft", -12.6, 21, 1.2, 1.2, ivory)
    m.c("collar", 21, 22.4, 2.4, 2.4, gold)
    for i, (dx, dz) in enumerate(((-2.2, 0), (2.2, 0), (0, -2.2), (0, 2.2))):   # four bowed cage bars
        m.c(f"bar_low_{i}", 22.4, 25, 0.5, 0.5, gold, dx=dx * 0.7, dz=dz * 0.7)
        m.c(f"bar_mid_{i}", 25, 28, 0.5, 0.5, gold, dx=dx, dz=dz)
        m.c(f"bar_top_{i}", 28, 30.6, 0.5, 0.5, gold, dx=dx * 0.7, dz=dz * 0.7)
    m.c("crown", 30.6, 31.6, 2.6, 2.6, gold)
    m.c("prism", 24.6, 28.4, 1.9, 1.9, prism, rot=("y", 45, [8, 26.5, 8]))
    m.c("glow_prism", 25.4, 27.6, 1.0, 1.0, glowp, rot=("y", 45, [8, 26.5, 8]))
    return scaled_display(1.05)


def hollowbane_tachi(m, p, s, a):
    lacquer, hamon, silver = m.mat("dark", p, s), m.mat("glow", s, "#3B1677"), m.mat("metal", a)
    wrap = m.mat("wrap", "#2A2530")
    m.grip(-7, 3, 1.4, wrap, silver)
    m.c("tsuba", 3, 3.7, 3.6, 3.6, silver)
    m.c("habaki", 3.7, 4.8, 1.6, 1.2, silver)
    m.taper("blade", 4.8, 29, 1.7, 1.2, 0.6, lacquer, 8, dx0=0, dx1=-2.6)   # curved single edge
    for i in range(4):                                             # hamon line along the edge, following the curve
        t0, t1 = i / 4, (i + 1) / 4
        y0, y1 = 4.8 + 24.2 * t0, 4.8 + 24.2 * t1
        dx = -2.6 * ((t0 + t1) / 2) ** 2
        m.c(f"glow_hamon_{i + 1}", y0, y1 + 0.01, 0.35, 0.65, hamon, dx=dx + 0.55)
    m.c("kissaki", 29, 30.5, 0.9, 0.55, lacquer, dx=-2.8, rot=("z", 22.5, [5.2, 29, 8]))
    return scaled_display(0.8)


def cinder_crown(m, p, s, a):
    obsidian, veins, magma = m.mat("dark", p, s), m.mat("veins", p, s), m.mat("glow", a, s)
    grip = m.mat("wrap", "#2B1A1F")
    m.c("pommel", -7, -5.4, 2.4, 2.4, obsidian)
    m.grip(-5.4, 3, 1.7, grip)
    m.c("guard", 3, 4.8, 8, 2.4, obsidian)
    for i, dx in enumerate((-3.2, -1.6, 0, 1.6, 3.2)):             # crown of five spikes
        m.c(f"spike_{i}", 4.8, 7 + (1.2 if dx == 0 else 0), 0.9, 0.9, magma, dx=dx)
    m.taper("blade", 4.8, 26, 6.2, 5.4, 1.4, obsidian, 4)
    m.c("glow_cracks_F", 6, 25, 5.4, 0.02, veins, dz=0.72)
    m.c("glow_cracks_B", 6, 25, 5.4, 0.02, veins, dz=-0.72)
    m.c("tip", 26, 28.4, 4.0, 1.2, obsidian)
    return scaled_display(1.0)


def wroughtnaut_bulwark(m, p, s, a):
    iron, rust, rivet = m.mat("metal", p), m.mat("dark", s, "#C46A4E"), m.mat("metal", a)
    edge, handle = m.mat("edge", "#A9AEB3"), m.mat("wood", "#3B2E25", "#251C16")
    m.c("haft", -8, 22, 1.4, 1.4, handle)
    m.c("pommel", -9.4, -8, 2, 2, iron)
    m.c("plate", 9, 24, 7.5, 1.3, iron, dx=3.6)
    m.c("rust_streak", 10, 21, 2, 1.32, rust, dx=2.2)
    m.c("edge", 9.6, 23.4, 0.8, 1.4, edge, dx=7.6)
    for r in range(3):
        for col in range(3):
            m.c(f"rivet_{r}_{col}", 12 + r * 3.5, 12.8 + r * 3.5, 0.8, 1.6, rivet, dx=1.5 + col * 2.1)
    m.c("cap", 22, 23.6, 2.2, 2.2, iron)
    return scaled_display(0.95)


def skyreach_spear(m, p, s, a):
    shaft, gold, vane, white = m.mat("metal", s), m.mat("metal", "#E8D27A"), m.mat("feather", p, a), m.mat("edge", a)
    glowtip = m.mat("glow", s, "#C9B25E")
    m.c("butt", -15, -13.6, 1.3, 1.3, gold)
    m.c("shaft", -13.6, 20, 0.9, 0.9, shaft)
    for y in (-4, 4, 12):
        m.c(f"wrap_{y}", y, y + 1.0, 1.2, 1.2, white)
    m.c("collar", 20, 21.4, 1.8, 1.8, gold)
    for i, sign in enumerate((-1, 1)):                             # two pairs of feather vanes
        m.c(f"vane_{i}_a", 17, 21, 2.4, 0.01, vane, dx=1.6 * sign, rot=("z", 22.5 * sign, [8, 21, 8]))
        m.c(f"vane_{i}_b", 17, 21, 0.01, 2.4, vane, dz=1.6 * sign, rot=("x", -22.5 * sign, [8, 21, 8]))
    m.taper("tip", 21.4, 31.5, 1.3, 0.3, 0.6, white, 5)
    m.c("glow_tip", 27, 31.6, 0.3, 0.3, glowtip)
    return scaled_display(1.15)


def hydras_tri_edge(m, p, s, a):
    scale, venom, black = m.mat("scale", p), m.mat("glow", s, "#2E7F12"), m.mat("dark", a, p)
    edge = m.mat("edge", "#9FE0BE")
    m.grip(-4, 3, 1.5, black, scale)
    m.c("guard", 3, 4.4, 6, 1.8, scale)
    m.taper("root", 4.4, 9, 3.2, 2.6, 0.9, scale, 2)
    for i, (rot, dx) in enumerate(((-22.5, 1.2), (0, 0), (22.5, -1.2))):   # three prongs
        org = [8 + dx, 9, 8]
        y1 = 22 if rot == 0 else 19
        m.c(f"prong_{i}", 9, y1, 1.3, 0.8, scale, dx=dx, rot=("z", rot, org) if rot else None)
        m.c(f"prong_edge_{i}", 9.5, y1 - 0.3, 0.3, 0.85, edge, dx=dx + 0.5, rot=("z", rot, org) if rot else None)
        m.c(f"head_{i}", y1, y1 + 1.6, 1.8, 1.4, black, dx=dx, rot=("z", rot, org) if rot else None)
        m.c(f"glow_eyes_{i + 1}", y1 + 0.6, y1 + 1.1, 1.9, 0.3, venom, dx=dx, dz=0.6, rot=("z", rot, org) if rot else None)
    return DISPLAY


def undergloom_scythe(m, p, s, a):
    blade, bone, cord, edge = m.mat("metal", p), m.mat("bone", s, "#B5AC93"), m.mat("wrap", a), m.mat("edge", "#9FD3CB")
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
        m.box(f"edge_{i}", [x - L, y - b - 0.4, 7.7], [x, y - b, 8.3], edge, rot)
        r = math.radians(ang)
        x, y = x - L * math.cos(r), y - L * math.sin(r)
    return scaled_display(1.05)


def sculkheart_dagger(m, p, s, a):
    glass, core, black = m.mat("dark", p, s), m.mat("glow", s, "#0E6E77"), m.mat("dark", a, p)
    m.grip(-3, 3, 1.4, black, black)
    for i, (dx, rot) in enumerate(((-1.6, 22.5), (1.6, -22.5), (-1.0, 45), (1.0, -45))):   # sculk tendril guard
        m.c(f"tendril_{i}", 3, 5.2, 0.5, 0.5, black, dx=dx, rot=("z", rot, [8 + dx, 3, 8]))
    m.taper("blade", 3.4, 12.5, 2.4, 1.0, 0.9, glass, 4)
    m.c("glow_core", 3.6, 11.4, 0.6, 1.0, core)
    return DISPLAY


def choirbreaker_gauntlets(m, p, s, a):
    chrome, red, black = m.mat("metal", p), m.mat("glow", s, "#6E0B18"), m.mat("dark", a, "#3A3A3A")
    for i in range(3):                                             # wrist servo rings
        m.c(f"servo_{i}", -3 + i * 1.3, -2 + i * 1.3, 3.6, 3.6, black)
    m.c("plate_back", 1, 5, 4.4, 0.8, chrome, dz=2.3)
    m.c("plate_front", 4, 6, 4.6, 4.2, chrome)
    for i in range(4):                                             # knuckle ridges
        m.c(f"ridge_{i}", 6, 6.8, 0.8, 1.2, chrome, dx=-1.7 + i * 1.13, dz=1.4)
    m.c("glow_emitter_1", 2, 3.2, 1.2, 0.4, red, dx=-1, dz=2.75)
    m.c("glow_emitter_2", 2, 3.2, 1.2, 0.4, red, dx=1, dz=2.75)
    return DISPLAY


def harbingers_railblade(m, p, s, a):
    gun, neon, hazard = m.mat("metal", p), m.mat("glow", s, "#127A06"), m.mat("wrap", a)
    m.grip(-6, 2.5, 1.6, gun, gun)
    m.c("housing", 2.5, 5.5, 4.4, 2.6, gun)
    m.c("emitter_L", 5.5, 6.5, 1.2, 2.0, hazard, dx=-1.6)
    m.c("emitter_R", 5.5, 6.5, 1.2, 2.0, hazard, dx=1.6)
    m.c("rail_L", 5.5, 28, 0.9, 1.2, gun, dx=-1.25)
    m.c("rail_R", 5.5, 28, 0.9, 1.2, gun, dx=1.25)
    m.c("glow_channel", 6, 27.5, 1.6, 0.5, neon)
    for y in (10, 16, 22):                                         # hazard coils
        m.c(f"coil_{y}", y, y + 1.2, 3.8, 1.6, hazard)
    m.c("tip", 28, 29.5, 3.4, 1.2, gun)
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
    m.taper("blade", 4.6, 27, 4.6, 1.6, 1.2, void, 7, edge=grey, edge_w=0.4)
    for side in (-1, 1):                                           # gold seams running up both faces
        m.c(f"glow_seam_F{side}", 5.4, 24, 0.3, 1.3, gold, dx=0.9 * side)
    m.c("glow_core", 5.4, 22, 0.5, 1.28, gold)
    m.c("chips", 12, 20, 0.45, 1.25, grey, dx=2.05)
    m.c("tip", 27, 29.4, 0.9, 0.9, grey)
    return scaled_display(1.0)


def emberhold_oathblade(m, p, s, a):
    white, crimson, flame, edge = m.mat("metal", p), m.mat("metal", s), m.mat("glow", a, "#FFD9A0"), m.mat("edge", "#FFFFFF")
    m.c("pommel", -5, -3.6, 2, 2, crimson)
    m.grip(-3.6, 3, 1.5, m.mat("wrap", s))
    m.c("guard", 3, 4.3, 6.6, 1.8, crimson)
    m.c("crest", 2.4, 5, 2.4, 2.2, crimson)
    m.taper("blade", 4.3, 22, 2.6, 1.8, 0.8, white, 5, edge=edge)
    m.c("tip", 22, 24, 1.0, 0.7, white)
    for i, (y, h) in enumerate(((8, 3.2), (13, 4.0), (18, 2.8))):  # white flame tongues along the edge
        m.c(f"glow_flame_{i + 1}", y, y + h, 0.7, 0.6, flame, dx=1.7, rot=("z", -22.5, [9.4, y, 8]))
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
                patch = bevel(patch)
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
