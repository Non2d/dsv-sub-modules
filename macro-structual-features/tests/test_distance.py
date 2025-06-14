"""Test functions for Distance feature calculation"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from features.distance import calc_distance


def test_distance():
    """Test distance calculation"""
    print("=== Testing Distance Calculation ===")
    
    # Mock data for testing
    round_data = {
        "speeches": [
            {"ADUs": [{"id": 0}, {"id": 1}]},
            {"ADUs": [{"id": 2}, {"id": 3}]},
            {"ADUs": [{"id": 4}, {"id": 5}]},
            {"ADUs": [{"id": 6}, {"id": 7}]},
            {"ADUs": [{"id": 8}, {"id": 9}]},
            {"ADUs": [{"id": 10}, {"id": 11}]},
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
    
    attacks = [(8, 0), (10, 2), (8, 4), (10, 6)]
    len_att_src_by_speech = [0, 0, 0, 0, 2, 2]
    
    result = calc_distance(round_data, attacks, mock_l, len_att_src_by_speech)
    expected = 3 / 4
    
    print(f"Test 1 - Basic far rebuttals:")
    print(f"  Expected: {expected}")
    print(f"  Actual: {result}")
    print(f"  Match: {abs(result - expected) < 0.001}")


if __name__ == "__main__":
    test_distance()