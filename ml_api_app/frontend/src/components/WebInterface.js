import React, { useState, useEffect } from 'react';
import axios from 'axios';

function WebInterface({ chatSessionId }) {
  const [webActions, setWebActions] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [url, setUrl] = useState('');

  useEffect(() => {
    if (chatSessionId) {
      fetchWebActions();
    }
  }, [chatSessionId]);

  const fetchWebActions = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/get_web_action_history/${chatSessionId}`);
      setWebActions(response.data.actions);
    } catch (error) {
      console.error('Failed to fetch web actions:', error);
    }
  };

  const performWebSearch = async () => {
    try {
      const response = await axios.post('http://localhost:5000/web_search', {
        query: searchQuery,
        session_id: chatSessionId
      });
      console.log('Search results:', response.data.results);
      fetchWebActions();
    } catch (error) {
      console.error('Failed to perform web search:', error);
    }
  };

  const loadUrlContent = async () => {
    try {
      const response = await axios.post('http://localhost:5000/load_url_content', {
        url,
        session_id: chatSessionId
      });
      console.log('URL content:', response.data.content);
      fetchWebActions();
    } catch (error) {
      console.error('Failed to load URL content:', error);
    }
  };

  return (
    <div className="web-interface">
      <h2>Web Actions</h2>
      <div>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Enter search query"
        />
        <button onClick={performWebSearch}>Search</button>
      </div>
      <div>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter URL"
        />
        <button onClick={loadUrlContent}>Load Content</button>
      </div>
      <ul>
        {webActions.map((action, index) => (
          <li key={index}>
            {action.type} - {action.timestamp}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default WebInterface;
