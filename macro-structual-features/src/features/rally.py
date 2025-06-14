"""
Rally feature calculation
"""

from typing import Dict, Any, List, Tuple


def filter_rally(arrays_list):
    """Filter rally duplicates"""
    if not arrays_list:
        return []
    
    rev = list(reversed(arrays_list))
    result = rev[0]  # 最長ターンは確定で採用
    for i in range(1, len(arrays_list)):
        for rally in rev[i]:
            if not any(all(item in condition for item in rally) for condition in result):
                result.append(rally)
    return result


def calc_rally(attacks: List[Tuple[int, int]], num_speeches: int) -> float:
    """
    Calculate Rally feature
    
    Args:
        attacks: List of attack tuples (src, dst)
        num_speeches: Number of speeches
        
    Returns:
        Rally score (total rally / num_rebuttals / num_speeches)
    """
    if not attacks:
        return 0.0
    
    att_rally_lists = []
    att_2_list = []
    
    # Find 2-attack rallies
    for att1 in reversed(attacks):
        for att2 in [att_dst_candidate for att_dst_candidate in reversed(attacks) if att_dst_candidate[0] < att1[0]]:
            if att1[1] == att2[0]:
                att_2_list.append([att1, att2])
    
    att_rally_lists.append(att_2_list)
    
    # Extend to longer rallies
    att_n_list = [0]
    while len(att_n_list) > 0:
        att_n_list = []
        for rally in reversed(att_rally_lists[-1]):
            for att_dst in [att_dst_candidate for att_dst_candidate in reversed(attacks) if att_dst_candidate[0] < rally[-1][0]]:
                if rally[-1][1] == att_dst[0]:
                    att_n_list.append(rally + [att_dst])
        if len(att_n_list) > 0:
            att_rally_lists.append(att_n_list)
    
    # Filter rallies to remove duplicates
    att_rally_lists_filtered = filter_rally(att_rally_lists)
    
    if not att_rally_lists_filtered:
        return 0.0
    
    # ノーラリー（単体の反論）も含めて全反論をカバー
    att_noRally_list = [[att] for att in attacks if not any(att in att_list for att_list in att_rally_lists_filtered)]
    raw_list = list(reversed(att_rally_lists_filtered + att_noRally_list))
    
    if not raw_list:
        return 0.0
        
    # 最大ラリー長を計算
    max_rally_len = max(len(rally_content) for rally_content in raw_list) if raw_list else 1
    rally_grouped_by_len = [[] for _ in range(max_rally_len)]
    
    for rally_content in raw_list:
        rally_grouped_by_len[len(rally_content) - 1].append(rally_content)
    
    rally_len_list_grouped = [len(sublist) for sublist in rally_grouped_by_len]
    total_rally = sum(rally_len_list_grouped[i] * i for i in range(len(rally_len_list_grouped)))
    
    num_rebuttals = len(attacks)
    
    if num_speeches == 0 or num_rebuttals == 0:
        return 0.0
    
    # 最終結果の計算式
    return total_rally / num_rebuttals / num_speeches


