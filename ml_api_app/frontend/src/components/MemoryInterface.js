import React, { useState, useEffect } from 'react';
import axios from 'axios';
import useChatSessionStore from '../store/chatSessionStore';
import './MemoryInterface.css';

function MemoryInterface() {
  const [memoryActions, setMemoryActions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const { chatSessionId } = useChatSessionStore();

  useEffect(() => {
    if (chatSessionId) {
      fetchMemoryActions();
    }
  }, [chatSessionId]);

  const fetchMemoryActions = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`http://localhost:5000/get_memory_action_history/${chatSessionId}`);
      console.log('Memory actions:', response.data);
      setMemoryActions(response.data || []);
    } catch (error) {
      console.error('Failed to fetch memory actions:', error);
      setError('Failed to load memory actions. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const getActionIcon = (type) => {
    switch (type) {
      case 'actions_result': return '🔍';
      case 'final_status': return '🏁';
      case 'iterations': return '🔄';
      default: return '📝';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const renderActionDetails = (action) => {
    if (action.type === 'actions_result' && action.details && Object.keys(action.details).length > 0) {
      return (
        <ul className="action-details-list">
          {Object.entries(action.details).map(([key, value]) => (
            <li key={key}>
              <strong>{key}:</strong> {typeof value === 'string' ? value : JSON.stringify(value)}
            </li>
          ))}
        </ul>
      );
    } else if (action.type === 'final_status' || action.type === 'iterations') {
      return <span className="action-details">{action.details}</span>;
    }
    return null;
  };

  if (isLoading) {
    return <div className="memory-interface">Loading memory actions...</div>;
  }

  if (error) {
    return <div className="memory-interface error">{error}</div>;
  }

  return (
    <div className="memory-interface">
      <h2>Memory Actions</h2>
      {memoryActions.length === 0 ? (
        <p>No memory actions recorded yet.</p>
      ) : (
        <div className="memory-list">
          {memoryActions.map((action, index) => (
            <div key={index} className="memory-item">
              <div className="memory-icon">{getActionIcon(action.type)}</div>
              <div className="memory-content">
                <div className="memory-header">
                  <span className="memory-type">{action.type.charAt(0).toUpperCase() + action.type.slice(1)}</span>
                  <span className="memory-timestamp">{formatTimestamp(action.timestamp)}</span>
                </div>
                {renderActionDetails(action)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MemoryInterface;
