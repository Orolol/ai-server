import React, { useState } from 'react';
import axios from 'axios';

function ConfigInterface({ setChatSessionId, setMessages }) {
  const [aiProvider, setAiProvider] = useState('openai');
  const [strength, setStrength] = useState('weak');
  const [systemMessage, setSystemMessage] = useState('');

  const startChatSession = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/chat/start', {
        ai_provider: aiProvider,
        strength: strength,
        system_message: systemMessage
      });

      if (response.data.session_id) {
        setChatSessionId(response.data.session_id);
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to start chat session:', error);
    }
  };

  const clearMemory = async () => {
    try {
      await axios.post('http://localhost:5000/api/memory/clear');
      setMessages([]);
    } catch (error) {
      console.error('Failed to clear memory:', error);
    }
  };

  return (
    <div className="config-interface">
      <h2>Configuration</h2>
      <select value={aiProvider} onChange={(e) => setAiProvider(e.target.value)}>
        <option value="openai">OpenAI</option>
        <option value="anthropic">Anthropic</option>
        <option value="huggingface">HuggingFace</option>
      </select>
      <select value={strength} onChange={(e) => setStrength(e.target.value)}>
        <option value="weak">Weak</option>
        <option value="medium">Medium</option>
        <option value="strong">Strong</option>
      </select>
      <textarea
        value={systemMessage}
        onChange={(e) => setSystemMessage(e.target.value)}
        placeholder="System Message"
      />
      <button onClick={startChatSession}>Start Chat Session</button>
      <button onClick={clearMemory}>Clear Memory</button>
    </div>
  );
}

export default ConfigInterface;
