import React, { useState, useEffect } from 'react';
import axios from 'axios';
import useChatSessionStore from '../store/chatSessionStore';
import './MemoryInterface.css';

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
      setMemoryActions(response.data.history || []);
    } catch (error) {
      console.error('Failed to fetch memory actions:', error);
    }
  };

  const getActionIcon = (type) => {
    switch (type) {
      case 'add': return '➕';
      case 'delete': return '🗑️';
      case 'update': return '🔄';
      default: return '📝';
    }
  };

  return (
    <div className="memory-interface">
      <h2>Memory Actions</h2>
      <div className="memory-list">
        {memoryActions.map((action, index) => (
          <div key={index} className="memory-item">
            <div className="memory-icon">{getActionIcon(action.type)}</div>
            <div className="memory-content">
              <div className="memory-header">
                <span className="memory-type">{action.type}</span>
                <span className="memory-timestamp">{new Date(action.timestamp).toLocaleString()}</span>
              </div>
              <div className="memory-details">{action.details}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MemoryInterface;
