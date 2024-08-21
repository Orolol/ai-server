import create from 'zustand';
import axios from 'axios';

const useChatSessionStore = create((set, get) => ({
  chatSessionId: null,
  messages: [],
  sessionInfo: {
    chatsessionsid: null,
    creation_date: null,
    strong_model: null,
    weak_model: null,
    ai_provider: null,
    system_message: null
  },
  setChatSessionId: (id) => set({ chatSessionId: id }),
  setMessages: (messages) => set({ messages }),
  setSessionInfo: (info) => set({ sessionInfo: info }),
  fetchMessages: async () => {
    const { chatSessionId } = get();
    if (chatSessionId) {
      try {
        const response = await axios.get(`http://localhost:5000/get_messages/${chatSessionId}`);
        set({ messages: response.data.messages });
      } catch (error) {
        console.error('Failed to fetch messages:', error);
      }
    }
  },
  fetchSessionInfo: async (sessionId) => {
    try {
      const response = await axios.get(`http://localhost:5000/load_session/${sessionId}`);
      if (response.data.chatsessionsid) {
        set({
          sessionInfo: {
            chatsessionsid: response.data.chatsessionsid,
            creation_date: response.data.creation_date,
            strong_model: response.data.strong_model,
            weak_model: response.data.weak_model,
            ai_provider: response.data.ai_provider,
            system_message: response.data.system_message
          }
        });
      }
    } catch (error) {
      console.error('Failed to fetch session info:', error);
    }
  },
  startChatSession: async (aiProvider, systemMessage) => {
    try {
      const response = await axios.post('http://localhost:5000/start_chat', {
        ai_provider: aiProvider,
        system_message: systemMessage
      });

      if (response.data.chatsessionsid) {
        set({
          chatSessionId: response.data.chatsessionsid,
          messages: [],
          sessionInfo: {
            chatsessionsid: response.data.chatsessionsid,
            creation_date: response.data.creation_date,
            strong_model: response.data.strong_model,
            weak_model: response.data.weak_model,
            ai_provider: aiProvider,
            system_message: systemMessage
          }
        });
      }
    } catch (error) {
      console.error('Failed to start chat session:', error);
    }
  },
  reconnectToSession: async (sessionId) => {
    try {
      const response = await axios.get(`http://localhost:5000/load_session/${sessionId}`);
      if (response.data.chatsessionsid) {
        set({ 
          chatSessionId: response.data.chatsessionsid,
          sessionInfo: {
            chatsessionsid: response.data.chatsessionsid,
            creation_date: response.data.creation_date,
            strong_model: response.data.strong_model,
            weak_model: response.data.weak_model,
            ai_provider: response.data.ai_provider,
            system_message: response.data.system_message
          }
        });
        get().fetchMessages();
      }
    } catch (error) {
      console.error('Failed to reconnect to session:', error);
    }
  },
  clearMemory: async () => {
    try {
      await axios.post('http://localhost:5000/clear_memory');
      set({
        chatSessionId: null,
        messages: [],
        sessionInfo: {
          chatsessionsid: null,
          creation_date: null,
          strong_model: null,
          weak_model: null,
          ai_provider: null,
          system_message: null
        }
      });
    } catch (error) {
      console.error('Failed to clear memory:', error);
    }
  },
  endSession: async () => {
    const { chatSessionId } = get();
    try {
      await axios.post(`http://localhost:5000/end_session/${chatSessionId}`);
      set({
        chatSessionId: null,
        messages: [],
        sessionInfo: {
          chatsessionsid: null,
          creation_date: null,
          strong_model: null,
          weak_model: null,
          ai_provider: null,
          system_message: null
        }
      });
    } catch (error) {
      console.error('Failed to end session:', error);
    }
  }
}));

export default useChatSessionStore;
