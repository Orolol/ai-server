import streamlit as st
import requests

def web_interface():
    st.subheader("Web Search and URL Lookup")
    
    # Display web search results
    if st.button("Fetch Web Search Results"):
        response = requests.get("http://localhost:5000/get_web_search_results")
        if response.status_code == 200:
            search_results = response.json().get("search_results", [])
            for result in search_results:
                st.write(f"Query: {result['query']}")
                st.write(f"Result: {result['result']}")
                st.write("---")
        else:
            st.error("Failed to fetch web search results")

    # Add URL lookup functionality
    url = st.text_input("Enter URL to lookup")
    if st.button("Lookup URL"):
        if url:
            response = requests.post("http://localhost:5000/url_lookup", json={"url": url})
            if response.status_code == 200:
                st.write(response.json().get("content", "No content available"))
            else:
                st.error("Failed to lookup URL")
        else:
            st.warning("Please enter a URL")

    # Add more web-related functionality here as needed
