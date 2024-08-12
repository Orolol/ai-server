import streamlit as st
import requests

def chat_interface():
    st.markdown(
        """
        <style>
        .chat-container {
            height: calc(100vh - 200px);
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 10px;
            margin-bottom: 20px;
        }
        .stTextInput {
            position: fixed;
            bottom: 20px;
            width: calc(66.67% - 40px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state["messages"]:
            st.markdown(f"**{message['role']}:** {message['content']}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Force the container to update
    st.empty()

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
    
    # Force the container to update again after processing the message
    st.empty()

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
