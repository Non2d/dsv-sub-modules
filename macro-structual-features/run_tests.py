"""
Standalone test runner for macro-structural features
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Rebuttal, DebateData
from calculator import MacroStructuralCalculator
from sample_data import (
    get_sample_north_american_style,
    get_sample_asian_style,
    get_sample_interval_case,
    get_sample_rally_chain,
    get_sample_order_crossing
)


def test_basic_functionality():
    """Test basic functionality of all components"""
    print("=== Testing Basic Functionality ===")
    
    # Test DebateData
    speeches = [1, 3, 5, 7]
    rebuttals = [Rebuttal(src=2, dst=0), Rebuttal(src=4, dst=1)]
    data = DebateData(speeches, rebuttals)
    
    assert data.speech_id(0) == 1
    assert data.speech_id(2) == 2
    assert data.adus_in_speech(1) == [0, 1]
    assert data.sources(0, 2) == [2]
    print("✓ DebateData tests passed")
    
    # Test Calculator
    calculator = MacroStructuralCalculator(data)
    results = calculator.calculate_all()
    
    assert isinstance(results['distance'], float)
    assert isinstance(results['rally'], float)
    assert isinstance(results['interval'], float)
    assert isinstance(results['order'], float)
    print("✓ Calculator tests passed")
    
    print("✓ All basic functionality tests passed\n")


def test_sample_data():
    """Test all sample data sets"""
    print("=== Testing Sample Data ===")
    
    samples = [
        ("North American Style", get_sample_north_american_style()),
        ("Asian Style", get_sample_asian_style()),
        ("Interval Case", get_sample_interval_case()),
        ("Rally Chain", get_sample_rally_chain()),
        ("Order Crossing", get_sample_order_crossing()),
    ]
    
    for name, data in samples:
        print(f"Testing {name}...")
        calculator = MacroStructuralCalculator(data)
        results = calculator.calculate_all()
        
        # Verify all results are numbers
        for feature, value in results.items():
            assert isinstance(value, (int, float)), f"{feature} should be numeric"
        
        print(f"  Distance: {results['distance']:.4f}")
        print(f"  Rally: {results['rally']:.4f}")
        print(f"  Interval: {results['interval']:.4f}")
        print(f"  Order: {results['order']:.4f}")
        print("✓ Passed\n")
    
    print("✓ All sample data tests passed\n")


def test_edge_cases():
    """Test edge cases"""
    print("=== Testing Edge Cases ===")
    
    # Empty rebuttals
    data = DebateData([1, 3], [])
    calculator = MacroStructuralCalculator(data)
    results = calculator.calculate_all()
    assert results['distance'] == 0.0
    assert results['rally'] == 0.0
    assert results['interval'] == 0.0
    assert results['order'] == -1.0
    print("✓ Empty rebuttals test passed")
    
    # Single rebuttal
    data = DebateData([1, 3], [Rebuttal(src=2, dst=0)])
    calculator = MacroStructuralCalculator(data)
    results = calculator.calculate_all()
    print("✓ Single rebuttal test passed")
    
    print("✓ All edge case tests passed\n")


def demo():
    """Run demonstration"""
    print("=== Macro-Structural Features Demo ===\n")
    
    # Example with North American style
    data = get_sample_north_american_style()
    print(f"Sample Data - North American Style:")
    print(f"Speeches: {data.speeches}")
    print(f"Rebuttals: {data.rebuttals}")
    
    calculator = MacroStructuralCalculator(data)
    results = calculator.calculate_all()
    
    print("\nCalculated Features:")
    for feature, value in results.items():
        print(f"  {feature.capitalize()}: {value:.4f}")
    print()


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_sample_data()
        test_edge_cases()
        demo()
        print("🎉 All tests passed successfully!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()