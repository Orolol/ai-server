import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ConfigInterface({ chatSessionId, setChatSessionId, setMessages }) {
  const [aiProviders, setAiProviders] = useState([]);
  const [aiProvider, setAiProvider] = useState('');
  const [systemMessage, setSystemMessage] = useState('');
  const [existingSessions, setExistingSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sessionInfo, setSessionInfo] = useState({
    chatsessionsid: null,
    creation_date: null,
    strong_model: null,
    weak_model: null,
    ai_provider: null,
    system_message: null
  });

  useEffect(() => {
    fetchConfigOptions();
    fetchExistingSessions();
    if (chatSessionId) {
      fetchSessionInfo();
    }
  }, [chatSessionId]);

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
      if (JSON.stringify(response.data.sessions) !== JSON.stringify(existingSessions)) {
        setExistingSessions(response.data.sessions);
      }
    } catch (error) {
      console.error('Failed to fetch existing sessions:', error);
      setError('Failed to fetch existing sessions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchSessionInfo = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/session_info/${chatSessionId}`);
      setSessionInfo(response.data);
    } catch (error) {
      console.error('Failed to fetch session info:', error);
    }
  };

  const startChatSession = async () => {
    try {
      const response = await axios.post('http://localhost:5000/start_chat', {
        ai_provider: aiProvider,
        system_message: systemMessage
      });

      if (response.data.chatsessionsid) {
        setChatSessionId(response.data.chatsessionsid);
        setMessages([]);
        setSessionInfo({
          chatsessionsid: response.data.chatsessionsid,
          creation_date: response.data.creation_date,
          strong_model: response.data.strong_model,
          weak_model: response.data.weak_model,
          ai_provider: aiProvider,
          system_message: systemMessage
        });
      }
    } catch (error) {
      console.error('Failed to start chat session:', error);
      setError('Failed to start chat session. Please try again.');
    }
  };

  const reconnectToSession = async () => {
    if (!selectedSession) return;
    try {
      const response = await axios.get(`http://localhost:5000/load_session/${selectedSession}`);
      if (response.data.chatsessionsid) {
        setChatSessionId(response.data.chatsessionsid);
        fetchSessionInfo();
        // Fetch messages for this session
        const messagesResponse = await axios.get(`http://localhost:5000/get_messages/${response.data.chatsessionsid}`);
        setMessages(messagesResponse.data.messages);
      }
    } catch (error) {
      console.error('Failed to reconnect to session:', error);
      setError('Failed to reconnect to session. Please try again.');
    }
  };

  const clearMemory = async () => {
    try {
      await axios.post('http://localhost:5000/clear_memory');
      setMessages([]);
      setChatSessionId(null);
      setSessionInfo(null);
    } catch (error) {
      console.error('Failed to clear memory:', error);
      setError('Failed to clear memory. Please try again.');
    }
  };

  const endSession = async () => {
    try {
      await axios.post(`http://localhost:5000/end_session/${chatSessionId}`);
      setChatSessionId(null);
      setMessages([]);
      setSessionInfo(null);
    } catch (error) {
      console.error('Failed to end session:', error);
      setError('Failed to end session. Please try again.');
    }
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
              <p>Created At: {new Date(sessionInfo.creation_date).toLocaleString()}</p>
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
              <button onClick={startChatSession}>Start New Chat Session</button>
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
              <button onClick={reconnectToSession}>Reconnect to Session</button>
            </>
          )}
        </>
      )}
    </div>
  );
}

export default ConfigInterface;
