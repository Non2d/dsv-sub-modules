#!/usr/bin/env python3
"""
Simple usage example for macro-structural features calculator
"""

from models import Rebuttal, DebateData
from calculator import MacroStructuralCalculator


def main():
    """Basic usage example"""
    print("Macro-Structural Features Calculator - Usage Example\n")
    
    # Example 1: North American Parliamentary Style (6 speeches)
    print("=== Example 1: North American Style ===")
    
    # Define speech structure: 6 speeches with 2 statements each
    # Speeches end at indices: 1, 3, 5, 7, 9, 11
    speeches = [1, 3, 5, 7, 9, 11]
    
    # Define rebuttals: (source_adu_index, destination_adu_index)
    rebuttals = [
        Rebuttal(src=2, dst=0),   # Speech 2, statement 0 rebuts Speech 1, statement 0
        Rebuttal(src=4, dst=1),   # Speech 3, statement 0 rebuts Speech 1, statement 1  
        Rebuttal(src=6, dst=2),   # Speech 4, statement 0 rebuts Speech 2, statement 0
        Rebuttal(src=8, dst=3),   # Speech 5, statement 0 rebuts Speech 2, statement 1
        Rebuttal(src=10, dst=0),  # Speech 6, statement 0 rebuts Speech 1, statement 0 (distant rebuttal)
    ]
    
    # Create debate data and calculator
    data = DebateData(speeches, rebuttals)
    calculator = MacroStructuralCalculator(data)
    
    # Calculate all features
    results = calculator.calculate_all()
    
    print(f"Speeches: {speeches}")
    print(f"Rebuttals: {rebuttals}")
    print("\nMacro-Structural Features:")
    print(f"  Distance: {results['distance']:.4f} (ratio of distant rebuttals)")
    print(f"  Rally:    {results['rally']:.4f} (connectivity of rebuttal chains)")  
    print(f"  Interval: {results['interval']:.4f} (dispersion within speeches)")
    print(f"  Order:    {results['order']:.4f} (crossing pattern measure)")
    
    # Example 2: Custom case with rally chains
    print("\n=== Example 2: Rally Chain Pattern ===")
    
    speeches = [1, 3, 5, 7]
    rebuttals = [
        Rebuttal(src=2, dst=0),   # A rebuts initial argument
        Rebuttal(src=4, dst=2),   # B rebuts A (creates rally chain)  
        Rebuttal(src=6, dst=4),   # C rebuts B (extends rally chain)
    ]
    
    data = DebateData(speeches, rebuttals)
    calculator = MacroStructuralCalculator(data)
    results = calculator.calculate_all()
    
    print(f"Speeches: {speeches}")
    print(f"Rebuttals: {rebuttals}")
    print(f"Rally Chain: 0 → 2 → 4 → 6")
    print(f"Rally Score: {results['rally']:.4f}")
    
    print("\n=== Feature Interpretations ===")
    print("Distance: Higher values indicate more temporal separation between rebuttals")
    print("Rally:    Higher values indicate more connected argument chains")
    print("Interval: Higher values indicate more dispersed rebuttals within speeches")
    print("Order:    -1 means no crossing; positive values indicate crossing complexity")


if __name__ == "__main__":
    main()