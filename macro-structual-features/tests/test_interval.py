"""
Test functions for Interval feature calculation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from features.interval import calc_interval


def test_interval():
    """Test interval calculation"""
    print("=== Testing Interval Calculation ===")
    
    # Test case 1: Basic interval calculation
    # Speech 0: 5 ADUs (0-4), attacks: (0,10), (2,10), (4,10) -> interval = 4-0-1 = 3, normalized = 3/(5-2) = 1.0
    att_src_by_speech = [
        [(0, 10), (2, 10), (4, 10)],  # 3 attacks to same target from speech 0
        [(5, 15), (6, 15)],           # 2 attacks to same target from speech 1
        []                            # No attacks from speech 2
    ]
    
    len_adu_by_speech = [5, 4, 3]  # Speech lengths
    
    result = calc_interval(att_src_by_speech, len_adu_by_speech)
    # Speech 0: (4-0-1)/(5-2) = 3/3 = 1.0
    # Speech 1: (6-5-1)/(4-2) = 0/2 = 0.0
    # Total: 1.0 + 0.0 = 1.0
    expected = 1.0
    
    print(f"Test 1 - Basic interval:")
    print(f"  Expected: {expected}")
    print(f"  Actual: {result}")
    print(f"  Match: {abs(result - expected) < 0.001}")
    
    # Test case 2: Multiple groups in same speech
    att_src_by_speech2 = [
        [(0, 10), (2, 10), (1, 15), (3, 15)],  # 2 groups in speech 0
        []
    ]
    
    len_adu_by_speech2 = [6, 3]
    
    result2 = calc_interval(att_src_by_speech2, len_adu_by_speech2)
    # Group 1: (2-0-1)/(6-2) = 1/4 = 0.25
    # Group 2: (3-1-1)/(6-2) = 1/4 = 0.25
    # Total: 0.25 + 0.25 = 0.5
    expected2 = 0.5
    
    print(f"\nTest 2 - Multiple groups:")
    print(f"  Expected: {expected2}")
    print(f"  Actual: {result2}")
    print(f"  Match: {abs(result2 - expected2) < 0.001}")
    
    # Test case 3: No shared targets
    att_src_by_speech3 = [
        [(0, 10), (1, 11), (2, 12)],  # All different targets
        []
    ]
    
    len_adu_by_speech3 = [5, 3]
    
    result3 = calc_interval(att_src_by_speech3, len_adu_by_speech3)
    expected3 = 0.0  # No shared targets = no intervals
    
    print(f"\nTest 3 - No shared targets:")
    print(f"  Expected: {expected3}")
    print(f"  Actual: {result3}")
    print(f"  Match: {abs(result3 - expected3) < 0.001}")


if __name__ == "__main__":
    test_interval()