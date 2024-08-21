import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import ConfigInterface from './components/ConfigInterface';
import MemoryInterface from './components/MemoryInterface';
import WebInterface from './components/WebInterface';
import useChatSessionStore from './store/chatSessionStore';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('config');
  const { chatSessionId, fetchMessages } = useChatSessionStore();

  useEffect(() => {
    if (chatSessionId) {
      fetchMessages();
    }
  }, [chatSessionId, fetchMessages]);

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'config':
        return <ConfigInterface />;
      case 'memory':
        return <MemoryInterface />;
      case 'web':
        return <WebInterface />;
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
          <ChatInterface />
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
