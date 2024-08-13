import streamlit as st
import requests
import time
import threading

def web_interface(session_id):
    if 'update_thread' not in st.session_state:
        st.session_state.update_thread = None
    st.subheader("Web Actions")
    
    # Create a placeholder for the history
    history_placeholder = st.empty()
    
    # Start a background task to update the history if not already running
    if st.session_state.update_thread is None or not st.session_state.update_thread.is_alive():
        st.write("Fetching web action history...")
        st.session_state.update_thread = threading.Thread(target=update_history_background, args=(session_id, history_placeholder))
        st.session_state.update_thread.start()
    
    # Web search functionality
    st.subheader("Web Search")
    search_query = st.text_input("Enter search query")
    if st.button("Search"):
        if search_query:
            response = requests.post("http://localhost:5000/web_search", json={"query": search_query, "session_id": session_id})
            if response.status_code == 200:
                st.write("Search Results:")
                st.write(response.json().get("results", "No results available"))
                # The history will be automatically updated by the background task
            else:
                st.error("Failed to perform web search")
        else:
            st.warning("Please enter a search query")

    # URL content loading functionality
    st.subheader("Load URL Content")
    url = st.text_input("Enter URL to load")
    if st.button("Load Content"):
        if url:
            response = requests.post("http://localhost:5000/load_url_content", json={"url": url, "session_id": session_id})
            if response.status_code == 200:
                st.write("URL Content:")
                st.write(response.json().get("content", "No content available"))
                # The history will be automatically updated by the background task
            else:
                st.error("Failed to load URL content")
        else:
            st.warning("Please enter a URL")

def update_history_background(session_id, placeholder):
    while True:
        response = requests.get(f"http://localhost:5000/get_web_action_history/{session_id}")
        if response.status_code == 200:
            actions = response.json().get("actions", [])
            placeholder.empty()
            with placeholder.container():
                if actions:
                    for action in actions:
                        with st.expander(f"{action['type']} - {action['timestamp']}"):
                            st.json(action['details'])
                else:
                    st.info("No web actions found in the history.")
        else:
            placeholder.empty()
            with placeholder.container():
                st.error("Failed to fetch web action history")
        time.sleep(2)  # Wait for 2 seconds before the next update
        st.experimental_rerun()
