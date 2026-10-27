#!/usr/bin/env python3
"""Generate FTB Quests (1.20.1 / 2001.x) SNBT for Terrestrial Tribulations.

Writes pack/config/ftbquests/quests/{data.snbt, chapter_groups.snbt, chapters/*.snbt, lang/en_us.snbt}.
Quest and task IDs are stable 16-hex strings derived from their keys, so re-generating keeps player progress.
Schema checked against FTBTeam/FTB-Quests@1.20.1/main (Quest/ItemTask/KillTask/AdvancementTask/ItemReward/XPReward
readData, BaseQuestFile.VERSION = 13). On 1.20.1 titles and descriptions are stored inline, so no lang file is used.
"""
import hashlib
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "pack", "config", "ftbquests", "quests")


def qid(key):
    return hashlib.md5(("tt:" + key).encode()).hexdigest()[:16].upper()


def s(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def item(i, count=1):
    return f'{{ Count: {count}b, id: {s(i)} }}'


# Task helpers -> SNBT strings
def t_item(i, count=1):
    return f'type: "item", item: {item(i)}' + (f", count: {count}L" if count > 1 else "")
def t_kill(entity, n):
    return f'type: "kill", entity: {s(entity)}, value: {n}L'
def t_adv(adv):
    return f'type: "advancement", advancement: {s(adv)}, criterion: ""'
def t_check():
    return 'type: "checkmark"'
def t_dim(dim):
    return f'type: "dimension", dimension: {s(dim)}'

# Reward helpers
def r_item(i, count=1):
    return f'type: "item", item: {item(i, min(count, 64))}'
def r_xp(n):
    return f'type: "xp", xp: {n}'
def r_stage(stage):
    """Grants a KubeJS stage (used by story gates). The command needs operator rights, hence elevate_perms."""
    return f'type: "command", command: "/kubejs stages add @p {stage}", elevate_perms: true, silent: true'


# --------------------------------------------------------------------------------------------------
# Quest content. Each quest: key, title, subtitle, description lines, tasks, rewards, deps (keys), x, y, main(bool)
CHAPTERS = [
    {
        "key": "welcome", "title": "Welcome to Velmora", "icon": "minecraft:book",
        "quests": [
            dict(key="w_welcome", title="Welcome, Shard-Born", sub="Start here", main=True, x=0, y=0,
                 desc=["&6Velmora is broken.&r Seven hundred years ago Queen Ysolde shattered the Aether Crown, and the realms drifted apart.",
                       "", "You woke in the ash fields with no memory and a warmth in your chest that won't go away.",
                       "", "This book guides you. &eGold-framed quests&r are the main story; the rest are optional side paths and tutorials.",
                       "", "&7Tick the box to begin."],
                 tasks=[t_check()], rewards=[r_item("minecraft:bread", 4)]),
            dict(key="w_origin", title="Heritage and Fate", sub="Who were you?", x=2, y=-1, deps=["w_welcome"],
                 desc=["When you first joined, you chose a &eHeritage&r (your bloodline) and a &eFate&r (your calling).",
                       "", "&6Fates:&r Vanguard, Duelist, Warden, Ranger, Arcanist, Spellweaver, Reaper, Summoner, Artificer.",
                       "A tenth Fate, &dAscendant&r, is said to awaken only in those who have walked far down two paths...",
                       "", "&7Missed the screen? It appears on first join. Tick the box once you've chosen."],
                 tasks=[t_check()], rewards=[r_xp(25)]),
            dict(key="w_skilltree", title="The Skill Tree", sub="Experience becomes power", x=2, y=1, deps=["w_welcome"],
                 desc=["Experience you earn becomes &eskill points&r in the &6Passive Skill Tree&r.",
                       "", "Open it from your inventory (or its keybind in Controls) and spend your first point.",
                       "Every Fate starts on a different edge of the tree. Story keystones unlock as the campaign advances."],
                 tasks=[t_check()], rewards=[r_xp(50)]),
            dict(key="w_stance", title="Battle Stance", sub="Epic Fight basics", x=4, y=0, deps=["w_origin", "w_skilltree"],
                 desc=["Press &eR&r to switch between &6Battle Mode&r and Mining Mode.",
                       "", "In Battle Mode: &eleft click&r chains your weapon's combo, &esprint + attack&r dashes in, and your dodge key rolls you through danger.",
                       "Every weapon type has its own moveset. Karambits are fast and cruel; greatswords are slow and devastating."],
                 tasks=[t_check()], rewards=[r_item("minecraft:cooked_beef", 4)]),
        ],
    },
    {
        "key": "ch1", "title": "Chapter 1: The Broken Frontier", "icon": "minecraft:campfire",
        "quests": [
            dict(key="c1_ash", title="Ash and Embers", sub="Breathe. Stand.", main=True, x=0, y=0, deps=["w_welcome"],
                 desc=["&o\"Breathe. Stand. Whatever happened here, the night will not wait for answers.\"",
                       "", "The ash fields stretch in every direction. Smoke rises to the east.",
                       "", "&71. Punch a tree for logs.\n2. Turn them into planks.\n3. Craft a &eCrafting Table&7."],
                 tasks=[t_item("minecraft:crafting_table")], rewards=[r_item("minecraft:bread", 4), r_xp(50)]),
            dict(key="c1_cleaver", title="Something Sharp", sub="Ugly. Effective.", main=True, x=2, y=0, deps=["c1_ash"],
                 desc=["You can't face the night with bare hands.",
                       "", "Craft a &eFrontier Cleaver&r: 2 Flint, 1 Bone, 1 Stick (check JEI for the shape).",
                       "Its &6Scavenger's Edge&r squeezes extra food from every hunt, and you'll need it."],
                 tasks=[t_item("tt:frontier_cleaver")], rewards=[r_item("minecraft:torch", 8), r_xp(50)]),
            dict(key="c1_stone", title="Stone and Spark", sub="Tools of the frontier", x=2, y=-2, deps=["c1_ash"],
                 desc=["Stone tools last longer and a furnace turns raw ore and meat into something useful.",
                       "", "Craft a &eStone Pickaxe&r and a &eFurnace&r."],
                 tasks=[t_item("minecraft:stone_pickaxe"), t_item("minecraft:furnace")], rewards=[r_item("minecraft:coal", 8), r_xp(40)]),
            dict(key="c1_shelter", title="Shelter Before Dark", sub="Walls first, questions later", main=True, x=4, y=0, deps=["c1_cleaver"],
                 desc=["The Hollowed hunt at night. Build four walls, a door, and sleep through your first night.",
                       "", "&7Sleep in a bed to complete this quest."],
                 tasks=[t_adv("minecraft:adventure/sleep_in_bed")], rewards=[r_item("minecraft:white_wool", 3), r_xp(60)]),
            dict(key="c1_night", title="The First Night", sub="They come in the dark", main=True, x=6, y=0, deps=["c1_shelter"],
                 desc=["Some nights you can't sleep through. The dead walk the ash fields and something drives them.",
                       "", "Defeat &e5 Zombies&r. Try Battle Mode (&eR&r) and dodge their swings rather than trading hits."],
                 tasks=[t_kill("minecraft:zombie", 5)], rewards=[r_item("minecraft:iron_ingot", 2), r_xp(80)]),
            dict(key="c1_iron", title="Iron in the Ash", sub="Real metal", x=6, y=-2, deps=["c1_stone"],
                 desc=["Iron is the line between surviving and living. Mine iron ore and smelt it."],
                 tasks=[t_adv("minecraft:story/smelt_iron")], rewards=[r_item("minecraft:iron_ingot", 3), r_xp(60)]),
            dict(key="c1_hunt", title="Hunter's Instinct", sub="Know your enemies", x=8, y=2, deps=["c1_night"],
                 desc=["Skeletons keep their distance. Spiders leap. Learn their patterns before something worse learns yours.",
                       "", "Defeat &e3 Skeletons&r and &e3 Spiders&r."],
                 tasks=[t_kill("minecraft:skeleton", 3), t_kill("minecraft:spider", 3)], rewards=[r_item("minecraft:arrow", 16), r_xp(80)]),
            dict(key="c1_smoke", title="Voices in the Smoke", sub="East, where the fires burn", main=True, x=8, y=0, deps=["c1_night"],
                 desc=["Following the smoke, you find a ring of tents and frightened faces: the last of the &cEmber Accord&r.",
                       "", "An old woman with ash in her braids studies you. &o\"You walked through the Hollow fields and lived. No one lives.\"",
                       "", "&6Elder Maera&r: &o\"Sit. Eat. Then tell me why the Hollowed turned away from you.\"",
                       "", "&7(Elder Maera's NPC arrives with the Emberhold build. Tick to continue.)"],
                 tasks=[t_check()], rewards=[r_item("minecraft:cooked_porkchop", 6), r_xp(100)]),
            dict(key="c1_karambit", title="Teeth for the Night", sub="Maera's gift", main=True, x=10, y=0, deps=["c1_smoke", "c1_iron"],
                 desc=["&6Elder Maera&r unrolls a scrap of leather with a curved blade sketched on it.",
                       "", "&o\"Ember scouts carried these. Small enough to hide, cruel enough to matter.\"",
                       "", "Craft a &eRustbite Karambit&r: 2 Iron Ingots, 1 Leather, 1 Stick.",
                       "Same bite as an iron sword, but faster. Its &6Reversal Cut&r rewards a well-timed dodge."],
                 tasks=[t_item("tt:rustbite_karambit")], rewards=[r_item("minecraft:leather", 4), r_xp(120)]),
            dict(key="c1_finale", title="The Ember Accord", sub="Chapter 1 complete", main=True, x=12, y=0, deps=["c1_karambit", "c1_hunt"],
                 desc=["The refugees need walls, a name and someone who doesn't die.",
                       "", "&6Elder Maera&r presses a sealed document into your hands: the &eEmberhold Charter&r.",
                       "&o\"Find good ground. Plant this. We'll follow.\"",
                       "", "&eChapter 2: The First Settlement&r begins: found Emberhold with MineColonies' Town Hall."],
                 tasks=[t_check()], rewards=[r_item("tt:emberhold_charter"), r_xp(200), r_stage("tt_ch1_done")]),
        ],
    },
    {
        "key": "combat", "title": "Combat Fundamentals", "icon": "tt:rustbite_karambit",
        "quests": [
            dict(key="cb_dodge", title="Read, Dodge, Punish", sub="The combat loop", x=0, y=0, deps=["w_stance"],
                 desc=["Every enemy telegraphs. Watch the wind-up, dodge &ethrough&r the swing, then punish the recovery window.",
                       "", "Dodging costs stamina. Spend it wisely: an empty bar means you're stuck trading blows."],
                 tasks=[t_check()], rewards=[r_xp(40)]),
            dict(key="cb_weapon", title="Know Your Weapon", sub="Abilities and tooltips", x=2, y=0, deps=["cb_dodge"],
                 desc=["Every Terrestrial Tribulations weapon has a unique &6ability&r, a colour all its own and a story behind it. Read the tooltip.",
                       "", "Obtain a &eFrontier Cleaver&r and hover over it."],
                 tasks=[t_item("tt:frontier_cleaver")], rewards=[r_xp(30)]),
            dict(key="cb_elites", title="Champions of the Dark", sub="Elite enemies", x=4, y=0, deps=["cb_weapon"],
                 desc=["Some monsters spawn as &cChampions&r: tougher, named and gifted with affixes (fire, frost, shielding and worse).",
                       "", "Their name tag tells you their rank. Higher ranks drop better loot. Retreat is not cowardice."],
                 tasks=[t_check()], rewards=[r_item("minecraft:golden_apple"), r_xp(60)]),
        ],
    },
]


def quest_snbt(q):
    tasks = ",\n".join(f'\t\t\t\t{{ id: "{qid(q["key"] + ":task:" + str(i))}", {t} }}' for i, t in enumerate(q["tasks"]))
    rewards = ",\n".join(f'\t\t\t\t{{ id: "{qid(q["key"] + ":reward:" + str(i))}", {r} }}' for i, r in enumerate(q["rewards"]))
    deps = ", ".join(f'"{qid(d)}"' for d in q.get("deps", []))
    desc = ", ".join(s(line) for line in "\n".join(q["desc"]).split("\n"))
    return (f'\t\t{{\n\t\t\tid: "{qid(q["key"])}"\n\t\t\ttitle: {s(q["title"])}\n\t\t\tsubtitle: {s(q["sub"])}\n'
            f'\t\t\tdescription: [{desc}]\n\t\t\tx: {float(q["x"])}d\n\t\t\ty: {float(q["y"])}d\n'
            f'\t\t\tshape: "{"gear" if q.get("main") else "circle"}"\n' + (f'\t\t\tsize: 1.5d\n' if q.get("main") else "")
            + f'\t\t\tdependencies: [{deps}]\n\t\t\ttasks: [\n{tasks}\n\t\t\t]\n\t\t\trewards: [\n{rewards}\n\t\t\t]\n\t\t}}')


def main():
    os.makedirs(os.path.join(OUT, "chapters"), exist_ok=True)
    shutil.rmtree(os.path.join(OUT, "lang"), ignore_errors=True)
    with open(os.path.join(OUT, "data.snbt"), "w") as f:
        f.write('{\n\tversion: 13\n\ttitle: "Terrestrial Tribulations"\n\ticon: { Count: 1b, id: "minecraft:book" }\n\tgrid_scale: 0.5d\n'
                '\tdefault_reward_team: false\n\tdefault_consume_items: false\n\tdefault_quest_shape: "circle"\n'
                '\tdrop_book_on_death: false\n\tpause_game: false\n\tprogression_mode: "linear"\n\tdetection_delay: 20\n}\n')
    with open(os.path.join(OUT, "chapter_groups.snbt"), "w") as f:
        f.write("{\n\tchapter_groups: [ ]\n}\n")
    lang = []
    all_keys = {q["key"] for c in CHAPTERS for q in c["quests"]}
    for i, c in enumerate(CHAPTERS):
        for q in c["quests"]:
            for d in q.get("deps", []):
                assert d in all_keys, f"missing dependency {d} in {q['key']}"
            lang.append(f'\tquest.{qid(q["key"])}.title: {s(q["title"])}')
            lang.append(f'\tquest.{qid(q["key"])}.quest_subtitle: {s(q["sub"])}')
            lang.append(f'\tquest.{qid(q["key"])}.quest_desc: [' + ", ".join(s(l) for l in "\n".join(q["desc"]).split("\n")) + "]")
        lang.append(f'\tchapter.{qid("chapter:" + c["key"])}.title: {s(c["title"])}')
        body = ",\n".join(quest_snbt(q) for q in c["quests"])
        with open(os.path.join(OUT, "chapters", c["key"] + ".snbt"), "w") as f:
            f.write(f'{{\n\tid: "{qid("chapter:" + c["key"])}"\n\tgroup: ""\n\torder_index: {i}\n\tfilename: "{c["key"]}"\n'
                    f'\ttitle: {s(c["title"])}\n\ticon: {item(c["icon"])}\n\tdefault_quest_shape: ""\n\tdefault_hide_dependency_lines: false\n'
                    f'\tquest_links: [ ]\n\timages: [ ]\n\tquests: [\n{body}\n\t]\n}}\n')
    # circular dependency check
    deps = {q["key"]: q.get("deps", []) for c in CHAPTERS for q in c["quests"]}
    def visit(k, stack):
        assert k not in stack, f"circular dependency at {k}"
        for d in deps[k]:
            visit(d, stack | {k})
    for k in deps:
        visit(k, set())
    print(f"Generated {sum(len(c['quests']) for c in CHAPTERS)} quests in {len(CHAPTERS)} chapters (no missing or circular dependencies).")


if __name__ == "__main__":
    main()
