#!/usr/bin/env python3
"""Generate the Origins (Forge 1.20.1, Apoli) datapack: 4 Heritages (added to origins:origin) + the Fate layer.

Formats checked against EdwinMindcraft/origins-architectury@1.20.x/forge (OriginLayer codec) and
EdwinMindcraft/apoli@1.20.x/forge (attribute, effect_immunity, modify_falling, invulnerability).
Output: pack/kubejs/data/{tt,origins}/...
"""
import json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, "pack", "kubejs", "data")
ISS = "irons_spellbooks:"  # attribute IDs checked in iron431/irons-spells-n-spellbooks@1.20.1-legacy AttributeRegistry


def w(path, obj):
    p = os.path.join(B, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def attr(attribute, value, op="addition"):
    return {"attribute": attribute, "operation": op, "value": value, "name": "tt"}


def power(pid, name, desc, body):
    w(f"tt/powers/{pid}.json", {"name": name, "description": desc, **body})
    return f"tt:{pid}"


def attrs(*mods):
    return {"type": "origins:attribute", "modifiers": list(mods)}


def immune(effect):
    return {"type": "origins:effect_immunity", "effect": effect}


def origin(oid, name, desc, icon, order, impact, powers):
    w(f"tt/origins/{oid}.json", {"name": name, "description": desc, "icon": {"item": icon},
                                 "order": order, "impact": impact, "powers": powers})
    return f"tt:{oid}"


HERITAGES = [
    ("ashborn", "Ashborn", "Frontier folk hardened by the ash fields after the Sundering. Tough, and need little.", "minecraft:charcoal", 1, [
        ("ashborn_hardy", "Ash-Hardened", "+2 max health.", attrs(attr("minecraft:generic.max_health", 2.0))),
        ("ashborn_lean", "Lean Living", "Immune to Hunger.", immune("minecraft:hunger"))]),
    ("verdant_kin", "Verdant Kin", "Children of the Verdant Pact groves. Swift and untouched by venom.", "minecraft:oak_sapling", 1, [
        ("verdant_swift", "Grove-Footed", "+5% movement speed.", attrs(attr("minecraft:generic.movement_speed", 0.05, "multiply_base"))),
        ("verdant_venom", "Sap-Blooded", "Immune to Poison.", immune("minecraft:poison"))]),
    ("cogkin", "Cogkin", "Descendants of the Tinker-Kings' engineers. Long reach, steady hands.", "minecraft:clock", 1, [
        ("cogkin_reach", "Tinker's Reach", "+1 block reach.", attrs(attr("forge:block_reach", 1.0))),
        ("cogkin_plating", "Riveted", "+1 armor toughness.", attrs(attr("minecraft:generic.armor_toughness", 1.0)))]),
    ("skyborn", "Skyborn", "Blood of the old Aether envoys. Light as air, frail as glass.", "minecraft:feather", 2, [
        ("skyborn_glide", "Feather-Fall", "You fall slowly and take no fall damage.",
         {"type": "origins:modify_falling", "velocity": 0.05, "take_fall_damage": False}),
        ("skyborn_frail", "Hollow Bones", "-2 max health.", attrs(attr("minecraft:generic.max_health", -2.0)))]),
]

FATES = [
    ("vanguard", "Vanguard", "Frontline melee and defence.", "minecraft:iron_chestplate", [
        ("vanguard_plate", "Bulwark Plate", "+4 armor, +1 attack damage.",
         attrs(attr("minecraft:generic.armor", 4.0), attr("minecraft:generic.attack_damage", 1.0)))]),
    ("duelist", "Duelist", "Precision, combos and critical strikes.", "tt:rustbite_karambit", [
        ("duelist_tempo", "Tempo", "+15% attack speed, +5% movement speed.",
         attrs(attr("minecraft:generic.attack_speed", 0.15, "multiply_base"), attr("minecraft:generic.movement_speed", 0.05, "multiply_base")))]),
    ("warden", "Warden", "Survival, shields and protection.", "minecraft:shield", [
        ("warden_endure", "Endure", "+6 max health, +25% knockback resistance, +2 armor toughness.",
         attrs(attr("minecraft:generic.max_health", 6.0), attr("minecraft:generic.knockback_resistance", 0.25), attr("minecraft:generic.armor_toughness", 2.0)))]),
    ("ranger", "Ranger", "Ranged combat and mobility.", "minecraft:bow", [
        ("ranger_stride", "Pathfinder", "+10% movement speed, +1 luck.",
         attrs(attr("minecraft:generic.movement_speed", 0.10, "multiply_base"), attr("minecraft:generic.luck", 1.0)))]),
    ("arcanist", "Arcanist", "Direct magical damage and spell mastery.", "minecraft:enchanted_book", [
        ("arcanist_focus", "Arcane Focus", "+15% spell power, +100 max mana, -4 max health.",
         attrs(attr(ISS + "spell_power", 0.15, "multiply_base"), attr(ISS + "max_mana", 100.0), attr("minecraft:generic.max_health", -4.0)))]),
    ("spellweaver", "Spellweaver", "Utility, control and elemental effects.", "minecraft:amethyst_shard", [
        ("spellweaver_flow", "Ley Flow", "+25% mana regeneration, +10% cooldown reduction.",
         attrs(attr(ISS + "mana_regen", 0.25, "multiply_base"), attr(ISS + "cooldown_reduction", 0.10)))]),
    ("reaper", "Reaper", "Curses, lifesteal and dark powers.", "minecraft:wither_rose", [
        ("reaper_hunger", "Grave Hunger", "+2 attack damage, -2 max health.",
         attrs(attr("minecraft:generic.attack_damage", 2.0), attr("minecraft:generic.max_health", -2.0))),
        ("reaper_ward", "Deathless", "Immune to Wither.", immune("minecraft:wither"))]),
    ("summoner", "Summoner", "Companions and minions.", "minecraft:bone", [
        ("summoner_bond", "Bond of Many", "+20% summon damage, +50 max mana.",
         attrs(attr(ISS + "summon_damage", 0.20, "multiply_base"), attr(ISS + "max_mana", 50.0)))]),
    ("artificer", "Artificer", "Machinery, gadgets and technological combat.", "minecraft:piston", [
        ("artificer_kit", "Toolkit", "+1.5 block reach, +2 armor, +5% attack speed.",
         attrs(attr("forge:block_reach", 1.5), attr("minecraft:generic.armor", 2.0), attr("minecraft:generic.attack_speed", 0.05, "multiply_base")))]),
]


def main():
    for d in ("tt/powers", "tt/origins", "tt/origin_layers"):
        shutil.rmtree(os.path.join(B, d), ignore_errors=True)
    her = [origin(oid, n, d, icon, 100 + i, imp, [power(*p) for p in pw]) for i, (oid, n, d, icon, imp, pw) in enumerate(HERITAGES)]
    w("origins/origin_layers/origin.json", {"replace": False, "origins": her})
    fates = [origin(fid, n, d + " Your Fate deepens as you invest in the Passive Skill Tree.", icon, i, 1, [power(*p) for p in pw])
             for i, (fid, n, d, icon, pw) in enumerate(FATES)]
    # All fields the OriginLayer codec reads; gui_title omitted (optional, defaults).
    w("tt/origin_layers/fate.json", {
        "order": 10, "origins": fates, "enabled": True, "name": "Fate",
        "missing_name": "Unbound", "missing_description": "No Fate chosen.",
        "allow_random": False, "allow_random_unchoosable": False, "random_exclusions": [],
        "auto_choose": False, "hidden": False})
    # Gods and Heroes (ghmorak / super_powers layer) was dropped 2026-10-31; Origins Heritage + Fate only.
    sp = os.path.join(B, "origins", "origin_layers", "super_powers")
    if os.path.isdir(sp):
        shutil.rmtree(sp, ignore_errors=True)
    print(f"Generated {len(her)} heritages and {len(fates)} fates.")


if __name__ == "__main__":
    main()
