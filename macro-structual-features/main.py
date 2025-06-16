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
from calc_accuracy import calc_accuracy

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
    
    # Get version info from the first calculator
    calculator_sample = MacroStructuralCalculator(debate_scripts[0])
    versions = calculator_sample.get_versions()
    
    # Create versioned column names
    versioned_columns = {}
    for feature in feature_names:
        versioned_columns[feature] = f"{feature}_v{versions[feature]}"
    
    for i, round_data in enumerate(debate_scripts):
        calculator = MacroStructuralCalculator(round_data)
        features = calculator.calculate_all()
        
        result = {
            'debate_id': i,
            'title': round_data['source']['title'],
            versioned_columns['distance']: features['distance'],
            versioned_columns['interval']: features['interval'],
            versioned_columns['order']: features['order'],
            versioned_columns['rally']: features['rally'],
        }
        results.append(result)
        print(f"Debate {i}: {features}")
    
    # Find maximum values for normalization
    max_values = {}
    for feature_name in feature_names:
        valid_values = []
        versioned_col = versioned_columns[feature_name]
        for result in results:
            value = result[versioned_col]
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
            versioned_col = versioned_columns[feature_name]
            original_value = result[versioned_col]
            if original_value is not None and original_value != -1 and max_values[feature_name] > 0:
                normalized_value = original_value / max_values[feature_name]
            else:
                normalized_value = 0.0
            
            normalized_result[versioned_col] = normalized_value
        
        normalized_results.append(normalized_result)
    
    # Create version suffix for file names
    version_suffix = f"_distance=v{versions['distance']}-interval=v{versions['interval']}-rally=v{versions['rally']}-order=v{versions['order']}"
    
    # Save original results to TSV
    # original_output_path = os.path.join(script_dir, 'data/dst', f'macro_structural_features{version_suffix}.tsv')
    # with open(original_output_path, 'w', newline='', encoding='utf-8') as f:
    #     fieldnames = ['debate_id', 'title'] + [versioned_columns[f] for f in feature_names]
    #     writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
    #     writer.writeheader()
    #     writer.writerows(results)
    
    # Save normalized results to TSV
    # normalized_output_path = os.path.join(script_dir, 'data/dst', f'normalized_macro_structural_features{version_suffix}.tsv')
    # with open(normalized_output_path, 'w', newline='', encoding='utf-8') as f:
    #     fieldnames = ['debate_id', 'title'] + [versioned_columns[f] for f in feature_names]
    #     writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
    #     writer.writeheader()
    #     writer.writerows(normalized_results)
    
    # print(f"\nOriginal results saved to: {original_output_path}")
    # print(f"Normalized results saved to: {normalized_output_path}")
    
    # Display normalization statistics
    print(f"\nNormalization Statistics:")
    for feature_name in feature_names:
        versioned_col = versioned_columns[feature_name]
        normalized_values = [r[versioned_col] for r in normalized_results]
        min_norm = min(normalized_values)
        max_norm = max(normalized_values)
        avg_norm = sum(normalized_values) / len(normalized_values)
        print(f"  {versioned_col}: min={min_norm:.4f}, max={max_norm:.4f}, avg={avg_norm:.4f}")
    
    # Calculate and add score to normalized results
    for i, result in enumerate(normalized_results):
        score = calculate_score(
            result[versioned_columns['distance']],  # normalized distance
            result[versioned_columns['rally']],     # normalized rally
            result[versioned_columns['interval']],  # normalized interval
            result[versioned_columns['order']]      # normalized order
        )
        result['score'] = score
    
    # Save normalized results with score to TSV
    scored_output_path = os.path.join(script_dir, 'data/dst', f'macro_structural_features_with_socre_{version_suffix}.tsv')
    with open(scored_output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['debate_id', 'title'] + [versioned_columns[f] for f in feature_names] + ['score']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(normalized_results)
    
    print(f"Scored results saved to: {scored_output_path}")
    
    # Transform features: 1-distance, 1-interval
    transformed_results = []
    for result in normalized_results:
        transformed_result = result.copy()
        # Apply transformations with updated column names
        old_distance_col = versioned_columns['distance']
        old_interval_col = versioned_columns['interval']
        
        # Create new column names
        new_distance_col = f"1-{old_distance_col}"
        new_interval_col = f"1-{old_interval_col}"
        
        # Remove old columns and add transformed ones
        del transformed_result[old_distance_col]
        del transformed_result[old_interval_col]
        transformed_result[new_distance_col] = 1 - result[old_distance_col]
        transformed_result[new_interval_col] = 1 - result[old_interval_col]
        
        # Recalculate score with transformed values
        transformed_score = calculate_score(
            transformed_result[new_distance_col],  # 1-distance
            transformed_result[versioned_columns['rally']],     # rally (unchanged)
            transformed_result[new_interval_col],  # 1-interval
            transformed_result[versioned_columns['order']]      # order (unchanged)
        )
        transformed_result['score'] = transformed_score
        transformed_results.append(transformed_result)
    
    # Save transformed results to TSV
    transformed_output_path = os.path.join(script_dir, 'data/dst', f'macro_structural_features_transformed_{version_suffix}.tsv')
    with open(transformed_output_path, 'w', newline='', encoding='utf-8') as f:
        # Update fieldnames for transformed columns
        transformed_fieldnames = ['debate_id', 'title']
        for feature in feature_names:
            if feature in ['distance', 'interval']:
                transformed_fieldnames.append(f"1-{versioned_columns[feature]}")
            else:
                transformed_fieldnames.append(versioned_columns[feature])
        transformed_fieldnames.append('score')
        
        writer = csv.DictWriter(f, fieldnames=transformed_fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(transformed_results)
    
    print(f"Transformed results saved to: {transformed_output_path}")
    
    # Display calculated scores for verification
    print(f"\nCalculated Scores:")
    for result in normalized_results:
        print(f"  ID {result['debate_id']+1}: {result['score']:.9f}")
    
    print(f"\nTransformed Scores:")
    for result in transformed_results:
        print(f"  ID {result['debate_id']+1}: {result['score']:.9f}")
    
    # Calculate accuracy/correlation with ground truth
    calc_accuracy(script_dir)


if __name__ == "__main__":
    main()