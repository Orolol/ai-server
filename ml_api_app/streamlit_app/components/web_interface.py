import streamlit as st
import requests

def web_interface(session_id):
    st.subheader("Web Actions")
    
    # Automatically fetch and display web action history
    fetch_and_display_history(session_id)
    
    # Web search functionality
    st.subheader("Web Search")
    search_query = st.text_input("Enter search query")
    if st.button("Search"):
        if search_query:
            response = requests.post("http://localhost:5000/web_search", json={"query": search_query, "session_id": session_id})
            if response.status_code == 200:
                st.write("Search Results:")
                st.write(response.json().get("results", "No results available"))
                # Refresh the history after a new search
                fetch_and_display_history(session_id)
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
                # Refresh the history after loading URL content
                fetch_and_display_history(session_id)
            else:
                st.error("Failed to load URL content")
        else:
            st.warning("Please enter a URL")

def fetch_and_display_history(session_id):
    response = requests.get(f"http://localhost:5000/get_web_action_history/{session_id}")
    if response.status_code == 200:
        actions = response.json().get("actions", [])
        if actions:
            for action in actions:
                with st.expander(f"{action['type']} - {action['timestamp']}"):
                    st.json(action['details'])
        else:
            st.info("No web actions found in the history.")
    else:
        st.error("Failed to fetch web action history")
