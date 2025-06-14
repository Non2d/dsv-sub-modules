#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import DebateData, Rebuttal
from calculator import MacroStructuralCalculator

def test_distance_calculation():
    """Test distance calculation with simple data"""
    
    # Simple test case: 6 speeches (like North American style)
    # Speech boundaries: [1, 3, 5, 7, 9, 11] (ADUs 0-1, 2-3, 4-5, 6-7, 8-9, 10-11)
    speeches = [1, 3, 5, 7, 9, 11]
    
    # Test rebuttals from speech 4+ (speeches 4, 5, 6)
    rebuttals = [
        Rebuttal(src=6, dst=0),   # Speech 4 -> Speech 1, distance = 1-4 = -3 (absolute: 3)
        Rebuttal(src=8, dst=2),   # Speech 5 -> Speech 2, distance = 2-5 = -3 (absolute: 3) 
        Rebuttal(src=10, dst=4),  # Speech 6 -> Speech 3, distance = 3-6 = -3 (absolute: 3)
        Rebuttal(src=6, dst=2),   # Speech 4 -> Speech 2, distance = 2-4 = -2 (absolute: 2)
    ]
    
    # No POIs for simplicity
    poi_adus = []
    
    debate_data = DebateData(speeches, rebuttals, poi_adus)
    calculator = MacroStructuralCalculator(debate_data)
    
    print("=== Test Case 1: Basic Distance Calculation ===")
    print(f"Speeches: {speeches}")
    print(f"Number of speeches: {len(speeches)}")
    print(f"Rebuttals: {rebuttals}")
    
    # Debug the distance calculation step by step
    rebuttals_from_speech_4_plus = [
        r for r in debate_data.rebuttals 
        if debate_data.speech_id(r.src) >= 4
    ]
    
    print(f"\nRebuttals from speech 4+: {len(rebuttals_from_speech_4_plus)}")
    for r in rebuttals_from_speech_4_plus:
        src_speech = debate_data.speech_id(r.src)
        dst_speech = debate_data.speech_id(r.dst)
        distance = dst_speech - src_speech
        print(f"  Rebuttal {r.src}->{r.dst}: speech {src_speech}->{dst_speech}, distance={distance}")
        
        # Check distant rebuttal conditions
        num_speeches = len(debate_data.speeches)
        is_distant = (src_speech == num_speeches - 2 and abs(distance) >= 2) or abs(distance) >= 3
        print(f"    num_speeches={num_speeches}, src_speech={src_speech}")
        print(f"    Condition 1 (second-to-last speech): {src_speech == num_speeches - 2 and abs(distance) >= 2}")
        print(f"    Condition 2 (distance >= 3): {abs(distance) >= 3}")
        print(f"    Is distant: {is_distant}")
    
    distance_score = calculator.calc_distance()
    print(f"\nDistance score: {distance_score}")

def test_distance_with_poi():
    """Test distance calculation with POI"""
    
    speeches = [1, 3, 5, 7, 9, 11]
    
    # Same rebuttals but with POI
    rebuttals = [
        Rebuttal(src=6, dst=0),   # Speech 4 -> Speech 1
        Rebuttal(src=8, dst=2),   # Speech 5 -> Speech 2
        Rebuttal(src=7, dst=3),   # POI in speech 4 -> Speech 2 (should be invalid)
    ]
    
    # ADU 7 is a POI (appears in speech 4 but belongs to opposition)
    poi_adus = [7]
    
    debate_data = DebateData(speeches, rebuttals, poi_adus)
    calculator = MacroStructuralCalculator(debate_data)
    
    print("\n=== Test Case 2: Distance with POI ===")
    print(f"Speeches: {speeches}")
    print(f"Rebuttals: {rebuttals}")
    print(f"POI ADUs: {poi_adus}")
    
    # Check team assignments
    for r in rebuttals:
        src_team = debate_data.effective_team(r.src)
        dst_team = debate_data.effective_team(r.dst)
        is_valid = calculator._is_valid_rebuttal(r)
        print(f"  Rebuttal {r.src}->{r.dst}: {src_team} -> {dst_team}, valid: {is_valid}")
    
    distance_score = calculator.calc_distance()
    print(f"\nDistance score with POI: {distance_score}")

def test_actual_data_sample():
    """Test with actual data from JSON"""
    
    # Load actual data
    from data.json2argument_framework import create_single_debate_data_from_json
    
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'debate_scripts.json')
    
    try:
        debate_data = create_single_debate_data_from_json(json_path, 0)
        calculator = MacroStructuralCalculator(debate_data)
        
        print("\n=== Test Case 3: Actual Data Sample ===")
        print(f"Speeches: {debate_data.speeches}")
        print(f"Total rebuttals: {len(debate_data.rebuttals)}")
        print(f"POI ADUs: {debate_data.poi_adus}")
        
        # Check rebuttals from speech 4+
        rebuttals_from_speech_4_plus = [
            r for r in debate_data.rebuttals 
            if debate_data.speech_id(r.src) >= 4
        ]
        print(f"Rebuttals from speech 4+: {len(rebuttals_from_speech_4_plus)}")
        
        valid_rebuttals_from_speech_4_plus = [
            r for r in rebuttals_from_speech_4_plus 
            if calculator._is_valid_rebuttal(r)
        ]
        print(f"Valid rebuttals from speech 4+: {len(valid_rebuttals_from_speech_4_plus)}")
        
        if valid_rebuttals_from_speech_4_plus:
            print("Sample valid rebuttals:")
            for r in valid_rebuttals_from_speech_4_plus[:5]:
                src_speech = debate_data.speech_id(r.src)
                dst_speech = debate_data.speech_id(r.dst)
                distance = dst_speech - src_speech
                print(f"  {r.src}->{r.dst}: speech {src_speech}->{dst_speech}, distance={distance}")
        
        distance_score = calculator.calc_distance()
        print(f"Distance score: {distance_score}")
        
    except Exception as e:
        print(f"Error loading actual data: {e}")

if __name__ == "__main__":
    test_distance_calculation()
    test_distance_with_poi() 
    test_actual_data_sample()