# Story NPCs: Chapters 7–8 (Easy NPC dialogue scripts)

Same setup as `ch1-ch2-dialogue.md`. Quest names in *italics* are working titles until the quest book is built.
Story beats (`docs/00-kickoff.md`, `design/story/boss-roles.md`): **Ch7 The Shattered Realms**: the realm portals open (stage `tt_ch7_realms`, see `kubejs/config/tt_story_gates.json`); Shards wait in the Twilight Forest (Naga → Lich → Hydra → Ur-Ghast), the Aether (Slider → Valkyrie Queen → Sun Spirit), the Undergarden (Forgotten Guardian) and the Otherside (Warden), with Alex's Caves as an optional deep-realm Shard. Every Shard makes the Regent's voice clearer. **Ch8 The Rise of Heroes**: the Iron Choir is revealed (the Stranger is one of them), its prototype war-engine (**Netherite Monstrosity**) is defeated, and suit research opens (stage `tt_ch8_heroes`, the hero packs' items).

## Archivist Sol: lore keeper (Ch7 on)
**Look:** elderly, bald, spectacles on a chain, carries a lectern on his back like a pack. **Voice:** gentle, pedantic, loves footnotes.
**Role:** realm briefings before each Shard, the "Regent's Words" and Shard collections, lore unlocks. Placement: the Emberhold library (built at Town stage).

**Dialogue: "Seven Pieces"** (Ch7 opener, *The Shattered Realms*)
1. **Sol:** Ah. The Shard-Born. Do sit; this will take a while, and I've been waiting forty years to say it to someone.
2. **Sol:** When Queen Ysolde broke the Crown, the pieces didn't simply fall. They *fled*, into the realms that the Convergence held together. Each realm closed around its Shard like a fist.
   - ▶ "Where are they?" → 3
   - ▶ "Why can I open the portals now?" → 4
3. **Sol:** A twilit forest under endless dusk. Islands above the clouds. A garden beneath the roots of the world. And somewhere the echo of a sound lives on, the Otherside. → 5
4. **Sol:** Because you carry one already. Shard calls to Shard. The doors remember the Crown. → 5
5. **Sol:** Each realm has a keeper, and none of them will hand it over politely. Shall I tell you which to start with? I have opinions. *(opens the realm briefings: Twilight, Aether, Undergarden, Otherside)*

**Realm briefings (short lines, one per realm):**
- **Twilight:** "The dusk-forest's keepers are a chain: serpent, lich, hydra, and something weeping in a tower. Each guards the next. Tamsin's people know the way in."
- **Aether:** "Above the clouds the Valkyries hold trials. They respect courage, and they enjoy watching people fall."
- **Undergarden:** "Below the roots there's a vault, and a guardian that has forgotten everything except the vault."
- **Otherside:** "Whatever you do down there, do it quietly. Something listens. It hears heartbeats."

**Ambient:** "Footnote seven is the important one." · "Please don't bleed on the scrolls." · "Ysolde wrote in the margins. She had terrible handwriting."

## Tamsin Rootwarden: the Twilight Shard (Ch7)

**Dialogue: "The Long Dusk"** (Ch7, *The Twilight Shard*)
1. **Tamsin:** You planted your saplings. We remember. So now we'll tell you the way into the dusk.
2. **Tamsin:** The Twilight is not ours. It is older. Its keepers were set there by the Crown, and the Crown is gone, so they guard out of habit, and hunger.
   - ▶ "Will the Pact help?" → 3
   - ▶ "What happens when I take the Shard?" → 4
3. **Tamsin:** We'll keep the portal grove safe while you're inside. That is all we can do. → 5
4. **Tamsin:** The dusk will thin. The forest will breathe again. And the voice in your head will speak louder. We hear it too, through the roots. → 5
5. **Tamsin:** Kill the serpent first. Everything after is worse. *(starts the Twilight warden chain; the Hydra drops trophies for the Hydra's Tri-Edge; the Ur-Ghast guards Crown Shard #1)*

## Elder Maera: the voice grows louder (Ch7)

**Dialogue: "Three Shards"** (Ch7, after the third Shard)
1. **Maera:** You haven't slept in days. Don't tell me otherwise; I can see it.
   - ▶ "He talks to me every night now." → 2
   - ▶ "I'm fine." → 3
2. **Maera:** Then tell me what he says. Out loud, here, in the light. Words lose their teeth in daylight. → 4
3. **Maera:** You were a better liar when you first came. You've grown honest, and tired. → 4
4. **Maera:** He wants you to think you're the same, you and him. Both survived the Sundering, both carry the Crown. But he took it. You were *made* from it. That's not the same at all.
5. **Maera:** Finish the realms. Then come home for a while. Emberhold needs to see your face. *(Ch7 completes when all four main Shards are held)*

## The Stranger: the reveal (Ch8)

**Dialogue: "A Better Offer"** (Ch8 opener, *The Iron Choir*; the Stranger's trades are removed after this)
1. **The Stranger:** Four Shards. Remarkable. Truly. My employers are *so* impressed.
   - ▶ "Your employers?" → 2
   - ▶ "I knew it." → 3
2. **The Stranger:** The Iron Choir. We build what the Old Engines could only dream of. Suits that make a person into a weapon. → 4
3. **The Stranger:** Did you? Then you're cleverer than your Elder, who only *suspected*. → 4
4. **The Stranger:** The Regent showed us how. In return, we bring him the Shards. You could join us. We'd give you armour fit for a god.
   - ▶ "No." → 5
   - ▶ "What does the Regent give you?" → 6
5. **The Stranger:** Then we'll take them the hard way. → 7
6. **The Stranger:** A place in the new world. Order. No more Sundering, no more Hollowed, no more choosing. Doesn't that sound restful? → 7
7. **The Stranger:** Our engine is already walking toward your city. Do try to survive it. I've grown fond of you. *(disappears; starts the war-engine quest; boss: the Netherite Monstrosity)*

## Pell: suits (Ch8)

**Dialogue: "Reverse-Engineering"** (Ch8, after the Monstrosity falls)
1. **Pell:** It's *beautiful*. Horrible! But beautiful. Look at the actuators.
2. **Pell:** The Choir didn't invent this. They copied Old Engine war-frames and bolted Shard-power into them. Which means... we can too.
   - ▶ "Should we?" → 3
   - ▶ "Show me." → 4
3. **Pell:** Ilsabet says no. I say they're already using them on us. Rhosk says "hm". → 4
4. **Pell:** Give me time and the parts and I'll get a suit working. Not just one. The Choir's designs are in here; there are dozens. *(grants stage `tt_ch8_heroes`: hero-pack suits and items unlock)*

**Dialogue: "Choirbreaker"** (Ch8, after a Choir Herald falls)
1. **Pell:** Their gauntlets run on an overload circuit. If you punch something hard enough, everything electrical nearby just *stops*.
2. **Pell:** I rewired them for your hands. Please don't punch me. *(rewards Choirbreaker Gauntlets)*

## Ilsabet and Rhosk: Ch8 reactions
**Ilsabet:** "Suits. Of course. When frightened, people build bigger armour. Write down what the Regent says about them; I want to know what he's afraid of." · "If you must wear one, let me ward it. Shard-power leaks."
**Rhosk:** "The Thornwatch fought war-engines once, three centuries ago. We lost." · "A soldier in a suit is still a soldier. Remember which you are."

## Elder Maera: Ch8 lines
"I fed that man soup. Twice." · "Heroes, they'll call you now. Don't let them make you a statue; statues can't run." · *(suit research begins)* "Wear their armour if you must. Don't wear their reasons."
