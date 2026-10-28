#!/usr/bin/env python3
"""Pre-flight checks for the pack: catch broken files in the cloud, before a test session on the desktop.

Run by tools/build_prism.py after the generators; exits 1 on errors (warnings don't fail the build).

Checks:
  json        every .json / .mcmeta under pack/ parses
  items       every tt: item used anywhere (scripts, data, quests, models) is registered in a startup script
  weapons     every weapon in design/weapons/weapons.json has a model, texture, icon, lang name, Epic Fight
              capability and swing trail
  models      item model parents and textures resolve; elements stay inside [-16, 32]; rotations use one axis
              and an angle of 0, +-22.5 or +-45 (vanilla rejects anything else and shows the purple cube)
  lang        every registered tt: item has an English name
  scripts     KubeJS scripts pass a JavaScript syntax check (node), and the two Rhino traps that broke Test
              Build 1 are caught: a const declared inside try, and a top-level name without the tt prefix in
              server scripts (they share one scope with the hero packs)
  origins     origin layers list existing origins, origins list existing powers
  skills      the skill tree lists existing skills; skill connections point at existing skills
  animations  tt: player animations use known bones and easings, and every animation a power plays exists
  palladium   ability references inside a power (ability_ticks, ability_enabled) name abilities of that power
  quests      quest files have balanced braces
  modlists    modpack/curseforge-mods.json and pack/tt-sync/mods.json agree on which mods are in which stage

Usage: python3 tools/check_pack.py
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.environ.get("TT_CHECK_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tests point it at a copy
PACK = os.path.join(ROOT, "pack")
KJS = os.path.join(PACK, "kubejs")
TT_ASSETS = os.path.join(KJS, "assets", "tt")
TT_DATA = os.path.join(KJS, "data", "tt")

errors, warnings = [], []


def err(area, msg):
    errors.append(f"[{area}] {msg}")


def warn(area, msg):
    warnings.append(f"[{area}] {msg}")


def rel(p):
    return os.path.relpath(p, ROOT)


def load_all_json():
    out = {}
    for p in glob.glob(os.path.join(PACK, "**", "*.json"), recursive=True) + \
            glob.glob(os.path.join(PACK, "**", "*.mcmeta"), recursive=True):
        try:
            with open(p, encoding="utf-8") as fh:
                out[p] = json.load(fh)
        except (ValueError, UnicodeDecodeError) as e:
            err("json", f"{rel(p)}: {e}")
    return out


def registered_items():
    items = set()
    for p in glob.glob(os.path.join(KJS, "startup_scripts", "*.js")):
        items |= set(re.findall(r"event\.create\(\s*['\"](tt:[a-z0-9_]+)['\"]", open(p, encoding="utf-8").read()))
    return items


def check_items(items, docs):
    # Item IDs used as items: script string literals, quest item fields, "item" keys in data.
    used = {}
    for p in glob.glob(os.path.join(KJS, "server_scripts", "*.js")) + glob.glob(os.path.join(KJS, "client_scripts", "*.js")):
        for m in re.findall(r"['\"](tt:[a-z0-9_]+)['\"]", open(p, encoding="utf-8").read()):
            used.setdefault(m, rel(p))
    for p in glob.glob(os.path.join(PACK, "config", "ftbquests", "**", "*.snbt"), recursive=True):
        for m in re.findall(r'id:\s*"(tt:[a-z0-9_]+)"', open(p, encoding="utf-8").read()):
            used.setdefault(m, rel(p))
    for p, d in docs.items():
        for m in re.findall(r'"item":\s*"(tt:[a-z0-9_]+)"', json.dumps(d)):
            used.setdefault(m, rel(p))
    # Script literals also name tiers, stages, powers and more; only flag the ones that look like items here.
    item_like = re.compile(r"tt:[a-z0-9_]+$")
    for i, where in sorted(used.items()):
        if item_like.match(i) and i not in items and not _known_non_item(i):
            err("items", f"{i} is used in {where} but no startup script registers it")


NON_ITEM_PREFIXES = ("tt:cast_", "tt:weapon_raise", "tt:railblade_charge", "tt:gauntlet_charge")


def _known_non_item(i):
    # Names that live in other registries (powers, origins, skills, animations, stages) and are referenced as
    # strings in scripts.
    name = i.split(":", 1)[1]
    paths = [os.path.join(TT_DATA, sub, name + ".json") for sub in ("powers", "origins", "skills", "skill_trees")]
    paths.append(os.path.join(TT_DATA, "palladium", "powers", name + ".json"))
    return i.startswith(NON_ITEM_PREFIXES) or any(os.path.exists(p) for p in paths)


def check_weapons(items, lang):
    data = json.load(open(os.path.join(ROOT, "design", "weapons", "weapons.json"), encoding="utf-8"))
    for w in data["weapons"]:
        i = w["id"]
        if f"tt:{i}" not in items:
            err("weapons", f"tt:{i} is in weapons.json but not registered")
        if not os.path.exists(os.path.join(TT_ASSETS, "models", "item", i + ".json")):
            err("weapons", f"tt:{i} has no item model")
        if f"item.tt.{i}" not in lang:
            err("weapons", f"tt:{i} has no English name")
        cap = os.path.join(TT_DATA, "capabilities", "weapons", i + ".json")
        if not os.path.exists(cap) and w["family"] not in ("bow", "crossbow"):  # bows stay vanilla in Epic Fight
            warn("weapons", f"tt:{i} has no Epic Fight capability file")
        if not os.path.exists(os.path.join(TT_ASSETS, "item_skins", i + ".json")) and w["family"] not in ("bow", "crossbow", "gauntlets", "shield"):
            warn("weapons", f"tt:{i} has no swing trail")


def texture_exists(ref):
    ns, path = ref.split(":", 1) if ":" in ref else ("minecraft", ref)
    if ns != "tt":
        return True  # other mods' and vanilla textures can't be checked here
    return os.path.exists(os.path.join(TT_ASSETS, "textures", path + ".png"))


def model_exists(ref):
    ns, path = ref.split(":", 1) if ":" in ref else ("minecraft", ref)
    if ns != "tt":
        return True
    return os.path.exists(os.path.join(TT_ASSETS, "models", path + ".json"))


def check_model(p, m, where=""):
    name = rel(p) + where
    if "parent" in m and not model_exists(m["parent"]):
        err("models", f"{name}: parent {m['parent']} not found")
    for key, t in (m.get("textures") or {}).items():
        if not t.startswith("#") and not texture_exists(t):
            err("models", f"{name}: texture {key} = {t} not found")
    for e in m.get("elements", []):
        label = e.get("name", "?")
        for v in e.get("from", []) + e.get("to", []):
            if not -16 <= v <= 32:
                err("models", f"{name}: element {label} reaches {v}, outside [-16, 32]")
                break
        r = e.get("rotation")
        if r:
            if r.get("axis") not in ("x", "y", "z"):
                err("models", f"{name}: element {label} has rotation axis {r.get('axis')}")
            if r.get("angle") not in (0, 22.5, -22.5, 45, -45):
                err("models", f"{name}: element {label} has rotation angle {r.get('angle')} (only 0, +-22.5, +-45)")
        for face, f in (e.get("faces") or {}).items():
            tex = f.get("texture", "")
            if tex.startswith("#") and tex[1:] not in (m.get("textures") or {}) and "parent" not in m:
                err("models", f"{name}: element {label} face {face} uses undefined texture {tex}")
    # forge:separate_transforms nests whole models
    if m.get("loader") == "forge:separate_transforms":
        if "base" in m:
            check_model(p, m["base"], " (base)")
        for persp, sub in (m.get("perspectives") or {}).items():
            check_model(p, sub, f" ({persp})")


def check_models(docs):
    for p, m in docs.items():
        if os.path.join("assets", "tt", "models") in p:
            check_model(p, m)
    for p in glob.glob(os.path.join(TT_ASSETS, "textures", "**", "*.png.mcmeta"), recursive=True):
        if not os.path.exists(p[:-len(".mcmeta")]):
            err("models", f"{rel(p)} has no texture next to it")


def check_lang(items):
    p = os.path.join(TT_ASSETS, "lang", "en_us.json")
    lang = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    for i in sorted(items):
        if f"item.tt.{i.split(':')[1]}" not in lang:
            err("lang", f"{i} has no English name in {rel(p)}")
    return lang


TOP_LEVEL = re.compile(r"^(?:const|let|var|function)\s+([A-Za-z_$][\w$]*)", re.M)


def check_scripts():
    node = shutil.which("node")
    if not node:
        warn("scripts", "node not installed; JavaScript syntax not checked")
    for p in sorted(glob.glob(os.path.join(KJS, "*_scripts", "*.js"))):
        src = open(p, encoding="utf-8").read()
        if node:
            r = subprocess.run([node, "--check", p], capture_output=True, text=True)
            if r.returncode:
                err("scripts", f"{rel(p)}: syntax error\n      " + r.stderr.strip().splitlines()[-1])
        # Rhino: const inside a try block fails to load
        for m in re.finditer(r"\btry\s*\{", src):
            depth, i = 1, m.end()
            while i < len(src) and depth:
                depth += {"{": 1, "}": -1}.get(src[i], 0)
                i += 1
            body = src[m.end():i]
            if re.search(r"\bconst\s", body):
                line = src.count("\n", 0, m.start()) + 1
                err("scripts", f"{rel(p)}:{line}: const inside try (Rhino rejects it; use let)")
        if os.sep + "server_scripts" + os.sep in p:
            for name in TOP_LEVEL.findall(src):
                if not name.lstrip("$_").lower().startswith("tt"):
                    err("scripts", f"{rel(p)}: top-level name {name} needs the tt prefix (server scripts share one scope)")


def check_origins():
    origins = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(TT_DATA, "origins", "*.json"))}
    powers = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(TT_DATA, "powers", "*.json"))}
    for p in glob.glob(os.path.join(KJS, "data", "*", "origin_layers", "*.json")):
        for o in json.load(open(p, encoding="utf-8")).get("origins", []):
            oid = o if isinstance(o, str) else o.get("origins", [None])[0]
            if oid and oid.startswith("tt:") and oid[3:] not in origins:
                err("origins", f"{rel(p)} lists {oid}, which doesn't exist")
    for o in origins:
        p = os.path.join(TT_DATA, "origins", o + ".json")
        for pw in json.load(open(p, encoding="utf-8")).get("powers", []):
            if pw.startswith("tt:") and pw[3:] not in powers:
                err("origins", f"{rel(p)} grants {pw}, which doesn't exist")


def check_skills():
    skills = {}
    for p in glob.glob(os.path.join(TT_DATA, "skills", "*.json")):
        d = json.load(open(p, encoding="utf-8"))
        skills[d.get("id")] = (p, d)
    for p in glob.glob(os.path.join(TT_DATA, "skill_trees", "*.json")):
        for s in json.load(open(p, encoding="utf-8")).get("skillIds", []):
            if s not in skills:
                err("skills", f"{rel(p)} lists {s}, which has no skill file")
    for sid, (p, d) in skills.items():
        for key in ("directConnections", "longConnections", "oneWayConnections"):
            for s in d.get(key, []):
                if s not in skills:
                    err("skills", f"{rel(p)}: {key} points at missing {s}")


BONES = {"head", "torso", "body", "right_arm", "left_arm", "right_leg", "left_leg", "right_item", "left_item",
         "rightItem", "leftItem"}
EASINGS = {"linear", "step", "catmullrom"} | {f"ease{d}{k}" for d in ("In", "Out", "InOut")
                                             for k in ("Sine", "Cubic", "Quad", "Quart", "Quint", "Expo", "Circ", "Back", "Elastic", "Bounce")}


def check_animations(docs):
    anims = set()
    for p in glob.glob(os.path.join(KJS, "assets", "*", "player_animation", "*.json")):
        ns = p.split(os.sep + "assets" + os.sep)[1].split(os.sep)[0]
        d = docs.get(p, {})
        for name, a in (d.get("animations") or {}).items():
            anims.add(f"{ns}:{name}")
            for bone, tracks in a.get("bones", {}).items():
                if bone not in BONES:
                    err("animations", f"{rel(p)}: {name} animates unknown bone {bone}")
                for kind in ("rotation", "position"):
                    for t, kf in (tracks.get(kind) or {}).items() if isinstance(tracks.get(kind), dict) else ():
                        if isinstance(kf, dict) and kf.get("easing") and kf["easing"] not in EASINGS:
                            err("animations", f"{rel(p)}: {name}.{bone} uses unknown easing {kf['easing']}")
                        try:
                            if t != "vector" and float(t) > a.get("animation_length", 0) + 1e-6:
                                warn("animations", f"{rel(p)}: {name}.{bone} has a keyframe after the end ({t})")
                        except ValueError:
                            pass
    return anims


def check_palladium(docs, anims):
    for p, d in docs.items():
        if os.sep + os.path.join("palladium", "powers") + os.sep not in p:
            continue
        names = set((d.get("abilities") or {}).keys())
        for key, ab in (d.get("abilities") or {}).items():
            if ab.get("type") == "palladium:player_animation":
                a = ab.get("animation", "")
                if a.startswith("tt:") and a not in anims:
                    err("palladium", f"{rel(p)}: {key} plays {a}, which no animation file defines")
            conds = (ab.get("conditions") or {}).get("enabling", [])
            for c in conds if isinstance(conds, list) else [conds]:
                ref = c.get("ability")
                if ref and "#" not in ref and "power" not in c and ref not in names:
                    err("palladium", f"{rel(p)}: {key} refers to ability {ref}, which this power doesn't have")


def check_quests():
    for p in glob.glob(os.path.join(PACK, "config", "ftbquests", "**", "*.snbt"), recursive=True):
        src = re.sub(r'"(?:\\.|[^"\\])*"', '""', open(p, encoding="utf-8").read())
        if src.count("{") != src.count("}") or src.count("[") != src.count("]"):
            err("quests", f"{rel(p)}: unbalanced braces or brackets")


def norm(n):
    return re.sub(r"[^a-z0-9]", "", n.lower().replace("'n", "and").replace("&", "and"))


# Same mod, different name on each site; and mods that can't be in the CurseForge pack.
MODLIST_ALIASES = {"wakesforgeport": "wakesreforged", "fsang18sheropack": "fsang18sheroes"}
MODLIST_NOT_ON_CF = {"godsandheroes"}  # Modrinth-only, All Rights Reserved (see curseforge-mods.json _comment)


def check_modlists():
    cf = json.load(open(os.path.join(ROOT, "modpack", "curseforge-mods.json"), encoding="utf-8"))["mods"]
    mr = json.load(open(os.path.join(PACK, "tt-sync", "mods.json"), encoding="utf-8"))["mods"]
    cf_by = {norm(m["name"]): m for m in cf}
    for m in mr:
        if m.get("disabled"):
            continue
        key = norm(m["name"])
        if key in MODLIST_NOT_ON_CF:
            continue
        key = MODLIST_ALIASES.get(key, key)
        hit = cf_by.get(key) or next((c for k, c in cf_by.items() if key in k or k in key), None)
        if not hit:
            warn("modlists", f"{m['name']} (stage {m.get('stage')}) is in tt-sync/mods.json but not found in curseforge-mods.json")
        elif hit.get("stage") != m.get("stage"):
            err("modlists", f"{m['name']}: stage {m.get('stage')} in tt-sync/mods.json but {hit.get('stage')} in curseforge-mods.json")


def main():
    docs = load_all_json()
    items = registered_items()
    lang = check_lang(items)
    check_items(items, docs)
    check_weapons(items, lang)
    check_models(docs)
    check_scripts()
    check_origins()
    check_skills()
    anims = check_animations(docs)
    check_palladium(docs, anims)
    check_quests()
    check_modlists()
    for w in warnings:
        print("warning", w)
    for e in errors:
        print("ERROR  ", e)
    print(f"Pack check: {len(errors)} errors, {len(warnings)} warnings "
          f"({len(items)} items, {len(docs)} JSON files, {len(anims)} animations)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
