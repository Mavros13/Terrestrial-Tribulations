"""Writes the story NPCs as Easy NPC data-pack presets: pack/kubejs/data/tt/easy_npc/preset/<model>/<npc>.npc.snbt.
Source: the dialogue scripts in design/npcs/ch*-dialogue.md (edit those, not the presets). Run by build_prism.py.

Format checked against Easy NPC's 1.20.1 source (MarkusBordihn/BOs-Easy-NPC, default presets in
core/Common/src/main/resources/data/easy_npc/default_preset/, DataPresetDataFiles.java): data-pack presets live in
data/<namespace>/easy_npc/preset/ (since 6.x), are SNBT with PresetMetadata + data (the entity NBT), and dialogs are
DialogData.DialogDataSet entries (Label <= 32 chars, Texts picked at random, Buttons with OPEN_NAMED_DIALOG actions).
Place one in the world with:  /easy_npc preset import_new data tt:easy_npc/preset/<model>/<npc>.npc.snbt ~ ~ ~

Each NPC gets a "default" hub dialog (opened on right-click) with one button per scripted conversation, labelled with
its chapter, plus "Chat" (the ambient lines). Every script line is its own dialog; reply buttons follow the script's
arrows, and lines without replies get a "..." button to the next line. Trailing *(mechanics notes)* are left out:
rewards stay in the quest book, so talking never hands out items twice."""
import os, re

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
MAX_HUB = 5  # conversation buttons per hub page; the rest go behind "More..."


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
    npcs = {k: {"talks": [], "chat": []} for k in CAST}
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
            m = re.match(r'\*\*Dialogue: "([^"]+)"\*\*\s*\((.*)\)', line)
            if m and owner:
                talk = {"title": m.group(1), "ch": chapter(m.group(2)), "lines": []}
                npcs[owner]["talks"].append(talk)
                continue
            m = re.match(r"(\d+)\. \*\*([^*]+):\*\* (.*)", line)
            if m and talk is not None:
                nxt = re.search(r"→\s*(\d+)\s*$", m.group(3))
                talk["lines"].append({"n": int(m.group(1)), "text": clean(m.group(3)), "opts": [],
                                      "next": int(nxt.group(1)) if nxt else None})
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


def button(name, label, target):
    return "{Actions:[{Cmd:%s,Type:\"OPEN_NAMED_DIALOG\"}],Label:%s,Name:%s}" % (s(target), s(label), s(name))


def close_button(label):
    return "{Actions:[{Type:\"CLOSE_DIALOG\"}],Label:%s,Name:\"Goodbye\"}" % s(label)


def dialog(label, name, texts, buttons):
    b = f"Buttons:[{','.join(buttons)}]," if buttons else ""
    t = ",".join("{Text:%s}" % s(x) for x in texts)
    return "{%sLabel:%s,Name:%s,Texts:[%s]}" % (b, s(label), s(name[:32]), t)


def build(key, data):
    names, display, color, model, variant = CAST[key]
    dialogs, hub = [], []
    for i, talk in enumerate(data["talks"]):
        if not talk["lines"]:
            continue
        base = f"t{i}"
        hub.append((f"{talk['ch']} · {talk['title']}".strip(" ·"), f"{base}_{talk['lines'][0]['n']}"))
        nums = [ln["n"] for ln in talk["lines"]]
        for j, ln in enumerate(talk["lines"]):
            buttons = []
            for k, (reply, tgt) in enumerate(ln["opts"]):
                buttons.append(button(reply, f"{base}_{ln['n']}_b{k}", f"{base}_{tgt}") if tgt in nums
                               else close_button(f"{base}_{ln['n']}_b{k}").replace('Name:"Goodbye"', "Name:" + s(reply)))
            if not buttons:
                nxt = ln["next"] if ln["next"] in nums else (nums[j + 1] if j + 1 < len(nums) else None)
                buttons.append(button("...", f"{base}_{ln['n']}_b", f"{base}_{nxt}") if nxt else button("Back", f"{base}_{ln['n']}_b", "default"))
            dialogs.append(dialog(f"{base}_{ln['n']}", f"{talk['title']} {ln['n']}", [ln["text"]], buttons))
    if data["chat"]:
        dialogs.append(dialog("chat", "Chat", data["chat"], [button("Back", "chat_b", "default")]))
    # hub pages
    pages = [hub[i:i + MAX_HUB] for i in range(0, len(hub), MAX_HUB)] or [[]]
    for p, page in enumerate(pages):
        label = "default" if p == 0 else f"more{p}"
        buttons = [button(n, f"h{p}_{k}", tgt) for k, (n, tgt) in enumerate(page)]
        if p + 1 < len(pages):
            buttons.append(button("More...", f"h{p}_more", f"more{p + 1}"))
        if p == 0 and data["chat"]:
            buttons.append(button("Chat", "h0_chat", "chat"))
        buttons.append(close_button(f"h{p}_close"))
        greet = data["chat"][:3] or ["Yes?"]
        dialogs.append(dialog(label, display if p == 0 else f"{display} {p + 1}", greet if p == 0 else ["What else?"], buttons))
    meta = ("PresetMetadata:{author:\"Terrestrial Tribulations\",category:\"Story\",description:%s,"
            "entityTypeId:\"easy_npc:%s\",name:%s,variantType:%s,version:\"1.0.0\"}") % (
        s(f"Story NPC generated by tools/gen_npcs.py from design/npcs/. {len(hub)} conversations."), model, s(display), s(variant))
    body = ("data:{CustomName:%s,DialogData:{DialogDataSet:[%s],Type:\"STANDARD\"},EasyNPCVersion:3,Invulnerable:1b,"
            "ObjectiveData:{ObjectiveDataSet:[{Type:\"LOOK_AT_PLAYER\"},{Type:\"LOOK_AT_RESET\"}]},PersistenceRequired:1b,"
            "VariantType:%s,id:\"easy_npc:%s\"}") % (
        s('{"color":"%s","text":"%s"}' % (color, display)), ",\n".join(dialogs), s(variant), model)
    return model, "{\n" + meta + ",\n" + body + "\n}\n", len(hub), len(dialogs)


def main():
    npcs = parse()
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
