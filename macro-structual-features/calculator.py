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
        Calculate Distance feature (Far Rebuttal)
        Far Rebuttal条件：3人以上前 or Opp Reply以外かつ2人以上前
        
        Returns:
            Distance score as float
        """
        valid_rebuttals = [r for r in self.data.rebuttals if self._is_valid_rebuttal(r)]
        rebuttals_from_speech_4_plus = [
            r for r in valid_rebuttals 
            if self.data.speech_id(r.src) >= 4  # 4番目以降のスピーチから
        ]
        
        if not rebuttals_from_speech_4_plus:
            return 0.0
        
        num_far_rebuttals = 0
        num_speeches = len(self.data.speeches)
        
        for rebuttal in rebuttals_from_speech_4_plus:
            src_speech = self.data.speech_id(rebuttal.src)
            dst_speech = self.data.speech_id(rebuttal.dst)
            dist = src_speech - dst_speech  # 何人前に反論しているか
            
            # Far Rebuttalの条件：3人以上前 or Opp Reply以外かつ2人以上前
            if dist >= 3 or (src_speech != num_speeches - 1 and dist >= 2):
                num_far_rebuttals += 1
        
        return num_far_rebuttals / len(rebuttals_from_speech_4_plus)
    
    def calc_interval(self) -> float:
        """
        Calculate Interval feature (Algorithm 2)
        Considers POI team reversal when determining valid rebuttals
        
        Returns:
            Interval score as float
        """
        interval = 0.0
        valid_rebuttals = [r for r in self.data.rebuttals if self._is_valid_rebuttal(r)]
        
        # For each valid rebuttal destination
        for rebuttal in valid_rebuttals:
            dst_adu = rebuttal.dst
            
            # For each speech
            for speech_idx in range(1, len(self.data.speeches) + 1):
                sources = self._get_valid_sources(dst_adu, speech_idx)
                
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
        Considers POI team reversal when determining valid rebuttals
        
        Returns:
            Rally score as float
        """
        rally_degree = 0
        valid_rebuttals = [r for r in self.data.rebuttals if self._is_valid_rebuttal(r)]
        
        for i, rebuttal_i in enumerate(valid_rebuttals):
            for j, rebuttal_j in enumerate(valid_rebuttals):
                if i != j and rebuttal_i.dst == rebuttal_j.src:
                    rally_degree += 1
        
        num_speeches = len(self.data.speeches)
        num_rebuttals = len(valid_rebuttals)
        
        if num_speeches == 0 or num_rebuttals == 0:
            return 0.0
        
        return rally_degree / (num_speeches * num_rebuttals)
    
    def calc_order(self) -> float:
        """
        Calculate Order feature (Algorithm 4)
        Considers POI team reversal when determining valid rebuttals
        
        Returns:
            Order score as float, or -1 if no crossing rebuttals
        """
        num_crosses = 0
        valid_rebuttals = [r for r in self.data.rebuttals if self._is_valid_rebuttal(r)]
        
        for i, rebuttal_i in enumerate(valid_rebuttals):
            is_crossing = False
            
            for j, rebuttal_j in enumerate(valid_rebuttals):
                if i != j:
                    src_i_speech = self.data.speech_id(rebuttal_i.src)
                    src_j_speech = self.data.speech_id(rebuttal_j.src)
                    
                    # Check if both rebuttals are from the same speech and same effective team
                    if (src_i_speech == src_j_speech and 
                        self.data.effective_team(rebuttal_i.src) == self.data.effective_team(rebuttal_j.src)):
                        
                        # Check crossing condition
                        if ((rebuttal_j.src - rebuttal_i.src) * 
                            (rebuttal_j.dst - rebuttal_i.dst) < 0) or rebuttal_i.src == rebuttal_j.src:
                            is_crossing = True
                            break
            
            if is_crossing:
                num_crosses += 1
        
        if num_crosses == 0:
            return -1.0
        
        return len(valid_rebuttals) / num_crosses
    
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
    
    def _is_valid_rebuttal(self, rebuttal: Rebuttal) -> bool:
        """
        Check if a rebuttal is valid considering POI team rules
        A rebuttal is valid if source and destination belong to different teams
        
        Args:
            rebuttal: Rebuttal object to check
            
        Returns:
            True if valid, False otherwise
        """
        src_team = self.data.effective_team(rebuttal.src)
        dst_team = self.data.effective_team(rebuttal.dst)
        return src_team != dst_team
    
    def _get_valid_sources(self, dst_adu: int, speech_index: int) -> List[int]:
        """
        Get valid rebuttal sources for a destination ADU in a specific speech
        Considers POI team reversal
        
        Args:
            dst_adu: Destination ADU index
            speech_index: Speech index (1-indexed)
            
        Returns:
            List of valid source ADU indices
        """
        result = []
        for rebuttal in self.data.rebuttals:
            if (rebuttal.dst == dst_adu and 
                self.data.speech_id(rebuttal.src) == speech_index and
                self._is_valid_rebuttal(rebuttal)):
                result.append(rebuttal.src)
        return result