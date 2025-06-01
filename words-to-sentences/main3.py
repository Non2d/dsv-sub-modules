import pandas as pd
import nltk
from nltk.tokenize import PunktSentenceTokenizer
from collections import Counter
import os
import spacy
import re
import openai
from dotenv import load_dotenv

# 必要なデータをダウンロード（初回のみ）
nltk.download('punkt')

# spacyモデルの読み込み（英語）
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("警告: spacyの英語モデル 'en_core_web_sm' が見つかりません。")
    print("以下のコマンドでインストールしてください: python -m spacy download en_core_web_sm")
    nlp = None

def assign_speakers_to_words(words, speaker):
    """
    話者分離データを単語データに紐づける関数。

    Args:
        words (pd.DataFrame): 'start', 'end', 'text' 列を含む単語データ。
        speaker (pd.DataFrame): 'start', 'end', 'speaker' 列を含む話者分離データ。

    Returns:
        pd.DataFrame: 話者情報が追加された単語データ。
    """
    # 話者列を初期化
    words['speaker'] = None

    # データを 'start' 列でソート
    words = words.sort_values(by='start').reset_index(drop=True)
    speaker = speaker.sort_values(by='start').reset_index(drop=True)

    # ポインタを初期化
    speaker_index = 0
    speaker_count = len(speaker)

    # 各単語に対して話者を割り当て
    for i, word_row in words.iterrows():
        while speaker_index < speaker_count and speaker.loc[speaker_index, 'end'] < word_row['start']:
            # 話者データが単語の範囲より前にある場合、次の話者データに進む
            speaker_index += 1

        if speaker_index < speaker_count and speaker.loc[speaker_index, 'start'] <= word_row['end']:
            # 話者データが単語の範囲に重なる場合、話者を割り当て
            words.at[i, 'speaker'] = speaker.loc[speaker_index, 'speaker']

    # 'speaker' 列を1列目に移動
    speaker_column = words.pop('speaker')  # 'speaker' 列を取り出す
    words.insert(0, 'speaker', speaker_column)  # 'speaker' 列を1列目に挿入

    return words

def count_words(text):
    """
    英語テキスト内の単語数をカウントする関数。

    Args:
        text (str): 単語数をカウントするテキスト

    Returns:
        int: 単語数
    """
    return len(text.strip().split())

def split_long_sentence_with_spacy(text, max_words=30):
    """
    spacyを使用して文を分割する関数。
    
    Args:
        text (str): 分割するテキスト
        max_words (int): 最大単語数
        
    Returns:
        list: 分割された文のリスト
    """
    if nlp is None:
        return [text]  # spacyが利用できない場合はそのまま返す
    
    doc = nlp(text)
    sentences = []
    current_sentence = ""
    
    for sent in doc.sents:
        sentence_text = sent.text.strip()
        if count_words(current_sentence + sentence_text) <= max_words:
            current_sentence += sentence_text
        else:
            if current_sentence:
                sentences.append(current_sentence.strip())
            current_sentence = sentence_text
    
    if current_sentence:
        sentences.append(current_sentence.strip())
    
    return sentences if sentences else [text]

def find_word_boundaries(original_text, split_texts, word_data_list):
    """
    分割されたテキストが元の単語データのどの範囲に対応するかを特定する関数。
    
    Args:
        original_text (str): 元の文章
        split_texts (list): 分割された文章のリスト
        word_data_list (list): 元の文章を構成する単語データのリスト
        
    Returns:
        list: 各分割文に対応する単語データの範囲
    """
    result = []
    current_pos = 0
    word_index = 0
    
    for split_text in split_texts:
        # 分割文の開始位置を元のテキストから見つける
        start_pos = original_text.find(split_text.strip(), current_pos)
        if start_pos == -1:
            # 見つからない場合は近似で処理
            start_pos = current_pos
        
        end_pos = start_pos + len(split_text.strip())
        
        # この範囲に含まれる単語データを特定
        start_word_idx = word_index
        current_text_pos = 0
        
        # 単語データを順次確認して、分割文に含まれる範囲を特定
        for i, word_data in enumerate(word_data_list[word_index:], word_index):
            word_text = word_data['text']
            word_start_in_sentence = original_text.find(word_text, current_text_pos)
            
            if word_start_in_sentence >= start_pos and word_start_in_sentence < end_pos:
                current_text_pos = word_start_in_sentence + len(word_text)
                continue
            elif word_start_in_sentence >= end_pos:
                break
            else:
                current_text_pos = word_start_in_sentence + len(word_text)
                word_index += 1
        
        end_word_idx = word_index
        
        if start_word_idx < len(word_data_list) and end_word_idx <= len(word_data_list):
            word_range = word_data_list[start_word_idx:max(end_word_idx, start_word_idx + 1)]
            if word_range:
                result.append(word_range)
            word_index = end_word_idx
        
        current_pos = end_pos
    
    return result

def split_long_sentence_gpt_based(text, max_words=40):
    """
    Mocked GPT function: 全ての単語に '!' を付ける処理。

    Args:
        text (str): 分割するテキスト
        max_words (int): 最大単語数

    Returns:
        list: '!' を付けた文のリスト
    """
    try:
        print(f"Mocking GPT processing for text: {text[:50]}...")  # 最初の50文字を表示
        words = text.split()
        mocked_output = " ".join([word + "!" for word in words])
        return [mocked_output]
    except Exception as e:
        print(f"Error in mocked GPT function: {e}")
        return [text]
    
# def split_long_sentence_gpt_based(text, max_words=40):
#     """
#     GPTを使用して長い文を整形し、分割する関数。

#     Args:
#         text (str): 分割するテキスト
#         max_words (int): 最大単語数

#     Returns:
#         list: GPTによって整形・分割された文のリスト
#     """
#     try:
#         print(f"Using GPT to process text: {text[:50]}...")  # 最初の50文字を表示
#         load_dotenv()
#         api_key = os.getenv("OPENAI_API_KEY")
#         if api_key is None:
#             raise ValueError("環境変数 'OPENAI_API_KEY' が設定されていません。")
#         client = openai.OpenAI(api_key=api_key)

#         response = client.chat.completions.create(
#             model="gpt-4.1-nano-2025-04-14",
#             messages=[
#                 {"role": "user", "content": f"Please add appropriate punctuation (.,!?) to the following text without changing any of the original words. Do not use em dashes (—)."},
#                 {"role": "user", "content": f"The text is: {text}"}
#             ]
#         )
#         gpt_output = response.choices[0].message.content
#         sentences = [s.strip() for s in gpt_output.split("\n") if s.strip()]
#         return sentences
#     except Exception as e:
#         print(f"Error using GPT: {e}")
#         return [text]

def group_sentences_from_words(words: pd.DataFrame) -> pd.DataFrame:
    """
    単語単位のタイムスタンプを文単位に変換する関数。
    長い文は自動的に分割される。

    Args:
        words (pd.DataFrame): 'start', 'end', 'text', 'speaker' 列を含むデータフレーム。

    Returns:
        pd.DataFrame: 文単位の 'start', 'end', 'text', 'speaker' を含むデータフレーム。
    """
    # トークナイザーを初期化
    tokenizer = PunktSentenceTokenizer()

    merged_data = []
    current_sentence = ""
    current_word_data = []  # 現在の文を構成する単語データのリスト

    for index, row in words.iterrows():
        current_sentence += row['text']  # 文を結合
        current_word_data.append({
            'start': row['start'],
            'end': row['end'],
            'text': row['text'],
            'speaker': row['speaker']
        })

        # 文をトークナイズして区切る
        sentences = tokenizer.tokenize(current_sentence.strip())
        if len(sentences) > 1:  # 文が区切られた場合
            for sentence in sentences[:-1]:  # 最後の文以外を処理
                # この文に対応する単語データを特定
                sentence_word_data = []
                remaining_word_data = []
                current_pos = 0

                for word_data in current_word_data:
                    word_pos = current_sentence.find(word_data['text'], current_pos)
                    if word_pos != -1 and word_pos < len(sentence):
                        sentence_word_data.append(word_data)
                        current_pos = word_pos + len(word_data['text'])
                    else:
                        remaining_word_data.append(word_data)

                # 長い文の場合は分割
                if count_words(sentence) > 35:
                    spacy_sentences = split_long_sentence_with_spacy(sentence)
                    for spacy_sentence in spacy_sentences:
                        if count_words(spacy_sentence) > 35:
                            gpt_sentences = split_long_sentence_gpt_based(spacy_sentence)
                            for gpt_sentence in gpt_sentences:
                                merged_data.append(process_sentence(gpt_sentence, sentence_word_data))
                        else:
                            merged_data.append(process_sentence(spacy_sentence, sentence_word_data))
                else:
                    merged_data.append(process_sentence(sentence, sentence_word_data))

                current_word_data = remaining_word_data

            current_sentence = sentences[-1]  # 最後の文を次に持ち越し

    # 最後の文を保存
    if current_sentence.strip():
        merged_data.append(process_sentence(current_sentence.strip(), current_word_data))

    return pd.DataFrame(merged_data)

def process_sentence(sentence, word_data_list):
    """
    文を処理し、speaker, start, end を決定する補助関数。

    Args:
        sentence (str): 処理対象の文
        word_data_list (list): 文を構成する単語データのリスト

    Returns:
        dict: 文単位のデータ（speaker, start, end, text）
    """
    # 話者を決定（最頻出話者）
    speakers = [w['speaker'] for w in word_data_list if w['speaker'] is not None]
    if speakers:
        most_common_speaker = Counter(speakers).most_common(1)
        speaker = most_common_speaker[0][0] if most_common_speaker else None
    else:
        speaker = None

    # 文の開始と終了時間を決定
    start = word_data_list[0]['start'] if word_data_list else None
    end = word_data_list[-1]['end'] if word_data_list else None

    return {
        'speaker': speaker,
        'start': start,
        'end': end,
        'text': sentence.strip()
    }

if __name__ == "__main__":
    # src/diarizationとsrc/speech-recognitionの両方に同名ファイルがある前提
    diarization_dir = "src/diarization"
    speech_recognition_dir = "src/speech-recognition"
    dst_dir = "dst"

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
            speaker = pd.read_csv(diarization_file_path)

            words = assign_speakers_to_words(words, speaker)
            words.to_csv(intermediate_words_with_speakers_file_path, index=False, encoding="utf-8-sig")
            print(f"intermediate_words_with_speakers を {intermediate_words_with_speakers_file_path} に保存しました。")

            sentences = group_sentences_from_words(words)
            sentences.to_csv(sentences_file_path, index=False, encoding="utf-8-sig")
            print(f"処理が完了しました。結果は {sentences_file_path} に保存されました。")
            
            # 分割結果の統計を表示
            word_counts = sentences['text'].apply(count_words)
            print(f"文の単語数統計: 最小={word_counts.min()}, 最大={word_counts.max()}, 平均={word_counts.mean():.1f}")
            print(f"30ワード以上の文の数: {(word_counts > 30).sum()}")
            print(sentences.head())

        except Exception as e:
            print(f"エラーが発生しました: {e}")
