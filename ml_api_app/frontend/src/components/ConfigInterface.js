import React, { useState } from 'react';
import axios from 'axios';

function ConfigInterface({ setChatSessionId, setMessages }) {
  const [aiProvider, setAiProvider] = useState('openai');
  const [temperature, setTemperature] = useState(0.7);
  const [maxLength, setMaxLength] = useState(1024);
  const [systemMessage, setSystemMessage] = useState('');

  const startChatSession = async () => {
    try {
      const response = await axios.post('http://localhost:5000/start_chat', {
        ai_provider: aiProvider,
        temperature,
        max_length: maxLength,
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
      <select value={aiProvider} onChange={(e) => setAiProvider(e.target.value)}>
        <option value="openai">OpenAI</option>
        <option value="anthropic">Anthropic</option>
      </select>
      <input
        type="range"
        min="0"
        max="1"
        step="0.1"
        value={temperature}
        onChange={(e) => setTemperature(parseFloat(e.target.value))}
      />
      <input
        type="number"
        value={maxLength}
        onChange={(e) => setMaxLength(parseInt(e.target.value))}
      />
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
