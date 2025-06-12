"""
Main interface for macro-structural features calculation

Usage example:
    from macro_structual_features import MacroStructuralCalculator, DebateData, Rebuttal
    
    # Create debate data
    speeches = [1, 3, 5, 7, 9, 11]  # North American style
    rebuttals = [
        Rebuttal(src=2, dst=0),
        Rebuttal(src=4, dst=1),
        Rebuttal(src=6, dst=2),
    ]
    
    # Calculate features
    data = DebateData(speeches, rebuttals)
    calculator = MacroStructuralCalculator(data)
    results = calculator.calculate_all()
    
    print(results)
"""

try:
    from .models import Rebuttal, DebateData
    from .calculator import MacroStructuralCalculator
    from .sample_data import (
        get_sample_north_american_style,
        get_sample_asian_style,
        get_sample_interval_case,
        get_sample_rally_chain,
        get_sample_order_crossing
    )
except ImportError:
    from models import Rebuttal, DebateData
    from calculator import MacroStructuralCalculator
    from sample_data import (
        get_sample_north_american_style,
        get_sample_asian_style,
        get_sample_interval_case,
        get_sample_rally_chain,
        get_sample_order_crossing
    )


def demo():
    """Demonstration of the macro-structural features calculator"""
    print("=== Macro-Structural Features Calculator Demo ===\n")
    
    # Test with different sample data sets
    samples = [
        ("North American Style", get_sample_north_american_style()),
        ("Asian Style", get_sample_asian_style()),
        ("Interval Case", get_sample_interval_case()),
        ("Rally Chain", get_sample_rally_chain()),
        ("Order Crossing", get_sample_order_crossing()),
    ]
    
    for name, data in samples:
        print(f"--- {name} ---")
        print(f"Speeches: {data.speeches}")
        print(f"Rebuttals: {data.rebuttals}")
        
        calculator = MacroStructuralCalculator(data)
        results = calculator.calculate_all()
        
        print("Results:")
        for feature, value in results.items():
            print(f"  {feature.capitalize()}: {value:.4f}")
        print()


if __name__ == "__main__":
    demo()