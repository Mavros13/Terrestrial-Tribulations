"""Writes the story NPCs as Easy NPC data-pack presets: pack/kubejs/data/tt/easy_npc/preset/<model>/<npc>.npc.snbt.
Source: the dialogue scripts in design/npcs/ch*-dialogue.md (edit those, not the presets). Run by build_prism.py.

Format checked against Easy NPC's 1.20.1 source (MarkusBordihn/BOs-Easy-NPC, default presets in
core/Common/src/main/resources/data/easy_npc/default_preset/, DataPresetDataFiles.java): data-pack presets live in
data/<namespace>/easy_npc/preset/ (since 6.x), are SNBT with PresetMetadata + data (the entity NBT), and dialogs are
DialogData.DialogDataSet entries (Label <= 32 chars, Texts picked at random, Buttons with OPEN_NAMED_DIALOG actions).
Skins: our own textures from tools/gen_npc_skins.py (SkinData Type RESOURCE_LOCATION, Easy NPC 7.8+); the variant
stays as a fallback. Hub buttons carry PLAYER_TAG conditions on the story stages (KubeJS stages are player tags) and
the hub hides locked buttons (dialog Options ButtonConditionMode HIDE); at most six buttons fit on one dialog.
Place one in the world with:  /easy_npc preset import_new data tt:easy_npc/preset/<model>/<npc>.npc.snbt ~ ~ ~

Each NPC gets a "default" hub dialog (opened on right-click) with one button per scripted conversation, labelled with
its chapter, plus "Chat" (the ambient lines). Every script line is its own dialog; reply buttons follow the script's
arrows, and lines without replies get a "..." button to the next line. Trailing *(mechanics notes)* are left out:
rewards stay in the quest book, so talking never hands out items twice."""
import hashlib, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "design", "npcs")
OUT = os.path.join(ROOT, "pack", "kubejs", "data", "tt", "easy_npc", "preset")

# key: (match words in the script's headings/speaker labels, display name, name colour, entity model, skin variant)
CAST = {
    "maera": (["Elder Maera", "Maera"], "Elder Maera", "#D9483B", "humanoid_slim", "MAKENA"),
    "doran": (["Doran"], "Doran", "#E07B2E", "humanoid", "STEVE"),
    "rhosk": (["Captain Rhosk", "Rhosk"], "Captain Rhosk", "#4E8F3A", "humanoid", "KNIGHT_01"),
    "pell": (["Pell"], "Pell", "#C98A3D", "humanoid", "KAI"),
    "tamsin": (["Tamsin Rootwarden", "Tamsin"], "Tamsin Rootwarden", "#3FA34D", "humanoid_slim", "EFE"),
    "ilsabet": (["Ilsabet"], "Ilsabet", "#A77BE0", "humanoid_slim", "MAGE_01"),
    "stranger": (["The Stranger"], "The Stranger", "#9AA0A6", "humanoid", "NOOR"),
    "wren": (["Wren"], "Wren", "#5BB6E0", "humanoid_slim", "ALEX"),
    "sol": (["Archivist Sol", "Sol"], "Archivist Sol", "#D8C27A", "humanoid", "PROFESSOR_01"),
}
# Trade item names as the scripts write them -> item IDs (checked in game by the self-test's npc_trade_items)
TRADE_ITEMS = {
    "iron ingot": "minecraft:iron_ingot", "flint": "minecraft:flint", "emerald": "minecraft:emerald",
    "copper ingot": "minecraft:copper_ingot", "lapis": "minecraft:lapis_lazuli", "amethyst shard": "minecraft:amethyst_shard",
    "Rustbite Karambit": "tt:rustbite_karambit", "bone shard": "tt:bone_shard", "Old Engine fragment": "tt:old_engine_core",
    "Crown Shard dust": "tt:crown_shard_fragment",
    "andesite alloy": "create:andesite_alloy", "shaft": "create:shaft", "cogwheel": "create:cogwheel",
    "precision mechanism": "create:precision_mechanism",
    "arcane essence": "irons_spellbooks:arcane_essence", "blank rune": "irons_spellbooks:blank_rune",
    "ink of the scholar": "irons_spellbooks:rare_ink",
    "coal": "minecraft:coal", "arrow": "minecraft:arrow", "shield": "minecraft:shield", "grindstone": "minecraft:grindstone",
    "large cogwheel": "create:large_cogwheel", "water wheel": "create:water_wheel", "engineer's goggles": "create:goggles",
    "mechanical press": "create:mechanical_press", "paper": "minecraft:paper",
    "common ink": "irons_spellbooks:common_ink", "uncommon ink": "irons_spellbooks:uncommon_ink",
    "diamond": "minecraft:diamond", "name tag": "minecraft:name_tag", "ender pearl": "minecraft:ender_pearl",
    "netherite scrap": "minecraft:netherite_scrap", "totem of undying": "minecraft:totem_of_undying",
}
# "Talk to ..." quests that a conversation completes (owner, 2026-10-29: tick them for the player). The button that
# ends the talk runs FTB Quests' change_progress on the quest's check task (not the quest), so dependencies and
# reward claiming still work as usual: an early talk only fills the checkbox.
TALK_QUESTS = {
    ("maera", "First Meeting"): "c1_smoke", ("maera", "The Voice"): "c4_voice", ("maera", "The Crown Whole"): "c12_choice",
    ("doran", "The King's Fire"): "c6_crown", ("doran", "One Blade"): "c11_blade",
    ("stranger", "A Kind Word"): "c6_stranger", ("stranger", "A Better Offer"): "c8_reveal",
    ("sol", "Seven Pieces"): "c7_sol", ("pell", "Choirbreaker"): "c8_breaker",
}
GREET_QUESTS = {"rhosk": "c2_rhosk"}  # no Ch2 talk: his greeting is the intro, so Goodbye completes it
CHOICE_QUESTS = {"Reforge it.": "c12_reforge", "Let him have it.": "c12_surrender", "Shatter it.": "c12_shatter"}
MAX_BUTTONS = 6  # Easy NPC's dialog screen lays out at most six buttons (DialogScreenLayout); more pile up in one spot


def chapter_tag(ch):
    """Player tag that unlocks a chapter's conversations: the previous chapter's quest stage (KubeJS stages are
    vanilla player tags without Game Stages). Ch1 and Ch2 are open from the start (there is no tt_ch1_done)."""
    n = int(ch[2:]) if ch.startswith("Ch") and ch[2:].isdigit() else 0
    return f"tt_ch{n - 1}_done" if n >= 3 else None


def who(text):
    for key, (names, *_rest) in CAST.items():
        if any(text.startswith(n) for n in names):
            return key
    return None


def clean(text):
    text = re.sub(r"\s*→\s*(\d+|end)\s*$", "", text.strip())
    while True:  # trailing mechanics notes: *(rewards ...)*
        t = re.sub(r"\s*\*\([^()]*(\([^()]*\)[^()]*)*\)\*\s*$", "", text)
        if t == text:
            break
        text = t
    text = re.sub(r"\*\(([^)]*)\)\*", r"(\1)", text)  # scene directions stay, as plain brackets
    return text.replace("*", "").strip()


def chapter(context):
    m = re.search(r"Ch(\d+)", context)
    return f"Ch{m.group(1)}" if m else ""


def parse():
    npcs = {k: {"talks": [], "chat": [], "trades": []} for k in CAST}
    files = sorted(f for f in os.listdir(SRC) if re.match(r"ch\d+-ch\d+-dialogue\.md", f))
    files.sort(key=lambda f: int(re.match(r"ch(\d+)", f).group(1)))
    for f in files:
        owner, talk = None, None
        for raw in open(os.path.join(SRC, f), encoding="utf-8"):
            line = raw.rstrip("\n")
            if line.startswith("## "):
                head = line[3:]
                owner = who(head)
                if head.startswith("The ending choice"):
                    owner = "maera"
                talk = None
                if head.startswith("The ending choice"):
                    talk = {"title": "The Crown Whole", "ch": "Ch12", "lines": []}
                    npcs["maera"]["talks"].append(talk)
                continue
            m = re.match(r"\*\*Trades[^*]*:\*\* (.*)", line)
            if m and owner:
                for t in m.group(1).split(" · "):
                    t = re.sub(r"\s*\(.*\)\s*$", "", t.strip())
                    tm = re.match(r"(.+?) ×(\d+) → (.+?)(?: ×(\d+))?$", t)
                    assert tm, f"{f}: can't read trade '{t}'"
                    npcs[owner]["trades"].append((TRADE_ITEMS[tm.group(1)], int(tm.group(2)),
                                                  TRADE_ITEMS[tm.group(3)], int(tm.group(4) or 1)))
                continue
            m = re.match(r'\*\*Dialogue: "([^"]+)"\*\*\s*\((.*)\)', line)
            if m and owner:
                talk = {"title": m.group(1), "ch": chapter(m.group(2)), "lines": []}
                npcs[owner]["talks"].append(talk)
                continue
            m = re.match(r"(\d+)\. \*\*([^*]+):\*\* (.*)", line)
            if m and talk is not None:
                nxt = re.search(r"→\s*(\d+|end)\s*$", m.group(3))   # "→ end" closes the talk
                talk["lines"].append({"n": int(m.group(1)), "text": clean(m.group(3)), "opts": [],
                                      "next": (int(nxt.group(1)) if nxt.group(1).isdigit() else "end") if nxt else None})
                continue
            m = re.match(r'\s+- ▶ "([^"]+)"\s*→\s*(.*)', line)
            if m and talk is not None and talk["lines"]:
                tgt = m.group(2).strip()
                talk["lines"][-1]["opts"].append((m.group(1), int(tgt) if tgt.isdigit() else None))
                continue
            m = re.match(r"(?:- )?\*\*([^*]+):\*\*(.*)", line)
            if m and not line.startswith(("**Look", "**Role", "**Trades", "**Dialogue", "**Voice")):
                talk = None
                speaker = who(m.group(1)) or owner
                quotes = re.findall(r'"([^"]+)"', m.group(2))
                if speaker and quotes:
                    npcs[speaker]["chat"] += [q.replace("*", "") for q in quotes]
    return npcs


def s(v):
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'


def quest_task(key):
    """FTB Quests id of a quest's first task, as gen_quests.py writes it."""
    return hashlib.md5(("tt:" + key + ":task:0").encode()).hexdigest()[:16].upper()


def complete(keys):
    """COMMAND actions run by the NPC (not the player) at permission level 2, which change_progress needs. The preset
    import clamps both levels to the importer's own (Easy NPC PresetSanitizer), so an op places working NPCs."""
    return "".join(",{Cmd:%s,PermLevel:2,Type:\"COMMAND\"}" % s(f"/ftbquests change_progress @initiator complete {quest_task(k)}")
                   for k in keys)


def button(name, label, target, tag=None, quests=()):
    cond = "Conditions:[{Name:%s,Type:\"PLAYER_TAG\"}]," % s(tag) if tag else ""
    return "{Actions:[{Cmd:%s,Type:\"OPEN_NAMED_DIALOG\"}%s],%sLabel:%s,Name:%s}" % (
        s(target), complete(quests), cond, s(label), s(name))


def close_button(label, name="Goodbye", quests=()):
    return "{Actions:[{Type:\"CLOSE_DIALOG\"}%s],Label:%s,Name:%s}" % (complete(quests), s(label), s(name))


def dialog(label, name, texts, buttons, hide_locked=False):
    assert len(buttons) <= MAX_BUTTONS, f"{label}: {len(buttons)} buttons, Easy NPC shows at most {MAX_BUTTONS}"
    b = f"Buttons:[{','.join(buttons)}]," if buttons else ""
    o = "Options:{ButtonConditionMode:\"HIDE\"}," if hide_locked else ""
    t = ",".join("{Text:%s}" % s(x) for x in texts)
    return "{%sLabel:%s,Name:%s,%sTexts:[%s]}" % (b, s(label), s(name[:32]), o, t)


def trading(trades):
    """Easy NPC BASIC trading: TradingData.TradingDataSet (type, limits, restock) and the vanilla MerchantOffers list
    under Offers.Recipes (TradingDataCapable / TradingDataSet in Easy NPC's 1.20.1 source)."""
    if not trades:
        return ""
    offers = ",".join(
        "{buy:{Count:%db,id:%s},maxUses:16,priceMultiplier:0.0f,rewardExp:1b,sell:{Count:%db,id:%s},uses:0,xp:2}"
        % (n_in, s(i_in), n_out, s(i_out)) for i_in, n_in, i_out, n_out in trades)
    return ("Offers:{Recipes:{Recipes:[%s]}},TradingData:{TradingDataSet:{MaxUses:16,ResetsEveryMin:20,RewardedXP:2,"
            "Type:\"BASIC\"}}," % offers)


def build(key, data):
    names, display, color, model, variant = CAST[key]
    dialogs, hub = [], []
    for i, talk in enumerate(data["talks"]):
        if not talk["lines"]:
            continue
        base = f"t{i}"
        hub.append((talk["title"], f"{base}_{talk['lines'][0]['n']}", chapter_tag(talk["ch"])))
        nums = [ln["n"] for ln in talk["lines"]]
        done = [TALK_QUESTS[(key, talk["title"])]] if (key, talk["title"]) in TALK_QUESTS else []
        for j, ln in enumerate(talk["lines"]):
            buttons = []
            for k, (reply, tgt) in enumerate(ln["opts"]):   # a reply that ends the talk completes its quest
                buttons.append(button(reply, f"{base}_{ln['n']}_b{k}", f"{base}_{tgt}") if tgt in nums
                               else close_button(f"{base}_{ln['n']}_b{k}", reply,
                                                 done + ([CHOICE_QUESTS[reply]] if reply in CHOICE_QUESTS else [])))
            if not buttons:
                nxt = ln["next"] if ln["next"] in nums else (nums[j + 1] if j + 1 < len(nums) and ln["next"] != "end" else None)
                buttons.append(button("...", f"{base}_{ln['n']}_b", f"{base}_{nxt}") if nxt
                               else button("Back", f"{base}_{ln['n']}_b", "default", quests=done))
            dialogs.append(dialog(f"{base}_{ln['n']}", f"{talk['title']} {ln['n']}", [ln["text"]], buttons))
    if data["chat"]:
        dialogs.append(dialog("chat", "Chat", data["chat"], [button("Back", "chat_b", "default")]))
    # hub pages: talks of chapters the player hasn't reached are hidden (button conditions on the story stage tags)
    trade_tag = hub[0][2] if hub else None                             # the shop opens with the NPC's first talk
    pages, rest, first = [], list(hub), True
    while first or rest:
        fixed = 1 + ((1 if data["chat"] else 0) + (1 if data["trades"] else 0) if first else 0)  # Goodbye/Back, Chat, Trade
        cap = MAX_BUTTONS - fixed
        take = rest[:cap] if len(rest) <= cap else rest[:cap - 1]      # leave room for "More..."
        pages.append(take)
        rest, first = rest[len(take):], False
    for p, page in enumerate(pages):
        label = "default" if p == 0 else f"more{p}"
        buttons = [button(n, f"h{p}_{k}", tgt, tag) for k, (n, tgt, tag) in enumerate(page)]
        if p + 1 < len(pages):
            buttons.append(button("More...", f"h{p}_more", f"more{p + 1}", pages[p + 1][0][2]))
        if p == 0 and data["trades"]:
            cond = "Conditions:[{Name:%s,Type:\"PLAYER_TAG\"}]," % s(trade_tag) if trade_tag else ""
            buttons.append("{Actions:[{Type:\"OPEN_TRADING_SCREEN\"}],%sLabel:\"h0_trade\",Name:\"Trade\"}" % cond)
        if p == 0 and data["chat"]:
            buttons.append(button("Chat", "h0_chat", "chat"))
        buttons.append(close_button(f"h{p}_close", quests=[GREET_QUESTS[key]] if key in GREET_QUESTS else [])
                       if p == 0 else button("Back", f"h{p}_back", "default"))
        greet = data["chat"][:3] or ["Yes?"]
        dialogs.append(dialog(label, display if p == 0 else f"{display} {p + 1}", greet if p == 0 else ["What else?"],
                              buttons, hide_locked=True))
    meta = ("PresetMetadata:{author:\"Terrestrial Tribulations\",category:\"Story\",description:%s,"
            "entityTypeId:\"easy_npc:%s\",name:%s,variantType:%s,version:\"1.0.0\"}") % (
        s(f"Story NPC generated by tools/gen_npcs.py from design/npcs/. {len(hub)} conversations."), model, s(display), s(variant))
    body = ("data:{CustomName:%s,DialogData:{DialogDataSet:[%s],Type:\"STANDARD\"},EasyNPCVersion:3,Invulnerable:1b,"
            "ActionData:{ActionPermissionLevel:2},ObjectiveData:{ObjectiveDataSet:[{Type:\"LOOK_AT_PLAYER\"},{Type:\"LOOK_AT_RESET\"}]},PersistenceRequired:1b,"
            "SkinData:{Texture:%s,Type:\"RESOURCE_LOCATION\"},%sVariantType:%s,id:\"easy_npc:%s\"}") % (
        s('{"color":"%s","text":"%s"}' % (color, display)), ",\n".join(dialogs),
        s(f"tt:textures/entity/npc/{key}.png"), trading(data["trades"]), s(variant), model)
    return model, "{\n" + meta + ",\n" + body + "\n}\n", len(hub), len(dialogs)


def main():
    npcs = parse()
    missing = [k for k in TALK_QUESTS if k[1] not in [t["title"] for t in npcs[k[0]]["talks"]]]
    assert not missing, f"TALK_QUESTS names talks that don't exist: {missing}"
    total = 0
    for key, data in npcs.items():
        model, text, talks, n = build(key, data)
        os.makedirs(os.path.join(OUT, model), exist_ok=True)
        with open(os.path.join(OUT, model, key + ".npc.snbt"), "w", encoding="utf-8") as f:
            f.write(text)
        total += talks
    print(f"Story NPCs: {len(npcs)} presets, {total} conversations")


if __name__ == "__main__":
    main()
