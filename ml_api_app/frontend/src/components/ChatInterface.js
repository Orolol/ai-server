import React, { useState } from 'react';
import axios from 'axios';
import useChatSessionStore from '../store/chatSessionStore';
import './ChatInterface.css';

function ChatInterface() {
  const [userInput, setUserInput] = useState('');
  const { chatSessionId, messages, setMessages } = useChatSessionStore();

  const sendMessage = async () => {
    if (!userInput.trim() || !chatSessionId) return;

    try {
      const response = await axios.post('http://localhost:5000/send_message', {
        chatsessionsid: chatSessionId,
        message: userInput
      });

      if (response.data.response) {
        setMessages([
          ...messages,
          { role: 'user', content: userInput },
          { role: 'AI', content: response.data.response }
        ]);
        setUserInput('');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  return (
    <div className="chat-interface">
      <div className="message-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <strong>{message.role}:</strong> {message.content}
          </div>
        ))}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type your message..."
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default ChatInterface;
