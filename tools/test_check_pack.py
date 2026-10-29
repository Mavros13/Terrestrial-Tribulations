#!/usr/bin/env python3
"""Planted-error tests for tools/check_pack.py.

Copies the pack (and the files the checker reads beside it) into a scratch folder, plants one known fault at a time
("ghost errors"), runs the checker on the copy, and confirms the checker reports it. The real files are never
touched. A planted fault that the checker misses is a gap in the checker; the test fails and names it.

Kept small on purpose (one planted fault per major area) so it stays a quick final check; it is not part of the
normal build. Run it after changing check_pack.py.

Usage: python3 tools/test_check_pack.py        (prints one line per planted fault, exits 1 if any were missed)
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECK = os.path.join(ROOT, "tools", "check_pack.py")
COPY = ["pack", os.path.join("design", "weapons"), "modpack"]

M = "pack/kubejs/assets/tt/models/item"
T = "pack/kubejs/assets/tt/textures/item"
D = "pack/kubejs/data/tt"
S = "pack/kubejs/server_scripts"
LANG = "pack/kubejs/assets/tt/lang/en_us.json"
ANIM = "pack/kubejs/assets/tt/player_animation/tt_casts.json"
POWER = f"{D}/palladium/powers/cast_test.json"


# --- small helpers that edit the scratch copy -----------------------------------------------------------------
def path(root, rel):
    return os.path.join(root, *rel.split("/"))


def append(rel, text):
    def f(root):
        with open(path(root, rel), "a", encoding="utf-8") as fh:
            fh.write(text)
    return f


def replace(rel, old, new):
    def f(root):
        p = path(root, rel)
        s = open(p, encoding="utf-8").read()
        assert old in s, f"fixture text not found in {rel}: {old!r}"
        open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))
    return f


def delete(rel):
    return lambda root: os.remove(path(root, rel))


def write(rel, text):
    def f(root):
        os.makedirs(os.path.dirname(path(root, rel)), exist_ok=True)
        open(path(root, rel), "w", encoding="utf-8").write(text)
    return f


def edit_json(rel, fn):
    def f(root):
        p = path(root, rel)
        d = json.load(open(p, encoding="utf-8"))
        fn(d)
        json.dump(d, open(p, "w", encoding="utf-8"), indent=1)
    return f


def first_element(d):
    return d["elements"][0]


def set_rot(axis, angle):
    def fn(d):
        first_element(d)["rotation"] = {"origin": [8, 8, 8], "axis": axis, "angle": angle}
    return fn


def drop_lang(key):
    return edit_json(LANG, lambda d: d.pop(key))


def add_weapon(d):
    w = dict(d["weapons"][0])
    w["id"] = "ghost_blade"
    d["weapons"].append(w)


def first_anim(d):
    return next(iter(d["animations"].values()))


def set_stage(d):
    for m in d["mods"]:
        if m["name"] == "Jade":
            m["stage"] = "D"


# --- the planted faults: (name, plant, text the checker's output must contain) ---------------------------------
CASES = [
    ("broken JSON (trailing comma)", replace(f"{M}/gnawblade.json", "{", "{,"), "[json]"),
    ("item used in a recipe but never registered", replace(f"{S}/tt_recipes.js", "'tt:frontier_cleaver', [", "'tt:ghost_blade', ["), "tt:ghost_blade is used"),
    ("weapon without an English name", drop_lang("item.tt.gnawblade"), "tt:gnawblade has no English name"),
    ("element rotation angle 30", edit_json(f"{M}/gnawblade_3d.json", set_rot("z", 30)), "rotation angle 30"),
    ("const inside try (Rhino)", append(f"{S}/tt_recipes.js", "\ntry { const ttGhost = 1 } catch (e) {}\n"), "const inside try"),
    ("top-level name without tt prefix", append(f"{S}/tt_recipes.js", "\nlet ghostName = 1\n"), "top-level name ghostName"),
    ("origin grants a missing power", edit_json(f"{D}/origins/arcanist.json", lambda d: d["powers"].append("tt:ghost_power")), "grants tt:ghost_power"),
    ("power plays a missing animation", replace(POWER, '"tt:cast_flick"', '"tt:cast_ghost"'), "plays tt:cast_ghost"),
    ("mod in different stages in the two lists", edit_json("modpack/curseforge-mods.json", set_stage), "Jade: stage"),
]


def run_check(root):
    env = dict(os.environ, TT_CHECK_ROOT=root)
    r = subprocess.run([sys.executable, CHECK], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


def fresh_copy(base):
    root = tempfile.mkdtemp(dir=base)
    for c in COPY:
        shutil.copytree(os.path.join(ROOT, c), os.path.join(root, c))
    return root


def main():
    base = tempfile.mkdtemp(prefix="tt-check-")
    missed = []
    try:
        clean = fresh_copy(base)
        code, out = run_check(clean)
        if code != 0 or "0 errors, 0 warnings" not in out:
            print("The unmodified copy doesn't pass cleanly, so the planted-error results would mean nothing:\n" + out)
            return 1
        print(f"clean copy: passes ({out.strip().splitlines()[-1]})")
        for name, plant, expect in CASES:
            root = fresh_copy(base)
            plant(root)
            code, out = run_check(root)
            caught = expect in out and ("[" in out and ("ERROR" in out or "warning" in out))
            print(f"{'caught' if caught else 'MISSED'}  {name}")
            if not caught:
                missed.append(name)
                print("        checker said: " + " | ".join(out.strip().splitlines()[-3:]))
            shutil.rmtree(root)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print(f"\n{len(CASES) - len(missed)} of {len(CASES)} planted errors caught")
    return 1 if missed else 0


if __name__ == "__main__":
    sys.exit(main())
