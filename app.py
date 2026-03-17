import streamlit as st
import requests

# 🔑 HIDE API KEY (use secrets in production)
API_KEY = st.secrets["GROQ_API_KEY"]

# 🎨 PREMIUM UI STYLE
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}

.block-container {
    padding-top: 2rem;
}

/* Glass card */
.glass {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 16px;
    backdrop-filter: blur(10px);
}

/* Title */
h1 {
    text-align: center;
    font-weight: 700;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 10px;
}

/* Input */
textarea {
    border-radius: 10px !important;
}

</style>
""", unsafe_allow_html=True)

# 🎯 HEADER
st.markdown("<h1>🚀 AI Interview Simulator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#94a3b8;'>Practice smarter. Perform better.</p>", unsafe_allow_html=True)

st.divider()

# 🎛️ SIDEBAR SETTINGS
st.sidebar.title("⚙️ Interview Settings")

role = st.sidebar.selectbox(
    "Select Role",
    ["Software Engineer", "Frontend Developer", "Backend Developer", "Data Scientist", "AI Engineer", "HR"]
)

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Medium", "Hard"]
)

# 💬 SESSION STATE
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "score" not in st.session_state:
    st.session_state.score = 0
    st.session_state.questions = 0

# 🤖 AI FUNCTION
def ai_interviewer(user_input):

    system_prompt = f"""
    You are an AI Interviewer for {role} role.

    Difficulty: {difficulty}

    Your job:
    - Ask interview questions
    - Evaluate answers (score out of 10)
    - Give feedback
    - Ask next question

    If user asks doubt:
    - Explain clearly
    - Continue interview
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

    # 🎯 Extract score
    import re
    match = re.search(r'(\d+)/10', reply)
    if match:
        st.session_state.score += int(match.group(1))
        st.session_state.questions += 1

    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

    return reply

# 🚀 AUTO START
if len(st.session_state.chat_history) == 0:
    start = ai_interviewer("start interview")
    st.session_state.chat_history.append({"role": "assistant", "content": start})

# 💬 CHAT DISPLAY
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ⌨️ INPUT
user_input = st.chat_input("Type your answer...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    response = ai_interviewer(user_input)

    with st.chat_message("assistant"):
        st.markdown(response)

# 📊 SCORE PANEL
if st.session_state.questions > 0:
    st.sidebar.markdown("### 📊 Performance")
    st.sidebar.write(f"Score: {st.session_state.score}")
    st.sidebar.write(f"Questions: {st.session_state.questions}")
