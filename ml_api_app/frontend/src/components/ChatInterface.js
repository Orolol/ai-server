import React, { useState } from 'react';
import axios from 'axios';

function ChatInterface({ chatSessionId, messages, setMessages }) {
  const [userInput, setUserInput] = useState('');

  const sendMessage = async () => {
    if (!userInput.trim() || !chatSessionId) return;

    try {
      const response = await axios.post('http://localhost:5000/send_message', {
        chatsessionsid: chatSessionId,
        prompt: userInput
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
            {message.content}
          </div>
        ))}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default ChatInterface;
