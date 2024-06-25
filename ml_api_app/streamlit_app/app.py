import streamlit as st
import requests

st.title("Chat with AI")


def start_chat_session(params):
    response = requests.post("http://localhost:5000/start_chat",
                             json=params, headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        st.session_state["user_input"] = ""
        return response.json()["chatsessionsid"]
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

if "chat_started" not in st.session_state:
    st.session_state["chat_started"] = False

if "chat_params" not in st.session_state:
    st.session_state["chat_params"] = {}

# Start a new chat session
if not st.session_state["chat_started"]:
    st.subheader("Chat Session Parameters")
    col1, col2 = st.columns(2)
    with col1:
        ai_provider = st.selectbox("AI Provider", ["openai", "anthropic", "huggingface"], index=0)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    with col2:
        max_length = st.number_input("Max Length", min_value=1, max_value=4096, value=1024, step=1)
    system_message = st.text_area("System Message", "")
    
    if st.button("Start Chat Session"):
        params = {
            "ai_provider": ai_provider,
            "temperature": temperature,
            "max_length": max_length,
            "system_message": system_message
        }
        st.session_state["chatsessionsid"] = start_chat_session(params)
        if st.session_state["chatsessionsid"]:
            st.session_state["chat_started"] = True
            st.session_state["chat_params"] = params
            st.experimental_rerun()

if st.session_state["chat_started"]:
    st.info(f"You're chatting with {st.session_state['chat_params']['ai_provider']} model with temperature {st.session_state['chat_params']['temperature']} and max length {st.session_state['chat_params']['max_length']}")

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
