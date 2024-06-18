import streamlit as st
import requests

st.title("AI Server Frontend")

st.sidebar.header("Configuration")
api_url = st.sidebar.text_input("API URL", "http://localhost:5000/predict")

if "conversation" not in st.session_state:
    st.session_state.conversation = []

st.header("Chat Interface")
for message in st.session_state.conversation:
    st.write(f"{message['role']}: {message['content']}")

input_data = st.text_area("Enter your message here")

model_type = st.selectbox("Select Model Type", ["openai", "huggingface"])
model_name_or_key = st.text_input("Model Name or API Key")
agent_type = st.selectbox("Select Agent Type", ["coding", "chat"])

if st.button("Send"):
    st.session_state.conversation.append({"role": "user", "content": input_data})
    payload = {
        "data": input_data,
        "model_type": model_type,
        "model_name_or_key": model_name_or_key,
        "agent_type": agent_type
    }
    response = requests.post(api_url, json=payload)
    if response.status_code == 200:
        prediction = response.json().get("prediction", "")
        st.session_state.conversation.append({"role": "assistant", "content": prediction})
        st.success("Prediction: " + prediction)
    else:
        st.error("Error: " + response.text)
