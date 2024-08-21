import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import useChatSessionStore from '../store/chatSessionStore';
import './ChatInterface.css';

function ChatInterface() {
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { chatSessionId, messages, setMessages } = useChatSessionStore();

  const sendMessage = async () => {
    if (!userInput.trim() || !chatSessionId || isLoading) return;

    setIsLoading(true);
    const currentInput = userInput;
    setUserInput('');

    try {
      const response = await axios.post('http://localhost:5000/send_message', {
        chatsessionsid: chatSessionId,
        message: currentInput
      });

      if (response.data.response) {
        setMessages([
          ...messages,
          { role: 'user', content: currentInput },
          { role: 'AI', content: response.data.response }
        ]);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      // Optionally, you can add error handling UI here
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <div className="message-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <strong>{message.role}:</strong>
            <ReactMarkdown>
              {message.content.replace(/\[INVISIBLE TO USER\][\s\S]*?\[\/INVISIBLE TO USER\]/g, '')}
            </ReactMarkdown>
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
          disabled={isLoading}
        />
        <button onClick={sendMessage} disabled={isLoading}>
          {isLoading ? <span className="spinner"></span> : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default ChatInterface;
