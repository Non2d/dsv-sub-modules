"""
Interval feature calculation
"""

from typing import Dict, Any, List, Tuple


def calc_interval(att_src_by_speech: List[List[Tuple[int, int]]], 
                 len_adu_by_speech: List[int]) -> float:
    """
    Calculate Interval feature
    
    Args:
        att_src_by_speech: Attacks grouped by source speech
        len_adu_by_speech: Number of ADUs in each speech
        
    Returns:
        Sum of normalized intervals
    """
    att_dst_adu_src = []
    tmp_att_dst_adu_src = {}
    
    for atts in att_src_by_speech:
        for att in atts:
            if att[1] in tmp_att_dst_adu_src:
                tmp_att_dst_adu_src[att[1]].append(att)
            else:
                tmp_att_dst_adu_src[att[1]] = [att]
        tmp_att_dst_adu_src = {key: value for key, value in tmp_att_dst_adu_src.items() if len(value) > 1}
        tmp_att_dst_adu_src = list(tmp_att_dst_adu_src.values())
        att_dst_adu_src.append(tmp_att_dst_adu_src)
        tmp_att_dst_adu_src = {}

    intervals_normalized2 = []
    
    for j, atts in enumerate(att_dst_adu_src):
        for att in atts:
            tmp_x = att[-1][0] - att[0][0] - 1  # スピーチ内の間隔の総和
            speech_len = len_adu_by_speech[j]
            if speech_len > 2:
                intervals_normalized2.append(tmp_x / (speech_len - 2))
    
    # 最終結果は総和（平均ではない）
    return sum(intervals_normalized2)


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