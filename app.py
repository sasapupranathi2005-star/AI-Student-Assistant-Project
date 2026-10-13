
import json
import streamlit as st
from llm import get_answer


# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="AI Student Assistant",
    page_icon="🎓",
    layout="wide"
)


# ---------------- HOME DASHBOARD ----------------
st.title("🎓 AI Student Assistant")

st.markdown("""
### Welcome to Your AI Learning Space! 📚

Generate study notes and practice quizzes with AI.

Choose a feature below to get started.
""")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📚 Study Notes")
    st.write(
        "Generate detailed notes, short notes, "
        "exam preparation notes, and interview notes."
    )

with col2:
    st.subheader("📝 Quiz Generator")
    st.write(
        "Create multiple-choice quizzes, test your knowledge, "
        "and view your score with explanations."
    )

st.divider()


# ---------------- TABS ----------------
notes_tab, quiz_tab = st.tabs([
    "📚 Study Notes",
    "📝 Quiz Generator"
])


# ---------------- STUDY NOTES FEATURE ----------------
with notes_tab:
    st.subheader("📚 Generate Study Notes")

    topic = st.text_input(
        "Enter subject or topic",
        placeholder="Example: Java OOP Concepts",
        key="notes_topic"
    )

    level = st.selectbox(
        "Choose study level",
        ["Beginner", "Intermediate", "Advanced"],
        key="notes_level"
    )

    notes_format = st.selectbox(
        "Choose notes format",
        [
            "Detailed Notes",
            "Short Notes",
            "Exam Preparation Notes",
            "Interview Preparation Notes"
        ],
        key="notes_format"
    )

    if st.button("Generate Notes", type="primary"):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            prompt = f"""
Create study notes about {topic}.
Student level: {level}.
Format: {notes_format}.

Use simple English and clear headings.
Include:
1. Definition
2. Important concepts
3. Simple examples
4. Revision points
5. Practice questions

Keep the information educational and accurate.
"""

            with st.spinner("Generating study notes..."):
                try:
                    answer = get_answer(prompt)

                    if answer:
                        st.markdown(answer)

                        st.download_button(
                            "📥 Download Notes",
                            data=answer,
                            file_name="study_notes.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("No notes were generated.")

                except Exception as error:
                    st.error("Could not generate notes.")
                    st.caption(str(error))


# ---------------- QUIZ GENERATOR FEATURE ----------------
with quiz_tab:
    st.subheader("📝 Interactive Quiz")

    quiz_topic = st.text_input(
        "Enter quiz topic",
        placeholder="Example: Java OOP Concepts",
        key="quiz_topic"
    )

    question_count = st.selectbox(
        "Number of questions",
        [5, 10, 15, 20],
        key="question_count"
    )

    difficulty = st.selectbox(
        "Choose difficulty",
        ["Easy", "Medium", "Hard"],
        key="quiz_difficulty"
    )

    if st.button("Generate Quiz", type="primary"):
        if not quiz_topic.strip():
            st.warning("Please enter a topic.")
        else:
            prompt = f"""
Create exactly {question_count} multiple-choice
questions about {quiz_topic}.
Difficulty: {difficulty}.

Return ONLY valid JSON in this structure:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": 0,
      "explanation": "Explanation"
    }}
  ]
}}

The answer must be a zero-based integer:
0 for the first option,
1 for the second,
2 for the third,
3 for the fourth.

No markdown fences. No extra text.
"""

            with st.spinner("Generating quiz..."):
                try:
                    response = get_answer(prompt)

                    # Handle JSON enclosed in markdown fences
                    response = response.strip()

                    if response.startswith("```"):
                        response = response.split("\n", 1)[1]
                        if response.endswith("```"):
                            response = response[:-3].strip()

                    data = json.loads(response)
                    questions = data["questions"]

                    # Validate the generated quiz
                    valid_quiz = (
                        len(questions) == question_count
                        and all(
                            isinstance(q.get("question"), str)
                            and isinstance(q.get("options"), list)
                            and len(q["options"]) == 4
                            and isinstance(q.get("answer"), int)
                            and not isinstance(q.get("answer"), bool)
                            and q["answer"] in [0, 1, 2, 3]
                            and isinstance(q.get("explanation"), str)
                            for q in questions
                        )
                    )

                    if not valid_quiz:
                        raise ValueError(
                            "Quiz format is invalid. Please generate again."
                        )

                    st.session_state["active_quiz"] = questions
                    st.session_state["quiz_topic_name"] = quiz_topic
                    st.session_state["quiz_submitted"] = False
                    st.session_state["quiz_answers"] = {}

                    # Clear previous radio selections for the new quiz
                    for i in range(20):
                        st.session_state.pop(f"answer_{i}", None)

                except Exception as error:
                    st.error(
                        "Quiz generate avvaledu. Please try again."
                    )
                    st.caption(str(error))

    # Display generated quiz
    questions = st.session_state.get("active_quiz")

    if questions:
        st.divider()

        st.subheader(
            f"Quiz: {st.session_state['quiz_topic_name']}"
        )

        with st.form("interactive_quiz_form"):
            selected_answers = {}

            for i, question in enumerate(questions):
                st.markdown(
                    f"**{i + 1}. {question['question']}**"
                )

                selected_answers[i] = st.radio(
                    "Select your answer",
                    options=range(4),
                    format_func=lambda n, q=question: q["options"][n],
                    key=f"answer_{i}",
                    index=None
                )

            submitted = st.form_submit_button("Submit Quiz")

        if submitted:
            st.session_state["quiz_answers"] = selected_answers
            st.session_state["quiz_submitted"] = True

        # Display score and answer explanations
        if st.session_state.get("quiz_submitted"):
            answers = st.session_state["quiz_answers"]

            score = sum(
                1
                for i, question in enumerate(questions)
                if answers.get(i) == question["answer"]
            )

            percentage = score / len(questions) * 100

            st.divider()
            st.subheader("📊 Your Result")

            st.metric(
                "Score",
                f"{score} / {len(questions)}",
                f"{percentage:.0f}%"
            )

            for i, question in enumerate(questions):
                chosen = answers.get(i)
                correct = question["answer"]

                if chosen == correct:
                    st.success(f"Question {i + 1}: Correct!")
                else:
                    st.error(f"Question {i + 1}: Incorrect")

                if chosen is None:
                    st.write("Your answer: Not answered")
                else:
                    st.write(
                        f"Your answer: {question['options'][chosen]}"
                    )

                st.write(
                    f"Correct answer: {question['options'][correct]}"
                )
                st.write(
                    f"Explanation: {question['explanation']}"
                )
