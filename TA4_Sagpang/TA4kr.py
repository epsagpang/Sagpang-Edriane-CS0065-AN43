"""
TA3 - Implementing Knowledge Representation, Rule-Based Reasoning (RBR),
and Case-Based Reasoning (CBR)
 
Use case: Laptop Troubleshooting Assistant
Both reasoning systems try to answer the same question:
"What should we do about this laptop problem?"
"""
 
import sys
 
# =====================================================================
# PART 1 - KNOWLEDGE REPRESENTATION (KR)
# Task 1A - Knowledge base stored as a Python dictionary
# 6 facts about one object (a laptop), grouped into 3 categories.
# =====================================================================
facts = {
    "power": {                      # Category 1: power
        "turns_on": True,
        "charger_connected": False,
        "battery_percent": 12,
    },
    "performance": {                # Category 2: performance
        "cpu_temperature": 92,      # degrees Celsius
        "is_slow": True,
    },
    "status": {                     # Category 3: status / symptoms
        "fan_noise": True,
    },
}
 
 
def show_knowledge_base(kb):
    """Print the knowledge base in a readable format."""
    print("Knowledge Base (Facts about the Laptop):")
    for category, items in kb.items():
        print(f"  [{category.upper()}]")
        for name, value in items.items():
            print(f"    - {name}: {value}")
show_knowledge_base(facts)