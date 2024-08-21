import React, { useState, useEffect } from 'react';
import axios from 'axios';
import useChatSessionStore from '../store/chatSessionStore';

function ConfigInterface() {
  const [aiProviders, setAiProviders] = useState([]);
  const [aiProvider, setAiProvider] = useState('');
  const [systemMessage, setSystemMessage] = useState('');
  const [existingSessions, setExistingSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const {
    chatSessionId,
    sessionInfo,
    startChatSession,
    reconnectToSession,
    clearMemory,
    endSession,
    fetchSessionInfo
  } = useChatSessionStore();

  useEffect(() => {
    fetchConfigOptions();
    if (chatSessionId) {
      fetchSessionInfo(chatSessionId);
    } else {
      fetchExistingSessions();
    }
  }, [chatSessionId, fetchSessionInfo]);

  const fetchConfigOptions = async () => {
    if (aiProviders.length === 0) {
      setLoading(true);
      setError('');
      try {
        const response = await axios.get('http://localhost:5000/config_options');
        setAiProviders(response.data.ai_providers);
        setAiProvider(response.data.ai_providers[0]);
      } catch (error) {
        console.error('Failed to fetch configuration options:', error);
        setError('Failed to fetch configuration options. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  const fetchExistingSessions = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get('http://localhost:5000/list_sessions');
      setExistingSessions(response.data.sessions);
    } catch (error) {
      console.error('Failed to fetch existing sessions:', error);
      setError('Failed to fetch existing sessions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStartChatSession = () => {
    startChatSession(aiProvider, systemMessage);
  };

  const handleReconnectToSession = () => {
    if (!selectedSession) return;
    reconnectToSession(selectedSession);
  };

  return (
    <div className="config-interface">
      <h2>Configuration</h2>
      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && (
        <>
          {chatSessionId ? (
            <div>
              <h3>Current Session</h3>
              <p>Session ID: {sessionInfo.chatsessionsid}</p>
              <p>AI Provider: {sessionInfo.ai_provider}</p>
              <p>Created At: {sessionInfo.creation_date ? new Date(sessionInfo.creation_date).toLocaleString() : 'N/A'}</p>
              <p>System Message: {sessionInfo.system_message}</p>
              <p>Strong Model: {sessionInfo.strong_model}</p>
              <p>Weak Model: {sessionInfo.weak_model}</p>
              <button onClick={endSession}>End Session</button>
              <button onClick={clearMemory}>Clear Memory</button>
            </div>
          ) : (
            <div>
              <h3>Start New Session</h3>
              <select value={aiProvider} onChange={(e) => setAiProvider(e.target.value)}>
                {aiProviders.map((provider) => (
                  <option key={provider} value={provider}>
                    {provider}
                  </option>
                ))}
              </select>
              <textarea
                value={systemMessage}
                onChange={(e) => setSystemMessage(e.target.value)}
                placeholder="System Message"
              />
              <button onClick={handleStartChatSession}>Start New Chat Session</button>
            </div>
          )}
          
          {!chatSessionId && (
            <>
              <h3>Existing Sessions</h3>
              <select value={selectedSession} onChange={(e) => setSelectedSession(e.target.value)}>
                <option value="">Select a session</option>
                {existingSessions.map((session) => (
                  <option key={session.id} value={session.id}>
                    {session.id} - {new Date(session.created_at).toLocaleString()}
                  </option>
                ))}
              </select>
              <button onClick={handleReconnectToSession}>Reconnect to Session</button>
            </>
          )}
        </>
      )}
    </div>
  );
}

export default ConfigInterface;
