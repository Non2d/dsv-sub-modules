"""
Order feature calculation
"""

from typing import Dict, Any, List, Tuple
from itertools import combinations


def calc_order(att_src_by_speech: List[List[Tuple[int, int]]], 
              attacks: List[Tuple[int, int]], poi_adus: List[int],
              version: int = 1) -> float:
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
    reb_dst_shared = 0
    reb_crossed = 0
    
    for i, att_s in enumerate(att_src_by_speech):
        for att_pair in combinations(att_s, 2):
            if att_pair[0][0] in poi_adus or att_pair[1][0] in poi_adus: # POI絡みの反論は除外
                continue
            elif att_pair[0][0] == att_pair[1][0]:
                reb_src_shared += 1
            elif att_pair[0][1] == att_pair[1][1]:
                reb_dst_shared += 1
            elif att_pair[0][1] > att_pair[1][1]:  # 完全に交差する条件
                reb_crossed += 1
    
    reb_num = len(attacks) - len(atts_from_POI)
    
    if reb_num == 0 or (reb_src_shared + reb_crossed) == 0:
        return -1.0
    
    if version==1:
        order_value = reb_num / (reb_src_shared + reb_crossed)
    elif version==2:
        order_value = reb_num / (reb_src_shared + reb_dst_shared + reb_crossed)
    else:
        raise ValueError("Invalid version for order calculation.")
    
    return order_value
