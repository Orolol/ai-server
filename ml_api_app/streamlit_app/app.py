import streamlit as st
import requests
from ml_api_app.config.ai_providers_config import ai_providers_config

st.set_page_config(layout="wide")
st.title("Chat with AI")

def start_chat_session(params):
    response = requests.post("http://localhost:5000/start_chat",
                             json=params, headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        st.session_state["user_input_reset"] = ""
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

def restart_session():
    st.session_state["chatsessionsid"] = None
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""
    st.session_state["user_input_key"] = 0
    st.session_state["send_message"] = False
    st.session_state["chat_started"] = False
    st.session_state["chat_params"] = {}

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
    st.markdown(
        """
        <style>
        .chat-container {
            height: 500px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 10px;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state["messages"]:
            st.markdown(f"**{message['role']}:** {message['content']}")
        st.markdown('</div>', unsafe_allow_html=True)

    def send_message_callback():
        st.session_state["send_message"] = True

    # User input
    user_input = st.text_input("You: ", key=f"user_input_{st.session_state['user_input_key']}", on_change=send_message_callback)

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
                st.session_state["user_input_key"] += 1  # Increment the key
            st.experimental_rerun()  # Rerun to update the display
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
                st.success("Chat session started successfully!")
                st.experimental_rerun()
            else:
                st.error("Failed to start chat session. Please try again.")

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
    
    # Restart session button
    if st.button("Restart Session"):
        restart_session()
        st.success("Session restarted successfully!")
        st.experimental_rerun()
