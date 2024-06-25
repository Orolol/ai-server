import streamlit as st
import requests

st.title("Chat with AI")


def start_chat_session():
    data = {}
    response = requests.post("http://localhost:5000/start_chat",
                             json=data, headers={"Content-Type": "application/json"})
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
    response = requests.post("http://localhost:5000/send_message",
                             json=data, headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to send message")
        return None


# Initialize session state variables
if "chatsessionsid" not in st.session_state:
    st.session_state["chatsessionsid"] = None

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

if "send_message" not in st.session_state:
    st.session_state["send_message"] = False

# Start a new chat session
if st.session_state["chatsessionsid"] is None:
    if st.button("Start Chat Session"):
        st.session_state["chatsessionsid"] = start_chat_session()


def display_messages():
    st.markdown(
        """
        <style>
        .message-container {
            height: 600px;
            overflow-y: scroll;
            border: 1px solid #ccc;
            padding: 10px;
            display: flex;
            flex-direction: column-reverse;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    messages_html = '<div class="message-container">'
    for message in st.session_state["messages"]:
        messages_html += f"<p><strong>{message['role']}:</strong> {message['content']}</p>"
    messages_html += '</div>'
    st.markdown(messages_html, unsafe_allow_html=True)


def send_message_callback():
    st.session_state["send_message"] = True
    if st.session_state.get("send_message"):
        user_input = st.session_state["user_input"]
        if user_input:
            response = send_message(
                st.session_state["chatsessionsid"], user_input)
            if response:
                st.session_state["messages"].append(
                    {"role": "user", "content": user_input})
                if "response" in response:
                    st.session_state["messages"].append(
                        {"role": "AI", "content": response["response"]})
                else:
                    st.error("Unexpected response format")
                st.session_state["user_input"] = ""
        else:
            st.error("Please enter a message")
        st.session_state["send_message"] = False


display_messages()

# User input
user_input = st.text_input("You: ", st.session_state.get(
    "user_input_reset", ""), key="user_input", on_change=send_message_callback)


if st.session_state.get("send_message"):
    if user_input:
        response = send_message(st.session_state["chatsessionsid"], user_input)
        if response:
            st.session_state["messages"].append(
                {"role": "user", "content": user_input})
            if "response" in response:
                st.session_state["messages"].append(
                    {"role": "AI", "content": response["response"]})
            else:
                st.error("Unexpected response format")
            st.session_state["user_input"] = ""
    else:
        st.error("Please enter a message")
    st.session_state["send_message"] = False
