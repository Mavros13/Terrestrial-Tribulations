# Blockbench sources
- specs/weapons.md: modelling briefs for the 23 custom weapons, plus the export pipeline. **Start here.**
- models/weapons/: weapon `.bbmodel` sources (*Java Block/Item* projects, not GeckoLib)
- exports/weapons/: weapon *Block/Item Model* exports, `<id>.json` (`tools/build_content.py` installs them into the pack)
- textures/weapons/: weapon textures `<id>.png` (+ `.png.mcmeta`) and optional icons `<id>_icon.png` (16x16 or 32x32)
- previews/: review renders of the generated models (`_sheet.png` shows them all) and `weapon-viewer.html`, a 3D viewer built by `tools/build_model_viewer.py`; not shipped

**Our own models (owner's choice, 2026-10-28).** `tools/gen_models.py` builds the 3D model, animated texture, inventory icon and preview for 19 weapons (all but the four karambits, which use Karambit Vault x Punchy) straight into `exports/`, `textures/` and `previews/`. `tools/build_prism.py` runs it first. To hand-tune one in Blockbench, open its export, edit, export back to the same path, and delete the weapon's entry in `SHAPES` so the generator stops overwriting it.
- models/, animations/, textures/: GeckoLib sources for anything animated (none planned while content comes from existing mods)
- specs/: other rigging and animation shot lists
