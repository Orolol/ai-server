import React, { useState, useEffect } from 'react';
import axios from 'axios';

function MemoryInterface() {
  const [memories, setMemories] = useState([]);

  useEffect(() => {
    fetchMemories();
  }, []);

  const fetchMemories = async () => {
    try {
      const response = await axios.get('http://localhost:5000/search_memories');
      setMemories(response.data.results);
    } catch (error) {
      console.error('Failed to fetch memories:', error);
    }
  };

  return (
    <div className="memory-interface">
      <h2>Memory</h2>
      <ul>
        {memories.map((memory, index) => (
          <li key={index}>{memory}</li>
        ))}
      </ul>
    </div>
  );
}

export default MemoryInterface;
