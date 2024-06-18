import streamlit as st
import requests

st.title("Chat with AI")

def start_chat_session():
    response = requests.post("http://localhost:5000/start_chat", headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        return response.json()["chatsessionsid"]
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
    st.session_state["chatsessionsid"] = start_chat_session()

# User input
user_input = st.text_input("You: ", "")
if st.button("Send"):
    if user_input:
        response = send_message(st.session_state["chatsessionsid"], user_input)
        if response:
            st.write(f"AI: {response}")
    else:
        st.error("Please enter a message")
