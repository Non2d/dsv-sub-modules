"""
Sample input data for testing macro-structural features
"""

try:
    from .models import Rebuttal, DebateData
except ImportError:
    from models import Rebuttal, DebateData


def get_sample_north_american_style() -> DebateData:
    """
    Sample data for North American style debate (6 speeches)
    
    Returns:
        DebateData instance
    """
    # Each speech has 2 statements, speeches end at indices 1, 3, 5, 7, 9, 11
    speeches = [1, 3, 5, 7, 9, 11]
    
    # Sample rebuttals with various patterns
    rebuttals = [
        Rebuttal(src=2, dst=0),   # Speech 2 rebuts Speech 1
        Rebuttal(src=4, dst=1),   # Speech 3 rebuts Speech 1
        Rebuttal(src=5, dst=2),   # Speech 3 rebuts Speech 2 (rally chain)
        Rebuttal(src=6, dst=0),   # Speech 4 rebuts Speech 1 (distant)
        Rebuttal(src=8, dst=3),   # Speech 5 rebuts Speech 2
        Rebuttal(src=10, dst=4),  # Speech 6 rebuts Speech 3
    ]
    
    return DebateData(speeches, rebuttals)


def get_sample_asian_style() -> DebateData:
    """
    Sample data for Asian style debate (8 speeches)
    
    Returns:
        DebateData instance
    """
    # Each speech has 3 statements, speeches end at indices 2, 5, 8, 11, 14, 17, 20, 23
    speeches = [2, 5, 8, 11, 14, 17, 20, 23]
    
    # Sample rebuttals with crossing patterns
    rebuttals = [
        Rebuttal(src=3, dst=0),   # Speech 2 rebuts Speech 1
        Rebuttal(src=4, dst=1),   # Speech 2 rebuts Speech 1 (crossing pattern)
        Rebuttal(src=6, dst=2),   # Speech 3 rebuts Speech 1
        Rebuttal(src=9, dst=3),   # Speech 4 rebuts Speech 2 (rally)
        Rebuttal(src=12, dst=0),  # Speech 5 rebuts Speech 1 (very distant)
        Rebuttal(src=15, dst=6),  # Speech 6 rebuts Speech 3
        Rebuttal(src=18, dst=9),  # Speech 7 rebuts Speech 4
        Rebuttal(src=21, dst=12), # Speech 8 rebuts Speech 5
    ]
    
    return DebateData(speeches, rebuttals)


def get_sample_interval_case() -> DebateData:
    """
    Sample data specifically designed to test interval calculation
    
    Returns:
        DebateData instance with multiple rebuttals from same speech to same target
    """
    # 4 speeches with 5 statements each
    speeches = [4, 9, 14, 19]
    
    # Multiple rebuttals from speech 2 targeting ADU 0, with gaps between sources
    rebuttals = [
        Rebuttal(src=5, dst=0),   # First rebuttal from speech 2
        Rebuttal(src=7, dst=0),   # Second rebuttal from speech 2 (gap of 1)
        Rebuttal(src=9, dst=0),   # Third rebuttal from speech 2 (gap of 1)
        Rebuttal(src=12, dst=4),  # Rebuttal from speech 3
    ]
    
    return DebateData(speeches, rebuttals)


def get_sample_rally_chain() -> DebateData:
    """
    Sample data with clear rally chains (A→B→C pattern)
    
    Returns:
        DebateData instance with rally chains
    """
    speeches = [1, 3, 5, 7, 9, 11]
    
    # Create a rally chain: 0→2→4→6
    rebuttals = [
        Rebuttal(src=2, dst=0),   # A rebuts initial argument
        Rebuttal(src=4, dst=2),   # B rebuts A (rally)
        Rebuttal(src=6, dst=4),   # C rebuts B (rally)
        Rebuttal(src=8, dst=1),   # Independent rebuttal
    ]
    
    return DebateData(speeches, rebuttals)


def get_sample_order_crossing() -> DebateData:
    """
    Sample data with crossing rebuttal patterns
    
    Returns:
        DebateData instance with crossing rebuttals
    """
    speeches = [2, 5, 8, 11]
    
    # Crossing pattern: from same speech, rebuttals cross each other
    rebuttals = [
        Rebuttal(src=3, dst=0),   # Speech 2: later source to earlier dest
        Rebuttal(src=4, dst=1),   # Speech 2: earlier source to later dest (crossing)
        Rebuttal(src=6, dst=2),   # Speech 3: normal rebuttal
    ]
    
    return DebateData(speeches, rebuttals)