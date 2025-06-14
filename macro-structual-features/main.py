"""
Main execution script for macro-structural features calculation
"""

import json
import csv
from calculator import MacroStructuralCalculator


def main():
    """Calculate macro-structural features for all debates and save to TSV"""
    print("Calculating macro-structural features...")
    
    # Load data
    with open('data/debate_scripts.json', 'r', encoding='utf-8') as f:
        debate_scripts = json.load(f)
    
    print(f"Loaded {len(debate_scripts)} debate rounds")
    
    # Calculate features
    results = []
    for i, round_data in enumerate(debate_scripts):
        calculator = MacroStructuralCalculator(round_data)
        features = calculator.calculate_all()
        
        result = {
            'debate_id': i,
            'title': round_data['source']['title'],
            'distance': features['distance'],
            'interval': features['interval'],
            'order': features['order'],
            'rally': features['rally'],
        }
        results.append(result)
        print(f"Debate {i}: {features}")
    
    # Save to TSV
    with open('data/macro_structural_features.tsv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['debate_id', 'title', 'distance', 'interval', 'order', 'rally']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nResults saved to: data/macro_structural_features.tsv")


if __name__ == "__main__":
    main()