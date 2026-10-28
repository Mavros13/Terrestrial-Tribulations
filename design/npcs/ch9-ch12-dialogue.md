# Story NPCs: Chapters 9–12 (Easy NPC dialogue scripts)

Same setup as `ch1-ch2-dialogue.md`. Quest names in *italics* are working titles until the quest book is built.
Story beats (`docs/00-kickoff.md`, `design/story/boss-roles.md`, `design/story/heroes-integration.md`): **Ch9 War of the Realms**: the first Choir Herald (**The Harbinger**) falls (stage `tt_ch9_marks`, Harbinger's Railblade), the **Leviathan** the Choir woke (Abyssal Longbow), the Siege of Emberhold, city stage 4. **Ch10 The Mythic Crucible**: the Artifact Forge and the Crucible trials (Ender Guardian, Maledictus, Ancient Remnant; stage `tt_ch10_echoes`), Crown Shards #6–7, the Crownshard Karambits. **Ch11 The Final Convergence**: the Thornecutter is forged, the Ender Dragon as Malric's bound beast, then **Malric, the Hollow Regent** (boss still to be picked after Test Build 2). **Ch12 Beyond the Throne**: the ending choice (reforge the Crown, let Malric take it, or shatter it: the canonical ending), city stage 5, the Emberhold Oathblade.

## Captain Rhosk: war (Ch9)

**Dialogue: "The Herald"** (Ch9 opener, *War of the Realms*)
1. **Rhosk:** The Choir has stopped hiding. A war-machine walks the eastern road, and it sings while it kills.
2. **Rhosk:** They call it a Herald. My scouts call it other things.
   - ▶ "Then we stop it before it reaches anyone." → 3
   - ▶ "Can the Thornwatch hold it?" → 4
3. **Rhosk:** Good. That's the first order I've liked from you. → 5
4. **Rhosk:** No. That's why I'm asking you. It costs me something to say that. → 5
5. **Rhosk:** Bring it down. Whatever is inside, bring it to your tinker. *(boss: the Harbinger; grants `tt_ch9_marks` and the Harbinger core)*

**Dialogue: "Hold the Walls"** (Ch9 climax, *The Siege of Emberhold*)
1. **Rhosk:** They're coming for your city now. Hollowed, Choir soldiers, and things I don't have names for.
2. **Rhosk:** The Thornwatch will stand on Emberhold's walls. All of us. I don't think we've ever done that for anyone.
   - ▶ "Thank you." → 3
   - ▶ "Why now?" → 4
3. **Rhosk:** Thank me after. → 5
4. **Rhosk:** Because you held the Thorn Gate for us when you didn't have to. The Thornwatch pays its debts. → 5
5. **Rhosk:** Ring the bell when you're ready. *(starts the siege wave event; city stage 4 on success)*

## Pell: the Railblade (Ch9)

**Dialogue: "Rail Lance"** (Ch9, after the Harbinger)
1. **Pell:** Its core is a *rail accelerator*. Do you know what that means? It means it throws things very, very fast.
2. **Pell:** I've built it into a blade. Charge it and point it at something you dislike. Possibly from a distance. Definitely from a distance.
   - ▶ "Is it safe?" → 3
   - ▶ "Perfect." → 4
3. **Pell:** Nothing about this week is safe. → 4
4. **Pell:** Also, the core unlocks the bigger Mark suits. The Choir's blueprints made sense once I had a real one in my hands. *(rewards Harbinger's Railblade; higher Satsu Marks open)*

## Wren: the drowned city (Ch9 side)

**Dialogue: "Something in the Water"** (Ch9 side, *The Sunken City*)
1. **Wren:** So. I found a city. Under the sea. With lights on.
2. **Wren:** And something huge moving around it. The Choir woke it, I think; their ships have been circling for weeks.
   - ▶ "Show me." → 3
   - ▶ "Leave it sleeping." → 4
3. **Wren:** I knew you'd say that. Here's the map. I drew the big thing smaller than it is so you wouldn't worry. → end
4. **Wren:** It's not sleeping anymore. That's the problem. Here's the map. *(marks the sunken city; the Leviathan's scales go to Doran for the Abyssal Longbow)*

## Doran: Ch9–10 forging

**Dialogue: "Undertow"** (Ch9, with Leviathan scales)
1. **Doran:** These scales are still wet. They've been out of the sea a week.
2. **Doran:** A bow, I think. The string from its sinew. Whatever you shoot will want to come back to the deep. *(rewards Abyssal Longbow)*

**Dialogue: "The Last Karambits"** (Ch10, with two Crown Shard fragments)
1. **Doran:** I made your first karambit from scrap. Then from Hollow bone. Now you hand me pieces of a crown.
   - ▶ "You're the only one I'd trust with them." → 2
   - ▶ "Can you do it?" → 3
2. **Doran:** Hm. ...Don't say things like that while I'm holding a hammer. → 4
3. **Doran:** I've never done anything else. → 4
4. **Doran:** *(the next morning)* They hum. I don't like it. You will. *(rewards Crownshard Karambits)*

## Ilsabet: the Crucible (Ch10)

**Dialogue: "The Mythic Crucible"** (Ch10 opener)
1. **Ilsabet:** I've translated the last of Ysolde's margins. She didn't hide the final Shards in realms. She hid them in *trials*.
2. **Ilsabet:** The Crucible. A place the Crown built to test its bearers. Whatever guards it was made to be unbeatable by anyone unworthy.
   - ▶ "And if I'm unworthy?" → 3
   - ▶ "Then I'll be worthy." → 4
3. **Ilsabet:** Then we'll have learned something, and I'll write a very sad footnote. → 5
4. **Ilsabet:** Confidence. How refreshing, and how statistically unwise. → 5
5. **Ilsabet:** There are three tiers. Each opens the next. Take the Artifact Forge plans; you'll need everything it can make. *(opens the Crucible tiers I–III and the Artifact Forge; tier I grants `tt_ch10_echoes`)*

## Elder Maera: the long road (Ch10–11)

**Dialogue: "Seven"** (Ch10 finale, all seven Shards held)
1. **Maera:** Seven. All of them. You're holding the Crown in pieces.
2. **Maera:** Can you still hear yourself under his voice?
   - ▶ "Yes. Barely." → 3
   - ▶ "I'm not sure anymore." → 4
3. **Maera:** Barely is enough. It's always been enough for us. → 5
4. **Maera:** Then listen to mine. You are a child of this city. You ate my soup. You complained about it. → 5
5. **Maera:** He'll open the Convergence now. He has to; you have everything he needs. Doran's forging something for you. Go and see him. *(Chapter 11 begins)*

## Doran: the Thornecutter (Ch11)

**Dialogue: "One Blade"** (Ch11 opener, *The Final Convergence*)
1. **Doran:** Every blade I ever made for you was so you'd come back.
2. **Doran:** This one's different. This one's made to kill one thing. The Regent. Nothing else will feel it the same way.
   - ▶ "What's it made of?" → 3
   - ▶ "Thank you, Doran." → 4
3. **Doran:** A bit of everything you brought me. Ash. Fang. Iron. Crown. → 5
4. **Doran:** Hm. ...Come back. → 5
5. **Doran:** Thornecutter. Don't let him talk you out of swinging it. *(rewards Thornecutter; the Convergence opens)*

## Malric, the Hollow Regent: what the voice says (Ch11)
Malric is an existing boss renamed in lore (see `design/story/boss-roles.md`), not an Easy NPC. These lines are for the boss-bar name, title messages (`/title`) and quest text at each phase.
- **Arrival:** "Shard-Born. Little splinter of my Crown. Did you think you found them? They found you, for me."
- **Bound beast (the Ender Dragon) falls:** "You cut the leash. It doesn't matter. I don't need the beast. I need you to finish what Ysolde started."
- **Phase 2:** "Look at your world. Ash, Hollowed, cults in stolen armour. That's the Sundering's gift. One will, one Crown, and all of it ends."
- **Phase 3:** "You were made from the Crown. You *are* order. Stop fighting what you are."
- **Defeat:** "Then choose. You'll find it's harder than killing me."

## The ending choice (Ch12 opener, *Beyond the Throne*)
Spoken by Maera at the Convergence's heart (Easy NPC placed there for the scene) or as quest text. Each option is a quest in an FTB Quests `or` group.
1. **Maera:** It's over. And it isn't. The Crown is whole again in your hands.
2. **Maera:** You could wear it. No more Hollowed, no more Choir. Everyone safe, forever, because you'd decide what safe means.
3. **Maera:** You could give it to him. He's broken, but he isn't gone. He'd stop pretending to be kind.
4. **Maera:** Or you could do what Ysolde did. Break it. Properly, this time, so it can't come back. The realms drift apart. Nobody ever holds this much again. Not even you.
   - ▶ "Reforge it." → *(ending: The New Crown)*
   - ▶ "Let him have it." → *(ending: The Regent's Peace)*
   - ▶ "Shatter it." → *(canonical ending: The Free Realms)*
5. **Maera:** *(after Shatter)* Thank you. Now come home. We have a city to finish. *(city stage 5 work begins; the Infinite Crucible opens)*

## Ch12 postgame lines
**Maera:** "A Legendary Kingdom. I said forty mouths once. Now I can't count them." · *(when Emberhold reaches city stage 5)* "This is yours. Hold it." *(rewards the Emberhold Oathblade)*
**Pell:** "Infinite Crucible! Infinite! I've made a chart."
**Rhosk:** "The Thornwatch serves Emberhold now. Don't make me regret it. ...I won't."
**Ilsabet:** "I've written you into the histories. You come off rather well. Mostly."
**Doran:** "Hm. Good."
