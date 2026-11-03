# =====================================================================
# PART 2 - RULE-BASED REASONING (RBR)
# Task 2A - IF-THEN rules written as Python functions.
# Each rule returns an action if its condition is true, else None.
# =====================================================================
from TA4kr import facts, show_knowledge_base
def rule_low_battery(f):
    # IF battery is below 20% AND charger is not connected THEN plug in charger
    if f["power"]["battery_percent"] < 20 and not f["power"]["charger_connected"]:
        return "Plug in the charger"
 
 
def rule_no_power(f):
    # IF laptop does not turn on AND charger is connected THEN check the cable
    if not f["power"]["turns_on"] and f["power"]["charger_connected"]:
        return "Check the power cable and charger port"
 
 
def rule_overheating(f):
    # IF CPU temperature is above 85 C THEN clean vents and cooling fan
    if f["performance"]["cpu_temperature"] > 85:
        return "Clean the air vents and cooling fan"
 
 
def rule_slow_and_noisy(f):
    # IF laptop is slow AND fan is noisy THEN close heavy apps / check for malware
    if f["performance"]["is_slow"] and f["status"]["fan_noise"]:
        return "Close heavy programs and run a malware scan"
 
 
def rule_critical_battery_slow(f):
    # IF laptop is slow AND battery is under 20% THEN enable battery saver
    if f["performance"]["is_slow"] and f["power"]["battery_percent"] < 20:
        return "Turn on battery saver mode"
 
 
# The rule base: a list of all rule functions
rules = [
    rule_low_battery,
    rule_no_power,
    rule_overheating,
    rule_slow_and_noisy,
    rule_critical_battery_slow,
]
 
 
# Task 2B - Inference Engine
def inference_engine(kb, rule_list):
    """
    1. Reads the knowledge base
    2. Checks each rule
    3. Returns all actions inferred
    """
    actions = []
    for rule in rule_list:
        result = rule(kb)           # Check the rule against the facts
        if result is not None:      # Rule fired
            actions.append(result)
    return actions
 
 
# Task 2C - Display Output
def run_rbr():
    print("=" * 55)
    print("RULE-BASED REASONING (RBR)")
    print("=" * 55)
    show_knowledge_base(facts)
    print()
    actions = inference_engine(facts, rules)
    print("Rule-Based Reasoning Actions:")
    if actions:
        for action in actions:
            print(f"- {action}")
    else:
        print("- No rule matched the given facts")
    print()

if __name__ == "__main__":
    run_rbr()
 