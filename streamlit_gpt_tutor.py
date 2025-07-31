import streamlit as st
import openai
import json
import os
import re
import pandas as pd

st.set_page_config(page_title="STT 200 Coffee Shop Tutor", page_icon="☕")

st.title("🧠 STT 200 Coffee Shop Tutor (Coffee Shop Scenario)")
st.markdown("You’ll talk to an AI tutor about probability and keep working until you get full credit.")

# Sidebar info
with st.sidebar:
    st.header("Student Info")
    student_name = st.text_input("Full Name")
    student_id = st.text_input("Student ID (required to resume)", max_chars=20)
    student_email = st.text_input("Email (optional)")

openai.api_key = st.secrets["OPENAI_API_KEY"]


if not student_id:
    st.warning("Please enter your Student ID")
    st.stop()


session_id = student_id.strip()
session_file = f"gpt_session_{session_id}.json"
scenario = "Coffee Shop"

# Initialize or load session
if os.path.exists(session_file):
    with open(session_file, "r") as f:
        session_data = json.load(f)
    context = session_data["context"]
    log = session_data["log"]
    scores = session_data["scores"]
    feedbacks = session_data["feedbacks"]
    responses = session_data["responses"]
    st.success("🔄 Resumed your session.")
else:
    context = [
        {"role": "system", "content": "You are a friendly but rigorous statistics tutor for a student learning about probability. Ask one question at a time, based on a coffee shop's seasonal drink data. Use the rubric to evaluate responses. Keep a conversational tone."}
    ]
    log = []
    scores = []
    feedbacks = []
    responses = []
    st.info("🆕 New session started.")

# Show Coffee Shop table
if not log:
    st.markdown("""
    ### Coffee Shop Drink Sales Data
    | Season | Hot Drinks | Cold Drinks | Total |
    |--------|------------|-------------|--------|
    | Winter | 100        | 20          | 120    |
    | Spring | 60         | 40          | 100    |
    | Summer | 40         | 120         | 160    |
    | Fall   | 100        | 40          | 140    |
    | **Total** | **300** | **220**     | **520** |
    """)

rubric_prompt = """You are grading a student's response during a tutoring conversation about probability.
Use the following rubric:
- Correctness: 0-2
- Justification: 0-2
- Interpretation: 0-2
- Effort/Engagement: 0-2
Give a short explanation and final score (out of 8).
Student response:
"""

def gpt_grade_response(context, answer):
    messages = context + [{"role": "user", "content": rubric_prompt + answer}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message.content

def get_score_from_feedback(feedback_text):
    match = re.search(r"(\b[0-8])\s*/\s*8", feedback_text)
    return int(match.group(1)) if match else 0

# Main interaction
total_score = sum(scores)
if total_score < 32:
    if "last_question" not in st.session_state:
        question_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=context + [{"role": "user", "content": "Ask the next relevant probability question based on the Coffee Shop dataset."}]
        )
        question_text = question_response.choices[0].message.content
        st.session_state.last_question = question_text
        context.append({"role": "assistant", "content": question_text})
    else:
        question_text = st.session_state.last_question

    st.markdown(f"### 🧹 Question:\n{question_text}")
    answer = st.text_area("✏️ Your Answer:", height=150)
    if st.button("Submit Answer"):
        responses.append(answer)
        context.append({"role": "user", "content": answer})

        feedback = gpt_grade_response(context, answer)
        score = get_score_from_feedback(feedback)

        scores.append(score)
        feedbacks.append(feedback)
        log.append({"question": question_text, "response": answer, "score": score, "feedback": feedback})
        st.markdown(f"### 🧪 Feedback:\n{feedback}")
        st.success(f"✅ You scored {score}/8 on this response.")

        del st.session_state["last_question"]

        with open(session_file, "w") as f:
            json.dump({
                "context": context,
                "log": log,
                "scores": scores,
                "feedbacks": feedbacks,
                "responses": responses
            }, f)
        st.rerun()
else:
    st.balloons()
    st.success("🎉 Full credit achieved! Your session is complete.")
    log_data = {
        "Name": student_name,
        "ID": student_id,
        "Email": student_email,
        "Scenario": scenario,
        "Total Score": total_score
    }
    for i, entry in enumerate(log):
        log_data[f"Q{i+1} Text"] = entry["question"]
        log_data[f"Q{i+1} Response"] = entry["response"]
        log_data[f"Q{i+1} Score"] = entry["score"]
        log_data[f"Q{i+1} Feedback"] = entry["feedback"]
    log_df = pd.DataFrame([log_data])
    st.dataframe(log_df)
    st.download_button("📅 Download CSV", data=log_df.to_csv(index=False), file_name=f"results_{student_id}.csv", mime="text/csv")
