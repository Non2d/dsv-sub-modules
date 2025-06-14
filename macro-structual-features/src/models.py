"""
Data models for macro-structural features calculation
"""

from typing import List, Tuple, NamedTuple


class Rebuttal(NamedTuple):
    """Represents a rebuttal with source and destination ADU indices"""
    src: int
    dst: int


class DebateData:
    """Container for debate data and helper functions"""
    
    def __init__(self, speeches: List[int], rebuttals: List[Rebuttal], poi_adus: List[int] = None):
        """
        Initialize debate data
        
        Args:
            speeches: List of speech end indices (e.g., [1, 3, 5, 7, 9, 11])
            rebuttals: List of Rebuttal objects
            poi_adus: List of ADU indices that are Points of Information (POIs)
        """
        self.speeches = speeches
        self.rebuttals = rebuttals
        self.poi_adus = poi_adus or []
        self._speech_ranges = self._calculate_speech_ranges()
    
    def _calculate_speech_ranges(self) -> List[Tuple[int, int]]:
        """Calculate start and end ranges for each speech"""
        ranges = []
        start = 0
        for end_idx in self.speeches:
            ranges.append((start, end_idx))
            start = end_idx + 1
        return ranges
    
    def speech_id(self, adu_index: int) -> int:
        """
        Returns the index of the speech where ADU belongs (1-indexed)
        
        Args:
            adu_index: Index of the ADU
            
        Returns:
            Speech index (1-indexed)
        """
        for i, (start, end) in enumerate(self._speech_ranges):
            if start <= adu_index <= end:
                return i + 1
        raise ValueError(f"ADU index {adu_index} not found in any speech")
    
    def adus_in_speech(self, speech_index: int) -> List[int]:
        """
        Returns list of ADU indices in the given speech
        
        Args:
            speech_index: Speech index (1-indexed)
            
        Returns:
            List of ADU indices in the speech
        """
        if speech_index < 1 or speech_index > len(self.speeches):
            raise ValueError(f"Invalid speech index: {speech_index}")
        
        start, end = self._speech_ranges[speech_index - 1]
        return list(range(start, end + 1))
    
    def sources(self, dst_adu: int, speech_index: int) -> List[int]:
        """
        Returns list of rebuttal source indices that target dst_adu and belong to speech_index
        
        Args:
            dst_adu: Destination ADU index
            speech_index: Speech index (1-indexed)
            
        Returns:
            List of source ADU indices
        """
        result = []
        for rebuttal in self.rebuttals:
            if rebuttal.dst == dst_adu and self.speech_id(rebuttal.src) == speech_index:
                result.append(rebuttal.src)
        return result
    
    def is_poi(self, adu_index: int) -> bool:
        """
        Check if an ADU is a Point of Information (POI)
        
        Args:
            adu_index: Index of the ADU
            
        Returns:
            True if the ADU is a POI, False otherwise
        """
        return adu_index in self.poi_adus
    
    def effective_team(self, adu_index: int) -> str:
        """
        Get the effective team of an ADU considering POI rules
        
        Args:
            adu_index: Index of the ADU
            
        Returns:
            'gov' for Government team, 'opp' for Opposition team
        """
        speech_idx = self.speech_id(adu_index)
        
        # Normal team assignment: odd speeches = Government, even speeches = Opposition
        normal_team = 'gov' if speech_idx % 2 == 1 else 'opp'
        
        # If it's a POI, the team is reversed
        if self.is_poi(adu_index):
            return 'opp' if normal_team == 'gov' else 'gov'
        else:
            return normal_team