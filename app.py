import streamlit as st
import requests
import re

# ⚙️ PAGE CONFIG
st.set_page_config(
    page_title="AI Interview Simulator",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 🔒 HIDE STREAMLIT UI
st.markdown("""
<style>
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}

.block-container {
    padding-top: 2rem;
}

h1 {
    text-align: center;
    font-weight: 700;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# 🔑 API KEY
API_KEY = st.secrets["GROQ_API_KEY"]

# 🎯 HEADER
st.markdown("<h1>🚀 AI Interview Simulator</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Practice smarter. Perform better.</div>", unsafe_allow_html=True)
st.divider()

# 🎛️ SIDEBAR
st.sidebar.title("⚙️ Settings")

role = st.sidebar.selectbox(
    "Role",
    ["Software Engineer", "Frontend", "Backend", "Data Scientist", "AI Engineer", "HR"]
)

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Medium", "Hard"]
)

# 🔄 RESET
if st.sidebar.button("🔄 Restart"):
    st.session_state.chat_history = []
    st.session_state.score = 0
    st.session_state.questions = 0
    st.session_state.scores_list = []

# 💬 SESSION STATE
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "score" not in st.session_state:
    st.session_state.score = 0
    st.session_state.questions = 0
    st.session_state.scores_list = []

# 🤖 AI FUNCTION
def ai_interviewer(user_input):

    system_prompt = f"""
    You are an AI Interviewer for {role}.
    Difficulty: {difficulty}

    Ask questions, evaluate answers (/10), give feedback,
    and continue interview.
    """

    messages = [{"role": "system", "content": system_prompt}]
    messages += st.session_state.chat_history
    messages.append({"role": "user", "content": user_input})

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 300
        }
    )

    data = response.json()

    if "choices" not in data:
        return f"⚠️ API Error:\n{data}"

    reply = data["choices"][0]["message"]["content"]

    # extract score
    match = re.search(r'(\d+)/10', reply)
    if match:
        score = int(match.group(1))
        st.session_state.score += score
        st.session_state.questions += 1
        st.session_state.scores_list.append(score)

    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

    return reply

# 🚀 AUTO START
if len(st.session_state.chat_history) == 0:
    first = ai_interviewer("Start interview")
    st.session_state.chat_history.append({"role": "assistant", "content": first})

# 💬 CHAT DISPLAY
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 🛑 END BUTTON (FIXED POSITION)
if st.session_state.questions > 0:
    end_clicked = st.button("🛑 End Interview & Generate Report")

# ⌨️ INPUT (AFTER BUTTON)
user_input = st.chat_input("Type your answer...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    response = ai_interviewer(user_input)

    with st.chat_message("assistant"):
        st.markdown(response)

# 📊 PROGRESS BAR
if st.session_state.questions > 0:
    progress = min(st.session_state.questions / 10, 1.0)
    st.progress(progress)

# 📈 GRAPH
if len(st.session_state.scores_list) > 0:
    st.subheader("📈 Score Trend")
    st.line_chart(st.session_state.scores_list)

# 📊 SIDEBAR
if st.session_state.questions > 0:
    st.sidebar.markdown("### 📊 Performance")
    st.sidebar.write(f"Score: {st.session_state.score}")
    st.sidebar.write(f"Questions: {st.session_state.questions}")

# 📄 FINAL REPORT (FIXED)
if "end_clicked" in locals() and end_clicked:

    report_prompt = f"""
    Based on this interview:

    {st.session_state.chat_history}

    Give:
    - Overall performance
    - Strengths
    - Weaknesses
    - Improvement tips
    """

    report = ai_interviewer(report_prompt)

    st.subheader("📄 Final Report")
    st.write(report)
