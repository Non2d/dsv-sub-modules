"""
Demo script showing how to use the macro-structural features calculator
"""

import json
import sys
import os

# Add src directory to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from calculator import MacroStructuralCalculator


def demo():
    """Demonstrate basic usage of the calculator"""
    print("=== Macro-Structural Features Demo ===\n")
    
    # Load sample data
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'debate_scripts.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        debate_scripts = json.load(f)
    
    # Calculate features for first 3 debates
    for i in range(min(3, len(debate_scripts))):
        round_data = debate_scripts[i]
        calculator = MacroStructuralCalculator(round_data)
        features = calculator.calculate_all()
        
        print(f"Debate {i+1}: {round_data['source']['title']}")
        print(f"  Features:")
        print(f"    Distance: {features['distance']:.4f}")
        print(f"    Interval: {features['interval']:.4f}")
        print(f"    Rally: {features['rally']:.4f}")
        print(f"    Order: {features['order']:.4f}")
        print()


if __name__ == "__main__":
    demo()