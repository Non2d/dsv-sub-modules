import json
import sys
import os
from typing import List

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Rebuttal, DebateData


def create_debate_data_from_json(json_file_path: str) -> List[DebateData]:
    """
    JSONファイルからDebateDataオブジェクトのリストを作成する関数
    
    Args:
        json_file_path: debate_scripts.jsonファイルのパス
    
    Returns:
        DebateDataオブジェクトのリスト
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        debate_scripts = json.load(f)
    
    debate_data_list: List[DebateData] = []
    
    for debate_script in debate_scripts:
        # スピーチの境界を計算（各スピーチの最後のADUのインデックス）
        speeches = []
        current_index = -1
        
        for speech in debate_script['speeches']:
            current_index += len(speech['ADUs'])
            speeches.append(current_index)
        
        # リバッタルデータを構築
        rebuttals = []
        for attack in debate_script['attacks']:
            rebuttals.append(
                Rebuttal(
                    src=attack['from'],
                    dst=attack['to']
                )
            )
        
        # POIデータを取得
        poi_adus = debate_script.get('POIs', [])
        
        # DebateDataオブジェクトを作成
        debate_data = DebateData(speeches, rebuttals, poi_adus)
        debate_data_list.append(debate_data)
    
    return debate_data_list

def create_single_debate_data_from_json(json_file_path: str, index: int = 0) -> DebateData:
    """
    JSONファイルから指定されたインデックスのDebateDataオブジェクトを作成する関数
    
    Args:
        json_file_path: debate_scripts.jsonファイルのパス
        index: 取得したいディベートのインデックス（デフォルト: 0）
    
    Returns:
        DebateDataオブジェクト
    """
    debate_data_list = create_debate_data_from_json(json_file_path)
    
    if index >= len(debate_data_list):
        raise IndexError(f"Index {index} is out of range. Available debates: {len(debate_data_list)}")
    
    return debate_data_list[index]

# 使用例
if __name__ == "__main__":
    import csv
    from calculator_correct import MacroStructuralCalculatorCorrect
    
    # 絶対パスを使用
    json_path = os.path.join(os.path.dirname(__file__), 'debate_scripts.json')
    
    # 元のJSONデータを読み込む
    with open(json_path, 'r', encoding='utf-8') as f:
        debate_scripts = json.load(f)
    
    print(f"Loaded {len(debate_scripts)} debate rounds")
    
    # 各ディベートの特徴量を計算
    results = []
    for i, round_data in enumerate(debate_scripts):
        calculator = MacroStructuralCalculatorCorrect(round_data)
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
    
    # 結果をTSVファイルに出力
    output_path = os.path.join(os.path.dirname(__file__), 'macro_structural_features.tsv')
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['debate_id', 'title', 'distance', 'interval', 'order', 'rally']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nResults saved to: {output_path}")