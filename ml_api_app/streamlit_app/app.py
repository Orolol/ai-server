import streamlit as st
import requests

st.title("Chat with AI")

def start_chat_session():
    data = {}
    response = requests.post("http://localhost:5000/start_chat", json=data, headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        st.session_state["user_input"] = ""
        return response.json()["chatsessionsid"]
        st.session_state["user_input"] = ""
    else:
        st.error("Failed to start chat session")
        return None

def send_message(chatsessionsid, prompt):
    data = {
        "chatsessionsid": chatsessionsid,
        "prompt": prompt
    }
    response = requests.post("http://localhost:5000/send_message", json=data, headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to send message")
        return None

# Start a new chat session
if "chatsessionsid" not in st.session_state:
    if st.button("Start Chat Session"):
        st.session_state["chatsessionsid"] = start_chat_session()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

def display_messages():
    st.markdown(
        """
        <style>
        .message-container {
            height: 800px;
            overflow-y: scroll;
            border: 1px solid #ccc;
            padding: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.container():
        st.markdown('<div class="message-container">', unsafe_allow_html=True)
        for message in reversed(st.session_state["messages"]):
            st.write(f"{message['role']}: {message['content']}")
        st.markdown('</div>', unsafe_allow_html=True)

def send_message_callback():
    st.session_state["send_message"] = True

display_messages()

# User input
user_input = st.text_input("You: ", st.session_state.get("user_input_reset", ""), key="user_input", on_change=send_message_callback)

if st.session_state.get("send_message"):
    if user_input:
        response = send_message(st.session_state["chatsessionsid"], user_input)
        if response:
            st.session_state["messages"].append({"role": "user", "content": user_input})
            if "response" in response:
                st.session_state["messages"].append({"role": "AI", "content": response["response"]})
            else:
                st.error("Unexpected response format")
            st.session_state["user_input"] = ""
    else:
        st.error("Please enter a message")
    st.session_state["send_message"] = False
