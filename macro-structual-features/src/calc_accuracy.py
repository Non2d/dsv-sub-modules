"""
Calculate correlation between calculated scores and ground truth evaluation
"""

import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
import os


def load_data(script_dir):
    """Load score data and ground truth evaluation data"""
    # Load scored macro-structural features
    scored_path = os.path.join(script_dir, 'data/dst', 'scored_macro_structural_features.tsv')
    scored_df = pd.read_csv(scored_path, sep='\t')
    
    # Load ground truth evaluation
    eval_path = os.path.join(script_dir, 'data/src', 'evaluation_answer.csv')
    eval_df = pd.read_csv(eval_path)
    
    return scored_df, eval_df


def merge_data(scored_df, eval_df):
    """Merge score data with ground truth evaluation data"""
    # The debate_id in scored_df is 0-indexed, while id in eval_df is 1-indexed
    scored_df['id'] = scored_df['debate_id'] + 1
    
    # Merge on id
    merged_df = pd.merge(scored_df, eval_df[['id', 'evaluation']], on='id', how='inner')
    
    return merged_df


def calculate_correlations(merged_df):
    """Calculate Pearson and Spearman correlations between score and evaluation"""
    # Sort by ID to ensure consistent order
    merged_df = merged_df.sort_values('id').reset_index(drop=True)
    
    scores = merged_df['score'].values
    evaluations = merged_df['evaluation'].values
    
    # Debug print
    print("Raw data for correlation:")
    for i in range(len(scores)):
        print(f"ID {merged_df.iloc[i]['id']}: score={scores[i]:.10f}, eval={evaluations[i]:.6f}")
    
    # Remove any NaN values
    mask = ~(np.isnan(scores) | np.isnan(evaluations))
    scores_clean = scores[mask]
    evaluations_clean = evaluations[mask]
    
    if len(scores_clean) < 2:
        return None, None, None, None
    
    # Manual Pearson calculation for verification
    n = len(scores_clean)
    mean_x = np.mean(scores_clean)
    mean_y = np.mean(evaluations_clean)
    
    numerator = np.sum((scores_clean - mean_x) * (evaluations_clean - mean_y))
    denominator = np.sqrt(np.sum((scores_clean - mean_x)**2) * np.sum((evaluations_clean - mean_y)**2))
    
    manual_pearson = numerator / denominator if denominator != 0 else 0
    
    print(f"\nManual Pearson calculation:")
    print(f"n = {n}")
    print(f"mean_score = {mean_x:.10f}")
    print(f"mean_eval = {mean_y:.10f}")
    print(f"numerator = {numerator:.10f}")
    print(f"denominator = {denominator:.10f}")
    print(f"manual_pearson = {manual_pearson:.10f}")
    
    # Calculate correlations using scipy
    pearson_corr, pearson_p = pearsonr(scores_clean, evaluations_clean)
    spearman_corr, spearman_p = spearmanr(scores_clean, evaluations_clean)
    
    print(f"scipy_pearson = {pearson_corr:.10f}")
    
    return pearson_corr, pearson_p, spearman_corr, spearman_p


def print_results(merged_df, pearson_corr, pearson_p, spearman_corr, spearman_p):
    """Print correlation results and data summary"""
    print(f"\n=== Score vs Evaluation Correlation Analysis ===")
    print(f"Total samples: {len(merged_df)}")
    print(f"Score range: {merged_df['score'].min():.6f} - {merged_df['score'].max():.6f}")
    print(f"Evaluation range: {merged_df['evaluation'].min():.6f} - {merged_df['evaluation'].max():.6f}")
    print()
    
    # Debug: Print all data for verification
    print("All data for correlation verification:")
    print("ID | Score         | Evaluation")
    print("-" * 35)
    for _, row in merged_df.iterrows():
        print(f"{row['id']:2d} | {row['score']:12.10f} | {row['evaluation']:10.6f}")
    print()
    
    if pearson_corr is not None:
        print(f"Pearson Correlation: {pearson_corr:.10f} (p-value: {pearson_p:.6f})")
        print(f"Spearman Correlation: {spearman_corr:.6f} (p-value: {spearman_p:.6f})")
        
        # Interpret correlation strength
        abs_pearson = abs(pearson_corr)
        if abs_pearson >= 0.7:
            strength = "strong"
        elif abs_pearson >= 0.3:
            strength = "moderate"
        else:
            strength = "weak"
        
        direction = "positive" if pearson_corr > 0 else "negative"
        print(f"\nInterpretation: {strength} {direction} correlation")
        
        # Statistical significance
        if pearson_p < 0.01:
            print("Correlation is statistically significant (p < 0.01)")
        elif pearson_p < 0.05:
            print("Correlation is statistically significant (p < 0.05)")
        else:
            print("Correlation is not statistically significant (p >= 0.05)")
    else:
        print("Could not calculate correlations (insufficient data)")


def calc_accuracy(script_dir):
    """Main function to calculate accuracy/correlation"""
    try:
        # Load data
        scored_df, eval_df = load_data(script_dir)
        
        # Merge data
        merged_df = merge_data(scored_df, eval_df)
        
        # Calculate correlations
        pearson_corr, pearson_p, spearman_corr, spearman_p = calculate_correlations(merged_df)
        
        # Print results
        print_results(merged_df, pearson_corr, pearson_p, spearman_corr, spearman_p)
        
        return pearson_corr, spearman_corr
        
    except Exception as e:
        print(f"Error in accuracy calculation: {e}")
        return None, None