# Play-by-Play — Sample Red Greymon deck (goldfish)

**Mode:** goldfish (deck plays solitaire; opponent takes no actions and just passes memory
back). Deck resolved via `deck_lookup.py`; rules per `digimon_rules.md`. All card stats/effects
are the real values from `digimon_cards_dict.json`.

**Memory convention:** a single number = memory on *my* side. Paying costs lowers it; when it
drops below 0 with nothing pending, the turn passes (opponent gets that much). The goldfish
opponent passes, returning memory to me at 3.

**Opponent security stack** (fixed for this solitaire run, top → bottom): `Option`,
`Digimon 3000 DP`, `Digimon 5000 DP`, `Tamer`, `Digimon 4000 DP`.

Each turn lists the exact **Hand** contents right after the draw and again at end of turn.

Opening hand (after 1 mulligan) — 5: `BT1-010 Agumon`, `BT1-013 Muchomon`, `BT1-015 Greymon`,
`BT1-021 MetalGreymon`, `BT1-085 Tai Kamiya`.

---

## Turn 1 — Me (first player), memory 0
- **Unsuspend:** nothing on field.
- **Draw:** skipped (first player, turn 1).
- **Hand (5):** `BT1-010 Agumon`, `BT1-013 Muchomon`, `BT1-015 Greymon`, `BT1-021 MetalGreymon`,
  `BT1-085 Tai Kamiya`.
- **Breeding:** hatch `BT14-001 Koromon` (Lv.2) into the breeding area.
- **Main:**
  - Play `BT1-010 Agumon` (Lv.3, 2000 DP) for **3**. Memory `0 → -3`.
    `[On Play]`: reveal top 5, add `BT1-010 Agumon` (2nd) to hand, rest to bottom.
  - Agumon was played this turn → can't attack. Nothing else affordable.
- **Hand (5):** `BT1-013 Muchomon`, `BT1-015 Greymon`, `BT1-021 MetalGreymon`,
  `BT1-085 Tai Kamiya`, `BT1-010 Agumon`.
- **End of turn.** Memory `3` (opponent side).
  Board — **Me:** Battle: Agumon 2000 (sick). Breeding: Koromon. Security 5.

*Opponent turn: passes → memory returns to me at 3.*

---

## Turn 2 — Me, memory 3
- **Unsuspend:** Agumon.
- **Draw:** drew `AD1-001 Greymon`.
- **Hand (6):** `BT1-013 Muchomon`, `BT1-015 Greymon`, `BT1-021 MetalGreymon`,
  `BT1-085 Tai Kamiya`, `BT1-010 Agumon`, `AD1-001 Greymon`.
- **Breeding:** no action (Koromon is Lv.2 — can't move to battle yet).
- **Main:**
  - Digivolve battle **Agumon → `BT1-015 Greymon`** (Lv.4, 4000 DP), digivolve cost **2**.
    Memory `3 → 1`. **Draw 1** → drew `BT1-016 Tyrannomon`. Stack: Greymon / Agumon.
  - **Attack:** Greymon (4000) attacks the **player**. Security check → flip **Option** (no
    `[Security]`) → to trash. (Opponent security 5 → 4.)
  - Digivolve **Koromon → `BT1-010 Agumon`** in breeding, cost **0** (Lv.2 → Lv.3).
    Memory `1 → 1`. **Draw 1** → drew `BT1-021 MetalGreymon` (2nd). Koromon is now a
    **digivolution card**, so its inherited `[Your Turn][Once Per Turn] when a card leaves the
    opponent's security, <Draw 1>` is live for that line.
  - Pass to end turn: memory `→ -3`.
- **Hand (6):** `BT1-013 Muchomon`, `BT1-021 MetalGreymon`, `BT1-085 Tai Kamiya`,
  `AD1-001 Greymon`, `BT1-016 Tyrannomon`, `BT1-021 MetalGreymon`.
- **End of turn.** Memory `3` (opponent side).
  Board — **Me:** Battle: Greymon 4000 (suspended). Breeding: Agumon/Koromon. Sec 5.
  **Opp:** Security **4**.

*Opponent passes → memory to me at 3.*

---

## Turn 3 — Me, memory 3
- **Unsuspend:** Greymon.
- **Draw:** drew `BT1-085 Tai Kamiya` (2nd).
- **Hand (7):** `BT1-013 Muchomon`, `BT1-021 MetalGreymon`, `BT1-085 Tai Kamiya`,
  `AD1-001 Greymon`, `BT1-016 Tyrannomon`, `BT1-021 MetalGreymon`, `BT1-085 Tai Kamiya`.
- **Breeding:** **move** Agumon/Koromon to the battle area (Lv.3 is legal to move).
- **Main:** (do the free attack first, then spend into the opponent's side to end the turn)
  - **Attack:** Greymon (4000) attacks the player. Security check → flip **Digimon 3000 DP** →
    battle: Greymon 4000 vs 3000 → security Digimon loses (Security Digimon are **not deleted**
    for losing) → checked card to trash. Opponent security 4 → 3.
    Koromon inherited fires: **<Draw 1>** → drew `BT1-022 Garudamon`.
  - Play `BT1-085 Tai Kamiya` (Tamer) for **4**. Memory `3 → -1`. Sets up the memory-set engine
    and the red `<Security A.+1>` buff. Turn ends (memory on opponent side).
- **Hand (7):** `BT1-013 Muchomon`, `BT1-021 MetalGreymon`, `AD1-001 Greymon`,
  `BT1-016 Tyrannomon`, `BT1-021 MetalGreymon`, `BT1-085 Tai Kamiya`, `BT1-022 Garudamon`.
- **End of turn.** Memory `1` on the opponent side.
  Board — **Me:** Battle: Greymon 4000 (suspended), Agumon 2000. Tamer: Tai Kamiya. Sec 5.
  **Opp:** Security **3**.

*Opponent passes → memory to me at 3.*

---

## Turn 4 — Me, memory 3
- **Unsuspend:** Greymon, Agumon.
- **Start of Your Turn:** Tai Kamiya — memory is 3 (not ≤2), no change.
- **Draw:** drew `BT1-084 Omnimon`.
- **Hand (8):** `BT1-013 Muchomon`, `BT1-021 MetalGreymon`, `AD1-001 Greymon`,
  `BT1-016 Tyrannomon`, `BT1-021 MetalGreymon`, `BT1-085 Tai Kamiya`, `BT1-022 Garudamon`,
  `BT1-084 Omnimon`.
- **Breeding:** hatch a new `BT14-001 Koromon`.
- **Main:**
  - Digivolve **Greymon → `BT1-021 MetalGreymon`** (Lv.5, 7000 DP), cost **3**. Memory `3 → 0`.
    **Draw 1** → drew `AD1-004 WarGreymon`. Stack MetalGreymon/Greymon/Agumon.
  - **Attack:** MetalGreymon (7000) attacks the player. `[When Attacking] Gain 3 memory` →
    memory `0 → 3` (lose 3 at end of turn). Security check → flip **Digimon 5000 DP** → 7000 vs
    5000 → security Digimon loses, to trash. Opp security 3 → 2. Koromon inherited: **<Draw 1>**
    → drew `BT1-019 DarkTyrannomon`.
  - Play `BT1-013 Muchomon` (Lv.3, 5000 DP) for **3**. Memory `3 → 0`.
  - `[End of Turn]` MetalGreymon: lose 3 memory → memory `0 → -3`.
- **Hand (8):** `BT1-021 MetalGreymon`, `AD1-001 Greymon`, `BT1-016 Tyrannomon`,
  `BT1-085 Tai Kamiya`, `BT1-022 Garudamon`, `BT1-084 Omnimon`, `AD1-004 WarGreymon`,
  `BT1-019 DarkTyrannomon`.
- **End of turn.** Memory `3` (opponent side).
  Board — **Me:** MetalGreymon 7000 (suspended), Agumon 2000, Muchomon 5000 (sick). Tai Kamiya.
  **Opp:** Security **2**.

*Opponent passes → memory to me at 3.*

---

## Turn 5 — Me, memory 3
- **Unsuspend:** all.
- **Start of Your Turn:** Tai — memory 3, no change.
- **Draw:** drew `BT1-013 Muchomon` (2nd).
- **Hand (9):** `BT1-021 MetalGreymon`, `AD1-001 Greymon`, `BT1-016 Tyrannomon`,
  `BT1-085 Tai Kamiya`, `BT1-022 Garudamon`, `BT1-084 Omnimon`, `AD1-004 WarGreymon`,
  `BT1-019 DarkTyrannomon`, `BT1-013 Muchomon`.
- **Breeding:** move Koromon? still Lv.2 — no action.
- **Main:**
  - Digivolve **MetalGreymon → `BT1-022 Garudamon`** (Lv.5, 7000 DP, `<Piercing>`), cost **3**.
    Memory `3 → 0`. **Draw 1** → drew `BT1-015 Greymon`. Now 3 digivolution cards.
  - **Attack:** Garudamon (7000, `<Piercing>`) attacks the player. Security check → flip
    **Tamer** → to trash. Opp sec 2 → 1. Koromon inherited: **<Draw 1>** → drew
    `BT1-017 Birdramon`. (`<Piercing>` only adds a check when it deletes a Digimon *in battle*;
    the target was the player, so no extra check.)
  - Play `BT1-013 Muchomon` (2nd) for **3**. Memory `0 → -3`.
- **Hand (9):** `BT1-021 MetalGreymon`, `AD1-001 Greymon`, `BT1-016 Tyrannomon`,
  `BT1-085 Tai Kamiya`, `BT1-084 Omnimon`, `AD1-004 WarGreymon`, `BT1-019 DarkTyrannomon`,
  `BT1-015 Greymon`, `BT1-017 Birdramon`.
- **End of turn.** Memory `3` (opponent side).
  **Opp:** Security **1**.

*Opponent passes → memory to me at 3.*

---

## Turn 6 — Me, memory 3 — lethal attempt
- **Unsuspend:** all.
- **Draw:** drew `BT1-021 MetalGreymon` (3rd).
- **Hand (10):** `BT1-021 MetalGreymon`, `AD1-001 Greymon`, `BT1-016 Tyrannomon`,
  `BT1-085 Tai Kamiya`, `BT1-084 Omnimon`, `AD1-004 WarGreymon`, `BT1-019 DarkTyrannomon`,
  `BT1-015 Greymon`, `BT1-017 Birdramon`, `BT1-021 MetalGreymon`.
- **Main:**
  - With the opponent at **1 security**, one clean hit is lethal after it.
  - **Attack #1:** Garudamon (7000) attacks the player. Security check → flip **Digimon 4000 DP**
    → 7000 vs 4000 → wins, checked card to trash. Opponent security **1 → 0**.
  - **Attack #2:** Muchomon (5000, unsuspended) attacks the player. Opponent now has **0
    security** → the attack is successful with a security check available → **game won.**

---

## Result
- **Winner:** the sample deck (goldfish), on **turn 6**.
- Takeaways:
  - Clean curve: Agumon → Greymon → MetalGreymon → Garudamon kept a 7000 attacker online while
    the breeding line supplied a second body.
  - `BT14-001 Koromon`'s inherited `<Draw 1>` on security removal + `BT1-021 MetalGreymon`'s
    attack-memory swing drove strong card advantage — the deck never ran low on gas.
  - `BT1-085 Tai Kamiya` was mostly insurance here (memory never dipped to ≤2 on my turn); in a
    real game vs. a blocking opponent it enables the red `<Security A.+1>` finisher.
  - Top-end (`AD1-004 WarGreymon`, `BT1-084 Omnimon` at Play 15 / Digivolve 6) never came down —
    against real interaction you'd need it, but the 15-cost Omnimon is a heavy ask.
