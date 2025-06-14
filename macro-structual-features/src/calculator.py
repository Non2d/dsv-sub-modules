"""
Main calculator for macro-structural features
"""

import sys
import os
from typing import List, Dict, Any, Tuple
from itertools import groupby

# Add features directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'features'))
from features.distance import calc_distance
from features.interval import calc_interval
from features.rally import calc_rally
from features.order import calc_order


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


class MacroStructuralCalculator:
    """Calculator for macro-structural features"""
    
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
        # Group attacks by speech
        att_src_gen = {key: list(group) for key, group in groupby(self.attacks, key=lambda x: l(self.round_data, x[0])["speech_id"])}
        att_dst_gen = {key: list(group) for key, group in groupby(self.attacks, key=lambda x: l(self.round_data, x[1])["speech_id"])}
        
        for i in range(self.slen):
            if i not in att_src_gen:
                att_src_gen[i] = []
            if i not in att_dst_gen:
                att_dst_gen[i] = []
        
        self.att_src_by_speech = list(dict(sorted(att_src_gen.items())).values())
        self.att_dst_by_speech = list(dict(sorted(att_dst_gen.items())).values())
        
        # Calculate lengths
        self.len_att_src_by_speech = [len(atts) for atts in self.att_src_by_speech]
        self.len_att_dst_by_speech = [len(atts) for atts in self.att_dst_by_speech]
        
        # Calculate speech lengths (number of ADUs)
        self.len_adu_by_speech = []
        for s in self.round_data["speeches"]:
            self.len_adu_by_speech.append(len(s["ADUs"]))
    
    def calc_distance(self) -> float:
        """Calculate Distance feature (Far Rebuttal)"""
        return calc_distance(
            self.round_data, 
            self.attacks, 
            l, 
            self.len_att_src_by_speech
        )
    
    def calc_interval(self) -> float:
        """Calculate Interval feature"""
        return calc_interval(
            self.att_src_by_speech,
            self.len_adu_by_speech
        )
    
    def calc_rally(self) -> float:
        """Calculate Rally feature"""
        return calc_rally(
            self.attacks,
            self.slen
        )
    
    def calc_order(self) -> float:
        """Calculate Order feature"""
        return calc_order(
            self.att_src_by_speech,
            self.attacks,
            self.round_data.get("POIs", [])
        )
    
    def calculate_all(self) -> Dict[str, float]:
        """Calculate all four macro-structural features"""
        return {
            'distance': self.calc_distance(),
            'interval': self.calc_interval(),
            'rally': self.calc_rally(),
            'order': self.calc_order()
        }