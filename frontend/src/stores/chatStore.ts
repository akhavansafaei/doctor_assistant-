import { create } from 'zustand';
import { Message, Conversation } from '@/types';
import { v4 as uuidv4 } from 'uuid';

interface ChatState {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  isStreaming: boolean;
  currentStreamingMessage: string;
  isConnected: boolean;

  // Actions
  setConversations: (conversations: Conversation[]) => void;
  setCurrentConversation: (conversation: Conversation | null) => void;
  addMessage: (message: Message) => void;
  updateMessage: (id: string, content: string, metadata?: any) => void;
  startStreaming: () => void;
  appendToStream: (content: string) => void;
  endStreaming: (metadata?: any) => void;
  setConnected: (connected: boolean) => void;
  clearMessages: () => void;
  newConversation: () => void;
  deleteConversation: (id: string) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  currentConversation: null,
  messages: [],
  isStreaming: false,
  currentStreamingMessage: '',
  isConnected: false,

  setConversations: (conversations) => set({ conversations }),

  setCurrentConversation: (conversation) => {
    set({ currentConversation: conversation, messages: [] });
  },

  addMessage: (message) => {
    set((state) => ({
      messages: [...state.messages, message],
    }));

    // Update conversation
    if (get().currentConversation) {
      const updated: Conversation = {
        ...get().currentConversation!,
        message_count: get().messages.length,
        last_message: message.content.substring(0, 100),
        updated_at: new Date(),
      };
      set({ currentConversation: updated });

      // Update in conversations list
      set((state) => ({
        conversations: state.conversations.map((conv) =>
          conv.id === updated.id ? updated : conv
        ),
      }));
    }
  },

  updateMessage: (id, content, metadata) => {
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, content, metadata } : msg
      ),
    }));
  },

  startStreaming: () => {
    set({ isStreaming: true, currentStreamingMessage: '' });

    // Add empty message that will be filled
    const streamMessage: Message = {
      id: uuidv4(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      streaming: true,
    };

    set((state) => ({
      messages: [...state.messages, streamMessage],
    }));
  },

  appendToStream: (content) => {
    set((state) => ({
      currentStreamingMessage: state.currentStreamingMessage + content,
    }));

    // Update the last message
    set((state) => ({
      messages: state.messages.map((msg, index) =>
        index === state.messages.length - 1 && msg.streaming
          ? { ...msg, content: msg.content + content }
          : msg
      ),
    }));
  },

  endStreaming: (metadata) => {
    set({ isStreaming: false, currentStreamingMessage: '' });

    // Mark message as not streaming
    set((state) => ({
      messages: state.messages.map((msg, index) =>
        index === state.messages.length - 1
          ? { ...msg, streaming: false, metadata }
          : msg
      ),
    }));
  },

  setConnected: (connected) => set({ isConnected: connected }),

  clearMessages: () => set({ messages: [] }),

  newConversation: () => {
    const newConv: Conversation = {
      id: uuidv4(),
      session_id: uuidv4(),
      title: 'New Conversation',
      created_at: new Date(),
      updated_at: new Date(),
      message_count: 0,
    };

    set((state) => ({
      conversations: [newConv, ...state.conversations],
      currentConversation: newConv,
      messages: [],
    }));
  },

  deleteConversation: (id) => {
    set((state) => ({
      conversations: state.conversations.filter((conv) => conv.id !== id),
    }));

    // If deleted conversation was current, clear it
    if (get().currentConversation?.id === id) {
      set({ currentConversation: null, messages: [] });
    }
  },
}));
