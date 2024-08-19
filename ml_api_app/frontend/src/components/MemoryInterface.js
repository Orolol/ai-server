import React, { useState, useEffect } from 'react';
import axios from 'axios';

function MemoryInterface() {
  const [memories, setMemories] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchMemories();
  }, []);

  const fetchMemories = async () => {
    try {
      const response = await axios.get('http://localhost:5000/memory/search', {
        params: { keywords: searchQuery }
      });
      setMemories(response.data.results);
    } catch (error) {
      console.error('Failed to fetch memories:', error);
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
    </div>
  );
}

export default MemoryInterface;
