#!/usr/bin/env python3
"""Update digimon_cards_dict.json for specific card numbers by calling the
digimoncard.io public API (the same endpoint the Streamlit Data Fetcher uses).

Only the card numbers passed on the command line are fetched and written; every
other entry in the dictionary is left untouched.

Guard: only data returned by the API is ever written. Each record must validate
as a genuine API payload (correct id + API provenance fields) and is sanitized to
a whitelist of known API fields, so playtest-generated or otherwise foreign content
can never be written into the dictionary.

Usage:
    python3 app/update_cards.py BT25-084 LM-032 BT6-081 ...
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT_PATH = os.path.join(REPO_ROOT, "digimon_cards_dict.json")
API_HOST = "digimoncard.io"
API_URL = "https://digimoncard.io/api-public/search?card={}"

# Whitelist of fields the digimoncard.io API returns. Only these are ever copied
# into the dictionary, so nothing outside the API payload (e.g. text generated
# during a playtest) can be written.
ALLOWED_FIELDS = frozenset({
    "name", "type", "id", "level", "play_cost", "evolution_cost",
    "evolution_color", "evolution_level", "xros_req", "color", "color2",
    "digi_type", "digi_type2", "digi_type3", "digi_type4", "form", "dp",
    "attribute", "rarity", "stage", "artist", "main_effect", "source_effect",
    "link_requirements", "link_dp", "alt_effect", "series", "pretty_url",
    "date_added", "tcgplayer_name", "tcgplayer_id", "set_name",
})
# Provenance fields the real API always includes; their presence is what
# distinguishes a genuine API record from arbitrary/generated content.
PROVENANCE_FIELDS = ("id", "name", "type", "pretty_url", "series")

CARD_NUMBER_RE = re.compile(r"^[A-Za-z]{1,4}\d{0,2}-\d{2,3}[A-Za-z]?$")


def fetch_card(card_number: str) -> list:
    url = API_URL.format(urllib.parse.quote(card_number))
    # Guard: never fetch from anywhere other than the trusted API host.
    if urllib.parse.urlparse(url).hostname != API_HOST:
        raise ValueError(f"refusing non-API host in URL: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if not isinstance(data, list):
        raise ValueError("unexpected API response shape (expected a list)")
    return data


def is_api_record(card_number: str, variant: dict) -> bool:
    """True only if `variant` looks like a genuine API payload for this number."""
    if not isinstance(variant, dict):
        return False
    # Must carry the API's provenance fields with non-empty values.
    if any(not variant.get(f) for f in PROVENANCE_FIELDS):
        return False
    # The record must actually be for the requested card number.
    return str(variant.get("id", "")).upper() == card_number.upper()


def pick_variant(card_number: str, variants: list) -> dict | None:
    """Pick the API printing whose id matches exactly, sanitized to API fields.

    Returns None if no fetched variant is a valid API record for this number,
    guaranteeing only API-sourced data is ever written to the dictionary.
    """
    valid = [v for v in variants if is_api_record(card_number, v)]
    if not valid:
        return None
    src = valid[0]
    # Copy ONLY whitelisted API fields (preserving the API's key order) — drop
    # any extra/foreign keys entirely.
    card = {k: v for k, v in src.items() if k in ALLOWED_FIELDS}
    # Keep the dict-key field populated so the static index.html shows the number.
    card["cardnumber"] = card.get("id", card_number)
    return card


def main(argv):
    if not argv:
        print("Provide one or more card numbers, e.g. BT25-084 LM-032")
        return 1

    with open(DICT_PATH, "r", encoding="utf-8") as fh:
        cards = json.load(fh)

    updated, skipped = [], []
    for i, number in enumerate(argv):
        if not CARD_NUMBER_RE.match(number):
            print(f"  ! {number}: not a valid card number, skipping")
            skipped.append(number)
            continue
        try:
            variants = fetch_card(number)
        except Exception as e:  # network / HTTP errors
            print(f"  ! {number}: fetch failed ({e})")
            skipped.append(number)
            continue
        card = pick_variant(number, variants)
        if not card:
            # Guard: the API returned nothing that validates as a genuine record
            # for this number, so we write nothing rather than risk bad data.
            print(f"  ! {number}: no valid API record found, not written")
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
