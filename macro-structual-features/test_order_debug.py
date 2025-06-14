#!/usr/bin/env python3

import sys
import os
import json
from itertools import combinations

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from calculator_correct import MacroStructuralCalculatorCorrect

def test_order_calculation():
    """Test order calculation with actual data"""
    
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'debate_scripts.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        debate_scripts = json.load(f)
    
    # Test first few debates
    for i in range(min(3, len(debate_scripts))):
        round_data = debate_scripts[i]
        calculator = MacroStructuralCalculatorCorrect(round_data)
        
        print(f"\n=== Debate {i}: {round_data['source']['title']} ===")
        print(f"Total attacks: {len(calculator.attacks)}")
        print(f"POIs: {round_data.get('POIs', [])}")
        
        # POI attacks
        atts_from_POI = []
        for att in calculator.attacks:
            if att[0] in round_data["POIs"]:
                atts_from_POI.append(att)
        print(f"POI attacks: {len(atts_from_POI)}")
        
        # Check attacks by speech
        reb_src_shared = 0
        reb_crossed = 0
        
        print(f"Attacks by speech:")
        for j, att_s in enumerate(calculator.fs["general"]["speech"]["att_src"]):
            print(f"  Speech {j}: {len(att_s)} attacks - {att_s}")
            
            pairs_checked = 0
            pairs_poi_skipped = 0
            pairs_src_shared = 0
            pairs_crossed = 0
            
            for att_pair in combinations(att_s, 2):
                pairs_checked += 1
                if att_pair[0][0] in round_data["POIs"] or att_pair[1][0] in round_data["POIs"]:
                    pairs_poi_skipped += 1
                    continue
                elif att_pair[0][0] == att_pair[1][0]:
                    reb_src_shared += 1
                    pairs_src_shared += 1
                elif att_pair[0][1] > att_pair[1][1]:
                    reb_crossed += 1
                    pairs_crossed += 1
            
            print(f"    Pairs: {pairs_checked}, POI skipped: {pairs_poi_skipped}, Src shared: {pairs_src_shared}, Crossed: {pairs_crossed}")
        
        print(f"Total reb_src_shared: {reb_src_shared}")
        print(f"Total reb_crossed: {reb_crossed}")
        
        reb_num = len(calculator.attacks) - len(atts_from_POI)
        print(f"reb_num (total - POI): {reb_num}")
        
        if reb_num == 0 or (reb_src_shared + reb_crossed) == 0:
            order_result = -1.0
        else:
            order_result = reb_num / (reb_src_shared + reb_crossed)
        
        print(f"Expected Order: {order_result}")
        
        actual_order = calculator.calc_order()
        print(f"Actual Order: {actual_order}")
        print(f"Match: {abs(order_result - actual_order) < 0.001}")

if __name__ == "__main__":
    test_order_calculation()