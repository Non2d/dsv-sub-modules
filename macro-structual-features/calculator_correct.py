"""
Correct implementation of macro-structural features based on the original code
"""

import sys
import os
from typing import List, Dict, Any, Tuple
from itertools import combinations, groupby
# import numpy as np  # Not needed for basic functionality

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models import DebateData, Rebuttal


def localize(round_data, adu_id):
    """Find speech_id and local_id for an ADU"""
    initial_IDs = []
    for s in round_data["speeches"]:
        initial_IDs.append(s["ADUs"][0]["id"])
    
    # Find which speech this ADU belongs to
    speech_id = 0
    for i, start_id in enumerate(initial_IDs):
        if adu_id >= start_id:
            speech_id = i
        else:
            break
    
    return {"speech_id": speech_id, "local_id": adu_id - initial_IDs[speech_id]}


def l(round_data, adu_id):
    """Alias for localize function"""
    return localize(round_data, adu_id)


def filter_rally(arrays_list):
    """Filter rally duplicates"""
    rev = list(reversed(arrays_list))
    result = rev[0]  # 最長ターンは確定で採用
    for i in range(1, len(arrays_list)):
        for rally in rev[i]:
            if not any(all(item in condition for item in rally) for condition in result):
                result.append(rally)
    return result


class MacroStructuralCalculatorCorrect:
    """Correct implementation based on original code"""
    
    def __init__(self, round_data: Dict[str, Any]):
        """
        Initialize with original round data structure
        
        Args:
            round_data: Original JSON structure of a debate round
        """
        self.round_data = round_data
        self.slen = len(round_data["speeches"])
        self.attacks = []
        for attack in round_data["attacks"]:
            self.attacks.append(tuple(attack.values()))
        
        # Calculate basic features needed for macro features
        self._calculate_basic_features()
    
    def _calculate_basic_features(self):
        """Calculate basic features needed for macro structural features"""
        self.fs = {}
        
        # Basic feature structure
        self.fs["general"] = {
            "round": {"len_word": 0, "len_speech": 0, "len_ADU": 0, "attack": [], "att_src_adu": [], "att_dst_adu": []},
            "speech": {"len_ADU": [], "att_src": [[] for _ in range(self.slen)], "att_dst": [[] for _ in range(self.slen)], 
                      "len_att_src": [0]*self.slen, "len_att_dst": [0]*self.slen, 
                      "att_src_adu": [[] for _ in range(self.slen)], "att_dst_adu": [[] for _ in range(self.slen)]}
        }
        
        # Group attacks by speech
        att_src_gen = {key: list(group) for key, group in groupby(self.attacks, key=lambda x: l(self.round_data, x[0])["speech_id"])}
        att_dst_gen = {key: list(group) for key, group in groupby(self.attacks, key=lambda x: l(self.round_data, x[1])["speech_id"])}
        
        for i in range(self.slen):
            if i not in att_src_gen:
                att_src_gen[i] = []
            if i not in att_dst_gen:
                att_dst_gen[i] = []
        
        att_src_gen_sorted = list(dict(sorted(att_src_gen.items())).values())
        att_dst_gen_sorted = list(dict(sorted(att_dst_gen.items())).values())
        self.fs["general"]["speech"]["att_src"] = att_src_gen_sorted
        self.fs["general"]["speech"]["att_dst"] = att_dst_gen_sorted
        
        # Basic round features
        self.fs["general"]["round"]["len_speech"] = self.slen
        self.fs["general"]["round"]["len_ADU"] = self.round_data["speeches"][-1]["ADUs"][-1]["id"] + 1
        self.fs["general"]["round"]["attack"] = self.attacks
        
        # Basic speech features
        for s in self.round_data["speeches"]:
            self.fs["general"]["speech"]["len_ADU"].append(len(s["ADUs"]))
            
        self.fs["general"]["speech"]["len_att_src"] = [len(nums) for nums in self.fs["general"]["speech"]["att_src"]]
        self.fs["general"]["speech"]["len_att_dst"] = [len(nums) for nums in self.fs["general"]["speech"]["att_dst"]]
    
    def calc_distance(self) -> float:
        """Calculate Distance feature (Far Rebuttal)"""
        # 元のコードに完全に合わせる
        fs_far = {"speech": {"len": [0] * self.slen}, "round": {"len": 0, "ratio": 0}}
        
        for src, dst in self.attacks:
            dist = l(self.round_data, src)["speech_id"] - l(self.round_data, dst)["speech_id"]
            if dist >= 3 or (l(self.round_data, src)["speech_id"] != self.slen - 2 and dist >= 2):
                fs_far["speech"]["len"][l(self.round_data, src)["speech_id"]] += 1
        
        fs_far["round"]["len"] = sum(fs_far["speech"]["len"])
        
        # 4番目以降のスピーチからの総反論数
        total_attacks_from_4th = sum(self.fs["general"]["speech"]["len_att_src"][3:])
        
        if total_attacks_from_4th == 0:
            return 0.0
        
        fs_far["round"]["ratio"] = fs_far["round"]["len"] / total_attacks_from_4th
        return fs_far["round"]["ratio"]
    
    def calc_interval(self) -> float:
        """Calculate Interval feature"""
        # 最終結果: sum(fs["interval"]["round"]["intervals_normalized2"])
        att_dst_adu_src = []
        tmp_att_dst_adu_src = {}
        
        for atts in self.fs["general"]["speech"]["att_src"]:
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
                speech_len = self.fs["general"]["speech"]["len_ADU"][j]
                if speech_len > 2:
                    intervals_normalized2.append(tmp_x / (speech_len - 2))
        
        # 最終結果は総和（平均ではない）
        return sum(intervals_normalized2)
    
    def calc_rally(self) -> float:
        """Calculate Rally feature"""
        # 最終結果: fs["rally"]["total"]/len(fs["general"]["round"]["attack"])/fs["general"]["round"]["len_speech"]
        att_rally_lists = []
        att_2_list = []
        
        # Find 2-attack rallies
        for att1 in reversed(self.attacks):
            for att2 in [att_dst_candidate for att_dst_candidate in reversed(self.attacks) if att_dst_candidate[0] < att1[0]]:
                if att1[1] == att2[0]:
                    att_2_list.append([att1, att2])
        
        att_rally_lists.append(att_2_list)
        
        # Extend to longer rallies
        att_n_list = [0]
        while len(att_n_list) > 0:
            att_n_list = []
            for rally in reversed(att_rally_lists[-1]):
                for att_dst in [att_dst_candidate for att_dst_candidate in reversed(self.attacks) if att_dst_candidate[0] < rally[-1][0]]:
                    if rally[-1][1] == att_dst[0]:
                        att_n_list.append(rally + [att_dst])
            if len(att_n_list) > 0:
                att_rally_lists.append(att_n_list)
        
        # Filter rallies to remove duplicates
        att_rally_lists_filtered = filter_rally(att_rally_lists)
        
        # Calculate total rally score
        if not att_rally_lists_filtered:
            return 0.0
        
        # ノーラリー（単体の反論）も含めて全反論をカバー
        att_noRally_list = [[att] for att in self.attacks if not any(att in att_list for att_list in att_rally_lists_filtered)]
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
        
        num_speeches = self.slen
        num_rebuttals = len(self.attacks)
        
        if num_speeches == 0 or num_rebuttals == 0:
            return 0.0
        
        # 最終結果の計算式
        return total_rally / num_rebuttals / num_speeches
    
    def calc_order(self) -> float:
        """Calculate Order feature"""
        # 元のコードに完全に合わせる
        atts_from_POI = []
        for att in self.attacks:
            if att[0] in self.round_data["POIs"]:
                atts_from_POI.append(att)
        
        # スピーチごとに反論の組を列挙
        reb_src_shared = 0
        reb_crossed = 0
        
        for i, att_s in enumerate(self.fs["general"]["speech"]["att_src"]):
            for att_pair in combinations(att_s, 2):
                if att_pair[0][0] in self.round_data["POIs"] or att_pair[1][0] in self.round_data["POIs"]:
                    continue
                elif att_pair[0][0] == att_pair[1][0]:
                    reb_src_shared += 1
                elif att_pair[0][1] > att_pair[1][1]:  # この条件が重要！
                    reb_crossed += 1
        
        reb_num = len(self.attacks) - len(atts_from_POI)
        
        if reb_num == 0 or (reb_src_shared + reb_crossed) == 0:
            return -1.0
        
        order_value = reb_num / (reb_src_shared + reb_crossed)
        # 最終結果は逆数
        return 1.0 / order_value
    
    def calculate_all(self) -> Dict[str, float]:
        """Calculate all four macro-structural features"""
        return {
            'distance': self.calc_distance(),
            'interval': self.calc_interval(),
            'rally': self.calc_rally(),
            'order': self.calc_order()
        }