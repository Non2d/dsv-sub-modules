import pandas as pd
from collections import Counter
import os
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("警告: spacyの英語モデル 'en_core_web_sm' が見つかりません。")
    nlp = None

def assign_speakers_to_words(words, diarizations):
    """
    話者分離データを単語データに紐づける関数。
    Args:
        words (pd.DataFrame): 'start', 'end', 'text' 列を含む単語データ。
        diarizations (pd.DataFrame): 'start', 'end', 'speaker' 列を含む話者分離データ。
    Returns:
        pd.DataFrame: 話者情報が追加された単語データ。
    """
    # 話者列を1列目に初期化
    words.insert(0, 'speaker', None)
    
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
    
    return words

# def group_sentences_from_words(words: pd.DataFrame) -> pd.DataFrame:
#     """
#     単語単位のタイムスタンプ付き文字起こしデータを文単位に変換する関数。話者情報が欠けている場合、直前の話者を参照する。
#     1単語追加ごとに文分割を試み、文が区切られた場合はその時点で文を保存するという逐次的なアプローチを採用。
#     Args:
#         words (pd.DataFrame): 単語単位の 'start', 'end', 'text', 'speaker' 列を含むデータフレーム。
#     Returns:
#         pd.DataFrame: 文単位の 'start', 'end', 'text', 'speaker' 列を含むデータフレーム。
#     """
#     sentences = []
#     current_sentence = ""
#     start_time = None
#     end_time = None
#     speakers_in_sentence = []
#     last_valid_speaker = None  # 前回の有効な話者を記録

#     for index, row in words.iterrows():
#         if start_time is None:
#             start_time = row['start']

#         current_sentence += row['text']
#         end_time = row['end']
#         if row['speaker'] is not None:
#             speakers_in_sentence.append(row['speaker'])
#             last_valid_speaker = row['speaker']

#         # spaCy を使用して文を分割
#         doc = nlp(current_sentence.strip())
#         tmp_sentences = [sent.text for sent in doc.sents]

#         is_last_row = (index == words.index[-1])
#         if len(tmp_sentences) > 1 or is_last_row:  # 文が区切られた場合、または最後の行の場合
#             sentences_to_process = tmp_sentences if is_last_row else tmp_sentences[:-1]

#             for sentence in sentences_to_process:
#                 # 話者の頻度をカウントして最頻出話者を選択
#                 if speakers_in_sentence:
#                     most_common_speaker = Counter(speakers_in_sentence).most_common(1)[0][0]
#                 else:
#                     most_common_speaker = last_valid_speaker

#                 sentences.append({
#                     'speaker': most_common_speaker,
#                     'start': start_time,
#                     'end': end_time,
#                     'text': sentence,
#                 })

#                 if not is_last_row:
#                     start_time = None
#                     speakers_in_sentence = []

#             if not is_last_row:
#                 current_sentence = tmp_sentences[-1]

#     return pd.DataFrame(sentences)

def group_sentences_from_words(words: pd.DataFrame) -> pd.DataFrame:
    """
    単語単位のタイムスタンプ付き文字起こしデータを文単位に変換する関数。
    全単語を結合してから文分割し、各文に対応する単語範囲を特定してタイムスタンプと話者を決定する。
    
    Args:
        words (pd.DataFrame): 単語単位の 'start', 'end', 'text', 'speaker' 列を含むデータフレーム。
    Returns:
        pd.DataFrame: 文単位の 'start', 'end', 'text', 'speaker' 列を含むデータフレーム。
    """
    if words.empty:
        return pd.DataFrame(columns=['start', 'end', 'text', 'speaker'])
    
    # 話者情報の補完（欠けている場合は直前の話者を参照）
    words = words.copy()
    last_valid_speaker = None
    for i, row in words.iterrows():
        if pd.notna(row['speaker']) and row['speaker'] is not None:
            last_valid_speaker = row['speaker']
        elif last_valid_speaker is not None:
            words.at[i, 'speaker'] = last_valid_speaker
    
    # 全単語を結合
    full_text = ''.join(words['text'].astype(str))
    
    # spaCyで文分割
    doc = nlp(full_text)
    sentence_texts = [sent.text for sent in doc.sents]
    
    sentences = []
    word_idx = 0
    char_offset = 0
    
    for sentence_text in sentence_texts:
        sentence_start_time = None
        sentence_end_time = None
        speakers_in_sentence = []
        
        # この文に含まれる単語を特定
        sentence_char_end = char_offset + len(sentence_text)
        sentence_word_start_idx = word_idx
        
        # 文に含まれる単語を収集
        while word_idx < len(words):
            word = words.iloc[word_idx]
            word_text = str(word['text'])
            word_char_start = char_offset
            word_char_end = char_offset + len(word_text)
            
            # 単語が文の範囲内にある場合
            if word_char_start < sentence_char_end:
                if sentence_start_time is None:
                    sentence_start_time = word['start']
                sentence_end_time = word['end']
                
                if pd.notna(word['speaker']):
                    speakers_in_sentence.append(word['speaker'])
                
                char_offset = word_char_end
                word_idx += 1
                
                # 文の終端に達した場合
                if word_char_end >= sentence_char_end:
                    break
            else:
                break
        
        # 話者決定（最頻出話者を選択）
        if speakers_in_sentence:
            most_common_speaker = Counter(speakers_in_sentence).most_common(1)[0][0]
        else:
            most_common_speaker = None
        
        sentences.append({
            'speaker': most_common_speaker,
            'start': sentence_start_time,
            'end': sentence_end_time,
            'text': sentence_text,
        })
        
        # 次の文の開始位置を設定
        char_offset = sentence_char_end
    
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
            print(f"intermediate_words_with_speakers を {intermediate_words_with_speakers_file_path} に保存しました。")

            sentences = group_sentences_from_words(words)
            sentences.to_csv(sentences_file_path, index=False, encoding="utf-8-sig")
            print(f"処理が完了しました。結果は {sentences_file_path} に保存されました。")
            print(sentences.head())

        except Exception as e:
            print(f"エラーが発生しました: {e}")
