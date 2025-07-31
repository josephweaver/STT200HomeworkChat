import streamlit as st
import openai
import json
import os
import re
import pandas as pd




st.set_page_config(page_title="STT 200 Coffee Shop Tutor", page_icon="☕")
st.title("🧠 STT 200 Coffee Shop Tutor (Coffee Shop Scenario)")
st.markdown("You’ll talk to an AI tutor about probability. When you're done, click 'Grade Conversation' to get feedback and your score.")

# Sidebar for student info
with st.sidebar:
    st.header("Student Info")
    student_id = st.text_input("Student ID (required to save progress)", max_chars=20)
    student_name = st.text_input("Full Name (optional)")
    student_email = st.text_input("Email (optional)")

if not student_id or not api_key:
    st.warning("Please enter your Student ID.")
    st.stop()

openai.api_key = api_key
session_file = f"gpt_session_{student_id.strip()}.json"
scenario = "Coffee Shop"

# load the general instructions
with open("instruction.txt",'r') as f:
    instructions= f.read()

# load the lesson plan.
with open("coffee.txt",'r') as f:
    lession= f.read()

welcome_msg = "Welcome! Let's start working through questions together. please try and be verbose about what you are think and fully explain your final answer."

# Load or initialize chat history
if os.path.exists(session_file):
    with open(session_file, "r") as f:
        data = json.load(f)
    context = data["context"]
    conversation = data["conversation"]
else:
    context = [
        {"role": "system", "content": instructions},
        {"role": "assistant", "content": st.session_state["scenario_text"]},
        {"role": "assistant", "content": welcome_msg}
    ]
    conversation = []

# # Display Coffee Shop table
# st.markdown("""
# ### Coffee Shop Drink Sales Data
# | Season | Hot Drinks | Cold Drinks | Total |
# |--------|------------|-------------|--------|
# | Winter | 100        | 20          | 120    |
# | Spring | 60         | 40          | 100    |
# | Summer | 40         | 120         | 160    |
# | Fall   | 100        | 40          | 140    |
# | **Total** | **300** | **220**     | **520** |
# """)

# Display conversation
for entry in conversation:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

# Chat input
if prompt := st.chat_input("Type your answer or ask a question..."):
    context.append({"role": "user", "content": prompt})
    conversation.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=context
    )
    assistant_message = response.choices[0].message.content
    context.append({"role": "assistant", "content": assistant_message})
    conversation.append({"role": "assistant", "content": assistant_message})
    with st.chat_message("assistant"):
        st.markdown(assistant_message)

    with open(session_file, "w") as f:
        json.dump({"context": context, "conversation": conversation}, f)

# Grading rubric
rubric_prompt = """You are grading a student's overall conversation with a tutor about probability, using the coffee shop scenario.
Evaluate the entire dialog for:
- Correctness (0-2)
- Justification (0-2)
- Interpretation (0-2)
- Effort/Engagement (0-2)
Provide a short explanation and a final score out of 8.
Here is the full conversation:
"""

def grade_entire_conversation(conversation):
    conv_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation])
    grading_prompt = rubric_prompt + conv_text
    result = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": grading_prompt}]
    )
    return result.choices[0].message.content

# Grade Button
if st.button("🎓 Grade Conversation"):
    with st.spinner("Grading your work..."):
        feedback = grade_entire_conversation(conversation)
        st.subheader("🧪 Feedback:")
        st.markdown(feedback)
        result_df = pd.DataFrame({
            "Name": [student_name],
            "ID": [student_id],
            "Email": [student_email],
            "Feedback": [feedback]
        })
        st.download_button("Download Feedback CSV", result_df.to_csv(index=False), file_name=f"gpt_grading_{student_id}.csv", mime="text/csv")
