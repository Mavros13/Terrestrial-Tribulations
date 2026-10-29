"""Paints a 64x64 player skin for each story NPC (owner, 2026-10-29: "we need custom skins for each npc").
Looks come from the **Look:** lines in design/npcs/*.md. Output: pack/kubejs/assets/tt/textures/entity/npc/<npc>.png,
used by gen_npcs.py through Easy NPC's RESOURCE_LOCATION skin type (SkinData {Type, Texture}; added in Easy NPC 7.8).
Also writes blockbench/previews/npc-skins.png (front and back of every skin, 4x) for review. Run by build_prism.py.

Standard skin layout (1.8+): each part is a box unwrapped as top/bottom on the first row and right/front/left/back
below; the second layer (hat, jacket, sleeves, trousers) sits at its own offset. Slim models have 3-pixel arms."""
import os, random
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "pack", "kubejs", "assets", "tt", "textures", "entity", "npc")
PREVIEW = os.path.join(ROOT, "blockbench", "previews", "npc-skins.png")

# part: (base u, v, overlay u, v, width, height, depth); arm width is 3 for slim skins
PARTS = {"head": (0, 0, 32, 0, 8, 8, 8), "body": (16, 16, 16, 32, 8, 12, 4),
         "rarm": (40, 16, 40, 32, 4, 12, 4), "larm": (32, 48, 48, 48, 4, 12, 4),
         "rleg": (0, 16, 0, 32, 4, 12, 4), "lleg": (16, 48, 0, 48, 4, 12, 4)}


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (c[3],)


class Skin:
    def __init__(self, slim, seed):
        self.img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        self.slim = slim
        self.rng = random.Random(seed)

    def faces(self, part, overlay=False):
        bu, bv, ou, ov, w, h, d = PARTS[part]
        if part in ("rarm", "larm") and self.slim:
            w = 3
        u, v = (ou, ov) if overlay else (bu, bv)
        return {"top": (u + d, v, w, d), "bottom": (u + d + w, v, w, d), "right": (u, v + d, d, h),
                "front": (u + d, v + d, w, h), "left": (u + d + w, v + d, d, h), "back": (u + d + w + d, v + d, w, h)}

    def px(self, part, face, x, y, color, overlay=False, noise=0.06):
        fx, fy, fw, fh = self.faces(part, overlay)[face]
        if 0 <= x < fw and 0 <= y < fh and color is not None:
            c = hexc(color) if isinstance(color, str) else color
            if noise:
                c = shade(c, 1 + self.rng.uniform(-noise, noise))
            self.img.putpixel((fx + x, fy + y), c)

    def fill(self, part, fn, overlay=False, faces=("top", "bottom", "right", "front", "left", "back"), noise=0.06):
        """fn(face, x, y, w, h) -> colour or None, for every pixel of the chosen faces."""
        for face in faces:
            _, _, fw, fh = self.faces(part, overlay)[face]
            for y in range(fh):
                for x in range(fw):
                    self.px(part, face, x, y, fn(face, x, y, fw, fh), overlay, noise)

    def side_width(self, part, face):
        return self.faces(part)[face][2]


def bands(rows, default=None):
    """Colour by row (from the top of a side face): rows = [(last_row_inclusive, colour), ...]."""
    def colour(y):
        for last, c in rows:
            if y <= last:
                return c
        return default
    return colour


def paint_base(s, k):
    """Head, torso, arms and legs from a look dictionary k."""
    skin, hair = k["skin"], k.get("hair")
    # head: skin, hair on top/back/sides down to hair_len rows, face on the front
    hl = k.get("hair_len", 2)

    def strand(x, y):
        """Hair with strands: every third column a shade darker, scattered highlights."""
        c = hexc(hair)
        if (x + (y // 3)) % 3 == 0:
            return shade(c, 0.82)
        if (x * 5 + y * 3) % 11 == 0:
            return shade(c, 1.18)
        return c

    def head(face, x, y, w, h):
        if face == "top":
            return strand(x, y) if hair else skin
        if face == "bottom":
            return shade(hexc(skin), 0.8)
        if hair and face == "back" and y < k.get("hair_back", 6):
            return strand(x, y)
        if hair and face in ("left", "right") and (y < hl + 1 or (y < k.get("hair_back", 6) and
                                                                    ((face == "right" and x < 3) or (face == "left" and x > 4)))):
            return strand(x, y)
        if hair and face == "front" and (y < hl or (y == hl and x in (0, 7))):
            return strand(x, y)
        return skin
    s.fill("head", head)
    f = lambda x, y, c: s.px("head", "front", x, y, c, noise=0)
    eye_white, eye = k.get("eye_white", "#EDEDED"), k.get("eyes", "#3B2A1A")
    for x0 in (1, 5):
        f(x0, 4, eye_white if x0 == 1 else eye)
        f(x0 + 1, 4, eye if x0 == 1 else eye_white)
        f(x0, 5, shade(hexc(skin), 0.93))               # soft shadow under the eyes
        f(x0 + 1, 5, shade(hexc(skin), 0.93))
    if k.get("cheeks"):
        f(1, 5, k["cheeks"])
        f(6, 5, k["cheeks"])
    f(1, 3, shade(hexc(hair or skin), 0.8))   # brows
    f(2, 3, shade(hexc(hair or skin), 0.8))
    f(5, 3, shade(hexc(hair or skin), 0.8))
    f(6, 3, shade(hexc(hair or skin), 0.8))
    f(3, 5, shade(hexc(skin), 0.85))          # nose
    f(4, 5, shade(hexc(skin), 0.85))
    for x in (3, 4):
        f(x, 6, k.get("mouth", shade(hexc(skin), 0.62)))
    if k.get("beard"):
        for x in range(8):
            for y in (5, 6, 7) if x in (0, 1, 6, 7) else (6, 7) if x in (2, 5) else (7,):
                f(x, y, k["beard"])
        for face in ("left", "right"):
            for x in range(8):
                for y in (6, 7):
                    if (face == "right" and x > 4) or (face == "left" and x < 3):
                        s.px("head", face, x, y, k["beard"])
    if k.get("wrinkles"):
        f(0, 5, shade(hexc(skin), 0.88))
        f(7, 5, shade(hexc(skin), 0.88))
        f(1, 2, shade(hexc(skin), 0.9))
        f(6, 2, shade(hexc(skin), 0.9))

    # torso: rows of clothing, belt
    torso = bands(k["torso"])
    s.fill("body", lambda face, x, y, w, h: torso(y) if face not in ("top", "bottom") else
           (torso(0) if face == "top" else torso(11)))
    # arms: sleeve rows then hand
    for arm in ("rarm", "larm"):
        sleeve = k.get("sleeve", 7)
        hand = k.get("hands", skin)
        if arm == "larm" and k.get("left_hand"):
            hand = k["left_hand"]
        acol = bands([(sleeve, k["arm"]), (11, hand)])
        s.fill(arm, lambda face, x, y, w, h, acol=acol, hand=hand: acol(y) if face not in ("top", "bottom")
               else (k["arm"] if face == "top" else hand))
        if sleeve < 11:
            for face in ("right", "front", "left", "back"):
                for x in range(s.side_width(arm, face)):
                    s.px(arm, face, x, sleeve, shade(hexc(k["arm"]), 0.75))
    # legs
    legs = bands(k["legs"])
    for leg in ("rleg", "lleg"):
        s.fill(leg, lambda face, x, y, w, h: legs(y) if face not in ("top", "bottom")
               else (legs(0) if face == "top" else shade(hexc(legs(11)), 0.7)))
        boot_top = next((last for last, c in k["legs"] if c == k["legs"][-1][1]), None)
        top_row = max([last for last, c in k["legs"][:-1]] or [8]) + 1
        for face in ("right", "front", "left", "back"):
            for x in range(4):
                s.px(leg, face, x, 11, shade(hexc(k["legs"][-1][1]), 0.6))      # sole
                if top_row <= 10:
                    s.px(leg, face, x, top_row, shade(hexc(k["legs"][-1][1]), 1.22))  # boot cuff
    for arm in ("rarm", "larm"):
        if k.get("sleeve", 7) < 10:
            for x in range(s.side_width(arm, "front")):
                s.px(arm, "front", x, 11, shade(hexc(k.get("hands", skin) if arm == "rarm" or not k.get("left_hand")
                                                     else k["left_hand"]), 0.86))


def finish(s):
    """Volume: a soft top-to-bottom gradient on every side face, darker outer columns, and a neck shadow."""
    img = s.img
    for part in ("body", "rarm", "larm", "rleg", "lleg"):
        for overlay in (False, True):
            for face, (fx, fy, fw, fh) in s.faces(part, overlay).items():
                if face in ("top", "bottom"):
                    continue
                for y in range(fh):
                    for x in range(fw):
                        c = img.getpixel((fx + x, fy + y))
                        if c[3] == 0:
                            continue
                        f = 1.05 - 0.12 * y / (fh - 1)
                        if face in ("front", "back") and x in (0, fw - 1):
                            f *= 0.9
                        if face in ("left", "right"):
                            f *= 0.95
                        img.putpixel((fx + x, fy + y), shade(c, f))
    fx, fy, fw, fh = s.faces("body")["front"]
    for x in range(1, fw - 1):
        img.putpixel((fx + x, fy), shade(img.getpixel((fx + x, fy)), 0.85))


# ---------- the cast ----------
def maera(s):
    k = {"skin": "#C9946B", "hair": "#A7A9AC", "hair_len": 2, "hair_back": 8, "eyes": "#5A4632", "wrinkles": True,
         "torso": [(11, "#3B2E2A")], "arm": "#3B2E2A", "sleeve": 8, "legs": [(9, "#3B2E2A"), (11, "#4A3424")]}
    paint_base(s, k)
    crimson, brass = "#A3212A", "#D8A93A"
    # crimson shawl over the shoulders and down the front in a V (jacket layer)
    s.fill("body", lambda face, x, y, w, h: crimson if (y < 3 or (face == "front" and y < 7 - abs(x - 3.5) * 1.2)
                                                         or (face == "back" and y < 6)) else None,
           overlay=True, faces=("top", "right", "front", "left", "back"))
    for x, y in ((1, 2), (6, 2)):
        s.px("body", "front", x, y, brass, overlay=True, noise=0)
    for arm in ("rarm", "larm"):
        s.fill(arm, lambda face, x, y, w, h: crimson if y < 3 else None, overlay=True,
               faces=("top", "right", "front", "left", "back"))
    # two ash-grey braids falling over the shoulders (hat layer on the head sides, then the jacket front)
    for x in (0, 7):
        for y in range(6):
            s.px("body", "front", x, y, "#9A9C9F" if y % 2 else "#B9BBBE", overlay=True)
    s.px("body", "front", 0, 6, crimson, overlay=True, noise=0)
    s.px("body", "front", 7, 6, crimson, overlay=True, noise=0)
    s.fill("head", lambda face, x, y, w, h: "#A7A9AC" if face == "top" or (face != "bottom" and y < 1) else None,
           overlay=True)


def doran(s):
    k = {"skin": "#6B4A35", "hair": "#1E1A18", "hair_len": 1, "hair_back": 4, "beard": "#1E1A18", "eyes": "#2A1E14",
         "torso": [(11, "#2B2724")], "arm": "#2B2724", "sleeve": 1, "legs": [(8, "#3A332D"), (11, "#1F1A16")]}
    paint_base(s, k)
    leather = "#6E4526"
    s.fill("body", lambda face, x, y, w, h: leather if face == "front" and (y > 1 or x in (1, 2, 5, 6)) else
           ("#4A2E18" if face in ("left", "right") and y == 7 else None), overlay=True,
           faces=("front", "left", "right"))
    for x in range(8):
        s.px("body", "front", x, 7, "#4A2E18", overlay=True)
    for leg in ("rleg", "lleg"):
        s.fill(leg, lambda face, x, y, w, h: leather if face == "front" and y < 7 else None, overlay=True,
               faces=("front",))
    # ember-orange tattoos on the forearms, soot on the face
    for arm in ("rarm", "larm"):
        for face in ("front", "right", "left"):
            for y in (3, 5, 7):
                for x in range(s.side_width(arm, face)):
                    if (x + y) % 3 == 0:
                        s.px(arm, face, x, y, "#F07A1A", noise=0.15)
    for x, y in ((0, 4), (6, 2), (7, 3), (1, 6)):
        s.px("head", "front", x, y, "#3E2C21")


def rhosk(s):
    green, bronze, dark = "#3F6B34", "#B0813B", "#24401F"
    k = {"skin": "#C08A62", "hair": "#4A3423", "hair_len": 1, "hair_back": 5, "eyes": "#2F4A2A",
         "beard": None, "torso": [(0, bronze), (9, green), (10, bronze), (11, green)], "arm": green, "sleeve": 8,
         "hands": "#5A4632", "legs": [(5, green), (6, bronze), (8, dark), (11, "#3A2A1C")]}
    paint_base(s, k)
    for x in range(8):                                     # breastplate trim and a centre ridge
        s.px("body", "front", x, 4, bronze)
    for y in range(1, 10):
        s.px("body", "front", 3, y, shade(hexc(green), 1.2))
        s.px("body", "front", 4, y, shade(hexc(green), 1.2))
    for arm in ("rarm", "larm"):                           # bronze pauldrons
        s.fill(arm, lambda face, x, y, w, h: bronze if y < 3 or face == "top" else None, overlay=True,
               faces=("top", "right", "front", "left", "back"))
    # dark green cloak on the back with a thorn sigil
    s.fill("body", lambda face, x, y, w, h: dark if face == "back" else None, overlay=True, faces=("back",))
    for x, y in ((3, 3), (4, 3), (3, 4), (4, 5), (3, 6), (4, 7), (2, 5), (5, 4), (1, 4), (6, 6)):
        s.px("body", "back", x, y, bronze, overlay=True, noise=0)
    s.px("head", "front", 2, 6, "#3A2A1C")                 # scar


def pell(s):
    copper, coat = "#C4622D", "#9C7A4F"
    k = {"skin": "#E2B48F", "hair": copper, "hair_len": 2, "hair_back": 6, "eyes": "#3F6A3A",
         "torso": [(11, coat)], "arm": coat, "sleeve": 8, "left_hand": "#C9A23A", "legs": [(8, "#4A4036"), (11, "#3A2A1C")]}
    paint_base(s, k)
    for face in ("front", "left", "right", "back"):        # frizzy hair spills over the hat layer
        s.fill("head", lambda f, x, y, w, h: (copper if (y < 2 or (y < 3 and (x + y) % 2)) else None),
               overlay=True, faces=(face,))
    s.fill("head", lambda f, x, y, w, h: copper, overlay=True, faces=("top",))
    for x in range(8):                                     # goggles strap and lenses pushed up
        s.px("head", "front", x, 1, "#3A2A1C", overlay=True, noise=0)
    for x in (1, 2, 5, 6):
        s.px("head", "front", x, 1, "#7FC9D6", overlay=True, noise=0)
    for face in ("left", "right", "back"):
        for x in range(8):
            s.px("head", face, x, 1, "#3A2A1C", overlay=True, noise=0)
    for x0, y0 in ((0, 3), (5, 3), (0, 7), (5, 7), (2, 9)):  # pockets everywhere
        for dx in range(3):
            for dy in range(2):
                s.px("body", "front", x0 + dx, y0 + dy, "#7A5C38")
    for y in range(12):
        s.px("body", "front", 3 + (y % 2), y, "#6B5032")
    for face in ("front", "right", "left", "back"):        # brass hand rivets
        s.px("larm", face, 1, 10, "#7A5E1E", noise=0)


def tamsin(s):
    bark, moss = "#6A4A30", "#4E7A2E"
    k = {"skin": bark, "hair": "#2E4A1E", "hair_len": 2, "hair_back": 8, "eyes": "#9BD06A",
         "torso": [(11, "#5A4430")], "arm": bark, "sleeve": -1, "legs": [(9, "#4A3A28"), (11, "#3A2A1C")]}
    paint_base(s, k)
    for part in ("head", "rarm", "larm"):                  # green spiral paint
        for face in ("front", "left", "right"):
            for (x, y) in ((1, 1), (2, 1), (2, 2), (1, 3), (0, 2)) if part != "head" else ((0, 6), (7, 6), (7, 7)):
                s.px(part, face, x, y + (5 if part != "head" else 0), "#7BC043", noise=0.1)
    # cloak of living moss over shoulders and back
    s.fill("body", lambda face, x, y, w, h: (moss if (face in ("back", "top") or y < 2 or
                                                      (face in ("left", "right") and y < 9)) and
                                             s.rng.random() > 0.08 else None),
           overlay=True, faces=("top", "right", "front", "left", "back"))
    for arm in ("rarm", "larm"):
        s.fill(arm, lambda face, x, y, w, h: moss if y < 2 else None, overlay=True,
               faces=("top", "right", "front", "left", "back"))
    for y in range(12):                                    # bow string across the chest
        s.px("body", "front", min(7, y * 2 // 3), y, "#C9B98A", overlay=True, noise=0)


def ilsabet(s):
    violet, white, silver = "#6A3FA0", "#E8E2F2", "#C9CED6"
    k = {"skin": "#EDD9CC", "hair": "#E9E4D8", "hair_len": 2, "hair_back": 9, "eyes": "#6A4FB0",
         "torso": [(11, violet)], "arm": violet, "sleeve": 9, "hands": "#EDD9CC",
         "legs": [(10, violet), (11, "#3A2A4A")]}
    paint_base(s, k)
    # robes fade from violet to white
    for part in ("body", "rleg", "lleg", "rarm", "larm"):
        offset = 0 if part in ("body", "rarm", "larm") else 12
        def grad(face, x, y, w, h, offset=offset, part=part):
            if part in ("rarm", "larm") and y > 9:
                return None
            t = (y + offset) / 23
            c1, c2 = hexc(violet), hexc(white)
            return tuple(int(c1[i] + (c2[i] - c1[i]) * t * 0.85) for i in range(3)) + (255,)
        s.fill(part, grad, faces=("right", "front", "left", "back"))
    for x in range(8):                                     # silver circlet with a violet gem
        s.px("head", "front", x, 1, silver, overlay=True, noise=0)
    s.px("head", "front", 3, 1, "#B07CFF", overlay=True, noise=0)
    s.px("head", "front", 4, 1, "#B07CFF", overlay=True, noise=0)
    for face in ("left", "right", "back"):
        for x in range(8):
            s.px("head", face, x, 1, silver, overlay=True, noise=0)
    for arm in ("rarm", "larm"):                           # ink-stained fingers
        s.px(arm, "front", 0, 11, "#1E1A3A", noise=0)
        s.px(arm, "front", 1, 11, "#1E1A3A", noise=0)
    for y in range(12):                                    # gold trim down the front
        s.px("body", "front", 3, y, "#C9A84A", noise=0.05)


def stranger(s):
    coat, glove = "#7D8288", "#2A2C30"
    k = {"skin": "#D9B79A", "hair": "#1A1A1C", "hair_len": 1, "hair_back": 5, "eyes": "#6E7884",
         "mouth": "#A8705A", "torso": [(11, coat)], "arm": coat, "sleeve": 9, "hands": glove,
         "legs": [(9, "#5E6268"), (11, "#18191B")]}
    paint_base(s, k)
    s.px("head", "front", 2, 6, "#A8705A", noise=0)           # polite smile
    s.px("head", "front", 5, 6, "#A8705A", noise=0)
    for x in range(8):                                         # lapels, a clean white collar, buttons
        s.px("body", "front", x, 0, "#EDEDED", noise=0.02)
    for y in range(1, 5):
        s.px("body", "front", 3 - (y > 2), y, "#5C6066")
        s.px("body", "front", 4 + (y > 2), y, "#5C6066")
    for y in (5, 7, 9):
        s.px("body", "front", 4, y, "#C9CED6", noise=0)
    s.fill("body", lambda face, x, y, w, h: coat if face != "front" or x in (0, 7) else None, overlay=True,
           faces=("right", "front", "left", "back"))                # coat tails reach the knees
    for leg in ("rleg", "lleg"):
        s.fill(leg, lambda face, x, y, w, h: coat if y < 5 and face != "front" else None, overlay=True,
               faces=("right", "left", "back"))


def wren(s):
    hood, fur = "#7A5634", "#E8DCC4"
    k = {"skin": "#E8BE96", "hair": "#2E1E14", "hair_len": 2, "hair_back": 6, "eyes": "#3A6EA8",
         "torso": [(8, "#4C6B8A"), (9, "#5A3A20"), (11, "#4C6B8A")], "arm": "#4C6B8A", "sleeve": 8,
         "legs": [(7, "#5A4632"), (11, "#4A3424")]}
    paint_base(s, k)
    # fur-lined hood (hat layer): hood on top, sides and back, fur edge around the face
    s.fill("head", lambda face, x, y, w, h: hood if face in ("top", "back") or (face in ("left", "right") and
                                                                                 (y < 7)) else None, overlay=True)
    for x in range(8):
        s.px("head", "front", x, 0, fur, overlay=True)
    for y in range(7):
        s.px("head", "front", 0, y, fur, overlay=True)
        s.px("head", "front", 7, y, fur, overlay=True)
    for face in ("left", "right"):
        for y in range(7):
            s.px("head", face, 7 if face == "left" else 0, y, fur, overlay=True)
    # rolled maps tucked in the belt
    for x, c in ((1, "#E9DFC3"), (2, "#D9CBA3"), (5, "#E9DFC3"), (6, "#D9CBA3")):
        for y in (7, 8, 9, 10):
            s.px("body", "front", x, y, c, overlay=True)
    for face in ("left", "right", "back"):
        for x in range(s.side_width("body", face)):
            if x % 2 == 0:
                for y in (7, 8, 9, 10):
                    s.px("body", face, x, y, "#E9DFC3", overlay=True)


def sol(s):
    robe = "#3D4E7A"
    k = {"skin": "#D7A985", "hair": None, "eyes": "#4A3A2A", "wrinkles": True, "beard": "#D9D6CF",
         "torso": [(11, robe)], "arm": robe, "sleeve": 9, "legs": [(9, robe), (11, "#3A2A1C")]}
    paint_base(s, k)
    for face in ("left", "right", "back"):                 # a white fringe around a bald head
        for x in range(8):
            if face == "back" or (face == "right" and x < 4) or (face == "left" and x > 3):
                s.px("head", face, x, 3, "#D9D6CF")
                s.px("head", face, x, 4, "#D9D6CF")
    for x in (0, 1, 2, 5, 6, 7):                           # spectacles and their chain
        s.px("head", "front", x, 4 if x in (0, 7) else 3, "#C9A84A", overlay=True, noise=0)
    for x in (1, 2, 5, 6):
        s.px("head", "front", x, 4, (220, 235, 245, 140), overlay=True, noise=0)
    s.px("head", "front", 3, 3, "#C9A84A", overlay=True, noise=0)
    s.px("head", "front", 4, 3, "#C9A84A", overlay=True, noise=0)
    for y in range(12):                                    # the lectern strapped to his back
        for x in range(8):
            s.px("body", "back", x, y, "#7A5230" if (x in (0, 7) or y in (0, 11, 5)) else "#946640", overlay=True)
    for face in ("left", "right"):
        s.fill("body", lambda f, x, y, w, h: "#5A3A20" if x == 1 else None, overlay=True, faces=(face,))
    for x in range(8):                                     # leather straps over the robe
        s.px("body", "front", x, 2 + abs(x - 3), "#5A3A20", overlay=True, noise=0)


def extras(s, key):
    """Second pass of signature details, painted after the base look of each NPC."""
    P = lambda part, face, x, y, c, o=True, n=0.04: s.px(part, face, x, y, c, overlay=o, noise=n)
    if key == "maera":
        for x in (0, 7):                                   # brass bands on the braids
            P("body", "front", x, 2, "#D8A93A", n=0)
            P("body", "front", x, 5, "#D8A93A", n=0)
        for leg in ("rleg", "lleg"):                       # embroidered hem
            for face in ("right", "front", "left", "back"):
                for x in range(4):
                    P(leg, face, x, 9, "#C08A2E" if x % 2 else "#8A2028", o=False)
        P("body", "front", 3, 8, "#FF6A3D", n=0)          # the glowing shard pendant
        P("body", "front", 4, 8, "#FFB04D", n=0)
        P("body", "front", 3, 7, "#C9A84A", n=0)
        P("body", "front", 4, 7, "#C9A84A", n=0)
    elif key == "doran":
        for y in range(2):                                 # apron straps over the shoulders
            P("body", "front", 1, y, "#4A2E18")
            P("body", "front", 6, y, "#4A2E18")
        for y in range(12):
            P("body", "back", 1 + (y * 6 // 11), y, "#4A2E18")
            P("body", "back", 6 - (y * 6 // 11), y, "#4A2E18")
        for x, y in ((2, 8), (3, 8), (4, 8), (2, 9), (3, 9), (4, 9)):   # pocket with a hammer handle
            P("body", "front", x, y, "#5A3820")
        P("body", "front", 5, 8, "#8A8F96", n=0)
        P("body", "front", 5, 9, "#6A4A2A", n=0)
        P("body", "front", 5, 10, "#6A4A2A", n=0)
        for leg in ("rleg", "lleg"):                       # steel toe caps
            for x in range(4):
                P(leg, "front", x, 10, "#8A8F96", o=False)
        for arm in ("rarm", "larm"):                       # the tattoos glow hot
            for face in ("front", "right", "left"):
                for x in range(s.side_width(arm, face)):
                    if (x + 4) % 3 == 0:
                        P(arm, face, x, 4, "#FFB347", o=False, n=0.1)
    elif key == "rhosk":
        for x, y in ((0, 1), (7, 1), (0, 9), (7, 9), (1, 5), (6, 5)):   # rivets
            P("body", "front", x, y, "#E0B35A", o=False, n=0)
        for x in range(8):                                 # sword belt with a bronze buckle
            P("body", "front", x, 10, "#3A2A1C", o=False)
        P("body", "front", 3, 10, "#E0B35A", o=False, n=0)
        P("body", "front", 4, 10, "#E0B35A", o=False, n=0)
        for face in ("left", "right"):                     # cloak edges hang at the sides
            for y in range(11):
                P("body", face, 3 if face == "left" else 0, y, "#24401F")
        for leg in ("rleg", "lleg"):                       # greave plates
            for x in range(4):
                P(leg, "front", x, 7, "#B0813B", o=False)
    elif key == "pell":
        for x in range(8):                                 # red scarf
            P("body", "front", x, 0, "#B03A2E")
            P("body", "front", x, 1, "#B03A2E" if x < 6 else None)
        for y in range(2, 6):
            P("body", "front", 5, y, "#B03A2E")
        for face in ("left", "right", "back"):
            for x in range(s.side_width("body", face)):
                P("body", face, x, 0, "#B03A2E")
        for x in range(8):                                 # tool belt with a wrench
            P("body", "front", x, 11, "#5A3A20", o=False)
        P("body", "front", 1, 10, "#9AA0A6", o=False, n=0)
        P("body", "front", 1, 11, "#9AA0A6", o=False, n=0)
        P("larm", "front", 1, 9, "#FFD866", o=False, n=0)  # the brass hand's ticking gear
    elif key == "tamsin":
        for face in ("front", "left", "right", "back"):    # leaf crown
            for x in range(8):
                if x % 2 == 0:
                    P("head", face, x, 0, "#5FA83A")
                elif face == "front" and x in (3, 5):
                    P("head", face, x, 0, "#F2C14E", n=0)
        for x, y, c in ((2, 1, "#E86AA0"), (6, 3, "#F2C14E"), (1, 7, "#E86AA0"), (5, 9, "#F2C14E")):
            P("body", "back", x, y, c, n=0)                # flowers in the moss
        for x, y in ((0, 0), (7, 1)):
            P("body", "front", x, y, "#E86AA0", n=0)
    elif key == "ilsabet":
        for y in range(8):                                 # long pale hair down her back
            for x in range(8):
                if y < 6 or x in (2, 3, 4, 5):
                    P("body", "back", x, y, "#E9E4D8" if (x + y // 3) % 3 else "#CFC8B8")
        for x, y in ((1, 3), (6, 3), (2, 6), (5, 6), (1, 9), (6, 9)):   # glowing runes
            P("body", "front", x, y, "#D8C2FF", o=False, n=0)
        for leg in ("rleg", "lleg"):
            P(leg, "front", 1, 4, "#D8C2FF", o=False, n=0)
            P(leg, "front", 2, 7, "#D8C2FF", o=False, n=0)
        for arm in ("rarm", "larm"):                       # wide sleeves flare at the wrist
            for face in ("right", "front", "left", "back"):
                for x in range(s.side_width(arm, face)):
                    P(arm, face, x, 9, "#8A63C0")
    elif key == "stranger":
        for face in ("front", "left", "right", "back"):    # grey wide-brimmed hat
            for x in range(8):
                P("head", face, x, 0, "#5C6066")
                P("head", face, x, 1, "#2A2C30")           # black band
        s.fill("head", lambda f, x, y, w, h: "#5C6066", overlay=True, faces=("top",))
        P("head", "front", 2, 4, "#C9D6E0", o=False, n=0)  # pale eyes that catch the light
        P("head", "front", 5, 4, "#C9D6E0", o=False, n=0)
        P("body", "front", 3, 1, "#7A1E2A", o=False, n=0)  # a dark red tie
        P("body", "front", 3, 2, "#7A1E2A", o=False, n=0)
        P("body", "front", 4, 2, "#7A1E2A", o=False, n=0)
    elif key == "wren":
        for x in range(8):                                 # red scarf
            P("body", "front", x, 0, "#C0392B")
        P("body", "front", 6, 1, "#C0392B")
        P("body", "front", 6, 2, "#A93226")
        for y in range(9):                                 # satchel strap across the chest
            P("body", "front", 7 - y * 7 // 8, y, "#6E4A2A")
        for leg in ("rleg", "lleg"):                       # fur-topped boots
            for face in ("right", "front", "left", "back"):
                for x in range(4):
                    P(leg, face, x, 8, "#E8DCC4")
    elif key == "sol":
        for x in range(1, 7):                              # long white beard over the robe
            for y in range(5 - int(abs(x - 3.5))):
                P("body", "front", x, y, "#E4E1DA" if (x + y) % 3 else "#CFCBC2")
        for x, y in ((1, 7), (6, 6), (2, 10), (5, 9)):    # star embroidery
            P("body", "front", x, y, "#E0C35A", o=False, n=0)
        for leg in ("rleg", "lleg"):
            P(leg, "front", 1, 3, "#E0C35A", o=False, n=0)
            P(leg, "front", 2, 6, "#E0C35A", o=False, n=0)


CAST = {"maera": (maera, True), "doran": (doran, False), "rhosk": (rhosk, False), "pell": (pell, False),
        "tamsin": (tamsin, True), "ilsabet": (ilsabet, True), "stranger": (stranger, False), "wren": (wren, True),
        "sol": (sol, False)}


def front_back(img, slim):
    """Flat front and back views of a skin (base + overlay layer) for the review sheet: 16x32 each."""
    view = Image.new("RGBA", (36, 32), (0, 0, 0, 0))
    aw = 3 if slim else 4

    def blit(part, face, overlay, dx, dy, flip=False):
        s = Skin(slim, 0)
        fx, fy, fw, fh = s.faces(part, overlay)[face]
        crop = img.crop((fx, fy, fx + fw, fy + fh))
        if flip:
            crop = crop.transpose(Image.FLIP_LEFT_RIGHT)
        view.alpha_composite(crop, (dx, dy))
    for ox, face in ((0, "front"), (19, "back")):
        cx = ox + 4 + (4 - aw)
        for overlay in (False, True):
            blit("head", face, overlay, cx + aw, 0)
            blit("body", face, overlay, cx + aw, 8)
            right, left = ("rarm", "larm") if face == "front" else ("larm", "rarm")
            blit(right, face, overlay, cx, 8)
            blit(left, face, overlay, cx + aw + 8, 8)
            rl, ll = ("rleg", "lleg") if face == "front" else ("lleg", "rleg")
            blit(rl, face, overlay, cx + aw, 20)
            blit(ll, face, overlay, cx + aw + 4, 20)
    return view


def main():
    os.makedirs(OUT, exist_ok=True)
    sheet = Image.new("RGBA", (36 * len(CAST), 32), (40, 44, 52, 255))
    for i, (key, (paint, slim)) in enumerate(CAST.items()):
        s = Skin(slim, key)
        paint(s)
        extras(s, key)
        finish(s)
        s.img.save(os.path.join(OUT, key + ".png"))
        sheet.alpha_composite(front_back(s.img, slim), (36 * i, 0))
    os.makedirs(os.path.dirname(PREVIEW), exist_ok=True)
    sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST).save(PREVIEW)
    print(f"NPC skins: {len(CAST)} ({', '.join(CAST)})")


if __name__ == "__main__":
    main()
