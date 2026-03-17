import streamlit as st
import requests
import re

# ⚙️ PAGE CONFIG
st.set_page_config(page_title="AI Interview Simulator", layout="centered")

# 🔑 API KEY
API_KEY = st.secrets["GROQ_API_KEY"]

# 🎨 SIMPLE CLEAN UI
st.title("🚀 AI Interview Simulator")
st.caption("Practice interviews with AI feedback")

# 🎛️ SIDEBAR
st.sidebar.title("⚙️ Settings")

role = st.sidebar.selectbox(
    "Role",
    [
        "Software Engineer",
        "Frontend Developer",
        "Backend Developer",
        "Data Scientist",
        "AI Engineer",
        "HR"
    ]
)

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Medium", "Hard"]
)

topic = st.sidebar.selectbox(
    "Topic",
    ["General", "DSA", "System Design", "Machine Learning", "Web Development"]
)

# 🔄 RESET BUTTON
if st.sidebar.button("🔄 Restart"):
    st.session_state.clear()
    st.rerun()

# 💬 STATE INIT
if "messages" not in st.session_state:
    st.session_state.messages = []

if "score" not in st.session_state:
    st.session_state.score = 0

if "q_count" not in st.session_state:
    st.session_state.q_count = 1

# 🤖 SAFE AI FUNCTION
def ask_ai(user_input):
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": f"""
You are an interviewer for {role}.
Difficulty: {difficulty}
Topic: {topic}

Rules:
- Ask one question at a time
- Evaluate answers
- ALWAYS give score like 7/10
- Give short feedback
- Continue interview
"""
                    },
                    *st.session_state.messages,
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.7,
                "max_tokens": 300
            }
        )

        data = response.json()

        if "choices" not in data:
            return f"⚠️ API Error:\n{data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Error: {str(e)}"

# 🚀 AUTO START
if len(st.session_state.messages) == 0:
    first = ask_ai("start interview")
    st.session_state.messages.append({"role": "assistant", "content": first})

# 💬 DISPLAY CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 🛑 END BUTTON (always visible)
end_clicked = st.button("🛑 End Interview")

# ⌨️ INPUT
user_input = st.chat_input("Type your answer...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    reply = ask_ai(user_input)

    # 🎯 SCORE EXTRACTION
    match = re.search(r'(\d+)/10', reply)
    if match:
        st.session_state.score += int(match.group(1))

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": reply})

    st.session_state.q_count += 1

    with st.chat_message("assistant"):
        st.markdown(reply)

# 📊 STATUS
st.write(f"### Question: {st.session_state.q_count}")
st.sidebar.write(f"Score: {st.session_state.score}")

# 📄 FINAL REPORT
if end_clicked:
    report = ask_ai(f"""
Based on this interview:
{st.session_state.messages}

Give:
- Overall performance
- Strengths
- Weaknesses
- Improvement tips
""")

    st.subheader("📄 Final Report")
    st.write(report)
