import streamlit as st
import openai
import json
import os
import re
import pandas as pd


st.set_page_config(page_title="STT 200 Coffee Shop Tutor", page_icon="☕")
st.title("🧠 STT 200 Coffee Shop Tutor (Coffee Shop Scenario)")
st.markdown("You’ll talk to an AI tutor about probability. When you're done, click 'Grade Conversation' to get feedback and your score.  The grading system can only see your responses so try to be verbose.")

# Sidebar for student info
with st.sidebar:
    st.header("Student Info")
    student_id = st.text_input("Student ID (required to save progress)", max_chars=20)
    student_name = st.text_input("Full Name (optional)")
    student_email = st.text_input("Email (optional)")

if not student_id:
    st.warning("Please enter your Student ID.")
    st.stop()


openai.api_key = st.secrets["OPENAI_API_KEY"]
session_file = f"gpt_session_{student_id.strip()}.json"
scenario = "Coffee Shop"

# load the general instructions
with open("instructions.txt",'r') as f:
    instructions= f.read()

# load the lesson plan.
with open("coffee.txt",'r') as f:
    lession= f.read()

# load the grader instructions.
with open("rubric.txt",'r') as f:
    rubric= f.read()


#welcome_msg = "Welcome! Let's start working through questions together. please try and be verbose about what you are thinking and fully explain your results."

# Load or initialize chat history
if os.path.exists(session_file):
    with open(session_file, "r") as f:
        data = json.load(f)
    context = data["context"]
    conversation = data["conversation"]
    # Display conversation
    for entry in conversation:
        with st.chat_message(entry["role"]):
            st.markdown(entry["content"])
else:
    context = [
        {"role": "system", "content": "Instructions: "+instructions},
        {"role": "assistant", "content": "Lession:"+lession},
        {"role": "assistant", "content": "Start the conversation by 1. introducing the scenario, 2. displaying the data as table (if any) 3. Ask the first question."}
    ]
    conversation = []
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=context
    )
    assistant_message = response.choices[0].message.content
    if re.search(r"\\bQ\\d+\\b", assistant_message):
        meta = "question"
    else:
        meta = "tutoring"
    context.append({"role": "assistant", "content": assistant_message,"meta":meta})
    conversation.append({"role": "assistant", "content": assistant_message,"meta":meta})
    with st.chat_message("assistant"):
        st.markdown(assistant_message)
    
    with open(session_file, "w") as f:
        json.dump({"context": context, "conversation": conversation}, f)



def get_conversation_text_user_focused(conversation, allquestions =False):
    filtered = []
    question = None
    for msg in conversation:
        if msg["role"] == "assistant":
            if msg["meta"]=='question':
                question = f"Assistant: {msg['content']}"
                if not allquestions: 
                    filtered = []
                else:
                    filtered.append(question)
            elif msg['meta']=='grading':
                filtered.append(f"Grader: {msg['content']}")
        elif msg["role"] == "user" and question:
            filtered.append(f"User: {msg['content']}")
    if not allquestions:
        filtered.insert(0,question)
    return "\n".join(filtered)
def grade_question(conversation):
    conv_text = get_conversation_text_user_focused(conversation,False)
    grading_prompt = rubric + conv_text
    result = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": grading_prompt + "\n Be as breif as possible."}]
    )
    return result.choices[0].message.content
def grade_entire_conversation(conversation):
    #conv_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation if msg['role']=='user'])
    conv_text = get_conversation_text_user_focused(conversation, True)
    grading_prompt = rubric + conv_text
    result = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": grading_prompt}]
    )
    return result.choices[0].message.content


# Chat input
if prompt := st.chat_input("Type your answer or ask a question..."):
    with st.spinner("thinking..."):
        context.append({"role": "user", "content": prompt})
        conversation.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        grade_results= grade_question(conversation)
        context.append({"role": "assistant", "content": grade_results,"meta": "grader"})
        conversation.append({"role": "assistant", "content": grade_results, "meta":"grader"})
        with st.chat_message("grader"):
            st.markdown(grade_results)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=context
        )
        assistant_message = response.choices[0].message.content
        if re.search(r"\\bQ\\d+\\b", assistant_message):
            meta = "question"
        else:
            meta = "tutoring"
        context.append({"role": "assistant", "content": assistant_message,"meta":meta})
        conversation.append({"role": "assistant", "content": assistant_message,"meta":meta})
        with st.chat_message("assistant"):
            st.markdown(assistant_message)

        with open(session_file, "w") as f:
            json.dump({"context": context, "conversation": conversation}, f)

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
