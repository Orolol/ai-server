import React, { useState, useEffect } from 'react';
import axios from 'axios';

function MemoryInterface() {
  const [memories, setMemories] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [memoryActions, setMemoryActions] = useState([]);

  useEffect(() => {
    fetchMemories();
    fetchMemoryActions();
  }, []);

  const fetchMemories = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/memory/search', {
        params: { query: searchQuery }
      });
      setMemories(response.data.results);
    } catch (error) {
      console.error('Failed to fetch memories:', error);
    }
  };

  const fetchMemoryActions = async () => {
    try {
      const response = await axios.get('http://localhost:5000/get_memory_action_history');
      setMemoryActions(response.data.history);
    } catch (error) {
      console.error('Failed to fetch memory actions:', error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchMemories();
  };

  return (
    <div className="memory-interface">
      <h2>Memory</h2>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search memories..."
        />
        <button type="submit">Search</button>
      </form>
      <ul>
        {memories.map((memory, index) => (
          <li key={index}>{memory.document}</li>
        ))}
      </ul>
      <h3>Memory Actions</h3>
      <ul>
        {memoryActions.map((action, index) => (
          <li key={index}>
            <strong>{action.agent_type}</strong> - {action.date}
            <br />
            Keywords: {action.keywords.join(', ')}
            <br />
            Summary: {action.interaction_summary}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default MemoryInterface;
