import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import ConfigInterface from './components/ConfigInterface';
import MemoryInterface from './components/MemoryInterface';
import WebInterface from './components/WebInterface';
import './App.css';

function App() {
  const [chatSessionId, setChatSessionId] = useState(null);
  const [messages, setMessages] = useState([]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>ML API Chat Interface</h1>
      </header>
      <div className="main-container">
        <div className="chat-container">
          <ChatInterface
            chatSessionId={chatSessionId}
            messages={messages}
            setMessages={setMessages}
          />
        </div>
        <div className="sidebar">
          <ConfigInterface
            setChatSessionId={setChatSessionId}
            setMessages={setMessages}
          />
          <MemoryInterface />
          <WebInterface chatSessionId={chatSessionId} />
        </div>
      </div>
    </div>
  );
}

export default App;
