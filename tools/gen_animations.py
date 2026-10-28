#!/usr/bin/env python3
"""Generate the pack's own player animations (tt:<name>) and a Palladium test power that plays them.

Writes:
  pack/kubejs/assets/tt/player_animation/tt_casts.json   playerAnimator, GeckoLib/Blockbench JSON (format 1.8.0)
  pack/kubejs/data/tt/palladium/powers/cast_test.json    test power: one key per cast, with charge and release effects
  blockbench/previews/cast-animations.html               3D review page (tools/anim_viewer_template.html), not shipped

Format checked against playerAnimator 1.20 (`GeckoLibSerializer`, `PlayerAnimationRegistry`): files in
assets/<ns>/player_animation/ register every animation in them as <ns>:<animation name>. Bones are head, torso
(bends the upper body), body (moves the whole player), right_arm, left_arm, right_leg, left_leg, right_item,
left_item. Rotations are degrees; positions are pixels. A keyframe's "easing" (easeOutBack, easeInOutSine...)
shapes the move INTO that keyframe. Pose conventions taken from Iron's Spells' animations: arm x -90 points
forward and -180 straight up; right arm y negative (left arm y positive) swings the hand toward the body's centre;
right arm z positive (left arm z negative) swings it outward; torso x positive leans forward.

Palladium (4.5.x, `PlayerAnimationAbility`) only fades in when another animation is already playing, and it never
stops a looping animation, so every cast here is a one-shot that returns to rest by itself.

Every cast follows the rules in docs/research/2026-10-28-spell-and-power-animations.md: an anticipation pose,
a fast release with overshoot, a short hold so the eye reads the pose, then an eased return. "release" is the
tick the effect should fire on, so the effects line up with the motion.

Usage: python3 tools/gen_animations.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANIM_OUT = os.path.join(ROOT, "pack", "kubejs", "assets", "tt", "player_animation", "tt_casts.json")
POWER_OUT = os.path.join(ROOT, "pack", "kubejs", "data", "tt", "palladium", "powers", "cast_test.json")
VIEWER_OUT = os.path.join(ROOT, "blockbench", "previews", "cast-animations.html")

REST = [0, 0, 0]


def k(t, ease="easeInOutSine", **bones):
    """One moment of an animation: time in seconds, the easing into it, and bone=rot or bone=(rot, pos)."""
    return (t, ease, bones)


# name: (description, length s, release tick, effect style, keyframes)
# Every bone that moves gets a rest keyframe at 0 and at the end automatically.
CASTS = {
    "cast_focus": (
        "Two-handed bolt: hands gather at the chest, then thrust forward.", 0.8, 6, "bolt", [
            k(0.2, "easeOutQuad", right_arm=[-55, -40, 0], left_arm=[-55, 40, 0], torso=[-6, 0, 0], head=[-4, 0, 0]),
            k(0.3, "easeOutBack", right_arm=[-95, -12, 0], left_arm=[-95, 12, 0], torso=[9, 0, 0], head=[3, 0, 0],
              right_leg=([-12, 0, 0], [0, 0, -1]), left_leg=([10, 0, 0], [0, 0, 1])),
            k(0.5, "linear", right_arm=[-92, -10, 0], left_arm=[-92, 10, 0], torso=[7, 0, 0]),
        ]),
    "cast_flick": (
        "Quick one-hand flick for cheap, fast spells.", 0.5, 4, "spark", [
            k(0.1, "easeOutQuad", right_arm=[-25, 10, 25], torso=[0, 12, 0]),
            k(0.18, "easeOutExpo", right_arm=[-105, -15, -5], torso=[4, -10, 0]),
            k(0.3, "linear", right_arm=[-98, -12, -3], torso=[3, -8, 0]),
        ]),
    "cast_slam": (
        "Overhead charge, then both fists drive into the ground.", 1.0, 9, "slam", [
            k(0.3, "easeOutCubic", right_arm=[-170, -10, 15], left_arm=[-170, 10, -15], torso=[-12, 0, 0],
              head=[-12, 0, 0], right_leg=([-6, 0, 0], [0, 1, 0]), left_leg=([-6, 0, 0], [0, 1, 0])),
            k(0.45, "easeInExpo", right_arm=[-35, -15, 5], left_arm=[-35, 15, -5], torso=([32, 0, 0], [0, -3, -2]),
              head=([10, 0, 0], [0, -3, -2]), right_leg=([20, 0, 0], [0, -2, 2]), left_leg=([-25, 0, 0], [0, -2, -3])),
            k(0.7, "linear", right_arm=[-38, -15, 5], left_arm=[-38, 15, -5], torso=([30, 0, 0], [0, -3, -2]),
              head=([8, 0, 0], [0, -3, -2]), right_leg=([18, 0, 0], [0, -2, 2]), left_leg=([-22, 0, 0], [0, -2, -3])),
        ]),
    "cast_rise": (
        "Summoning: hands sweep up from low and wide to overhead.", 1.1, 12, "rise", [
            k(0.25, "easeOutQuad", right_arm=[-15, 0, 40], left_arm=[-15, 0, -40], torso=[10, 0, 0], head=[12, 0, 0]),
            k(0.6, "easeOutCubic", right_arm=[-160, 0, 30], left_arm=[-160, 0, -30], torso=[-10, 0, 0],
              head=[-18, 0, 0]),
            k(0.85, "linear", right_arm=[-163, 0, 28], left_arm=[-163, 0, -28], torso=[-9, 0, 0], head=[-16, 0, 0]),
        ]),
    "cast_ward": (
        "Ward: arms cross over the chest, then burst open.", 0.9, 8, "ward", [
            k(0.25, "easeOutQuad", right_arm=[-90, -60, 0], left_arm=[-80, 60, 0], torso=[8, 0, 0], head=[8, 0, 0]),
            k(0.4, "easeOutBack", right_arm=[-75, 15, 65], left_arm=[-75, -15, -65], torso=[-6, 0, 0], head=[-4, 0, 0]),
            k(0.65, "linear", right_arm=[-72, 15, 62], left_arm=[-72, -15, -62], torso=[-5, 0, 0]),
        ]),
    "cast_blink": (
        "Blink: crouch and lean, arms swept back, then snap upright.", 0.6, 5, "blink", [
            k(0.2, "easeInQuad", right_arm=[35, 0, 15], left_arm=[35, 0, -15], torso=([28, 0, 0], [0, -2, -1]),
              head=([-10, 0, 0], [0, -2, -2]), right_leg=([-25, 0, 0], [0, -1, -2]), left_leg=([20, 0, 0], [0, -1, 2])),
            k(0.3, "easeOutBack", right_arm=[-20, 0, 10], left_arm=[-20, 0, -10], torso=[-4, 0, 0], head=[-2, 0, 0],
              right_leg=REST, left_leg=REST),
        ]),
    "weapon_raise": (
        "Weapon ability: raise the blade to the sky, off hand braced out.", 1.0, 7, "raise", [
            k(0.2, "easeOutQuad", right_arm=[-60, 20, 15], left_arm=[-30, 0, -25], torso=[6, 15, 0]),
            k(0.35, "easeOutBack", right_arm=[-178, -5, -8], left_arm=[-50, 0, -55], torso=[-8, -5, 0],
              head=[-22, 0, 0]),
            k(0.75, "linear", right_arm=[-175, -5, -6], left_arm=[-48, 0, -52], torso=[-7, -4, 0], head=[-20, 0, 0]),
        ]),
}

# Particles at the hands while charging, and a burst plus sound on the release tick. Commands run as the player
# (Palladium CommandAbility, permission 2). "execute anchored eyes" makes ^ ^ ^ follow where the player looks.
EFFECTS = {
    "bolt": ("minecraft:enchant", "minecraft:end_rod", "minecraft:entity.evoker.cast_spell", 0.6),
    "spark": ("minecraft:electric_spark", "minecraft:crit", "minecraft:entity.illusioner.cast_spell", 0.6),
    "slam": ("minecraft:ash", "minecraft:explosion", "minecraft:entity.generic.explode", 0.0),
    "rise": ("minecraft:soul", "minecraft:sculk_soul", "minecraft:entity.evoker.prepare_summon", 0.0),
    "ward": ("minecraft:wax_on", "minecraft:totem_of_undying", "minecraft:item.trident.return", 0.0),
    "blink": ("minecraft:portal", "minecraft:reverse_portal", "minecraft:entity.enderman.teleport", 0.0),
    "raise": ("minecraft:electric_spark", "minecraft:flash", "minecraft:item.trident.thunder", 0.0),
}


def keyed(t):
    return f"{t:.4f}".rstrip("0").rstrip(".") if t else "0.0"


def build_animation(length, frames):
    bones = {}
    used = sorted({b for _, _, bs in frames for b in bs})
    for bone in used:
        rot, pos = {"0.0": {"vector": REST}}, {"0.0": {"vector": REST}}
        has_pos = False
        for t, ease, bs in frames:
            if bone not in bs:
                continue
            v = bs[bone]
            r, p = (v if isinstance(v, tuple) else (v, REST))
            rot[keyed(t)] = {"vector": r, "easing": ease}
            pos[keyed(t)] = {"vector": p, "easing": ease}
            has_pos = has_pos or p != REST
        rot[keyed(length)] = {"vector": REST, "easing": "easeInOutSine"}
        pos[keyed(length)] = {"vector": REST, "easing": "easeInOutSine"}
        bones[bone] = {"rotation": rot}
        if has_pos:
            bones[bone]["position"] = pos
    return {"animation_length": length, "bones": bones}


def particle(p, where, count, spread, speed):
    return f"execute anchored eyes run particle {p} {where} {spread} {spread} {spread} {speed} {count} normal"


def build_power(order):
    abilities = {}
    for i, name in enumerate(order):
        desc, length, release, style, _ = CASTS[name]
        charge_p, burst_p, sound, reach = EFFECTS[style]
        ticks = round(length * 20)
        # Enabled ticks count back down after an ability ends, so effects also require the cast to be running.
        live = {"type": "palladium:ability_enabled", "ability": name}
        hands = f"^ ^-0.45 ^{0.45 + reach * 0.5:.2f}"
        burst_at = f"^ ^-0.4 ^{0.8 + reach:.2f}" if reach else "~ ~0.1 ~" if style == "slam" else "^ ^-0.6 ^0.3"
        abilities[name] = {
            "type": "palladium:player_animation", "animation": f"tt:{name}", "list_index": i,
            "title": name.replace("_", " ").title(), "description": {"text": desc},
            "conditions": {"enabling": [{"type": "palladium:activation", "ticks": ticks, "cooldown": ticks + 10}]},
        }
        abilities[name + "_charge"] = {
            "type": "palladium:command", "hidden": True, "hidden_in_bar": True,
            "commands": [particle(charge_p, hands, 3, 0.12, 0.02)],
            "conditions": {"enabling": [live, {"type": "palladium:ability_ticks", "ability": name, "min": 1,
                                               "max": max(1, release - 1)}]},
        }
        abilities[name + "_release"] = {
            "type": "palladium:command", "hidden": True, "hidden_in_bar": True, "commands": [],
            "first_tick_commands": [particle(burst_p, burst_at, 1 if burst_p in ("minecraft:explosion", "minecraft:flash") else 25,
                                             0.25, 0.08),
                                    f"playsound {sound} player @a ~ ~ ~ 0.8 1.1"],
            "conditions": {"enabling": [live, {"type": "palladium:ability_ticks", "ability": name, "min": release,
                                               "max": release}]},
        }
    return {
        "name": "Cast Test (dev)",
        "icon": "minecraft:blaze_rod",
        "abilities": abilities,
    }


def main():
    anims = {name: build_animation(c[1], c[4]) for name, c in CASTS.items()}
    os.makedirs(os.path.dirname(ANIM_OUT), exist_ok=True)
    with open(ANIM_OUT, "w", encoding="utf-8") as fh:
        json.dump({"format_version": "1.8.0", "animations": anims}, fh, indent=1)
    os.makedirs(os.path.dirname(POWER_OUT), exist_ok=True)
    with open(POWER_OUT, "w", encoding="utf-8") as fh:
        json.dump(build_power(list(CASTS)), fh, indent=2)
    viewer = [{"name": n, "desc": c[0], "length": c[1], "release": c[2], "style": c[3], "bones": anims[n]["bones"]}
              for n, c in CASTS.items()]
    template = open(os.path.join(ROOT, "tools", "anim_viewer_template.html"), encoding="utf-8").read()
    with open(VIEWER_OUT, "w", encoding="utf-8") as fh:
        fh.write(template.replace("/*__DATA__*/[]", json.dumps(viewer, separators=(",", ":"))))
    print(f"Wrote {len(anims)} tt: player animations and the tt:cast_test power")


if __name__ == "__main__":
    main()
