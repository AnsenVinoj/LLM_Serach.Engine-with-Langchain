from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st

# LangChain / Google GenAI imports
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
# pyrefly: ignore [missing-import]
from langchain_google_genai import ChatGoogleGenerativeAI

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(page_title="Gemini AI Assistant", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# ---------------------------
# Load keys from environment
# ---------------------------
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_KEY

os.environ["LANGCHAIN_TRACING_V2"] = "true"

# ---------------------------
# Premium CSS Styling
# ---------------------------
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

/* Main Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    color: #f8fafc;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Chat Input Styling */
[data-testid="stChatInput"] {
    background-color: rgba(30, 41, 59, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    color: white !important;
}

/* Title Styling */
.gradient-text {
    background: linear-gradient(to right, #a855f7, #ec4899, #f43f5e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 0px;
    padding-bottom: 0px;
}

.subtitle {
    color: #94a3b8;
    font-size: 16px;
    margin-bottom: 30px;
}

/* Message styling */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 10px;
    backdrop-filter: blur(4px);
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ---------------------------
# Sidebar controls
# ---------------------------
with st.sidebar:
    st.markdown("## ✨ Settings")
    
    MODEL_OPTIONS = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]
    selected_model = st.selectbox("Intelligence Level", MODEL_OPTIONS, index=0)
    
    temperature = st.slider("Creativity", min_value=0.0, max_value=1.0, value=0.5, step=0.05)
    
    st.divider()
    
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    if not GOOGLE_KEY:
        st.error("⚠️ GOOGLE_API_KEY not found in .env")

# ---------------------------
# Session state: chat history
# ---------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------------
# Prompt template & chain (Updated for memory)
# ---------------------------
# MessagesPlaceholder dynamic injections allow LangChain to inject the list of tuples directly
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a highly advanced AI assistant. You are insightful, concise, and helpful. Format your responses elegantly in markdown."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{question}")
])

llm = ChatGoogleGenerativeAI(model=selected_model, temperature=temperature)
parser = StrOutputParser()
chain = prompt | llm | parser

# ---------------------------
# Main UI
# ---------------------------
st.markdown('<h1 class="gradient-text">✨ Gemini AI Workspace</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Experience the power of Google Generative AI</p>', unsafe_allow_html=True)

# Display Chat History using native chat elements
for role, text in st.session_state.history:
    with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "✨"):
        st.markdown(text)

# Chat Input
if user_query := st.chat_input("Message Gemini..."):
    # Immediately show user message
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_query)

    # Generate and show assistant response
    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("Thinking..."):
            try:
                # Format the session history into the structure LangChain expects: ("user"/"assistant", "text")
                formatted_history = [(role, text) for role, text in st.session_state.history]
                
                # Invoke the chain passing BOTH context history and the new question
                response = chain.invoke({
                    "chat_history": formatted_history,
                    "question": user_query
                })
                
                st.markdown(response)
                
                # Append to session state ONLY after a successful execution to maintain integrity
                st.session_state.history.append(("user", user_query))
                st.session_state.history.append(("assistant", response))
                
            except Exception as e:
                error_msg = f"**Error calling model:** {str(e)}"
                st.error(error_msg)