import streamlit as st
import requests

st.set_page_config(page_title="AI Interview")

API_KEY = st.secrets["GROQ_API_KEY"]

# Sidebar
role = st.sidebar.selectbox("Role", ["Software Engineer", "Data Scientist"])
difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

# Reset button
if st.sidebar.button("Restart"):
    st.session_state.clear()
    st.rerun()

# State
if "messages" not in st.session_state:
    st.session_state.messages = []

def ask_ai(user_input):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": f"You are an interviewer for {role}, difficulty {difficulty}"},
                *st.session_state.messages,
                {"role": "user", "content": user_input}
            ]
        }
    )

    data = response.json()
    return data["choices"][0]["message"]["content"]

# Auto start
if len(st.session_state.messages) == 0:
    first = ask_ai("start interview")
    st.session_state.messages.append({"role": "assistant", "content": first})

# Chat display
for msg in st.session_state.messages:
    st.write(f"**{msg['role']}**: {msg['content']}")

# End button (ALWAYS visible)
if st.button("End Interview"):
    st.write("Interview ended. Good job 👍")
    st.stop()

# Input
user_input = st.text_input("Your answer")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    reply = ask_ai(user_input)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
