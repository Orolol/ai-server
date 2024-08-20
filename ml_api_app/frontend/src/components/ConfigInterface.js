import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ConfigInterface({ setChatSessionId, setMessages }) {
  const [aiProviders, setAiProviders] = useState([]);
  const [strengths, setStrengths] = useState([]);
  const [aiProvider, setAiProvider] = useState('');
  const [strength, setStrength] = useState('');
  const [systemMessage, setSystemMessage] = useState('');
  const [existingSessions, setExistingSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState('');

  useEffect(() => {
    fetchExistingSessions();
    fetchConfigOptions();
  }, []);

  const fetchConfigOptions = async () => {
    try {
      const response = await axios.get('http://localhost:5000/config_options');
      setAiProviders(response.data.ai_providers);
      setStrengths(response.data.strengths);
      setAiProvider(response.data.ai_providers[0]);
      setStrength(response.data.strengths[0]);
    } catch (error) {
      console.error('Failed to fetch configuration options:', error);
    }
  };

  const fetchExistingSessions = async () => {
    try {
      const response = await axios.get('http://localhost:5000/list_sessions');
      setExistingSessions(response.data.sessions);
    } catch (error) {
      console.error('Failed to fetch existing sessions:', error);
    }
  };

  const startChatSession = async () => {
    try {
      const response = await axios.post('http://localhost:5000/start_chat', {
        ai_provider: aiProvider,
        strength: strength,
        system_message: systemMessage
      });

      if (response.data.chatsessionsid) {
        setChatSessionId(response.data.chatsessionsid);
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to start chat session:', error);
    }
  };

  const reconnectToSession = async () => {
    if (!selectedSession) return;
    try {
      const response = await axios.get(`http://localhost:5000/load_session/${selectedSession}`);
      if (response.data.chatsessionsid) {
        setChatSessionId(response.data.chatsessionsid);
        // You might want to fetch messages for this session here
      }
    } catch (error) {
      console.error('Failed to reconnect to session:', error);
    }
  };

  const clearMemory = async () => {
    try {
      await axios.post('http://localhost:5000/clear_memory');
      setMessages([]);
    } catch (error) {
      console.error('Failed to clear memory:', error);
    }
  };

  return (
    <div className="config-interface">
      <h2>Configuration</h2>
      <h3>Start New Session</h3>
      <select value={aiProvider} onChange={(e) => setAiProvider(e.target.value)}>
        {aiProviders.map((provider) => (
          <option key={provider} value={provider}>
            {provider}
          </option>
        ))}
      </select>
      <select value={strength} onChange={(e) => setStrength(e.target.value)}>
        {strengths.map((str) => (
          <option key={str} value={str}>
            {str}
          </option>
        ))}
      </select>
      <textarea
        value={systemMessage}
        onChange={(e) => setSystemMessage(e.target.value)}
        placeholder="System Message"
      />
      <button onClick={startChatSession}>Start New Chat Session</button>
      
      <h3>Existing Sessions</h3>
      <select value={selectedSession} onChange={(e) => setSelectedSession(e.target.value)}>
        <option value="">Select a session</option>
        {existingSessions.map((session) => (
          <option key={session.id} value={session.id}>
            {session.id} - {new Date(session.created_at).toLocaleString()}
          </option>
        ))}
      </select>
      <button onClick={reconnectToSession}>Reconnect to Session</button>
      
      <h3>Memory Management</h3>
      <button onClick={clearMemory}>Clear Memory</button>
    </div>
  );
}

export default ConfigInterface;
