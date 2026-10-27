#!/usr/bin/env python3
"""Build the Prism Launcher instance zip: dist/Terrestrial-Tribulations-TestBuild1.zip

1. Regenerates content (build_content.py, gen_quests.py).
2. Compiles pack/tt-sync/ModSync.java into ModSync.jar (Java 17 bytecode).
3. Zips prism/instance.cfg + prism/mmc-pack.json + pack/ (as the instance's minecraft/ folder).
4. Builds the CurseForge-format zips (build_curseforge.py).
"""
import os, shutil, subprocess, sys, tempfile, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "Terrestrial-Tribulations-TestBuild1"


def run(*cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def main():
    run(sys.executable, os.path.join(ROOT, "tools", "build_content.py"))
    run(sys.executable, os.path.join(ROOT, "tools", "gen_quests.py"))
    run(sys.executable, os.path.join(ROOT, "tools", "gen_origins.py"))
    run(sys.executable, os.path.join(ROOT, "tools", "gen_skilltree.py"))  # after build_content: merges into lang
    sync = os.path.join(ROOT, "pack", "tt-sync")
    with tempfile.TemporaryDirectory() as tmp:
        run("javac", "--release", "17", "-d", tmp, os.path.join(sync, "ModSync.java"))
        with open(os.path.join(tmp, "MANIFEST.MF"), "w") as f:
            f.write("Main-Class: ModSync\n")
        run("jar", "cfm", os.path.join(sync, "ModSync.jar"), os.path.join(tmp, "MANIFEST.MF"), "-C", tmp, ".")
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    out = os.path.join(ROOT, "dist", NAME + ".zip")
    skip = {"lock.json", "installed.json", "sync-report.txt", "MANUAL_DOWNLOADS.html"}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in ("instance.cfg", "mmc-pack.json"):
            z.write(os.path.join(ROOT, "prism", f), f"{NAME}/{f}")
        z.writestr(f"{NAME}/minecraft/mods/README.txt", "Mods are downloaded here automatically by TT ModSync when you press Launch.\n")
        base = os.path.join(ROOT, "pack")
        for dp, dn, fn in os.walk(base):
            for f in fn:
                if f in skip or f.endswith(".part"):
                    continue
                full = os.path.join(dp, f)
                z.write(full, f"{NAME}/minecraft/" + os.path.relpath(full, base).replace(os.sep, "/"))
    print("Built", out, os.path.getsize(out), "bytes")
    run(sys.executable, os.path.join(ROOT, "tools", "build_curseforge.py"))  # CurseForge-format zips (Prism imports these too)


if __name__ == "__main__":
    main()
