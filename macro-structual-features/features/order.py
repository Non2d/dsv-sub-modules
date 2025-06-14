"""
Order feature calculation
"""

from typing import Dict, Any, List, Tuple
from itertools import combinations


def calc_order(att_src_by_speech: List[List[Tuple[int, int]]], 
              attacks: List[Tuple[int, int]], poi_adus: List[int]) -> float:
    """
    Calculate Order feature
    
    Args:
        att_src_by_speech: Attacks grouped by source speech
        attacks: List of all attack tuples
        poi_adus: List of POI ADU IDs
        
    Returns:
        Order score (inverse of correspondence ratio)
    """
    # POI attacks
    atts_from_POI = []
    for att in attacks:
        if att[0] in poi_adus:
            atts_from_POI.append(att)
    
    # スピーチごとに反論の組を列挙
    reb_src_shared = 0
    reb_crossed = 0
    
    for i, att_s in enumerate(att_src_by_speech):
        for att_pair in combinations(att_s, 2):
            if att_pair[0][0] in poi_adus or att_pair[1][0] in poi_adus:
                continue
            elif att_pair[0][0] == att_pair[1][0]:
                reb_src_shared += 1
            elif att_pair[0][1] > att_pair[1][1]:  # この条件が重要！
                reb_crossed += 1
    
    reb_num = len(attacks) - len(atts_from_POI)
    
    if reb_num == 0 or (reb_src_shared + reb_crossed) == 0:
        return -1.0
    
    order_value = reb_num / (reb_src_shared + reb_crossed)
    # 最終結果は逆数
    return 1.0 / order_value


def test_order():
    """Test order calculation"""
    print("=== Testing Order Calculation ===")
    
    # Test case 1: Basic crossing and shared source
    att_src_by_speech = [
        [],  # Speech 0: no attacks
        [(10, 5), (10, 3), (11, 7)],  # Speech 1: shared source (10) and crossing
        [(20, 15), (21, 12)],         # Speech 2: crossing (15 > 12)
        []   # Speech 3: no attacks
    ]
    
    attacks = [(10, 5), (10, 3), (11, 7), (20, 15), (21, 12)]
    poi_adus = []
    
    result = calc_order(att_src_by_speech, attacks, poi_adus)
    # Speech 1: (10,5)-(10,3) = shared source, (10,5)-(11,7) = no crossing (5<7), (10,3)-(11,7) = no crossing (3<7)
    # Speech 2: (20,15)-(21,12) = crossing (15>12)
    # reb_src_shared = 1, reb_crossed = 1, reb_num = 5
    # order_value = 5 / (1+1) = 2.5, result = 1/2.5 = 0.4
    expected = 1.0 / 2.5
    
    print(f"Test 1 - Basic crossing and shared:")
    print(f"  Expected: {expected}")
    print(f"  Actual: {result}")
    print(f"  Match: {abs(result - expected) < 0.001}")
    
    # Test case 2: With POI attacks
    att_src_by_speech2 = [
        [(5, 10), (6, 10)],  # POI attack and normal attack
        [(15, 20), (16, 18)] # Crossing
    ]
    
    attacks2 = [(5, 10), (6, 10), (15, 20), (16, 18)]
    poi_adus2 = [5]  # ADU 5 is POI
    
    result2 = calc_order(att_src_by_speech2, attacks2, poi_adus2)
    # POI attack (5,10) is skipped
    # Speech 0: only (6,10) remains (no pairs)
    # Speech 1: (15,20)-(16,18) = crossing (20>18)
    # reb_src_shared = 0, reb_crossed = 1, reb_num = 3 (4-1 POI)
    # order_value = 3/1 = 3, result = 1/3
    expected2 = 1.0 / 3.0
    
    print(f"\nTest 2 - With POI attacks:")
    print(f"  Expected: {expected2}")
    print(f"  Actual: {result2}")
    print(f"  Match: {abs(result2 - expected2) < 0.001}")
    
    # Test case 3: No crossing or shared sources
    att_src_by_speech3 = [
        [(10, 5)],   # Single attack
        [(20, 15)],  # Single attack
        [(30, 25)]   # Single attack
    ]
    
    attacks3 = [(10, 5), (20, 15), (30, 25)]
    poi_adus3 = []
    
    result3 = calc_order(att_src_by_speech3, attacks3, poi_adus3)
    # No pairs can be formed (all speeches have only 1 attack)
    # reb_src_shared = 0, reb_crossed = 0, reb_num = 3
    # Should return -1.0 (division by zero case)
    expected3 = -1.0
    
    print(f"\nTest 3 - No pairs:")
    print(f"  Expected: {expected3}")
    print(f"  Actual: {result3}")
    print(f"  Match: {abs(result3 - expected3) < 0.001}")


if __name__ == "__main__":
    test_order()