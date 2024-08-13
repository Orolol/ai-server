import streamlit as st
from components.chat_interface import chat_interface
from components.config_interface import config_interface
from components.memory_interface import memory_interface
from components.web_interface import web_interface

st.set_page_config(layout="wide")
st.title("Chat with AI")

# Initialize session state variables
if "chatsessionsid" not in st.session_state:
    st.session_state["chatsessionsid"] = None
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""
if "user_input_key" not in st.session_state:
    st.session_state["user_input_key"] = 0
if "send_message" not in st.session_state:
    st.session_state["send_message"] = False
if "chat_started" not in st.session_state:
    st.session_state["chat_started"] = False
if "chat_params" not in st.session_state:
    st.session_state["chat_params"] = {}

# Create two columns
left_column, right_column = st.columns([2, 1])

with left_column:
    chat_interface()

with right_column:
    st.subheader("Workspace")
    tabs = st.tabs(["Configuration", "Memory", "Web"])
    
    with tabs[0]:
        config_interface()
    
    with tabs[1]:
        memory_interface()
    
    with tabs[2]:
        web_interface(st.session_state.get("chatsessionsid"))
