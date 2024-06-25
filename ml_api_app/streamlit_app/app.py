import streamlit as st
import requests
from ml_api_app.config.ai_providers_config import ai_providers_config

st.set_page_config(layout="wide")
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

# Create two columns
left_column, right_column = st.columns([2, 1])

with left_column:
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

    display_messages()

    def send_message_callback():
        st.session_state["send_message"] = True

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

with right_column:
    st.subheader("Chat Session Parameters")

    if not st.session_state["chat_started"]:
        ai_provider = st.selectbox("AI Provider", list(ai_providers_config.keys()), index=0)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        max_length = st.number_input("Max Length", min_value=1, max_value=4096, value=1024, step=1)
        
        weak_model = ai_providers_config[ai_provider]["weak_model"]
        strong_model = ai_providers_config[ai_provider]["strong_model"]
        
        st.info(f"Weak model: {weak_model}")
        st.info(f"Strong model: {strong_model}")
        
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
        ai_provider = st.session_state['chat_params']['ai_provider']
        weak_model = ai_providers_config[ai_provider]["weak_model"]
        strong_model = ai_providers_config[ai_provider]["strong_model"]
        st.info(f"You're chatting with {ai_provider} provider. Weak model: {weak_model}, Strong model: {strong_model}. Temperature: {st.session_state['chat_params']['temperature']}, Max length: {st.session_state['chat_params']['max_length']}")

    # Clear memory button
    if st.button("Clear Memory"):
        response = requests.post("http://localhost:5000/clear_memory")
        if response.status_code == 200:
            st.success("Memory cleared successfully")
            st.session_state["messages"] = []  # Clear the messages in the UI
        else:
            st.error(f"Failed to clear memory: {response.json().get('error', 'Unknown error')}")
