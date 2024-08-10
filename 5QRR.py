import pandas as pd
import streamlit as st
import io
import random

def load_quiz_data(file):
    # UTF-8エンコードで読み込み
    with io.TextIOWrapper(file, encoding='utf-8', errors='replace') as f:
        df = pd.read_csv(f)
    
    quiz_data = []
    for _, row in df.iterrows():
        options = [row["option1"], row["option2"], row["option3"], row["option4"], row["option5"]]
        # オプションのシャッフル
        correct_option = row["answer"]
        shuffled_options = options[:]
        random.shuffle(shuffled_options)
        correct_index = shuffled_options.index(correct_option)
        
        quiz_data.append({
            "question": row["question"],
            "options": shuffled_options,
            "correct_index": correct_index
        })
    return quiz_data

def main():
    st.title("五択クイズアプリ")

    # セッション状態の初期化
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = []
    if "incorrect_data" not in st.session_state:
        st.session_state.incorrect_data = []
    if "current_quiz_data" not in st.session_state:
        st.session_state.current_quiz_data = []

    uploaded_file = st.file_uploader("クイズデータのCSVファイルをアップロードしてください", type="csv")
    if uploaded_file is not None:
        try:
            # 初回ロード時のみデータを設定
            if not st.session_state.quiz_data:
                st.session_state.quiz_data = load_quiz_data(uploaded_file)
                st.session_state.current_quiz_data = st.session_state.quiz_data.copy()

            answers = {}
            incorrect_data = []

            for i, quiz in enumerate(st.session_state.current_quiz_data):
                st.markdown(f"**問題 {i + 1}**")
                st.write(quiz["question"])

                options = quiz["options"]
                numbered_options = [f"（{idx + 1}）{opt}" for idx, opt in enumerate(options)]
                
                selected_option = st.radio("", options=numbered_options, index=None, key=f"question_{i}")

                if selected_option is not None:
                    selected_index = numbered_options.index(selected_option)
                    answers[quiz["question"]] = selected_index
                else:
                    answers[quiz["question"]] = None

            if st.button("回答を送信"):
                score = 0
                incorrect_data = []

                for i, quiz in enumerate(st.session_state.current_quiz_data):
                    correct_index = quiz["correct_index"]
                    selected_index = answers[quiz["question"]]
                    is_correct = correct_index == selected_index

                    if not is_correct:
                        incorrect_data.append(quiz)

                    if is_correct:
                        score += 1

                st.session_state.current_quiz_data = incorrect_data.copy()  # 不正解データを次の問題セットに設定

                total_questions = len(st.session_state.current_quiz_data) + score  # 現在の問題数に基づいて正答率を計算
                accuracy_rate = (score / total_questions) * 100

                st.write(f"あなたのスコア: {score} / {total_questions}")
                st.write(f"正答率: {accuracy_rate:.2f}%")

                if len(st.session_state.current_quiz_data) == 0:
                    st.success("すべての問題に正解しました！")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
