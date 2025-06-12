"""
Main calculator for macro-structural features of rebuttals
"""

from typing import List

try:
    from .models import DebateData, Rebuttal
except ImportError:
    from models import DebateData, Rebuttal


class MacroStructuralCalculator:
    """Calculator for macro-structural features based on the four algorithms"""
    
    def __init__(self, debate_data: DebateData):
        """
        Initialize calculator with debate data
        
        Args:
            debate_data: DebateData instance containing speeches and rebuttals
        """
        self.data = debate_data
    
    def calc_distance(self) -> float:
        """
        Calculate Distance feature (Algorithm 1)
        
        Returns:
            Distance score as float
        """
        rebuttals_from_speech_4_plus = [
            r for r in self.data.rebuttals 
            if self.data.speech_id(r.src) >= 4
        ]
        
        if not rebuttals_from_speech_4_plus:
            return 0.0
        
        num_distant_rebuttals = 0
        num_speeches = len(self.data.speeches)
        
        for rebuttal in rebuttals_from_speech_4_plus:
            src_speech = self.data.speech_id(rebuttal.src)
            dst_speech = self.data.speech_id(rebuttal.dst)
            distance = dst_speech - src_speech
            
            # Check if this is a distant rebuttal
            if (src_speech == num_speeches - 2 and distance >= 2) or distance >= 3:
                num_distant_rebuttals += 1
        
        return num_distant_rebuttals / len(rebuttals_from_speech_4_plus)
    
    def calc_interval(self) -> float:
        """
        Calculate Interval feature (Algorithm 2)
        
        Returns:
            Interval score as float
        """
        interval = 0.0
        
        # For each rebuttal destination
        for rebuttal in self.data.rebuttals:
            dst_adu = rebuttal.dst
            
            # For each speech
            for speech_idx in range(1, len(self.data.speeches) + 1):
                sources = self.data.sources(dst_adu, speech_idx)
                
                if len(sources) > 1:
                    adus_in_speech = self.data.adus_in_speech(speech_idx)
                    speech_length = len(adus_in_speech)
                    
                    if speech_length > 2:  # Avoid division by zero
                        max_source = max(sources)
                        min_source = min(sources)
                        interval += (max_source - min_source - 1) / (speech_length - 2)
        
        return interval
    
    def calc_rally(self) -> float:
        """
        Calculate Rally feature (Algorithm 3)
        
        Returns:
            Rally score as float
        """
        rally_degree = 0
        
        for i, rebuttal_i in enumerate(self.data.rebuttals):
            for j, rebuttal_j in enumerate(self.data.rebuttals):
                if i != j and rebuttal_i.dst == rebuttal_j.src:
                    rally_degree += 1
        
        num_speeches = len(self.data.speeches)
        num_rebuttals = len(self.data.rebuttals)
        
        if num_speeches == 0 or num_rebuttals == 0:
            return 0.0
        
        return rally_degree / (num_speeches * num_rebuttals)
    
    def calc_order(self) -> float:
        """
        Calculate Order feature (Algorithm 4)
        
        Returns:
            Order score as float, or -1 if no crossing rebuttals
        """
        num_crosses = 0
        
        for i, rebuttal_i in enumerate(self.data.rebuttals):
            is_crossing = False
            
            for j, rebuttal_j in enumerate(self.data.rebuttals):
                if i != j:
                    src_i_speech = self.data.speech_id(rebuttal_i.src)
                    src_j_speech = self.data.speech_id(rebuttal_j.src)
                    
                    if src_i_speech == src_j_speech:
                        # Check crossing condition
                        if ((rebuttal_j.src - rebuttal_i.src) * 
                            (rebuttal_j.dst - rebuttal_i.dst) < 0) or rebuttal_i.src == rebuttal_j.src:
                            is_crossing = True
                            break
            
            if is_crossing:
                num_crosses += 1
        
        if num_crosses == 0:
            return -1.0
        
        return len(self.data.rebuttals) / num_crosses
    
    def calculate_all(self) -> dict:
        """
        Calculate all four macro-structural features
        
        Returns:
            Dictionary with all four feature scores
        """
        return {
            'distance': self.calc_distance(),
            'interval': self.calc_interval(),
            'rally': self.calc_rally(),
            'order': self.calc_order()
        }