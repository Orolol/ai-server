import React, { useState, useEffect } from 'react';
import axios from 'axios';
import useChatSessionStore from '../store/chatSessionStore';

function MemoryInterface() {
  const [memoryActions, setMemoryActions] = useState([]);
  const { chatSessionId } = useChatSessionStore();

  useEffect(() => {
    fetchMemoryActions();
  }, [chatSessionId]);

  const fetchMemoryActions = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/get_memory_action_history/${chatSessionId}`);
      console.log('Memory actions response:', response.data);
      setMemoryActions(response.data || []);
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
            <strong>{action.type}</strong> - {new Date(action.timestamp).toLocaleString()}
            <br />
            Details: {action.details}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default MemoryInterface;
