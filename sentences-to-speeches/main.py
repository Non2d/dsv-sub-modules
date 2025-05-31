import pandas as pd
import numpy as np
from typing import List, Tuple
from sklearn.cluster import KMeans
from scipy.signal import find_peaks

def detect_speech_segments(df: pd.DataFrame) -> List[Tuple[float, float]]:
    """
    発話データからスピーチセグメントを自動検出する
    
    Args:
        df: 入力データフレーム
    
    Returns:
        スピーチセグメントのリスト（開始時間、終了時間）
    """
    # 発話間の無音時間を計算
    df = df.sort_values('start')
    silence_durations = df['start'].values[1:] - df['end'].values[:-1]
    
    # 無音時間の分布から閾値を自動的に設定
    # 長い無音時間をピークとして検出
    peaks, _ = find_peaks(silence_durations, distance=10, height=np.percentile(silence_durations, 75))
    
    # スピーチセグメントの境界を特定
    boundaries = []
    current_start = df['start'].iloc[0]
    
    for i in range(len(df) - 1):
        if i in peaks:
            # 十分な無音時間がある場合、新しいセグメントの開始
            if silence_durations[i] > np.percentile(silence_durations, 90):
                boundaries.append((current_start, df['end'].iloc[i]))
                current_start = df['start'].iloc[i + 1]
    
    # 最後のセグメントを追加
    boundaries.append((current_start, df['end'].iloc[-1]))
    
    # セグメントの長さでクラスタリングして、メインスピーチと短い発話を分離
    segment_durations = [end - start for start, end in boundaries]
    if len(segment_durations) > 8:  # 8つ以上のセグメントがある場合
        kmeans = KMeans(n_clusters=2, random_state=42)
        clusters = kmeans.fit_predict(np.array(segment_durations).reshape(-1, 1))
        
        # 長いセグメント（メインスピーチ）のみを選択
        main_speech_indices = np.where(clusters == np.argmax(kmeans.cluster_centers_))[0]
        boundaries = [boundaries[i] for i in main_speech_indices]
    
    return sorted(boundaries, key=lambda x: x[0])

def classify_speeches(df: pd.DataFrame) -> pd.DataFrame:
    """
    スピーチを分類し、割り込み質問を特定する
    
    Args:
        df: 入力データフレーム（speaker, start, end, text列を含む）
    
    Returns:
        分類結果を含むデータフレーム
    """
    # 結果を格納する新しい列を追加
    df['speech_id'] = ''  # スピーチID（PM/LO/DPM/...）
    df['is_interruption'] = False  # 割り込み質問フラグ
    
    # スピーチセグメントを自動検出
    speech_boundaries = detect_speech_segments(df)
    
    # ディベートのスピーチ順序を定義
    speech_order = ['PM', 'LO', 'DPM', 'DLO', 'MG', 'MO', 'PMR', 'LOR']
    
    # 各スピーチのメインスピーカーを特定
    main_speakers = []
    for start, end in speech_boundaries:
        speech_df = df[(df['start'] >= start) & (df['start'] < end)]
        if not speech_df.empty:
            # 最も長く話している話者をメインスピーカーとする
            speaker_durations = speech_df.groupby('speaker')['end'].max() - speech_df.groupby('speaker')['start'].min()
            main_speaker = speaker_durations.idxmax()
            main_speakers.append(main_speaker)
    
    # 各発話を分類
    for i, (start, end) in enumerate(speech_boundaries):
        if i >= len(speech_order):
            break
            
        # 該当する時間帯の発話を取得
        mask = (df['start'] >= start) & (df['start'] < end)
        df.loc[mask, 'speech_id'] = speech_order[i]
        
        # 割り込み質問の判定
        if i < len(main_speakers):  # メインスピーカーが特定されている場合
            main_speaker = main_speakers[i]
            interruption_mask = mask & (df['speaker'] != main_speaker)
            
            # 連続した割り込み発話をグループ化
            interruption_groups = []
            current_group = []
            
            for idx in df[interruption_mask].index:
                if not current_group or idx == current_group[-1] + 1:
                    current_group.append(idx)
                else:
                    if current_group:
                        interruption_groups.append(current_group)
                    current_group = [idx]
            if current_group:
                interruption_groups.append(current_group)
            
            # 各グループが割り込み質問の条件を満たすか確認
            for group in interruption_groups:
                group_df = df.loc[group]
                duration = group_df['end'].max() - group_df['start'].min()
                if duration <= 30 and len(group) <= 3:  # 30秒以内で3文以下
                    df.loc[group, 'is_interruption'] = True
    
    return df

def main():
    # CSVファイルを読み込む
    input_file = "src/sentences_WSDC ｜ Western ｜ R2 - Wales v USA.csv"
    df = pd.read_csv(input_file)
    
    # 分類を実行
    result_df = classify_speeches(df)
    
    # 列の順序を変更
    columns = ['speech_id', 'is_interruption'] + [col for col in result_df.columns if col not in ['speech_id', 'is_interruption']]
    result_df = result_df[columns]
    
    # 出力ファイル名を生成（入力ファイル名 + _classified）
    input_filename = input_file.split('/')[-1]  # パスからファイル名を取得
    output_filename = input_filename.rsplit('.', 1)[0] + '_classified.csv'  # 拡張子の前で分割して_classifiedを追加
    output_file = f"dst/{output_filename}"
    
    # 結果を保存
    result_df.to_csv(output_file, index=False)
    print(f"分類結果を {output_file} に保存しました。")

if __name__ == "__main__":
    main()
