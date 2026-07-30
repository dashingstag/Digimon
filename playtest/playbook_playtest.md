Playbook: Playtest a Digimon Deck (Play-by-Play)

## Overview
Simulate a game of the Digimon Card Game for one or two given decklists and produce a
readable, turn-by-turn **play-by-play** of the match. The agent looks up every card's real
stats and effects from the repo's card dictionary, follows the official rules reference in the
repo, plays out the game making reasonable decisions for each side, and reports each action
(plays, digivolutions, attacks, security checks, memory swings) until a win condition is met.

## What's Needed From User
- **Decklist(s)** — a main deck (aim for 50 cards) and optional Digi-Egg deck (0–5), given as
  card numbers with quantities. Any of these line formats work:
  ```
  4 BT1-010
  3x AD1-001
  EX2-044 x2
  BT14-001        # quantity defaults to 1
  ```
- If the user provides **one** deck, playtest it as a "goldfish" (draw + develop with no
  interactive opponent) OR against a simple mirror/opponent — ask which, defaulting to a
  goldfish opening + curve-out over ~6 turns.
- If the user provides **two** decks, play them against each other to a win condition.
- Optional: which deck goes first (default: deck A / first player), and a turn cap (default 15).

## Procedure
1. Clone/enter `dashingstag/Digimon` and confirm `playtest/deck_lookup.py`,
   `playtest/digimon_rules.md`, and `digimon_cards_dict.json` are present.
2. Save each provided decklist to a file (e.g. `deckA.txt`, `deckB.txt`).
3. Run `python3 playtest/deck_lookup.py deckA.txt` (and for deckB) to resolve every card's
   type, color, level, play cost, digivolve cost, DP, traits, and effects.
4. **Fill in any missing/sparse cards before playing.** Collect the card numbers reported under
   `MISSING`, plus any resolved cards that come back stat-sparse (e.g. `type: "Unknown"` with
   null level/cost/DP — these are CSV stubs). Fetch full records for *only those numbers* from
   the same public API the Streamlit Data Fetcher uses, via the helper:
   ```
   python3 app/update_cards.py BT25-084 LM-032 EX1-066   # only the numbers that were missing/sparse
   ```
   It writes just those keys into `digimon_cards_dict.json` and leaves every other entry
   untouched. Then re-run `deck_lookup.py` and confirm `MISSING` is empty. If a number is still
   missing after the API call (genuinely not in the database), tell the user and do not invent
   stats for it. Note: this edits the local dictionary — commit it on a branch/PR only if the
   user wants the data change persisted; otherwise it's just a local fetch to enable the playtest.
5. Read `playtest/digimon_rules.md` in full and treat it as the rules authority (card text
   overrides general rules). Pay attention to: turn phases, the shared memory gauge and how
   turns end, the breeding area, digivolution + drawing, attacking/blocking/security checks,
   battles (DP comparison), and the effect-timing labels (`[On Play]`, `[When Digivolving]`,
   `[When Attacking]`, `[Security]`, `[Main]`, etc.).
6. Initialize the game state for each player: shuffle conceptually, draw 5 (allow one
   mulligan if the opening is unplayable), set 5 security cards, memory = 0. First player
   skips the turn-1 draw.
7. Play the game turn by turn. For each turn, walk the phases in order (Unsuspend → Draw →
   Breeding → Main) and, in the main phase, make reasonable, deck-appropriate decisions:
   develop the breeding line, digivolve up the curve, play Tamers/Options when useful, attack
   when profitable, and manage the memory gauge (remember passing/ending a turn hands memory
   to the opponent).
8. Emit a **play-by-play entry for every meaningful action** using the format in
   Specifications. Resolve each card's actual effect text and security-check outcomes, and
   keep a running board state (each player's field with current DP + digivolution depth,
   hand size, security count, and memory).
9. Continue until a win condition is met (opponent security hit at 0, or deck-out) or the turn
   cap is reached; if the cap is reached, stop and summarize the board position and who is
   ahead.
10. Deliver the full play-by-play log plus a short summary (winner/leader, key turning points,
   and any deck observations such as an awkward curve or missing engine pieces).

## Specifications
- **Deliverable:** a Markdown play-by-play. Structure each turn as:
  ```
  ## Turn N — <Player> (memory start: <M>)
  - Unsuspend: ...
  - Draw: drew <card> (hand: <n>)
  - Breeding: hatched <egg> / moved <Digimon> to battle area / no action
  - Main:
    - Played <name> (BTx-xxx) for <cost>. Memory <before> -> <after>. [On Play]: <what happened>
    - Digivolved <base> into <name> (BTx-xxx) for <cost>, drew a card. Now <DP> DP. Inherited: <...>
    - <name> attacks <target>. Block? <y/n>. Security check: flipped <card> -> <result>.
    - ...
  - End of turn. Memory: <M on opponent side>. Board: A[...] vs B[...]. Security A:n B:n.
  ```
- Every card referenced must use its **real** stats/effects from `deck_lookup.py` output.
- Security checks must flip a concrete security card and resolve its `[Security]` / battle
  outcome; Security Digimon are not deleted when they lose.
- The log must be internally consistent: memory, DP, security counts, and hand sizes track
  correctly turn to turn.
- End with a **Result** section naming the winner (or leader at the cap) and 2–4 bullet
  takeaways about the deck's performance.
- **Validation:** re-read the log and confirm no card has invented stats, memory never exceeds
  10 either way, no Digimon attacks the turn it was played (unless it has `<Rush>`), and every
  attack on the player performs a security check while security > 0.

## Advice and Pointers
- The card dictionary is authoritative for stats; the rules file is authoritative for
  procedure; individual card text overrides the general rules.
- Some older starter-set entries (e.g. `ST1-xx`) have sparse data in the dictionary — if a
  needed field is missing, say so rather than guessing, and prefer resolving with cards that
  have full data.
- Keep decisions plausible for the archetype rather than optimal; the goal is an illustrative,
  legal playtest the user can follow, not a solver.
- Represent the shared memory gauge as a single signed number (positive = current player's
  side). A turn ends when, with nothing pending, memory sits on the opponent's side.

## Forbidden Actions
- Do not invent card names, stats, or effects; only use data returned by `deck_lookup.py` (or
  fetched into the dictionary by `app/update_cards.py`).
- Do not hand-edit `digimon_cards_dict.json` or touch the card images. The only allowed change
  to the dictionary is via `app/update_cards.py` to fetch cards flagged missing/sparse.
- Do not skip security checks or let a freshly played Digimon attack the same turn (absent
  `<Rush>`).
