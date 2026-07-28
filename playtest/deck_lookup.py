#!/usr/bin/env python3
"""Resolve a Digimon decklist into full card details from digimon_cards_dict.json.

The playtest agent calls this to turn a raw decklist into structured card data
(costs, DP, levels, traits, effects) so it can simulate a game accurately.

Usage:
    python3 playtest/deck_lookup.py <decklist_file>
    python3 playtest/deck_lookup.py -            # read decklist from stdin
    python3 playtest/deck_lookup.py <file> --json   # machine-readable output

Decklist format (one card per line; quantities optional):
    4 BT1-010
    3x AD1-001
    EX2-044 x2
    ST1-02            # quantity defaults to 1
Lines that are blank or start with '#' or '//' are ignored.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DICT = os.path.join(REPO_ROOT, "digimon_cards_dict.json")

# Matches an optional leading quantity ("4", "3x"), the card number, and an
# optional trailing quantity ("x2", "*2").
# Set prefix (1-4 letters + optional 1-2 digit set number), a dash, then the
# 2-3 digit card number, e.g. BT14-001, AD1-001, EX2-044, ST1-02, P-040.
CARD_NUMBER_RE = re.compile(r"[A-Za-z]{1,4}\d{0,2}-\d{2,3}[A-Za-z]?", re.IGNORECASE)
LEADING_QTY_RE = re.compile(r"^\s*(\d+)\s*[xX]?\s+")
TRAILING_QTY_RE = re.compile(r"\s*[xX*]\s*(\d+)\s*$")


def load_cards(dict_path: str = DEFAULT_DICT) -> dict:
    with open(dict_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def parse_line(line: str) -> Optional[tuple[str, int]]:
    """Return (card_number, quantity) for a decklist line, or None to skip."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or stripped.startswith("//"):
        return None

    qty = 1
    lead = LEADING_QTY_RE.search(stripped)
    trail = TRAILING_QTY_RE.search(stripped)
    if lead:
        qty = int(lead.group(1))
        stripped = stripped[lead.end():]
    elif trail:
        qty = int(trail.group(1))
        stripped = stripped[: trail.start()]

    match = CARD_NUMBER_RE.search(stripped)
    if not match:
        return None
    return match.group(0).upper(), qty


def resolve_card(card_number: str, cards: dict) -> Optional[dict]:
    """Look up a card by number, case-insensitively."""
    if card_number in cards:
        return cards[card_number]
    for key, value in cards.items():
        if key.upper() == card_number:
            return value
    return None


def traits(card: dict) -> list[str]:
    out = []
    for key in ("digi_type", "digi_type2", "digi_type3", "digi_type4"):
        val = card.get(key)
        if val:
            out.append(str(val))
    return out


def effects(card: dict) -> dict:
    out = {}
    for key in ("main_effect", "source_effect", "alt_effect"):
        val = card.get(key)
        if val and str(val).strip():
            out[key] = str(val).strip()
    return out


def build_report(decklist_text: str, cards: dict) -> dict:
    entries = []
    missing = []
    total = 0
    for line in decklist_text.splitlines():
        parsed = parse_line(line)
        if parsed is None:
            continue
        number, qty = parsed
        card = resolve_card(number, cards)
        total += qty
        if card is None:
            missing.append({"cardnumber": number, "qty": qty})
            continue
        entries.append(
            {
                "cardnumber": card.get("cardnumber") or number,
                "qty": qty,
                "name": card.get("name"),
                "type": card.get("type"),
                "color": card.get("color"),
                "color2": card.get("color2"),
                "level": card.get("level"),
                "play_cost": card.get("play_cost"),
                "evolution_cost": card.get("evolution_cost"),
                "evolution_level": card.get("evolution_level"),
                "evolution_color": card.get("evolution_color"),
                "dp": card.get("dp"),
                "traits": traits(card),
                "effects": effects(card),
            }
        )

    def sort_key(e):
        # None levels last, then by level, cost, name.
        lvl = e["level"] if isinstance(e["level"], int) else 99
        cost = e["play_cost"] if isinstance(e["play_cost"], int) else 99
        return (lvl, cost, e["name"] or "")

    entries.sort(key=sort_key)

    by_type: dict[str, int] = {}
    curve: dict[str, int] = {}
    for e in entries:
        by_type[e["type"] or "Unknown"] = by_type.get(e["type"] or "Unknown", 0) + e["qty"]
        lvl = e["level"]
        label = f"Lv.{lvl}" if isinstance(lvl, int) else "No level"
        curve[label] = curve.get(label, 0) + e["qty"]

    return {
        "total_cards": total,
        "unique_cards": len(entries),
        "by_type": by_type,
        "level_curve": curve,
        "cards": entries,
        "missing": missing,
    }


def format_text(report: dict) -> str:
    lines = []
    lines.append(
        f"Deck summary: {report['total_cards']} cards "
        f"({report['unique_cards']} unique)"
    )
    if report["by_type"]:
        lines.append(
            "  Types: "
            + ", ".join(f"{k} {v}" for k, v in sorted(report["by_type"].items()))
        )
    if report["level_curve"]:
        lines.append(
            "  Levels: "
            + ", ".join(f"{k} {v}" for k, v in sorted(report["level_curve"].items()))
        )
    lines.append("")
    for e in report["cards"]:
        header = f"[{e['qty']}x] {e['cardnumber']}  {e['name']}"
        meta = []
        meta.append(e["type"] or "?")
        color = e["color"] + ("/" + e["color2"] if e["color2"] else "") if e["color"] else "?"
        meta.append(color)
        if isinstance(e["level"], int):
            meta.append(f"Lv.{e['level']}")
        if isinstance(e["play_cost"], int):
            meta.append(f"Play {e['play_cost']}")
        if isinstance(e["evolution_cost"], int):
            meta.append(f"Digivolve {e['evolution_cost']}")
        if isinstance(e["dp"], int):
            meta.append(f"{e['dp']} DP")
        if e["traits"]:
            meta.append("Traits: " + "/".join(e["traits"]))
        lines.append(header)
        lines.append("    " + " | ".join(meta))
        for ekey, etext in e["effects"].items():
            label = {
                "main_effect": "Effect",
                "source_effect": "Inherited",
                "alt_effect": "Digivolve/Alt",
            }.get(ekey, ekey)
            flat = " ".join(etext.split())
            lines.append(f"    {label}: {flat}")
        lines.append("")
    if report["missing"]:
        lines.append("MISSING (not found in dictionary):")
        for m in report["missing"]:
            lines.append(f"  {m['qty']}x {m['cardnumber']}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decklist", help="Path to decklist file, or '-' for stdin")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    parser.add_argument("--dict", default=DEFAULT_DICT, help="Path to card dictionary JSON")
    args = parser.parse_args(argv)

    if args.decklist == "-":
        decklist_text = sys.stdin.read()
    else:
        with open(args.decklist, "r", encoding="utf-8") as fh:
            decklist_text = fh.read()

    cards = load_cards(args.dict)
    report = build_report(decklist_text, cards)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(format_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
