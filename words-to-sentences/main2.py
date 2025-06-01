import os
import pandas as pd
import nltk, spacy


nltk.download('punkt')
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("警告: spacyの英語モデル 'en_core_web_sm' が見つかりません。")
    nlp = None

def assign_speakers_to_words(words, speaker_data):
    """
    話者分離データを単語データに紐づける関数。

    Args:
        words (pd.DataFrame): 'start', 'end', 'text' 列を含む単語データ。
        speaker_data (pd.DataFrame): 'start', 'end', 'speaker' 列を含む話者分離データ。

    Returns:
        pd.DataFrame: 話者情報が追加された単語データ。
    """
    # 話者列を初期化
    words['speaker'] = None

    # データを 'start' 列でソート
    words = words.sort_values(by='start').reset_index(drop=True)
    speaker_data = speaker_data.sort_values(by='start').reset_index(drop=True)

    # ポインタを初期化
    speaker_index = 0
    speaker_count = len(speaker_data)

    # 各単語に対して話者を割り当て
    for i, word_row in words.iterrows():
        while speaker_index < speaker_count and speaker_data.loc[speaker_index, 'end'] < word_row['start']:
            # 話者データが単語の範囲より前にある場合、次の話者データに進む
            speaker_index += 1

        if speaker_index < speaker_count and speaker_data.loc[speaker_index, 'start'] <= word_row['end']:
            # 話者データが単語の範囲に重なる場合、話者を割り当て
            words.at[i, 'speaker'] = speaker_data.loc[speaker_index, 'speaker']

    speaker_column = words.pop('speaker')
    words.insert(0, 'speaker', speaker_column)

    return words

def group_sentences_from_words(words):
    """
    単語データから文をグループ化する関数。

    Args:
        words (pd.DataFrame): 'speaker', 'start', 'end', 'text' 列を含む単語データ。

    Returns:
        pd.DataFrame: 'speaker', 'start', 'end', 'text' 列を含む文ごとにグループ化されたデータ。
    """
    from nltk.tokenize import PunktSentenceTokenizer

    tokenizer = PunktSentenceTokenizer()
    sentences = []
    current_sentence = ""
    current_word_data = []

    for _, row in words.iterrows():
        current_sentence += row['text']  # 文を結合
        current_word_data.append(row)

        # 文をトークナイズして区切る
        tokenized_sentences = tokenizer.tokenize(current_sentence.strip())
        if len(tokenized_sentences) > 1:  # 文が区切られた場合
            for sentence in tokenized_sentences[:-1]:  # 最後の文以外を処理
                # この文に対応する単語データを特定
                sentence_word_data = []
                remaining_word_data = []
                current_pos = 0

                for word_data in current_word_data:
                    # 単語の開始位置と終了位置を確認
                    word_start = word_data['start']
                    word_end = word_data['end']

                    # 文の範囲内にある単語のみを収集
                    if word_start >= sentence_word_data[0]['start'] and word_end <= sentence_word_data[-1]['end']:
                        sentence_word_data.append(word_data)
                    else:
                        remaining_word_data.append(word_data)

                if sentence_word_data:  # Ensure sentence_word_data is not empty
                    # 文の開始と終了時間を決定
                    print(f"Processing sentence: {sentence_word_data}")
                    start = min(word['start'] for word in sentence_word_data)
                    end = max(word['end'] for word in sentence_word_data)
                    text = sentence.strip()
                    speaker = sentence_word_data[0]['speaker'] if sentence_word_data else None
                    sentences.append({'speaker': speaker, 'start': start, 'end': end, 'text': text})

                current_word_data = remaining_word_data

            current_sentence = tokenized_sentences[-1]  # 最後の文を次に持ち越し

    # 最後の文を保存
    if current_sentence.strip() and current_word_data:  # Ensure current_word_data is not empty
        start = min(word['start'] for word in current_word_data)
        end = max(word['end'] for word in current_word_data)
        text = current_sentence.strip()
        speaker = current_word_data[0]['speaker'] if current_word_data else None
        sentences.append({'speaker': speaker, 'start': start, 'end': end, 'text': text})

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
            diarization = pd.read_csv(diarization_file_path)

            words = assign_speakers_to_words(words, diarization)
            words.to_csv(intermediate_words_with_speakers_file_path, index=False, encoding="utf-8-sig")
            print(f"intermediate_words_with_speakers を {intermediate_words_with_speakers_file_path} に保存しました。")

            sentences = group_sentences_from_words(words)
            sentences.to_csv(sentences_file_path, index=False, encoding="utf-8-sig")
            print(f"処理が完了しました。結果は {sentences_file_path} に保存されました。")

        except Exception as e:
            print(f"エラーが発生しました: {e}")