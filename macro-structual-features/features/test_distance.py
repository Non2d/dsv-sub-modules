"""
Test functions for Distance feature calculation
"""

from distance import calc_distance


def test_distance():
    """Test distance calculation"""
    print("=== Testing Distance Calculation ===")
    
    # Mock data for testing
    round_data = {
        "speeches": [
            {"ADUs": [{"id": 0}, {"id": 1}]},  # Speech 0: ADUs 0-1
            {"ADUs": [{"id": 2}, {"id": 3}]},  # Speech 1: ADUs 2-3
            {"ADUs": [{"id": 4}, {"id": 5}]},  # Speech 2: ADUs 4-5
            {"ADUs": [{"id": 6}, {"id": 7}]},  # Speech 3: ADUs 6-7
            {"ADUs": [{"id": 8}, {"id": 9}]},  # Speech 4: ADUs 8-9
            {"ADUs": [{"id": 10}, {"id": 11}]}, # Speech 5: ADUs 10-11
        ],
        "POIs": []
    }
    
    def mock_l(round_data, adu_id):
        """Mock localize function"""
        initial_IDs = [0, 2, 4, 6, 8, 10]
        speech_id = 0
        for i, start_id in enumerate(initial_IDs):
            if adu_id >= start_id:
                speech_id = i
            else:
                break
        return {"speech_id": speech_id, "local_id": adu_id - initial_IDs[speech_id]}
    
    # Test case 1: Basic far rebuttals
    attacks = [
        (8, 0),   # Speech 4 -> Speech 0 (dist = 4)
        (10, 2),  # Speech 5 -> Speech 1 (dist = 4) 
        (8, 4),   # Speech 4 -> Speech 2 (dist = 2, not last speech)
        (10, 6),  # Speech 5 -> Speech 3 (dist = 2, last speech)
    ]
    
    len_att_src_by_speech = [0, 0, 0, 0, 2, 2]  # 2 attacks from speech 4, 2 from speech 5
    
    result = calc_distance(round_data, attacks, mock_l, len_att_src_by_speech)
    expected = 3 / 4  # 3 far rebuttals out of 4 total from speech 4+
    
    print(f"Test 1 - Basic far rebuttals:")
    print(f"  Expected: {expected}")
    print(f"  Actual: {result}")
    print(f"  Match: {abs(result - expected) < 0.001}")
    
    # Test case 2: No far rebuttals
    attacks2 = [
        (8, 6),   # Speech 4 -> Speech 3 (dist = 1)
        (10, 8),  # Speech 5 -> Speech 4 (dist = 1)
    ]
    
    len_att_src_by_speech2 = [0, 0, 0, 0, 1, 1]
    
    result2 = calc_distance(round_data, attacks2, mock_l, len_att_src_by_speech2)
    expected2 = 0.0
    
    print(f"\nTest 2 - No far rebuttals:")
    print(f"  Expected: {expected2}")
    print(f"  Actual: {result2}")
    print(f"  Match: {abs(result2 - expected2) < 0.001}")


if __name__ == "__main__":
    test_distance()