# Blockbench sources
- specs/weapons.md: modelling briefs for the 23 custom weapons, plus the export pipeline. **Start here.**
- models/weapons/: weapon `.bbmodel` sources (*Java Block/Item* projects, not GeckoLib)
- exports/weapons/: weapon *Block/Item Model* exports, `<id>.json` (`tools/build_content.py` installs them into the pack)
- textures/weapons/: weapon textures `<id>.png` (+ `.png.mcmeta`) and optional 16x16 icons `<id>_icon.png`
- models/, animations/, textures/: GeckoLib sources for anything animated (none planned while content comes from existing mods)
- specs/: other rigging and animation shot lists
