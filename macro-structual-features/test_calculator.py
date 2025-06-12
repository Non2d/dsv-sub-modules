"""
Comprehensive test cases for macro-structural features calculator
"""

import unittest
from .models import Rebuttal, DebateData
from .calculator import MacroStructuralCalculator
from .sample_data import (
    get_sample_north_american_style,
    get_sample_asian_style,
    get_sample_interval_case,
    get_sample_rally_chain,
    get_sample_order_crossing
)


class TestDebateData(unittest.TestCase):
    """Test cases for DebateData class"""
    
    def setUp(self):
        """Set up test data"""
        self.speeches = [1, 3, 5, 7]  # 4 speeches, 2 statements each
        self.rebuttals = [
            Rebuttal(src=2, dst=0),
            Rebuttal(src=4, dst=1),
        ]
        self.data = DebateData(self.speeches, self.rebuttals)
    
    def test_speech_id(self):
        """Test speech_id method"""
        self.assertEqual(self.data.speech_id(0), 1)
        self.assertEqual(self.data.speech_id(1), 1)
        self.assertEqual(self.data.speech_id(2), 2)
        self.assertEqual(self.data.speech_id(3), 2)
        self.assertEqual(self.data.speech_id(4), 3)
        self.assertEqual(self.data.speech_id(5), 3)
        self.assertEqual(self.data.speech_id(6), 4)
        self.assertEqual(self.data.speech_id(7), 4)
    
    def test_speech_id_invalid(self):
        """Test speech_id with invalid input"""
        with self.assertRaises(ValueError):
            self.data.speech_id(100)
    
    def test_adus_in_speech(self):
        """Test adus_in_speech method"""
        self.assertEqual(self.data.adus_in_speech(1), [0, 1])
        self.assertEqual(self.data.adus_in_speech(2), [2, 3])
        self.assertEqual(self.data.adus_in_speech(3), [4, 5])
        self.assertEqual(self.data.adus_in_speech(4), [6, 7])
    
    def test_adus_in_speech_invalid(self):
        """Test adus_in_speech with invalid input"""
        with self.assertRaises(ValueError):
            self.data.adus_in_speech(0)
        with self.assertRaises(ValueError):
            self.data.adus_in_speech(5)
    
    def test_sources(self):
        """Test sources method"""
        # Rebuttal from speech 2 (src=2) to dst=0
        self.assertEqual(self.data.sources(0, 2), [2])
        # Rebuttal from speech 3 (src=4) to dst=1
        self.assertEqual(self.data.sources(1, 3), [4])
        # No rebuttals to dst=0 from speech 1
        self.assertEqual(self.data.sources(0, 1), [])


class TestMacroStructuralCalculator(unittest.TestCase):
    """Test cases for MacroStructuralCalculator"""
    
    def test_distance_calculation(self):
        """Test distance calculation with sample data"""
        data = get_sample_north_american_style()
        calculator = MacroStructuralCalculator(data)
        
        # Expected: rebuttals from speeches 4+ with distance ≥3 or (last-1 speech with distance ≥2)
        distance = calculator.calc_distance()
        self.assertIsInstance(distance, float)
        self.assertGreaterEqual(distance, 0.0)
        self.assertLessEqual(distance, 1.0)
    
    def test_distance_no_qualifying_rebuttals(self):
        """Test distance calculation with no qualifying rebuttals"""
        speeches = [1, 3]  # Only 2 speeches
        rebuttals = [Rebuttal(src=2, dst=0)]  # From speech 2, not ≥4
        data = DebateData(speeches, rebuttals)
        calculator = MacroStructuralCalculator(data)
        
        distance = calculator.calc_distance()
        self.assertEqual(distance, 0.0)
    
    def test_interval_calculation(self):
        """Test interval calculation with specific case"""
        data = get_sample_interval_case()
        calculator = MacroStructuralCalculator(data)
        
        interval = calculator.calc_interval()
        self.assertIsInstance(interval, float)
        self.assertGreaterEqual(interval, 0.0)
    
    def test_interval_no_multiple_sources(self):
        """Test interval calculation with no multiple sources to same target"""
        speeches = [1, 3, 5]
        rebuttals = [
            Rebuttal(src=2, dst=0),
            Rebuttal(src=4, dst=1),
        ]
        data = DebateData(speeches, rebuttals)
        calculator = MacroStructuralCalculator(data)
        
        interval = calculator.calc_interval()
        self.assertEqual(interval, 0.0)
    
    def test_rally_calculation(self):
        """Test rally calculation with rally chain"""
        data = get_sample_rally_chain()
        calculator = MacroStructuralCalculator(data)
        
        rally = calculator.calc_rally()
        self.assertIsInstance(rally, float)
        self.assertGreaterEqual(rally, 0.0)
    
    def test_rally_no_chains(self):
        """Test rally calculation with no chains"""
        speeches = [1, 3, 5]
        rebuttals = [
            Rebuttal(src=2, dst=0),
            Rebuttal(src=4, dst=1),
        ]
        data = DebateData(speeches, rebuttals)
        calculator = MacroStructuralCalculator(data)
        
        rally = calculator.calc_rally()
        self.assertEqual(rally, 0.0)
    
    def test_rally_empty_data(self):
        """Test rally calculation with empty rebuttals"""
        speeches = [1, 3]
        rebuttals = []
        data = DebateData(speeches, rebuttals)
        calculator = MacroStructuralCalculator(data)
        
        rally = calculator.calc_rally()
        self.assertEqual(rally, 0.0)
    
    def test_order_calculation(self):
        """Test order calculation with crossing patterns"""
        data = get_sample_order_crossing()
        calculator = MacroStructuralCalculator(data)
        
        order = calculator.calc_order()
        self.assertIsInstance(order, float)
        # Should be positive when there are crossings
        if order != -1:
            self.assertGreater(order, 0.0)
    
    def test_order_no_crossings(self):
        """Test order calculation with no crossings"""
        speeches = [1, 3, 5, 7]
        rebuttals = [
            Rebuttal(src=2, dst=0),
            Rebuttal(src=4, dst=1),
            Rebuttal(src=6, dst=2),
        ]
        data = DebateData(speeches, rebuttals)
        calculator = MacroStructuralCalculator(data)
        
        order = calculator.calc_order()
        self.assertEqual(order, -1.0)
    
    def test_calculate_all(self):
        """Test calculating all features at once"""
        data = get_sample_north_american_style()
        calculator = MacroStructuralCalculator(data)
        
        results = calculator.calculate_all()
        
        self.assertIn('distance', results)
        self.assertIn('interval', results)
        self.assertIn('rally', results)
        self.assertIn('order', results)
        
        for feature, value in results.items():
            self.assertIsInstance(value, float, f"{feature} should be float")


class TestSampleData(unittest.TestCase):
    """Test cases for sample data validity"""
    
    def test_north_american_sample(self):
        """Test North American style sample data"""
        data = get_sample_north_american_style()
        self.assertEqual(len(data.speeches), 6)
        self.assertGreater(len(data.rebuttals), 0)
        
        # Test that all rebuttals reference valid ADUs
        max_adu = data.speeches[-1]
        for rebuttal in data.rebuttals:
            self.assertLessEqual(rebuttal.src, max_adu)
            self.assertLessEqual(rebuttal.dst, max_adu)
    
    def test_asian_sample(self):
        """Test Asian style sample data"""
        data = get_sample_asian_style()
        self.assertEqual(len(data.speeches), 8)
        self.assertGreater(len(data.rebuttals), 0)
        
        # Test that all rebuttals reference valid ADUs
        max_adu = data.speeches[-1]
        for rebuttal in data.rebuttals:
            self.assertLessEqual(rebuttal.src, max_adu)
            self.assertLessEqual(rebuttal.dst, max_adu)
    
    def test_interval_sample(self):
        """Test interval-specific sample data"""
        data = get_sample_interval_case()
        self.assertGreater(len(data.rebuttals), 0)
        
        # Should have multiple rebuttals to same destination
        destinations = [r.dst for r in data.rebuttals]
        self.assertGreater(len(destinations), len(set(destinations)))
    
    def test_rally_chain_sample(self):
        """Test rally chain sample data"""
        data = get_sample_rally_chain()
        
        # Should have at least one rally chain (where dst of one = src of another)
        sources = [r.src for r in data.rebuttals]
        destinations = [r.dst for r in data.rebuttals]
        
        has_chain = any(dst in sources for dst in destinations)
        self.assertTrue(has_chain)
    
    def test_order_crossing_sample(self):
        """Test order crossing sample data"""
        data = get_sample_order_crossing()
        
        # Should have rebuttals from same speech
        speech_counts = {}
        for rebuttal in data.rebuttals:
            speech = data.speech_id(rebuttal.src)
            speech_counts[speech] = speech_counts.get(speech, 0) + 1
        
        has_multiple_from_same_speech = any(count > 1 for count in speech_counts.values())
        self.assertTrue(has_multiple_from_same_speech)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_empty_rebuttals(self):
        """Test with no rebuttals"""
        speeches = [1, 3, 5]
        rebuttals = []
        data = DebateData(speeches, rebuttals)
        calculator = MacroStructuralCalculator(data)
        
        results = calculator.calculate_all()
        self.assertEqual(results['distance'], 0.0)
        self.assertEqual(results['interval'], 0.0)
        self.assertEqual(results['rally'], 0.0)
        self.assertEqual(results['order'], -1.0)
    
    def test_single_speech(self):
        """Test with single speech"""
        speeches = [2]
        rebuttals = [Rebuttal(src=1, dst=0)]
        data = DebateData(speeches, rebuttals)
        calculator = MacroStructuralCalculator(data)
        
        # Should not crash
        results = calculator.calculate_all()
        self.assertIsInstance(results, dict)
    
    def test_self_rebuttal(self):
        """Test with self-referential rebuttal"""
        speeches = [1, 3]
        rebuttals = [Rebuttal(src=2, dst=2)]  # Self-rebuttal
        data = DebateData(speeches, rebuttals)
        calculator = MacroStructuralCalculator(data)
        
        # Should handle gracefully
        results = calculator.calculate_all()
        self.assertIsInstance(results, dict)


if __name__ == '__main__':
    unittest.main()