import streamlit as st
import requests

def chat_interface():
    st.markdown(
        """
        <style>
        .chat-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 10px;
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
        }
        .message {
            margin-bottom: 10px;
            padding: 5px 10px;
            border-radius: 5px;
            max-width: 80%;
        }
        .user-message {
            align-self: flex-end;
            background-color: #e6f3ff;
        }
        .ai-message {
            align-self: flex-start;
            background-color: #f0f0f0;
        }
        .stTextInput {
            position: fixed;
            bottom: 20px;
            width: calc(100% - 80px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state["messages"]:
            role_class = "user-message" if message['role'] == "user" else "ai-message"
            st.markdown(f'<div class="message {role_class}">{message["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # User input
    user_input = st.text_input("You: ", key=f"user_input_{st.session_state['user_input_key']}")

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
