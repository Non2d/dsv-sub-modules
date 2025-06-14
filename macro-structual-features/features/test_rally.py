"""
Test functions for Rally feature calculation
"""

from rally import calc_rally


def test_rally():
    """Test rally calculation"""
    print("=== Testing Rally Calculation ===")
    
    # Test case 1: Simple rally chain A->B->C
    attacks = [
        (10, 5),   # A->B
        (15, 10),  # B->C (forms rally)
        (20, 25),  # Unrelated attack
    ]
    
    num_speeches = 6
    
    result = calc_rally(attacks, num_speeches)
    # Rally: [[(15, 10), (10, 5)]] (length 2)
    # No rally: [(20, 25)] (length 1)
    # total_rally = 1*2 + 1*0 = 2 (1 rally of length 2, 1 no-rally)
    # result = 2 / 3 / 6 = 0.111...
    expected = 2 / 3 / 6
    
    print(f"Test 1 - Simple rally chain:")
    print(f"  Expected: {expected}")
    print(f"  Actual: {result}")
    print(f"  Match: {abs(result - expected) < 0.001}")
    
    # Test case 2: No rallies
    attacks2 = [
        (10, 5),
        (15, 20),
        (25, 30),
    ]
    
    result2 = calc_rally(attacks2, num_speeches)
    # All no-rally: 3 attacks of length 1
    # total_rally = 3*0 = 0
    expected2 = 0.0
    
    print(f"\nTest 2 - No rallies:")
    print(f"  Expected: {expected2}")
    print(f"  Actual: {result2}")
    print(f"  Match: {abs(result2 - expected2) < 0.001}")
    
    # Test case 3: Long rally chain A->B->C->D
    attacks3 = [
        (30, 20),  # A->B
        (25, 30),  # B->C
        (15, 25),  # C->D (forms 3-rally)
    ]
    
    result3 = calc_rally(attacks3, num_speeches)
    # Rally: [[(15, 25), (25, 30), (30, 20)]] (length 3)
    # total_rally = 1*3 = 3
    # result = 3 / 3 / 6 = 0.166...
    expected3 = 3 / 3 / 6
    
    print(f"\nTest 3 - Long rally chain:")
    print(f"  Expected: {expected3}")
    print(f"  Actual: {result3}")
    print(f"  Match: {abs(result3 - expected3) < 0.001}")


if __name__ == "__main__":
    test_rally()