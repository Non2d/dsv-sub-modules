"""
Main execution script for macro-structural features calculation
"""

import json
import csv
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from calculator import MacroStructuralCalculator


def calculate_score(norm_distance, norm_rally, norm_interval, norm_order):
    """Calculate score using the formula: norm(rally) + norm(order) + (1-norm(interval)) + (1-norm(distance))"""
    return norm_rally + norm_order + (1 - norm_interval) + (1 - norm_distance)


def main():
    """Calculate macro-structural features for all debates and save to TSV"""
    print("Calculating macro-structural features...")
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load data
    data_path = os.path.join(script_dir, 'data/src', 'debate_scripts.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        debate_scripts = json.load(f)
    
    print(f"Loaded {len(debate_scripts)} debate rounds")
    
    # Calculate features for all debates
    results = []
    feature_names = ['distance', 'interval', 'order', 'rally']
    
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
    
    # Find maximum values for normalization
    max_values = {}
    for feature_name in feature_names:
        valid_values = []
        for result in results:
            value = result[feature_name]
            if value is not None and value != -1 and value > 0:
                valid_values.append(value)
        
        if valid_values:
            max_values[feature_name] = max(valid_values)
        else:
            max_values[feature_name] = 1.0
    
    print(f"\nMaximum values for normalization:")
    for feature_name, max_val in max_values.items():
        print(f"  {feature_name}: {max_val:.6f}")
    
    # Normalize features and save only normalized values
    normalized_results = []
    for result in results:
        normalized_result = {
            'debate_id': result['debate_id'],
            'title': result['title'],
        }
        
        for feature_name in feature_names:
            original_value = result[feature_name]
            if original_value is not None and original_value != -1 and max_values[feature_name] > 0:
                normalized_value = original_value / max_values[feature_name]
            else:
                normalized_value = 0.0
            
            normalized_result[feature_name] = normalized_value
        
        normalized_results.append(normalized_result)
    
    # Save original results to TSV
    original_output_path = os.path.join(script_dir, 'data/dst', 'macro_structural_features.tsv')
    with open(original_output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['debate_id', 'title', 'distance', 'interval', 'order', 'rally']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(results)
    
    # Save normalized results to TSV
    normalized_output_path = os.path.join(script_dir, 'data/dst', 'normalized_macro_structural_features.tsv')
    with open(normalized_output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['debate_id', 'title', 'distance', 'interval', 'order', 'rally']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(normalized_results)
    
    print(f"\nOriginal results saved to: {original_output_path}")
    print(f"Normalized results saved to: {normalized_output_path}")
    
    # Display normalization statistics
    print(f"\nNormalization Statistics:")
    for feature_name in feature_names:
        normalized_values = [r[feature_name] for r in normalized_results]
        min_norm = min(normalized_values)
        max_norm = max(normalized_values)
        avg_norm = sum(normalized_values) / len(normalized_values)
        print(f"  {feature_name}: min={min_norm:.4f}, max={max_norm:.4f}, avg={avg_norm:.4f}")
    
    # Calculate and add score to normalized results
    for i, result in enumerate(normalized_results):
        score = calculate_score(
            result['distance'],  # normalized distance
            result['rally'],     # normalized rally
            result['interval'],  # normalized interval
            result['order']      # normalized order
        )
        result['score'] = score
    
    # Save normalized results with score to TSV
    scored_output_path = os.path.join(script_dir, 'data/dst', 'scored_macro_structural_features.tsv')
    with open(scored_output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['debate_id', 'title', 'distance', 'interval', 'order', 'rally', 'score']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(normalized_results)
    
    print(f"Scored results saved to: {scored_output_path}")
    
    # Display calculated scores for verification
    print(f"\nCalculated Scores:")
    for result in normalized_results:
        print(f"  ID {result['debate_id']+1}: {result['score']:.9f}")
    


if __name__ == "__main__":
    main()