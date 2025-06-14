"""
Run all feature tests
"""

import sys
import os

# Add tests directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tests'))

from test_distance import test_distance


def run_all_tests():
    """Run all feature tests"""
    print("Running all macro-structural feature tests...\n")
    
    test_distance()
    print()
    
    print("All tests completed!")


if __name__ == "__main__":
    run_all_tests()