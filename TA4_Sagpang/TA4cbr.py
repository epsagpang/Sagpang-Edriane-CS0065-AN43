# =====================================================================
# PART 3 - CASE-BASED REASONING (CBR)
# Task 3A - Case base: past problems and the solutions that worked
# =====================================================================
import sys
from TA4kr import facts, show_knowledge_base
case_base = [
    {"problem": {"wont_turn_on": True,  "noise": False, "overheating": False, "slow": False, "battery_drains_fast": False},
     "solution": "Check power cable."},
    {"problem": {"wont_turn_on": False, "noise": True,  "overheating": True,  "slow": True,  "battery_drains_fast": False},
     "solution": "Clean the cooling fan and replace thermal paste."},
    {"problem": {"wont_turn_on": False, "noise": False, "overheating": False, "slow": True,  "battery_drains_fast": False},
     "solution": "Free up disk space and restart the laptop."},
    {"problem": {"wont_turn_on": False, "noise": True,  "overheating": False, "slow": False, "battery_drains_fast": False},
     "solution": "Check for loose parts or a failing fan."},
]
 
 
# Task 3B - Retrieve step (similarity matching)
def similarity(new_problem, old_problem):
    """Fraction of features whose values match (0.0 to 1.0)."""
    matches = sum(1 for key in new_problem
                  if old_problem.get(key) == new_problem[key])
    return matches / len(new_problem)
 
 
def retrieve(new_problem, cases):
    """Return the most similar case and its similarity score."""
    best_case, best_score = None, -1
    for case in cases:
        score = similarity(new_problem, case["problem"])
        print(f"  Similarity with case -> {score:.2f}  ({case['solution']})")
        if score > best_score:
            best_case, best_score = case, score
    return best_case, best_score
 
 
# Task 3C - Reuse step
def reuse(best_case):
    """Reuse the solution of the most similar case."""
    return best_case["solution"]
 
 
# Task 3D - Revise step
def revise(solution):
    """Let the student adjust the solution manually, or keep it unchanged."""
    print(f"\nSuggested solution: {solution}")
    answer = input("Type a revised solution (or press Enter to keep it): ").strip()
    if not sys.stdin.isatty():      # echo input when it is piped (for the report)
        print(answer)
    return answer if answer else solution
 
 
# Task 3E - Retain step
def retain(new_problem, final_solution, cases):
    """Add the new case to the case base."""
    cases.append({"problem": new_problem, "solution": final_solution})
    print(f"\nNew case retained. Case base now has {len(cases)} cases.")
 
 
def run_cbr():
    print("=" * 55)
    print("CASE-BASED REASONING (CBR)")
    print("=" * 55)
 
    # New problem to solve (matches the same laptop as the RBR facts)
    new_problem = {"wont_turn_on": False, "noise": True,
                   "overheating": True, "slow": True,
                   "battery_drains_fast": True}
    print("New problem:", new_problem)
    print(f"Case base size before: {len(case_base)}\n")
 
    print("RETRIEVE:")
    best_case, score = retrieve(new_problem, case_base)
    print(f"  Best match score: {score:.2f}")
 
    print("\nREUSE:")
    solution = reuse(best_case)
    print(f"  Reused solution: {solution}")
 
    print("\nREVISE:", end="")
    final_solution = revise(solution)
    print(f"Final solution: {final_solution}")
 
    print("\nRETAIN:", end="")
    retain(new_problem, final_solution, case_base)
    print()
 
 
if __name__ == "__main__":
    run_cbr()
 