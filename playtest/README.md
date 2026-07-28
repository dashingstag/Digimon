# Digimon Deck Playtest Agent

Tools and reference material for a **Devin playtest agent** that takes a Digimon Card Game
decklist, looks up real card details, follows the official rules, and produces a turn-by-turn
**play-by-play** of a simulated game.

## Contents

| File | Purpose |
|---|---|
| `digimon_rules.md` | Rules reference distilled from the official Comprehensive Rules Manual (Ver. 4.1). The agent's rules authority. |
| `deck_lookup.py` | Resolves a decklist into full card details (cost, DP, level, traits, effects) from `../digimon_cards_dict.json`. |
| `playbook_playtest.md` | The playbook (agent procedure) that drives the play-by-play simulation. |
| `sample_decklist.txt` | Example decklist for trying the tool. |

## Quick start

```bash
# Human-readable card breakdown of a decklist
python3 playtest/deck_lookup.py playtest/sample_decklist.txt

# Machine-readable JSON (what the agent consumes)
python3 playtest/deck_lookup.py playtest/sample_decklist.txt --json

# Read a decklist from stdin
cat mydeck.txt | python3 playtest/deck_lookup.py -
```

### Decklist format

One card per line, quantity optional (`# ...` and `// ...` lines are ignored):

```
4 BT1-010
3x AD1-001
EX2-044 x2
BT14-001        # quantity defaults to 1
```

## How the agent uses these

1. Runs `deck_lookup.py` to get accurate stats/effects for every card in the deck(s).
2. Reads `digimon_rules.md` for turn structure, memory, digivolution, and combat rules.
3. Follows `playbook_playtest.md` to simulate the game and emit a play-by-play log.

The playbook is also registered as a Devin playbook so it can be launched directly on any
decklist.
