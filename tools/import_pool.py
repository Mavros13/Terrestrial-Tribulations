#!/usr/bin/env python3
"""Imports YMS2001's Pool and Billiards data pack + resource pack (Squid Workshop, MPL-2.0) into the pack.

Owner's pick (2026-10-30), in place of the Pool Table mod (no 1.20.1 Forge build). CurseForge 1481772 /
Modrinth mksguUIH, resource pack Modrinth mdBvgTLC; source https://github.com/MingshiYangUIUC/Pool-Minecraft-Squid-Workshop-Project.
A data pack can't go in a CurseForge manifest or a Forge mods folder, so its files are copied unchanged (except the recipes, see skip_recipes):
  the 1.16-1.20 data pack's data/      -> pack/kubejs/data/   (KubeJS loads it for every world, like a global data pack)
  the 1.16-1.20 resource pack          -> pack/resourcepacks/Pool and Billiards/  (switched on by Default Options)
MPL-2.0 allows this; each copy keeps the LICENSE and a NOTICE with the source and commit.
Not run by build_prism.py (it needs the network). To update: set COMMIT to a newer commit on main and run it again.
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "https://github.com/MingshiYangUIUC/Pool-Minecraft-Squid-Workshop-Project"
COMMIT = "a830e0801bc295d349b6dc95eeb9953bd261e894"  # v1.3.7, 2026-10-23
VERSION = "v1.3.7-mc1.16_1.20"
DATA = os.path.join(ROOT, "pack", "kubejs", "data")
NAMESPACES = ["app", "math", "pool"]
FUNCTION_TAGS = os.path.join(DATA, "minecraft", "tags", "functions")
RP = os.path.join(ROOT, "pack", "resourcepacks", "Pool and Billiards")
NOTICE = (f"Pool and Billiards {VERSION} by YMS2001 (Squid Workshop), MPL-2.0 (see LICENSE).\n"
          f"Source: {REPO} (commit {COMMIT}).\nCopied into Terrestrial Tribulations by tools/import_pool.py, unchanged except that the data pack's recipes (1.20.5+ format) are left out.\n")


def skip_recipes(folder, names):
    # data/pool/recipes use the 1.20.5+ item-component format (the pack says recipes need 1.20.5+): on 1.20.1 all 53
    # fail to parse and log errors. Recipe mode is off by default; cue sticks and tables come from the pool menu.
    return ["recipes"] if os.path.basename(folder) == "pool" and os.path.basename(os.path.dirname(folder)) == "data" else []


def main():
    tmp = tempfile.mkdtemp()
    try:
        src = os.path.join(tmp, "repo")
        subprocess.run(["git", "clone", "-q", REPO, src], check=True)
        subprocess.run(["git", "-C", src, "checkout", "-q", COMMIT], check=True)
        dp = os.path.join(src, "Pool-Datapack-Squid-Workshop-1.16-1.20")
        found = sorted(os.listdir(os.path.join(dp, "data")))
        if found != sorted(NAMESPACES + ["minecraft"]):
            sys.exit(f"unexpected namespaces in the data pack: {found}")
        for ns in NAMESPACES:
            shutil.rmtree(os.path.join(DATA, ns), ignore_errors=True)
            shutil.copytree(os.path.join(dp, "data", ns), os.path.join(DATA, ns), ignore=skip_recipes)
        with open(os.path.join(DATA, "pool", "NOTICE.txt"), "w", encoding="utf-8") as f:
            f.write(NOTICE)
        shutil.copy(os.path.join(src, "LICENSE"), os.path.join(DATA, "pool", "LICENSE"))
        # load/tick function tags (the only files under data/minecraft); we have none of our own to merge with
        os.makedirs(FUNCTION_TAGS, exist_ok=True)
        for tag in ("load.json", "tick.json"):
            shutil.copy(os.path.join(dp, "data", "minecraft", "tags", "functions", tag), os.path.join(FUNCTION_TAGS, tag))
        shutil.rmtree(RP, ignore_errors=True)
        shutil.copytree(os.path.join(src, "Pool-Resourcepack-Squid-Workshop-1.16-1.20"), RP)
        shutil.copy(os.path.join(src, "LICENSE"), os.path.join(RP, "LICENSE"))
        with open(os.path.join(RP, "NOTICE.txt"), "w", encoding="utf-8") as f:
            f.write(NOTICE)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"Pool and Billiards {VERSION} imported")


if __name__ == "__main__":
    main()
