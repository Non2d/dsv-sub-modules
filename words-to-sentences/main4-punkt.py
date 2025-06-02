import pandas as pd
import nltk
from nltk.tokenize import PunktSentenceTokenizer
from collections import Counter
import os

# 必要なデータをダウンロード（初回のみ）
nltk.download('punkt')

def assign_speakers_to_words(words, diarizations):
    """
    話者分離データを単語データに紐づける関数。

    Args:
        words (pd.DataFrame): 'start', 'end', 'text' 列を含む単語データ。
        diarizations (pd.DataFrame): 'start', 'end', 'speaker' 列を含む話者分離データ。

    Returns:
        pd.DataFrame: 話者情報が追加された単語データ。
    """
    # 話者列を初期化
    words['speaker'] = None

    # データを 'start' 列でソート
    words = words.sort_values(by='start').reset_index(drop=True)
    diarizations = diarizations.sort_values(by='start').reset_index(drop=True)

    # ポインタを初期化
    speaker_index = 0
    speaker_count = len(diarizations)

    # 各単語に対して話者を割り当て
    for i, word_row in words.iterrows():
        while speaker_index < speaker_count and diarizations.loc[speaker_index, 'end'] < word_row['start']:
            # 話者データが単語の範囲より前にある場合、次の話者データに進む
            speaker_index += 1

        if speaker_index < speaker_count and diarizations.loc[speaker_index, 'start'] <= word_row['end']:
            # 話者データが単語の範囲に重なる場合、話者を割り当て
            words.at[i, 'speaker'] = diarizations.loc[speaker_index, 'speaker']

    # 'speaker' 列を1列目に移動
    speaker_column = words.pop('speaker')  # 'speaker' 列を取り出す
    words.insert(0, 'speaker', speaker_column)  # 'speaker' 列を1列目に挿入

    return words

def group_sentences_from_words(words: pd.DataFrame) -> pd.DataFrame:
    """
    単語単位のタイムスタンプを文単位に変換する関数。

    Args:
        data (pd.DataFrame): 'start', 'end', 'text', 'speaker' 列を含むデータフレーム。

    Returns:
        pd.DataFrame: 文単位の 'start', 'end', 'text', 'speaker' を含むデータフレーム。
    """
    # トークナイザーを初期化
    tokenizer = PunktSentenceTokenizer()

    sentences = []
    current_sentence = ""
    start_time = None
    end_time = None
    speakers_in_sentence = []

    last_valid_speaker = None  # 前回の有効な話者を記録

    for index, row in words.iterrows():
        if start_time is None:
            start_time = row['start']  # 文の開始時間を設定

        current_sentence += row['text']  # 文を結合
        end_time = row['end']  # 文の終了時間を更新
        if row['speaker'] is not None:  # 話者が None でない場合のみ追加
            speakers_in_sentence.append(row['speaker'])
            last_valid_speaker = row['speaker']

        # 文をトークナイズして区切る
        tmp_sentences = tokenizer.tokenize(current_sentence.strip())
        if len(tmp_sentences) > 1:  # 文が区切られた場合
            for sentence in tmp_sentences[:-1]:  # 最後の文以外を保存
                # 話者の頻度をカウントして最頻出話者を選択
                if speakers_in_sentence:  # 話者リストが空でない場合のみ処理
                    most_common_speaker = Counter(speakers_in_sentence).most_common(1)[0][0]
                else:
                    most_common_speaker = last_valid_speaker  # 話者がいない場合は前回の話者を設定

                sentences.append({
                    'speaker': most_common_speaker,
                    'start': start_time,
                    'end': end_time,
                    'text': sentence,
                })
                # 文をリセット
                start_time = None
                speakers_in_sentence = []
            current_sentence = tmp_sentences[-1]  # 最後の文を次に持ち越し

    # 最後の文を保存
    if current_sentence:
        if speakers_in_sentence:  # 話者リストが空でない場合のみ処理
            most_common_speaker = Counter(speakers_in_sentence).most_common(1)[0][0]
        else:
            most_common_speaker = last_valid_speaker # 話者がいない場合は前回の話者を設定

        sentences.append({
            'speaker': most_common_speaker,
            'start': start_time,
            'end': end_time,
            'text': current_sentence.strip(),
        })

    return pd.DataFrame(sentences)

if __name__ == "__main__":
    # src/diarizationとsrc/speech-recognitionの両方に同名ファイルがある前提
    diarization_dir = "src/diarization"
    speech_recognition_dir = "src/speech-recognition"
    dst_dir = "dst"

    # speech-recognition側のcsvファイル名一覧を取得（拡張子除く）
    file_names = [
        os.path.splitext(f)[0]
        for f in os.listdir(speech_recognition_dir)
        if f.endswith(".csv")
    ]

    for file_name in file_names:
        speech_recognition_file_path = os.path.join(speech_recognition_dir, f"{file_name}.csv")
        diarization_file_path = os.path.join(diarization_dir, f"{file_name}.csv")
        intermediate_words_with_speakers_file_path = os.path.join(dst_dir, f"intermediate_words_with_speakers_{file_name}.csv")
        sentences_file_path = os.path.join(dst_dir, f"sentences_{file_name}.csv")

        try:
            words = pd.read_csv(speech_recognition_file_path)
            diarizations = pd.read_csv(diarization_file_path)

            words = assign_speakers_to_words(words, diarizations)
            words.to_csv(intermediate_words_with_speakers_file_path, index=False, encoding="utf-8-sig")
            print(f"words_with_speakers を {intermediate_words_with_speakers_file_path} に保存しました。")

            sentences = group_sentences_from_words(words)
            sentences.to_csv(sentences_file_path, index=False, encoding="utf-8-sig")
            print(f"処理が完了しました。結果は {sentences_file_path} に保存されました。")
            print(sentences.head())

        except Exception as e:
            print(f"エラーが発生しました: {e}")
