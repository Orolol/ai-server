import streamlit as st
import requests
from ml_api_app.config.ai_providers_config import ai_providers_config

def config_interface():
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

def start_chat_session(params):
    response = requests.post("http://localhost:5000/start_chat",
                             json=params, headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        st.session_state["user_input_reset"] = ""
        return response.json()["chatsessionsid"]
    else:
        st.error("Failed to start chat session")
        return None

def restart_session():
    st.session_state["chatsessionsid"] = None
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""
    st.session_state["user_input_key"] = 0
    st.session_state["send_message"] = False
    st.session_state["chat_started"] = False
    st.session_state["chat_params"] = {}
