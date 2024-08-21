import React, { useState, useEffect } from 'react';
import axios from 'axios';

function MemoryInterface() {
  const [memoryActions, setMemoryActions] = useState([]);

  useEffect(() => {
    fetchMemoryActions();
  }, []);

  const fetchMemoryActions = async () => {
    try {
      const response = await axios.get('http://localhost:5000/get_memory_action_history');
      console.log('Memory actions response:', response.data);
      setMemoryActions(response.data.history || []);
    } catch (error) {
      console.error('Failed to fetch memory actions:', error);
    }
  };

  return (
    <div className="memory-interface">
      <h2>Memory Actions</h2>
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
