import streamlit as st
import requests

def memory_interface():
    st.subheader("Memory Actions")
    
    # Display memory actions
    if st.button("Fetch Memory Actions"):
        response = requests.get("http://localhost:5000/get_memory_actions")
        if response.status_code == 200:
            memory_actions = response.json().get("memory_actions", [])
            for action in memory_actions:
                st.write(f"Action: {action['action']}, Data: {action['data']}")
        else:
            st.error("Failed to fetch memory actions")

    # Add more memory-related functionality here as needed
