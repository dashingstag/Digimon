#!/usr/bin/env python3
"""Update digimon_cards_dict.json for specific card numbers by calling the
digimoncard.io public API (the same endpoint the Streamlit Data Fetcher uses).

Only the card numbers passed on the command line are fetched and written; every
other entry in the dictionary is left untouched.

Usage:
    python3 app/update_cards.py BT25-084 LM-032 BT6-081 ...
"""
import json
import os
import sys
import time
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT_PATH = os.path.join(REPO_ROOT, "digimon_cards_dict.json")
API_URL = "https://digimoncard.io/api-public/search?card={}"


def fetch_card(card_number: str) -> list:
    url = API_URL.format(card_number)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def pick_variant(card_number: str, variants: list) -> dict | None:
    """Choose the printing whose id matches the requested number exactly."""
    exact = [v for v in variants if str(v.get("id", "")).upper() == card_number.upper()]
    chosen = (exact or variants)
    if not chosen:
        return None
    card = dict(chosen[0])
    # Keep the dict-key field populated so the static index.html shows the number.
    card.setdefault("cardnumber", card.get("id", card_number))
    return card


def main(argv):
    if not argv:
        print("Provide one or more card numbers, e.g. BT25-084 LM-032")
        return 1

    with open(DICT_PATH, "r", encoding="utf-8") as fh:
        cards = json.load(fh)

    updated, skipped = [], []
    for i, number in enumerate(argv):
        try:
            variants = fetch_card(number)
        except Exception as e:  # network / HTTP errors
            print(f"  ! {number}: fetch failed ({e})")
            skipped.append(number)
            continue
        card = pick_variant(number, variants)
        if not card:
            print(f"  ! {number}: not found in API")
            skipped.append(number)
            continue
        cards[number] = card
        print(f"  + {number}: {card.get('name')} ({card.get('type')}, "
              f"Lv.{card.get('level')}, play {card.get('play_cost')}, "
              f"DP {card.get('dp')})")
        updated.append(number)
        if i % 5 == 4:
            time.sleep(1)

    with open(DICT_PATH, "w", encoding="utf-8") as fh:
        json.dump(cards, fh, ensure_ascii=False, indent=2)

    print(f"\nUpdated {len(updated)}; skipped {len(skipped)}: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
