"""
Distance (Far Rebuttal) feature calculation
"""

from typing import Dict, Any, List, Tuple


def calc_distance(round_data: Dict[str, Any], attacks: List[Tuple[int, int]], 
                 l_func, len_att_src_by_speech: List[int]) -> float:
    """
    Calculate Distance feature (Far Rebuttal)
    
    Args:
        round_data: Original JSON structure of a debate round
        attacks: List of attack tuples (src, dst)
        l_func: Function to get speech_id from ADU id
        len_att_src_by_speech: Number of attacks from each speech
        
    Returns:
        Distance score as float
    """
    slen = len(round_data["speeches"])
    fs_far = {"speech": {"len": [0] * slen}, "round": {"len": 0, "ratio": 0}}
    
    for src, dst in attacks:
        dist = l_func(round_data, src)["speech_id"] - l_func(round_data, dst)["speech_id"]
        if dist >= 3 or (l_func(round_data, src)["speech_id"] != slen - 2 and dist >= 2):
            fs_far["speech"]["len"][l_func(round_data, src)["speech_id"]] += 1
    
    fs_far["round"]["len"] = sum(fs_far["speech"]["len"])
    
    # 4番目以降のスピーチからの総反論数
    total_attacks_from_4th = sum(len_att_src_by_speech[3:])
    
    if total_attacks_from_4th == 0:
        return 0.0
    
    fs_far["round"]["ratio"] = fs_far["round"]["len"] / total_attacks_from_4th
    return fs_far["round"]["ratio"]


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
