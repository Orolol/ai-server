import streamlit as st
import requests

def web_interface():
    st.subheader("Web Actions")
    
    # Display all web actions performed by agents
    if st.button("Show Web Action History"):
        response = requests.get("http://localhost:5000/get_web_action_history")
        if response.status_code == 200:
            actions = response.json().get("actions", [])
            for action in actions:
                st.write(f"Action: {action['type']}")
                st.write(f"Details: {action['details']}")
                st.write(f"Timestamp: {action['timestamp']}")
                st.write("---")
        else:
            st.error("Failed to fetch web action history")

    # Web search functionality
    st.subheader("Web Search")
    search_query = st.text_input("Enter search query")
    if st.button("Search"):
        if search_query:
            response = requests.post("http://localhost:5000/web_search", json={"query": search_query})
            if response.status_code == 200:
                st.write("Search Results:")
                st.write(response.json().get("results", "No results available"))
            else:
                st.error("Failed to perform web search")
        else:
            st.warning("Please enter a search query")

    # URL content loading functionality
    st.subheader("Load URL Content")
    url = st.text_input("Enter URL to load")
    if st.button("Load Content"):
        if url:
            response = requests.post("http://localhost:5000/load_url_content", json={"url": url})
            if response.status_code == 200:
                st.write("URL Content:")
                st.write(response.json().get("content", "No content available"))
            else:
                st.error("Failed to load URL content")
        else:
            st.warning("Please enter a URL")
