"""
Macro-Structural Features Calculator for Parliamentary Debate Rebuttals

This module implements algorithms to calculate four macro-structural features:
- Distance: Measures temporal distance of rebuttals
- Rally: Measures connectivity of rebuttal chains
- Interval: Measures dispersion of rebuttals within speeches
- Order: Measures crossing patterns of rebuttals
"""

from .calculator import MacroStructuralCalculator
from .models import Rebuttal, DebateData

__version__ = "1.0.0"
__all__ = ["MacroStructuralCalculator", "Rebuttal", "DebateData"]