"""
Run all feature tests
"""

import sys
import os

# Add features directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'features'))

from features.distance import test_distance
from features.interval import test_interval
from features.rally import test_rally
from features.order import test_order


def run_all_tests():
    """Run all feature tests"""
    print("Running all macro-structural feature tests...\n")
    
    test_distance()
    print()
    
    test_interval()
    print()
    
    test_rally()
    print()
    
    test_order()
    print()
    
    print("All tests completed!")


if __name__ == "__main__":
    run_all_tests()