#!/usr/bin/env python3
"""Build CurseForge-format modpack zips that Prism Launcher (and the CurseForge app) import directly:
  dist/Terrestrial-Tribulations-TestBuild1-CurseForge.zip  (stages A-C)
  dist/Terrestrial-Tribulations-TestBuild2-CurseForge.zip  (all stages)

Format (CurseForge "minecraftModpack" manifest v1, as read by Prism's Flame importer):
  manifest.json  {minecraft: {version, modLoaders: [{id: "forge-<ver>", primary}]}, manifestType, manifestVersion,
                  name, version, author, files: [{projectID, fileID, required}], overrides: "overrides"}
  overrides/     copied into the instance's minecraft/ folder.
Every mod, including libraries, must be listed: the importer does not resolve dependencies.
Data: modpack/curseforge-mods.json. Overrides: pack/ without tt-sync/ (ModSync isn't needed when the
launcher downloads the mods itself). Run after the generators (build_prism.py calls this).
"""
import json, os, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILDS = [("Terrestrial-Tribulations-TestBuild1-CurseForge", "Test Build 1", "C"),
          ("Terrestrial-Tribulations-TestBuild2-CurseForge", "Test Build 2", "D")]
SKIP_DIRS = {"tt-sync"}
# --release: one zip with every stage and without the test-only files listed in tools/dev_only.txt, named and
# versioned from "pack_version" in modpack/curseforge-mods.json (bump it for every public release)
RELEASE = ("Terrestrial-Tribulations-Release-CurseForge", "Release", "Z")


def dev_only():
    lines = open(os.path.join(ROOT, "tools", "dev_only.txt"), encoding="utf-8").read().splitlines()
    return {l.strip() for l in lines if l.strip() and not l.startswith("#")}


def main():
    data = json.load(open(os.path.join(ROOT, "modpack", "curseforge-mods.json"), encoding="utf-8"))
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    release = "--release" in sys.argv
    skip = dev_only() if release else set()
    for name, label, max_stage in ([RELEASE] if release else BUILDS):
        mods = [m for m in data["mods"] if m["stage"] <= max_stage]
        manifest = {
            "minecraft": {"version": data["minecraft"],
                          "modLoaders": [{"id": "forge-" + data["forge"], "primary": True}]},
            "manifestType": "minecraftModpack",
            "manifestVersion": 1,
            "name": "Terrestrial Tribulations (" + label + ")",
            "version": label,
            "author": "Mavros13",
            "files": [{"projectID": m["projectID"], "fileID": m["fileID"], "required": True} for m in mods],
            "overrides": "overrides",
        }
        if release:  # versioned file and manifest: Terrestrial-Tribulations-<pack_version>-CurseForge.zip
            name, label = f"Terrestrial-Tribulations-{data['pack_version']}-CurseForge", data["pack_version"]
            manifest["name"], manifest["version"] = "Terrestrial Tribulations", label
        out = os.path.join(ROOT, "dist", name + ".zip")
        base = os.path.join(ROOT, "pack")
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("manifest.json", json.dumps(manifest, indent=2))
            z.writestr("modlist.html", "<ul>\n" + "".join(
                f"<li><a href=\"https://www.curseforge.com/projects/{m['projectID']}\">{m['name']}</a></li>\n" for m in mods) + "</ul>\n")
            for dp, dn, fn in os.walk(base):
                dn[:] = [d for d in dn if not (dp == base and d in SKIP_DIRS)]
                for f in fn:
                    full = os.path.join(dp, f)
                    if os.path.relpath(full, base).replace(os.sep, "/") in skip:
                        continue
                    z.write(full, "overrides/" + os.path.relpath(full, base).replace(os.sep, "/"))
        print("Built", out, len(mods), "mods,", os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
