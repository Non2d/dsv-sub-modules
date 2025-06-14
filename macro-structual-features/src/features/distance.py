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


