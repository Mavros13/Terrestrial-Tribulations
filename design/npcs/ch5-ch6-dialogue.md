# Story NPCs: Chapters 5–6 (Easy NPC dialogue scripts)

Same setup as `ch1-ch2-dialogue.md`: Easy NPC editor, *Advanced Dialog* for reply buttons. Quest names in *italics* are working titles until the quest book is built.
Story beats (`docs/00-kickoff.md`, `design/story/boss-roles.md`): **Ch5 Kingdoms in Conflict**: the player helps the Lumen Conclave or the Cogwright Guild (both stay open; the story needs either), Emberhold reaches city stage 3 (Town), and the Thornwatch siege ends with the **Night Lich** (BoMD), the first Hollow general. **Ch6 The Arcane & Mechanical Age**: full magic and AE2, the Nether arc against **Ignis** (Cataclysm), and Wren's northern side quest to **Frostmaw** (Mowzie's Mobs). "The Stranger" (secretly Iron Choir) arrives here to set up Ch8.

## Ilsabet: Lumen Conclave enchanter (Ch5 on)
**Look:** tall, pale, silver circlet, robes that shift from violet to white in the light, ink-stained fingers. **Voice:** precise, a little cold, curious about the player the way a scholar is curious about a specimen.
**Role:** Conclave faction lead; gives the Prism Ward Staff; later the enchanting and spell-upgrade NPC. Placement: the Conclave tower in Emberhold (Town stage).
**Trades:** lapis ×12 → arcane essence ×4 · amethyst shard ×8 → blank rune ×2 · Crown Shard dust ×1 → ink of the scholar ×1

**Dialogue: "A Specimen"** (Ch5, *The Conclave's Offer*)
1. **Ilsabet:** So you're the Shard-Born. I expected you to glow.
   - ▶ "Disappointed?" → 2
   - ▶ "What does the Conclave want?" → 3
2. **Ilsabet:** Intrigued. Things that glow are easy to understand. → 3
3. **Ilsabet:** Knowledge. The Convergence was a lattice of ley-lines. You are, as far as I can tell, a piece of it that learned to walk. I would like to know how.
   - ▶ "And in return?" → 4
   - ▶ "I'm not your experiment." → 5
4. **Ilsabet:** Spells. Real ones, not hedge-witch tricks. And a tower in your city that keeps the Hollowed at a distance. → 6
5. **Ilsabet:** Everyone is someone's experiment. I'm only honest about it. → 6
6. **Ilsabet:** The Cogwrights will offer you engines. Take them too, if you like. But engines don't answer when the Regent whispers. *(starts the Conclave line; unlocks the Iron's Spells tab)*

**Dialogue: "Bent Light"** (Ch5, Conclave line complete)
1. **Ilsabet:** You did what I asked, and faster than my apprentices. Insulting, really.
2. **Ilsabet:** Take this. Light bends around it, and so does anything thrown at you while you cast. *(rewards Prism Ward Staff)*
3. **Ilsabet:** One more thing. When you hear him, the Regent, write down exactly what he says. Words are evidence. *(unlocks the "Regent's Words" collection log)*

**Ambient:** "Don't touch the circle." · "Mana is a debt. Spend it wisely." · "Interesting. No, not you. Well, also you."

## Pell: the Cogwright offer (Ch5)

**Dialogue: "The Guild Wants You"** (Ch5, *The Cogwright Offer*)
1. **Pell:** I told the Guild about you. They didn't believe me. Then I told them about the Foundry guardian and they *really* didn't believe me.
2. **Pell:** Anyway. They want a workshop in Emberhold. Real machines. Trains, eventually! Probably! If someone lays track!
   - ▶ "What do I get?" → 3
   - ▶ "Ilsabet says engines can't help against the Regent." → 4
3. **Pell:** Power. Storage that thinks for itself. A Breaker that doesn't need re-gluing. → 5
4. **Pell:** Ilsabet says a lot of things. The Old Engines ran on the *same* ley-lines her spells do. She just doesn't like that a gear understands them better. → 5
5. **Pell:** Build us a workshop and power it, and the Guild's yours. Mostly. They're very argumentative. *(starts the Cogwright line; the Breaker upgrades complete here)*

## Captain Rhosk: the Thornwatch siege (Ch5)

**Dialogue: "Old Walls"** (Ch5, *The Thornwatch Siege*)
1. **Rhosk:** Emberhold has walls now. Good walls. I said I'd see whether you deserved them.
2. **Rhosk:** Our fortress at the Thorn Gate is under siege. Not the usual Hollowed rabble. Something leads them. Something that remembers how to command.
   - ▶ "We'll help." → 3
   - ▶ "Why should Emberhold bleed for you?" → 4
3. **Rhosk:** Then you're more honourable than your settlement's size suggests. → 5
4. **Rhosk:** Because if the Thorn Gate falls, the next walls it reaches are yours. → 5
5. **Rhosk:** Bring every fighter you can spare. And bring that strange luck of yours. *(starts the siege; boss: the Night Lich)*

**Dialogue: "The Halberd"** (Ch5 finale, after the Night Lich)
1. **Rhosk:** A Hollow general. With a crown of bone and a voice like a tomb. The old kingdom's histories never mentioned *those*.
   - ▶ "It spoke to me before it died." → 2
   - ▶ "It's done. That's what matters." → 3
2. **Rhosk:** Then keep that to yourself. Some of my soldiers already whisper that you're half-Hollow. → 4
3. **Rhosk:** It matters. It also means there will be more of them. → 4
4. **Rhosk:** The Thornwatch pays its debts. This halberd held the Thorn Gate for three hundred years. Hold something with it. *(rewards Thornwatch Halberd; Emberhold reaches city stage 3 when the Town Hall is upgraded)*

**Ambient (Ch5 on):** "Stand straight. People are watching you now." · "My soldiers still don't trust you. I've told them to try harder." · "The Thorn Gate stands. That's your doing."

## The Stranger: arrives in Ch6 (secretly Iron Choir; revealed in Ch8)
**Look:** a traveller in a grey coat, too clean for the road, gloves never off, polite smile. **Voice:** warm, flattering, asks more than it answers. Never says where it's from.
**Role:** merchant of rare Old Engine parts; quietly gathers information about the player and the Shards. Players who read closely should be suspicious; nothing in Ch6 confirms it.
**Trades:** emerald ×6 → Old Engine fragment ×1 · emerald ×12 → precision mechanism ×2 · Crown Shard dust ×1 → emerald ×20 (*a very generous price, which is the point*)

**Dialogue: "A Kind Word"** (Ch6, first meeting)
1. **The Stranger:** The Shard-Born of Emberhold! I've heard so much. All good, of course.
   - ▶ "Who are you?" → 2
   - ▶ "Heard from whom?" → 3
2. **The Stranger:** A trader. A collector. Someone who appreciates the old craft. → 4
3. **The Stranger:** Oh, people talk. Travellers, soldiers. Everyone likes a hero. → 4
4. **The Stranger:** If you ever find more of those Shards, I'd pay handsomely just to *study* one. Purely academic.
   - ▶ "Not for sale." → 5
   - ▶ "I'll think about it." → 6
5. **The Stranger:** Of course, of course. The offer stands. → end
6. **The Stranger:** That's all I ask. *(adds the Stranger's trades)*

**Ambient:** "Fine weather for it." · "Such a clever city. Who designed the walls?" · "Do give my regards to the Elder."

## Wren: scout, northern side quest (Ch6)
**Look:** young, wiry, fur-lined hood, a dozen maps rolled in her belt. **Voice:** quick, cheerful, exaggerates everything.
**Role:** exploration quests; points the player to Frostmaw and, later, to dimension portals.

**Dialogue: "The Big White"** (Ch6 side, *North of Everything*)
1. **Wren:** You've been everywhere, right? Wrong! You haven't been north.
2. **Wren:** There's a thing up there. Big. White. Tusks like *this*. The villagers call it Frostmaw and leave it offerings.
   - ▶ "So leave it alone." → 3
   - ▶ "Show me." → 4
3. **Wren:** It ate the offerings. And the village's goats. And some of the village. → 4
4. **Wren:** Here's a map. I marked where I *think* it sleeps. If I'm wrong, run. *(marks the Frostmaw area; the Frostmaw Fang drops from it)*

**Ambient:** "I found a cave shaped like a nose." · "Maps are just promises that something's there." · "Did you know the snow up north is *blue*? It's not. But it could be."

## Doran: the Cinder Crown (Ch6, Nether arc)

**Dialogue: "The King's Fire"** (Ch6, after Ignis)
1. **Doran:** That's the heart of a fire-king? Hm.
2. **Doran:** Hottest thing I'll ever touch. Probably the last, if I'm careless.
   - ▶ "Can you forge it?" → 3
   - ▶ "Too dangerous?" → 4
3. **Doran:** Forge it? No. I can only coax it. → 5
4. **Doran:** Everything worth forging is. → 5
5. **Doran:** *(three days later)* Cinder Crown. Leaves fire where it swings. Mind your own boots. *(rewards Cinder Crown)*

## Elder Maera: Ch5–6 lines
**Ch5 (faction choice):** "The Conclave and the Guild both want to own you. Let them both think they do." · *(city stage 3)* "A Town. We had forty mouths when you found us."
**Ch6 (after the Nether):** "You smell of brimstone. Bathe before you sit on anything." · *(about the Stranger)* "That trader smiles too much. I'm old enough to distrust that."
