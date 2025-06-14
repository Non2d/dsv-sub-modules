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


