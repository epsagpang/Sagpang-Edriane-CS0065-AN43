"""
TA3 - Case-Based Reasoning (CBR) System Development
Case Study 1: Disaster Response Decision Support System (DSS)

A simple CBR program that helps a Local Government Unit (LGU) plan its
response to a new disaster by reusing experience from past disasters.

The program follows the full CBR cycle (the "4 R's"):
    1. RETRIEVE - find the most similar past disaster(s) in the case base
    2. REUSE    - take the solution of the best-matching case
    3. REVISE   - adapt that solution to fit the new disaster
    4. RETAIN   - save the new problem + adapted solution as a new case

Run:
    python cbr_disaster_dss.py              -> runs the demo scenario
    python cbr_disaster_dss.py --interactive -> lets you type a new event
    python cbr_disaster_dss.py --reset       -> restores the original case base

Note: Case values are simplified, sample data for a class activity,
loosely inspired by real Philippine events.
"""

import json
import math
import os
import sys
from datetime import datetime

# File where the case base is stored (so learning persists between runs)
CASE_BASE_FILE = "case_base.json"


# =====================================================================
# 1. CASE REPRESENTATION
# Each case is a dictionary with three parts:
#   - "id" / "name"  : identifies the case
#   - "problem"      : features that describe the disaster situation
#   - "solution"     : the response plan that was used
#   - "outcome"      : how well the plan worked (used for learning)
# =====================================================================
INITIAL_CASES = [
    {
        "id": 1,
        "name": "Typhoon Ursula (2019)",
        "problem": {
            "disaster_type": "typhoon",
            "area_type": "rural",
            "wind_speed_kph": 195,
            "rainfall_mm": 150,
            "flood_risk": "medium",
            "affected_population": 120000,
            "warning_lead_time_hrs": 48,
        },
        "solution": {
            "evacuation_strategy": "Pre-emptive evacuation of coastal barangays",
            "evacuees": 30000,
            "evacuation_centers": 60,
            "shelter_capacity": 33000,
            "food_packs": 90000,
            "rescue_teams": 25,
            "rescue_boats": 10,
            "medical_teams": 12,
        },
        "outcome": {"success_rating": 4, "notes": "Coastal areas cleared early."},
    },
    {
        "id": 2,
        "name": "Typhoon Odette (2021)",
        "problem": {
            "disaster_type": "typhoon",
            "area_type": "urban",
            "wind_speed_kph": 195,
            "rainfall_mm": 250,
            "flood_risk": "high",
            "affected_population": 300000,
            "warning_lead_time_hrs": 36,
        },
        "solution": {
            "evacuation_strategy": "Forced evacuation of low-lying and coastal zones; schools used as shelters",
            "evacuees": 90000,
            "evacuation_centers": 150,
            "shelter_capacity": 99000,
            "food_packs": 270000,
            "rescue_teams": 60,
            "rescue_boats": 35,
            "medical_teams": 30,
        },
        "outcome": {"success_rating": 3, "notes": "Shelters overcrowded on day 2."},
    },
    {
        "id": 3,
        "name": "Tropical Storm Ondoy (2009)",
        "problem": {
            "disaster_type": "flood",
            "area_type": "urban",
            "wind_speed_kph": 85,
            "rainfall_mm": 450,
            "flood_risk": "high",
            "affected_population": 500000,
            "warning_lead_time_hrs": 12,
        },
        "solution": {
            "evacuation_strategy": "Vertical evacuation to upper floors + boat rescue in flooded streets",
            "evacuees": 150000,
            "evacuation_centers": 220,
            "shelter_capacity": 165000,
            "food_packs": 450000,
            "rescue_teams": 120,
            "rescue_boats": 80,
            "medical_teams": 45,
        },
        "outcome": {"success_rating": 2, "notes": "Short warning time; not enough boats."},
    },
    {
        "id": 4,
        "name": "Typhoon Ulysses (2020)",
        "problem": {
            "disaster_type": "typhoon",
            "area_type": "urban",
            "wind_speed_kph": 155,
            "rainfall_mm": 350,
            "flood_risk": "high",
            "affected_population": 400000,
            "warning_lead_time_hrs": 24,
        },
        "solution": {
            "evacuation_strategy": "Staged evacuation of riverside communities; roof-top rescue",
            "evacuees": 110000,
            "evacuation_centers": 180,
            "shelter_capacity": 121000,
            "food_packs": 330000,
            "rescue_teams": 90,
            "rescue_boats": 60,
            "medical_teams": 35,
        },
        "outcome": {"success_rating": 3, "notes": "Dam release worsened flooding."},
    },
    {
        "id": 5,
        "name": "Bohol Earthquake (2013)",
        "problem": {
            "disaster_type": "earthquake",
            "area_type": "rural",
            "wind_speed_kph": 0,
            "rainfall_mm": 0,
            "flood_risk": "low",
            "affected_population": 200000,
            "warning_lead_time_hrs": 0,
        },
        "solution": {
            "evacuation_strategy": "Move residents to open fields; structural checks before return",
            "evacuees": 50000,
            "evacuation_centers": 80,
            "shelter_capacity": 55000,
            "food_packs": 150000,
            "rescue_teams": 40,
            "rescue_boats": 0,
            "medical_teams": 25,
        },
        "outcome": {"success_rating": 4, "notes": "Tent cities set up quickly."},
    },
]


# =====================================================================
# Case base helpers (load / save)
# =====================================================================
def load_case_base():
    """Load cases from the JSON file; create it from INITIAL_CASES if missing."""
    if not os.path.exists(CASE_BASE_FILE):
        save_case_base(INITIAL_CASES)
    with open(CASE_BASE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_case_base(cases):
    """Write the whole case base back to the JSON file."""
    with open(CASE_BASE_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2)


# =====================================================================
# 2. SIMILARITY ASSESSMENT
# Weighted (global) similarity = sum(weight * local_similarity) / sum(weights)
#   - Categorical features: exact match = 1, related = partial, else 0
#   - Numeric features: 1 - |a - b| / range   (closer values -> higher score)
# =====================================================================

# How important each feature is when comparing disasters (total = 10)
WEIGHTS = {
    "disaster_type": 2.5,
    "area_type": 1.5,
    "flood_risk": 2.0,
    "rainfall_mm": 1.0,
    "wind_speed_kph": 1.0,
    "affected_population": 1.5,
    "warning_lead_time_hrs": 0.5,
}

# Value range of numeric features (used to normalize differences to 0..1)
NUMERIC_RANGES = {
    "rainfall_mm": 500,
    "wind_speed_kph": 300,
    "affected_population": 1_000_000,
    "warning_lead_time_hrs": 72,
}

# Partial similarity between related disaster types
# (a typhoon often causes flooding, so they are 60% similar)
TYPE_SIMILARITY = {
    ("typhoon", "flood"): 0.6,
    ("flood", "typhoon"): 0.6,
}

# Ordinal levels for flood risk (low < medium < high)
RISK_LEVEL = {"low": 0, "medium": 1, "high": 2}


def local_similarity(feature, new_value, old_value):
    """Similarity (0..1) between two values of ONE feature."""
    if feature == "disaster_type":
        if new_value == old_value:
            return 1.0
        return TYPE_SIMILARITY.get((new_value, old_value), 0.0)

    if feature == "area_type":
        return 1.0 if new_value == old_value else 0.0

    if feature == "flood_risk":
        # one level apart = 0.5, two levels apart = 0
        diff = abs(RISK_LEVEL[new_value] - RISK_LEVEL[old_value])
        return 1.0 - diff / 2

    # Numeric features
    rng = NUMERIC_RANGES[feature]
    diff = abs(new_value - old_value)
    return max(0.0, 1.0 - diff / rng)


def compute_similarity(new_problem, old_problem):
    """Global weighted similarity (0..1) between a new and a past problem."""
    total, weight_sum = 0.0, 0.0
    for feature, weight in WEIGHTS.items():
        sim = local_similarity(feature, new_problem[feature], old_problem[feature])
        total += weight * sim
        weight_sum += weight
    return total / weight_sum


def retrieve(new_problem, cases, k=3):
    """RETRIEVE: rank all past cases by similarity and return the top k."""
    ranked = []
    for case in cases:
        score = compute_similarity(new_problem, case["problem"])
        ranked.append((score, case))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return ranked[:k], ranked


# =====================================================================
# 3. CASE ADAPTATION (REUSE + REVISE)
# The retrieved plan is adjusted to the new event using simple rules:
#   - Scale evacuees and resources by the population ratio
#   - Increase evacuation rate if flood risk / rainfall is higher
#   - Add more rescue boats for urban flooding
#   - Add a 10% shelter buffer (more if the old case had overcrowding)
#   - Change evacuation strategy if warning time is short
# =====================================================================
def round_up(x):
    """Round up to a whole number (round first to ignore tiny float errors)."""
    return math.ceil(round(x, 6))


def adapt_solution(new_problem, retrieved_case):
    old_p = retrieved_case["problem"]
    old_s = retrieved_case["solution"]
    notes = []  # explanation of each adaptation (for transparency)

    # --- Rule 1: scale by affected population ---
    pop_ratio = new_problem["affected_population"] / old_p["affected_population"]
    notes.append(f"Population ratio = {new_problem['affected_population']:,} / "
                 f"{old_p['affected_population']:,} = {pop_ratio:.2f}")

    # --- Rule 2: evacuation rate depends on flood risk and rainfall ---
    old_rate = old_s["evacuees"] / old_p["affected_population"]
    risk_factor = {"low": 0.8, "medium": 1.0, "high": 1.2}[new_problem["flood_risk"]] / \
                  {"low": 0.8, "medium": 1.0, "high": 1.2}[old_p["flood_risk"]]
    rain_factor = 1.0
    if new_problem["rainfall_mm"] > old_p["rainfall_mm"]:
        rain_factor = 1.10
        notes.append("Rainfall is higher than the past case -> evacuate 10% more people")
    new_rate = min(old_rate * risk_factor * rain_factor, 0.60)  # cap at 60%
    evacuees = round_up(new_problem["affected_population"] * new_rate)
    notes.append(f"Evacuation rate {old_rate:.1%} -> {new_rate:.1%}  =>  {evacuees:,} evacuees")

    # --- Rule 3: shelters (10% buffer, 20% if the past case was overcrowded) ---
    buffer = 1.20 if "overcrowd" in retrieved_case["outcome"]["notes"].lower() else 1.10
    if buffer > 1.10:
        notes.append("Past case reported overcrowding -> shelter buffer raised to 20%")
    shelter_capacity = round_up(evacuees * buffer)
    people_per_center = old_s["shelter_capacity"] / old_s["evacuation_centers"]
    evacuation_centers = round_up(shelter_capacity / people_per_center)

    # --- Rule 4: relief and response resources scale with evacuees ---
    evac_ratio = evacuees / old_s["evacuees"]
    food_packs = round_up(evacuees * 3)  # 3 days of food packs per evacuee
    rescue_teams = round_up(old_s["rescue_teams"] * evac_ratio)
    medical_teams = round_up(old_s["medical_teams"] * evac_ratio)
    rescue_boats = round_up(old_s["rescue_boats"] * evac_ratio)

    # --- Rule 5: urban flooding needs extra boats ---
    if new_problem["area_type"] == "urban" and new_problem["flood_risk"] == "high":
        rescue_boats = round_up(rescue_boats * 1.25)
        notes.append("Urban area with HIGH flood risk -> +25% rescue boats")

    # --- Rule 6: strategy depends on warning lead time ---
    strategy = old_s["evacuation_strategy"]
    if new_problem["warning_lead_time_hrs"] < 24:
        strategy = "IMMEDIATE forced + vertical evacuation; " + strategy
        notes.append("Warning time < 24 hrs -> switch to immediate/forced evacuation")
    elif new_problem["warning_lead_time_hrs"] >= 48:
        strategy = "Staged departures over the 48-hr window; " + strategy
        notes.append("Warning time >= 48 hrs -> staged pre-emptive evacuation")

    adapted = {
        "evacuation_strategy": strategy,
        "evacuees": evacuees,
        "evacuation_centers": evacuation_centers,
        "shelter_capacity": shelter_capacity,
        "food_packs": food_packs,
        "rescue_teams": rescue_teams,
        "rescue_boats": rescue_boats,
        "medical_teams": medical_teams,
    }
    return adapted, notes


def revise_solution(solution):
    """REVISE: simple sanity checks so the plan is safe before it is used."""
    checks = []
    if solution["shelter_capacity"] < solution["evacuees"]:
        solution["shelter_capacity"] = round_up(solution["evacuees"] * 1.1)
        checks.append("Shelter capacity raised to cover all evacuees")
    if solution["medical_teams"] < 1:
        solution["medical_teams"] = 1
        checks.append("At least 1 medical team assigned")
    if not checks:
        checks.append("All checks passed (shelter >= evacuees, resources > 0)")
    return solution, checks


# =====================================================================
# 4. LEARNING (RETAIN)
# The new problem + adapted solution is stored as a new case
# so the system can reuse it next time.
# =====================================================================
def retain(cases, name, new_problem, solution, based_on, rating=4):
    new_case = {
        "id": max(c["id"] for c in cases) + 1,
        "name": name,
        "problem": new_problem,
        "solution": solution,
        "outcome": {
            "success_rating": rating,
            "notes": f"Adapted from '{based_on}' on {datetime.now():%Y-%m-%d %H:%M}",
        },
    }
    cases.append(new_case)
    save_case_base(cases)
    return new_case


# =====================================================================
# Display helpers
# =====================================================================
def line(char="=", n=78):
    print(char * n)


def show_problem(p):
    print(f"  Disaster type        : {p['disaster_type']}")
    print(f"  Area type            : {p['area_type']}")
    print(f"  Wind speed           : {p['wind_speed_kph']} kph")
    print(f"  Rainfall             : {p['rainfall_mm']} mm")
    print(f"  Flood risk           : {p['flood_risk']}")
    print(f"  Affected population  : {p['affected_population']:,}")
    print(f"  Warning lead time    : {p['warning_lead_time_hrs']} hrs")


def show_solution(s):
    print(f"  Evacuation strategy  : {s['evacuation_strategy']}")
    print(f"  Evacuees             : {s['evacuees']:,}")
    print(f"  Evacuation centers   : {s['evacuation_centers']:,}")
    print(f"  Shelter capacity     : {s['shelter_capacity']:,}")
    print(f"  Food packs           : {s['food_packs']:,}")
    print(f"  Rescue teams         : {s['rescue_teams']:,}")
    print(f"  Rescue boats         : {s['rescue_boats']:,}")
    print(f"  Medical teams        : {s['medical_teams']:,}")


def show_case_base(cases):
    print(f"  {'ID':<4}{'Case name':<36}{'Type':<12}{'Area':<7}{'Flood':<8}{'Population':>11}")
    line("-")
    for c in cases:
        p = c["problem"]
        print(f"  {c['id']:<4}{c['name'][:35]:<36}{p['disaster_type']:<12}"
              f"{p['area_type']:<7}{p['flood_risk']:<8}{p['affected_population']:>11,}")


# =====================================================================
# Input of a new problem
# =====================================================================
def demo_problem():
    """New event from the case study: typhoon with expected urban flooding."""
    return "New Typhoon - Urban Flooding", {
        "disaster_type": "typhoon",
        "area_type": "urban",
        "wind_speed_kph": 175,
        "rainfall_mm": 320,
        "flood_risk": "high",
        "affected_population": 350000,
        "warning_lead_time_hrs": 18,
    }


def ask(prompt, options=None, cast=str):
    """Ask until a valid value is typed."""
    while True:
        value = input(prompt).strip().lower()
        try:
            value = cast(value)
        except ValueError:
            print("   Please enter a number.")
            continue
        if options and value not in options:
            print(f"   Choose one of: {', '.join(options)}")
            continue
        return value


def input_problem():
    print("\nEnter the details of the NEW disaster event:")
    name = input("  Event name: ").strip() or "Unnamed Event"
    problem = {
        "disaster_type": ask("  Disaster type (typhoon/flood/earthquake): ",
                             ["typhoon", "flood", "earthquake"]),
        "area_type": ask("  Area type (urban/rural): ", ["urban", "rural"]),
        "wind_speed_kph": ask("  Wind speed (kph): ", cast=int),
        "rainfall_mm": ask("  Expected rainfall (mm): ", cast=int),
        "flood_risk": ask("  Flood risk (low/medium/high): ", ["low", "medium", "high"]),
        "affected_population": ask("  Affected population: ", cast=int),
        "warning_lead_time_hrs": ask("  Warning lead time (hrs): ", cast=int),
    }
    return name, problem


# =====================================================================
# MAIN - runs the full CBR cycle
# =====================================================================
def main():
    if "--reset" in sys.argv:
        save_case_base(INITIAL_CASES)
        print("Case base reset to the 5 original cases.")
        return

    line()
    print("   CASE-BASED REASONING: DISASTER RESPONSE DECISION SUPPORT SYSTEM")
    line()

    cases = load_case_base()
    print(f"\nCase base loaded: {len(cases)} past cases")
    show_case_base(cases)

    # ---------- INPUT: new problem ----------
    if "--interactive" in sys.argv:
        name, new_problem = input_problem()
    else:
        name, new_problem = demo_problem()

    print()
    line()
    print(f" [INPUT] NEW PROBLEM: {name}")
    line()
    show_problem(new_problem)

    # ---------- STEP 1: RETRIEVE ----------
    top_k, ranked = retrieve(new_problem, cases, k=3)
    print()
    line()
    print(" [STEP 1] RETRIEVE - Similarity ranking of all past cases")
    line()
    for rank, (score, case) in enumerate(ranked, start=1):
        bar = "#" * int(score * 30)
        print(f"  {rank}. {case['name'][:35]:<36}{score:7.2%}  {bar}")

    best_score, best_case = top_k[0]
    print(f"\n  >> Most similar case: {best_case['name']} (similarity = {best_score:.2%})")
    print(f"  >> Other similar cases: " +
          ", ".join(f"{c['name']} ({s:.0%})" for s, c in top_k[1:]))

    # Feature-by-feature breakdown for the best case (explains the score)
    print("\n  Feature breakdown vs. best case:")
    print(f"  {'Feature':<24}{'New':>12}{'Past':>12}{'Local sim':>11}{'Weight':>8}")
    for f, w in WEIGHTS.items():
        nv, ov = new_problem[f], best_case["problem"][f]
        print(f"  {f:<24}{str(nv):>12}{str(ov):>12}"
              f"{local_similarity(f, nv, ov):>11.2f}{w:>8.1f}")

    # ---------- STEP 2: REUSE ----------
    print()
    line()
    print(f" [STEP 2] REUSE - Solution of '{best_case['name']}'")
    line()
    show_solution(best_case["solution"])
    print(f"  Past outcome         : {best_case['outcome']['success_rating']}/5 - "
          f"{best_case['outcome']['notes']}")

    # ---------- STEP 3: REVISE (adapt) ----------
    adapted, notes = adapt_solution(new_problem, best_case)
    adapted, checks = revise_solution(adapted)
    print()
    line()
    print(" [STEP 3] REVISE - Adaptation rules applied")
    line()
    for n in notes:
        print(f"  * {n}")
    for c in checks:
        print(f"  * Check: {c}")

    print()
    line()
    print(" [OUTPUT] ADAPTED FINAL SOLUTION")
    line()
    show_solution(adapted)

    # ---------- STEP 4: RETAIN ----------
    new_case = retain(cases, name, new_problem, adapted, best_case["name"])
    print()
    line()
    print(" [STEP 4] RETAIN - Learning")
    line()
    print(f"  New case saved! (Case ID {new_case['id']}: {new_case['name']})")
    print(f"  Case base now has {len(cases)} cases (saved to {CASE_BASE_FILE})\n")
    print("  UPDATED CASE BASE:")
    show_case_base(cases)
    line()


if __name__ == "__main__":
    main()
