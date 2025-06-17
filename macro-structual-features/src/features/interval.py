"""
Interval feature calculation
"""
from typing import Dict, Any, List, Tuple

def calc_interval(att_src_by_speech: List[List[Tuple[int, int]]], 
                 len_adu_by_speech: List[int],
                 version: int = 1) -> float:
    """
    Calculate Interval feature
    
    Args:
        att_src_by_speech: Attacks grouped by source speech
        len_adu_by_speech: Number of ADUs in each speech
        version: Normalization update
            1: simple normalization
            2: minimum interval considered
        
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

    intervals_normalized = []
    dst_shard_reb_count = 0
    
    for j, atts in enumerate(att_dst_adu_src):
        speech_len = len_adu_by_speech[j]
        
        for att in atts:
            tmp_x = att[-1][0] - att[0][0] - 1  # スピーチ内の間隔の総和
            dst_shard_reb_count += len(att) - 1
            
            if version == 1:
                # intervals_normalized2 (シンプルな正規化)
                if speech_len > 2:
                    intervals_normalized.append(tmp_x / (speech_len - 2))
            
            elif version == 2:
                # intervals_normalized (最小間隔を考慮した正規化)
                tmp_min = len(att) - 2  # 最小可能間隔
                tmp_max = speech_len - len(att)  # 最大可能間隔
                if tmp_max != 0:
                    intervals_normalized.append((tmp_x - tmp_min) / tmp_max)
                else:
                    intervals_normalized.append(0)
            
            else:
                raise ValueError("Invalid version for interval calculation.")
    # print(f"dst_shard_reb_count: {dst_shard_reb_count}")
    # 最終結果は総和（平均ではない）
    return sum(intervals_normalized)
