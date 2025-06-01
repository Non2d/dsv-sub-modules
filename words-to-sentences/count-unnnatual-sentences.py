import pandas as pd
import os
from pathlib import Path

def count_long_sentences(file_path, min_words=35):
    """
    指定されたファイル内の長い文（指定単語数以上）をカウントする関数
    
    Args:
        file_path (str): 処理するCSVファイルのパス
        min_words (int): 長い文と判定する最小単語数
        
    Returns:
        tuple: (ファイル名, 長い文の数, 全文数)
    """
    try:
        df = pd.read_csv(file_path)
        total_sentences = len(df)
        long_sentences = sum(df['text'].str.split().str.len() >= min_words)
        return os.path.basename(file_path), long_sentences, total_sentences
    except Exception as e:
        print(f"エラーが発生しました ({file_path}): {e}")
        return os.path.basename(file_path), 0, 0

def main():
    # dstディレクトリのパス
    dst_dir = Path("dst")
    
    # 結果を格納するリスト
    results = []
    total_long_sentences = 0
    total_sentences = 0
    
    # dstディレクトリ内のすべてのCSVファイルを処理
    for file_path in dst_dir.glob("sentences_*.csv"):
        file_name, long_count, total = count_long_sentences(file_path)
        results.append((file_name, long_count, total))
        total_long_sentences += long_count
        total_sentences += total
    
    # 結果をDataFrameに変換
    df_results = pd.DataFrame(results, columns=['ファイル名', '長い文の数', '全文数'])
    df_results['割合(%)'] = (df_results['長い文の数'] / df_results['全文数'] * 100).round(1)
    
    # 合計行を追加
    total_row = pd.DataFrame([{
        'ファイル名': '合計',
        '長い文の数': total_long_sentences,
        '全文数': total_sentences,
        '割合(%)': (total_long_sentences / total_sentences * 100) if total_sentences > 0 else 0
    }])
    df_results = pd.concat([df_results, total_row], ignore_index=True)
    
    # 結果をCSVファイルに出力
    output_path = dst_dir / 'long_sentences_stats.csv'
    df_results.to_csv(output_path, index=False, encoding='utf-8')
    print(f"\n結果を {output_path} に出力しました。")

if __name__ == "__main__":
    main()
