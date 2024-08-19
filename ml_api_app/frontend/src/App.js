import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import ConfigInterface from './components/ConfigInterface';
import MemoryInterface from './components/MemoryInterface';
import WebInterface from './components/WebInterface';
import './App.css';

function App() {
  const [chatSessionId, setChatSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [activeTab, setActiveTab] = useState('config');

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'config':
        return (
          <ConfigInterface
            setChatSessionId={setChatSessionId}
            setMessages={setMessages}
          />
        );
      case 'memory':
        return <MemoryInterface />;
      case 'web':
        return <WebInterface chatSessionId={chatSessionId} />;
      default:
        return null;
    }
  };

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
        <div className="right-panel">
          <div className="tab-container">
            <button className={`tab ${activeTab === 'config' ? 'active' : ''}`} onClick={() => setActiveTab('config')}>Config</button>
            <button className={`tab ${activeTab === 'memory' ? 'active' : ''}`} onClick={() => setActiveTab('memory')}>Memory</button>
            <button className={`tab ${activeTab === 'web' ? 'active' : ''}`} onClick={() => setActiveTab('web')}>Web</button>
          </div>
          <div className="tab-content">
            {renderActiveTab()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
