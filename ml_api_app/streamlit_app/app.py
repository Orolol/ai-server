import streamlit as st
import requests

st.title("AI Server Frontend")

st.sidebar.header("Configuration")
api_url = st.sidebar.text_input("API URL", "http://localhost:5000/predict")

st.header("Input Data")
input_data = st.text_area("Enter your input data here")

model_type = st.selectbox("Select Model Type", ["openai", "huggingface"])
model_name_or_key = st.text_input("Model Name or API Key")
agent_type = st.selectbox("Select Agent Type", ["coding", "chat"])

if st.button("Predict"):
    payload = {
        "data": {"prompt": input_data},
        "model_type": model_type,
        "model_name_or_key": model_name_or_key,
        "agent_type": agent_type
    }
    response = requests.post(api_url, json=payload)
    if response.status_code == 200:
        st.success("Prediction: " + response.json().get("prediction", ""))
    else:
        st.error("Error: " + response.text)
