#!/usr/bin/env python3
"""Generate the Terrestrial Tribulations Passive Skill Tree (Daripher's Passive Skill Tree, 1.20.1).

Format checked against Daripher/Passive-Skill-Tree@1.20.1 (data/skilltree/skills/*.json, skill_trees/*.json,
SerializationHelper, StatRequirement, bonus serializers). Output:
  pack/kubejs/data/tt/skills/*.json, pack/kubejs/data/tt/skill_trees/shardborn.json
  skill names merged into pack/kubejs/assets/tt/lang/en_us.json (key: skill.tt.<id>.name)

Layout: 9 Fate spokes (start node + 10 nodes; notables at 5 and 10), a ring linking neighbouring Fates at the
5th node (hybrid builds), a quality-of-life node off every spoke, and a story keystone at the end of each spoke.
Keystones are tagged "keystone" and the tree allows at most 3 of them.
"""
import json, math, os, shutil, uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "pack", "kubejs", "data", "tt")
LANG = os.path.join(ROOT, "pack", "kubejs", "assets", "tt", "lang", "en_us.json")
ISS = "irons_spellbooks:"
NONE = {"type": "skilltree:none"}
TEX = "skilltree:textures/"


# ---------- bonus builders (shapes copied from the mod's own skill files) ----------
def attribute(attr, amount, op=0, key=""):
    return {"type": "skilltree:attribute", "attribute": attr, "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"tt:{key}:{attr}")),
            "name": "Skill", "amount": amount, "operation": op, "player_condition": NONE}

def damage(amount, cond="skilltree:none"):
    return {"type": "skilltree:damage", "amount": amount, "operation": 1, "player_multiplier": NONE, "enemy_multiplier": NONE,
            "player_condition": NONE, "damage_condition": {"type": cond}, "target_condition": NONE}

def damage_taken(amount, cond="skilltree:none"):
    return {"type": "skilltree:damage_taken", "amount": amount, "operation": 1, "player_multiplier": NONE, "attacker_multiplier": NONE,
            "player_condition": NONE, "damage_condition": {"type": cond}, "attacker_condition": NONE}

def crit_chance(chance):
    return {"type": "skilltree:crit_chance", "chance": chance, "player_multiplier": NONE, "enemy_multiplier": NONE,
            "player_condition": NONE, "damage_condition": {"type": "skilltree:melee"}, "target_condition": NONE}

def crit_damage(amount):
    return {"type": "skilltree:crit_damage", "amount": amount, "player_multiplier": NONE, "enemy_multiplier": NONE,
            "player_condition": NONE, "damage_condition": NONE, "target_condition": NONE}

def inflict(effect, chance, duration=100, amp=0):
    return {"type": "skilltree:inflict_effect", "chance": chance, "max_stacks": 0, "effect": effect, "duration": duration, "amplifier": amp,
            "event_listener": {"damage_condition": NONE, "target": "enemy", "type": "skilltree:attack"}}

def regen(pct, cooldown):
    return {"type": "skilltree:healing", "chance": 1.0, "amount": pct, "event_listener": {"cooldown": cooldown, "type": "skilltree:ticking"},
            "percentage_healing": True}

def xp(mult, source):
    return {"type": "skilltree:gained_experience", "multiplier": mult, "experience_source": source, "player_multiplier": NONE}

def loot(chance, kind):
    return {"type": "skilltree:loot_duplication", "chance": chance, "multiplier": 1.0, "loot_type": kind}

def avoid(chance, cond):
    return {"type": "skilltree:damage_avoidance", "chance": chance, "player_multiplier": NONE, "attacker_multiplier": NONE,
            "player_condition": NONE, "damage_condition": {"type": cond}, "attacker_condition": NONE}

def stat_req(stat_type, stat, minimum):
    return {"type": "skilltree:stat_value", "statTypeId": stat_type, "statId": stat, "minValue": minimum}


# ---------- content ----------
# Each Fate: (id, name, icon, lesser-node bonus pair, notable bonuses, QoL node, keystone)
FATES = [
    ("vanguard", "Vanguard", "sword_iron.png",
     lambda k: [attribute("minecraft:generic.armor", 1.0, key=k)], lambda k: [attribute("minecraft:generic.attack_damage", 0.5, key=k)],
     lambda k: [attribute("minecraft:generic.armor", 3.0, key=k), damage(0.05)],
     ("Long Arms", "glove_iron.png", lambda k: [attribute("forge:block_reach", 1.0, key=k)]),
     ("Unbroken Line", "Keystone, unlocked by slaying an Elder Guardian. The Thornwatch's oldest vow.",
      lambda k: [attribute("minecraft:generic.armor", 6.0, key=k), attribute("minecraft:generic.knockback_resistance", 0.3, key=k)],
      [stat_req("minecraft:killed", "minecraft:elder_guardian", 1)])),
    ("duelist", "Duelist", "sword_gold.png",
     lambda k: [attribute("minecraft:generic.attack_speed", 0.03, 1, key=k)], lambda k: [crit_chance(0.03)],
     lambda k: [crit_damage(0.15), attribute("minecraft:generic.movement_speed", 0.03, 1, key=k)],
     ("Trailblazer", "boots_leather.png", lambda k: [attribute("minecraft:generic.movement_speed", 0.05, 1, key=k)]),
     ("Bladedance", "Keystone, earned after 500 kills. Every cut sets up the next.",
      lambda k: [crit_damage(0.4), attribute("minecraft:generic.attack_speed", 0.10, 1, key=k)],
      [stat_req("minecraft:custom", "minecraft:mob_kills", 500)])),
    ("warden", "Warden", "chestplate_bronze_fur.png",
     lambda k: [attribute("minecraft:generic.max_health", 1.0, key=k)], lambda k: [attribute("minecraft:generic.knockback_resistance", 0.05, key=k)],
     lambda k: [damage_taken(-0.06), attribute("minecraft:generic.max_health", 2.0, key=k)],
     ("Soft Landing", "boots_bronze.png", lambda k: [damage_taken(-0.3, "skilltree:fall")]),
     ("Ember Heart", "Keystone, unlocked after sleeping through 10 nights. The hearth of Emberhold beats in you.",
      lambda k: [regen(0.02, 80), attribute("minecraft:generic.max_health", 4.0, key=k)],
      [stat_req("minecraft:custom", "minecraft:sleep_in_bed", 10)])),
    ("ranger", "Ranger", "bow_gold.png",
     lambda k: [damage(0.04, "skilltree:projectile")], lambda k: [attribute("minecraft:generic.movement_speed", 0.02, 1, key=k)],
     lambda k: [damage(0.10, "skilltree:projectile"), avoid(0.05, "skilltree:projectile")],
     ("Lucky Find", "treasure_chest.png", lambda k: [loot(0.05, "chests")]),
     ("Shardsense", "Keystone, unlocked by slaying a Warden. You feel hidden things before you see them.",
      lambda k: [damage(0.20, "skilltree:projectile"), attribute("minecraft:generic.luck", 2.0, key=k)],
      [stat_req("minecraft:killed", "minecraft:warden", 1)])),
    ("arcanist", "Arcanist", "potion_blue_small.png",
     lambda k: [attribute(ISS + "spell_power", 0.03, 1, key=k)], lambda k: [attribute(ISS + "max_mana", 15.0, key=k)],
     lambda k: [damage(0.08, "skilltree:magic"), attribute(ISS + "max_mana", 40.0, key=k)],
     ("Scholar", "eye_green.png", lambda k: [xp(0.10, "mobs")]),
     ("Crownbearer's Will", "Keystone, unlocked by slaying the Wither. A Crown Shard answers your call.",
      lambda k: [attribute(ISS + "spell_power", 0.15, 1, key=k), damage(0.10, "skilltree:magic")],
      [stat_req("minecraft:killed", "minecraft:wither", 1)])),
    ("spellweaver", "Spellweaver", "potion_cyan.png",
     lambda k: [attribute(ISS + "mana_regen", 0.05, 1, key=k)], lambda k: [attribute(ISS + "cooldown_reduction", 0.02, key=k)],
     lambda k: [attribute(ISS + "cooldown_reduction", 0.05, key=k), attribute(ISS + "mana_regen", 0.10, 1, key=k)],
     ("Prospector", "potion_yellow_big.png", lambda k: [xp(0.15, "ore")]),
     ("Ley Convergence", "Keystone, unlocked after drinking 50 potions. The ley lines bend to your weave.",
      lambda k: [attribute(ISS + "cooldown_reduction", 0.12, key=k), attribute(ISS + "mana_regen", 0.25, 1, key=k)],
      [stat_req("minecraft:used", "minecraft:potion", 50)])),
    ("reaper", "Reaper", "skull.png",
     lambda k: [attribute("minecraft:generic.attack_damage", 0.5, key=k)], lambda k: [inflict("minecraft:wither", 0.05, 60)],
     lambda k: [inflict("minecraft:weakness", 0.15, 80), damage(0.06)],
     ("Bone Harvest", "bone.png", lambda k: [loot(0.05, "mobs")]),
     ("Hollow Ward", "Keystone, earned after 1000 kills. The Hollowed's hunger becomes yours.",
      lambda k: [inflict("minecraft:wither", 0.25, 100, 1), damage(0.12)],
      [stat_req("minecraft:custom", "minecraft:mob_kills", 1000)])),
    ("summoner", "Summoner", "potion_indigo.png",
     lambda k: [attribute(ISS + "summon_damage", 0.04, 1, key=k)], lambda k: [attribute(ISS + "max_mana", 10.0, key=k)],
     lambda k: [attribute(ISS + "summon_damage", 0.10, 1, key=k), attribute(ISS + "max_mana", 30.0, key=k)],
     ("Deep Lungs", "potion_white.png", lambda k: [attribute("forge:swim_speed", 0.25, 1, key=k)]),
     ("Bond of Legions", "Keystone, unlocked by slaying the Ender Dragon. What you call, comes.",
      lambda k: [attribute(ISS + "summon_damage", 0.25, 1, key=k)],
      [stat_req("minecraft:killed", "minecraft:ender_dragon", 1)])),
    ("artificer", "Artificer", "glove_steel.png",
     lambda k: [attribute("forge:block_reach", 0.25, key=k)], lambda k: [attribute("minecraft:generic.armor_toughness", 0.5, key=k)],
     lambda k: [attribute("forge:entity_reach", 0.5, key=k), attribute("minecraft:generic.armor", 2.0, key=k)],
     ("Sure Step", "boots_gold.png", lambda k: [attribute("forge:step_height_addition", 0.5, key=k)]),
     ("Overclock", "Keystone, unlocked after using a crafting table 200 times. The Tinker-Kings would approve.",
      lambda k: [attribute("minecraft:generic.attack_speed", 0.10, 1, key=k), attribute("forge:entity_reach", 1.0, key=k), attribute("minecraft:generic.armor_toughness", 3.0, key=k)],
      [stat_req("minecraft:custom", "minecraft:interact_with_crafting_table", 200)])),
]

NOTABLE_NAMES = {
    "vanguard": ("Shieldwall", "Iron Discipline"), "duelist": ("Riposte", "Killing Rhythm"), "warden": ("Bulwark", "Last Stand"),
    "ranger": ("Hawkeye", "Wind Reader"), "arcanist": ("Arcane Surge", "Astral Font"), "spellweaver": ("Weave Flow", "Threaded Time"),
    "reaper": ("Grave Touch", "Soul Tithe"), "summoner": ("Pack Bond", "Legion's Call"), "artificer": ("Precision Tools", "Calibrated Frame"),
}


def main():
    for d in ("skills", "skill_trees"):
        shutil.rmtree(os.path.join(DATA, d), ignore_errors=True)
        os.makedirs(os.path.join(DATA, d))
    skills, names = {}, {}

    def node(sid, name, x, y, bonuses, kind="lesser", icon="void.png", start=False, reqs=None, tags=None):
        bg, border, size = {"lesser": ("background/lesser.png", "tooltip/lesser.png", 16),
                            "notable": ("background/notable.png", "tooltip/notable.png", 20),
                            "keystone": ("background/keystone.png", "tooltip/keystone.png", 24),
                            "class": ("background/class.png", "tooltip/gateway.png", 24)}[kind]
        skills[sid] = {"id": f"tt:{sid}", "bonuses": bonuses, "requirements": reqs or [], "directConnections": [],
                       "longConnections": [], "oneWayConnections": [], "tags": tags or [],
                       "backgroundTexture": TEX + "icons/" + bg, "iconTexture": TEX + "icons/" + icon, "borderTexture": TEX + border,
                       "positionX": round(x, 3), "positionY": round(y, 3), "buttonSize": size, "isStartingPoint": start}
        names[f"skill.tt.{sid}.name"] = name

    def link(a, b):
        skills[a]["directConnections"].append(f"tt:{b}")

    n = len(FATES)
    for i, (fid, fname, icon, lesser_a, lesser_b, notable, qol, keystone) in enumerate(FATES):
        ang = 2 * math.pi * i / n - math.pi / 2
        pos = lambda r, da=0.0: (r * math.cos(ang + da), r * math.sin(ang + da))
        node(f"{fid}_start", f"{fname}'s Path", *pos(60), lesser_a(f"{fid}_start"), "class", icon, start=True)
        prev = f"{fid}_start"
        for j in range(1, 11):
            sid = f"{fid}_{j}"
            if j in (5, 10):
                node(sid, NOTABLE_NAMES[fid][0 if j == 5 else 1], *pos(60 + j * 26), notable(sid), "notable", icon)
            else:
                node(sid, f"{fname} Training", *pos(60 + j * 26), (lesser_a if j % 2 else lesser_b)(sid), "lesser", icon)
            link(prev, sid)
            prev = sid
        qname, qicon, qbonus = qol
        node(f"{fid}_qol", qname, *pos(60 + 2 * 26, 0.16), qbonus(f"{fid}_qol"), "notable", qicon)
        link(f"{fid}_2", f"{fid}_qol")
        kname, kdesc, kbonus, kreq = keystone
        node(f"{fid}_keystone", kname, *pos(60 + 10 * 26 + 44), kbonus(f"{fid}_keystone"), "keystone", icon, reqs=kreq, tags=["keystone"])
        names[f"skill.tt.{fid}_keystone.description"] = kdesc
        link(f"{fid}_10", f"{fid}_keystone")
    for i in range(n):  # hybrid ring at the first notable
        link(f"{FATES[i][0]}_5", f"{FATES[(i + 1) % n][0]}_5")

    for sid, s in skills.items():
        with open(os.path.join(DATA, "skills", sid + ".json"), "w") as f:
            json.dump(s, f, indent=2)
    with open(os.path.join(DATA, "skill_trees", "shardborn.json"), "w") as f:
        json.dump({"id": "tt:shardborn", "skillIds": [f"tt:{k}" for k in skills], "skillLimitations": {"keystone": 3}}, f, indent=2)

    lang = json.load(open(LANG, encoding="utf-8")) if os.path.exists(LANG) else {}
    lang.update(names)
    with open(LANG, "w", encoding="utf-8") as f:
        json.dump(lang, f, indent=2, ensure_ascii=False)
    # sanity: every connection target exists
    for s in skills.values():
        for c in s["directConnections"]:
            assert c[3:] in skills, c
    print(f"Generated skill tree tt:shardborn with {len(skills)} skills "
          f"({sum(1 for s in skills.values() if 'keystone' in s['tags'])} keystones, max 3 per character).")


if __name__ == "__main__":
    main()
