# Digimon Card Game — Rules Reference (for the Playtest Agent)

Distilled from the **official Comprehensive Rules Manual Ver. 4.1** (last updated 2026‑06‑19).
Source PDF: https://world.digimoncard.com/rule/pdf/general_rule.pdf

This file is the rules authority the playtest agent uses to simulate a game. Card‑specific
text always overrides these general rules (rule 1‑3‑1). When card text and this file
conflict, follow the card.

---

## 1. Objective & win conditions

Two players. You win when any one of these happens:

- Your attacking Digimon makes a successful attack on the opponent **while they have 0
  security cards** (and the attack could perform at least 1 security check).
- Your opponent must draw during their draw phase but their **deck is empty** (deck‑out).
- An effect states a player wins/loses the game, or a player forfeits.

Security cards are the "life". A successful attack on the *player* triggers a **security
check** (flip the top security card and resolve it) instead of dealing damage directly.

---

## 2. Deck & components

- **Main deck:** exactly **50 cards** (Digimon / Tamer / Option). Max **4 copies** per card
  number.
- **Digi‑Egg deck:** **0–5 cards**, max 4 copies per card number. Lv.2 Digi‑Eggs live here.
- **Memory gauge:** one shared gauge, values 10…0…10. Left side = your memory, right side =
  opponent's. Memory never exceeds 10 in either direction.
- **Security stack:** 5 cards set face‑down at game start.

### Card fields used by the agent (from `digimon_cards_dict.json`)

| Field | Meaning |
|---|---|
| `name` | Card name |
| `cardnumber` / `id` | Card number (e.g. `BT1-010`) |
| `type` | `Digimon`, `Tamer`, `Option`, or `Digi-Egg` |
| `color` / `color2` | Card color(s) |
| `level` | Level (Lv.2 egg … Lv.7). `null`/`-` = no level |
| `play_cost` | Memory cost to play from hand |
| `evolution_cost` / `evolution_level` / `evolution_color` | Primary digivolve requirement + cost |
| `dp` | Digimon Power (battle strength) |
| `digi_type`..`digi_type4` | Traits (form/attribute/type) |
| `attribute` / `form` / `stage` | Additional trait info |
| `main_effect` | Upper text (the active effect box) |
| `source_effect` | Inherited effect (gained by whatever digivolves on top of this card) |
| `alt_effect` / `xros_req` | Extra digivolve / DigiXros / DNA lines |
| `link_requirements` / `link_dp` | Link data, if any |

---

## 3. Game areas

Deck, Digi‑Egg deck, **breeding area**, **battle area**, hand, trash, and security stack.
Public areas (trash, battle area, breeding area) are visible to both players; deck, hand,
security stack, Digi‑Egg deck are private.

A card moved between areas becomes a **new card** — it loses all prior states, effects, and
"per turn" counters (except stacking under another card in the battle area).

---

## 4. Setup

1. Both players shuffle deck and Digi‑Egg deck.
2. Rock‑paper‑scissors: winner chooses to go first or second (first player is common).
3. Both draw **5 cards**; each may mulligan once (shuffle back, redraw 5).
4. Each sets the **top 5 cards** of the deck as the face‑down security stack.
5. Memory marker to **0**. First player's turn begins.

---

## 5. Turn structure

Each turn runs four phases in order:

1. **Unsuspend phase** — turn player unsuspends (untaps) all their cards. Resolve any
   `[Start of Your Turn]` effects first.
2. **Draw phase** — draw 1 card. **The first player skips the draw on turn 1 only.**
3. **Breeding phase** — do exactly one of:
   - **Hatch:** if the breeding area is empty, put the top Digi‑Egg face‑up into breeding.
   - **Move:** move the Digimon in the breeding area into the battle area (only if it's Lv.3
     or higher). Once in the battle area it can be attacked/targeted.
   - **Do nothing.**
   > A Digimon in the breeding area is safe: it can't be attacked and can't attack.
4. **Main phase** — take any of the actions below, in any order, any number of times, as long
   as memory/costs allow. The phase (and turn) ends per the memory rule below.

### Main‑phase actions

- **Play** a Digimon or Tamer from hand (pay its play cost). Newly played Digimon **can't
  attack the turn they enter** the battle area (no summoning‑sickness exception unless the
  card has `<Rush>`).
- **Digivolve** a Digimon on the field (or in breeding) into a Digimon card in hand that lists
  a matching digivolve requirement; pay the digivolve cost, then **draw 1 card**. The new card
  stacks on top; lower cards become **digivolution cards** and keep their orientation.
- **Use** an Option card from hand (pay use cost; its `[Main]` effect resolves, then it goes
  to trash unless an effect keeps it).
- **Link** a card with `[Link]` onto one of your Digimon (pay link cost).
- **Attack** with an unsuspended Digimon (see §7).
- **Activate** an `[Main]`/activation‑type effect.
- **Pass:** immediately move memory to **3 on the opponent's side**.

### The memory rule (how turns actually end)

Memory is shared. Paying costs pushes the marker toward the opponent's side. **When, after
all processing resolves, memory is 1+ on the OPPONENT's side, the turn ends** and passes to
them (they start their turn with that much memory as a head start). So a turn continues while
you still have memory (0 or positive on your side); as soon as you go negative (into the
opponent's side) and nothing else is pending, the turn hands over. Passing sets memory to 3
on the opponent's side to end your turn cleanly.

---

## 6. Digivolution details

- A card's digivolve requirement is like "Digivolve from Lv.3 [trait/name]: Cost X". Match the
  requirement to a Digimon you control, pay Cost X of memory, place on top, **draw 1**.
- Digivolving **raises** the Digimon (higher level, new DP, new `main_effect`), and the
  Digimon keeps any **inherited effects** (`source_effect`) from the cards beneath it.
- Digivolving does **not** remove summoning sickness normally, BUT a Digimon that was played
  this turn and then digivolves loses the "played this turn" flag under DNA digivolution
  (8‑2‑2‑1‑7); for standard digivolve the stack can attack if the base could.
- Special digivolutions exist: **DNA Digivolution** (combine two Digimon), **Burst Digivolve**,
  **App Fusion**, **DigiXros** (place named cards underneath to reduce play cost),
  **Assembly** (place named cards from trash underneath). Follow the card's own text.

---

## 7. Attacking, blocking, security, battles

**Only the turn player attacks.** Attack sequence:

1. **Declare attack:** suspend one unsuspended Digimon and choose a target — either the
   **opponent (player)** or one of the opponent's **suspended** Digimon. Resolve `[When
   Attacking]` effects.
2. **Counter timing:** non‑turn player may activate one `[Counter]` effect.
3. **Block timing:** non‑turn player may suspend a `<Blocker>` Digimon to redirect the attack
   to itself.
4. **Resolve:**
   - **Attack on player, opponent has security > 0:** perform a **security check** — flip the
     top security card. If it's a Digimon, a battle happens between it (Security Digimon) and
     the attacker; Security Digimon are **not** deleted if they lose. Option/Tamer security
     effects labeled `[Security]` trigger. The checked card then goes to trash unless placed
     elsewhere.
   - **Attack on player, opponent has 0 security:** the attacker **wins the game** (if it can
     perform a security check).
   - **Attack on a Digimon:** a **battle** occurs.
5. **End of attack.**

**Battle:** compare DP. Higher DP wins; the loser is **deleted** (sent to trash with its
digivolution cards). Equal DP = **both deleted**.

Key combat keywords (full glossary is in the app's **Keywords** tab):
`<Blocker>`, `<Security A. +/-N>` (changes number of security cards checked),
`<Piercing>` (extra security check when it deletes a Digimon in battle),
`<Jamming>` (not deleted by battle with a Security Digimon), `<Rush>` (can attack the turn it
appears), `<Reboot>` (unsuspend on opponent's turn), `<Draw N>`, `<Recovery>`,
`<De-Digivolve N>`, `<Retaliation>`, `<Blitz>` (attack even when memory is on opponent side),
`<Alliance>`, `<Vortex>`, etc.

---

## 8. Effect timings (labels the agent must respect)

Effects fire based on bracketed labels. The agent must announce and resolve each one at the
right moment:

- `[On Play]` — when the card is played from hand.
- `[When Digivolving]` — when this card is the result of a digivolution.
- `[On Deletion]` — when this Digimon is deleted.
- `[When Attacking]` — when this Digimon declares an attack.
- `[Counter]` — usable by the non‑turn player during counter timing.
- `[Security]` — resolves when this card is flipped in a security check.
- `[Main]` — activatable in your main phase.
- `[Start of Your Turn]` / `[End of Your Turn]` / `[End of Opponent's Turn]` — phase timing.
- `[Your Turn]` / `[Opponent's Turn]` / `[All Turns]` — persistent, condition‑gated effects.
- `[Once Per Turn]` / `[X Per Turn]` — usage caps that reset each turn (and on becoming a new
  card).

Effect resolution rules: resolve one effect fully before the next; when multiple trigger at
once the **turn player resolves theirs first**, then the non‑turn player; a **prohibiting**
effect beats an **enabling** effect; mandatory effects must be done when possible; you must
choose at least 1 target when an effect says "choose".

---

## 9. Rule checks (cleanup)

After each action/effect resolves, check the board:

- A Digimon with **0 or less DP** is deleted.
- A Digimon with too many/illegal states is corrected per its text.
- Tamers/Options with no legal place go to trash.

---

## 10. Quick reference for the agent

- First player skips their turn‑1 draw.
- Newly played Digimon can't attack that turn unless it has `<Rush>`.
- Attacking suspends the attacker; targets must be the player or a **suspended** enemy Digimon.
- Digivolving draws a card and keeps inherited effects.
- Security check = flip top security; Digimon security cards fight the attacker but survive.
- Turn ends when memory sits on the opponent's side with nothing pending.
- Win by emptying the opponent's security and hitting them, or by decking them out.
