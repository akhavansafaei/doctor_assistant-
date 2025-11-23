import { useEffect, useRef, useCallback, useState } from 'react';
import { WSMessage } from '@/types';
import { wsService } from '@/services/websocket';
import { useChatStore } from '@/stores/chatStore';
import { useAuthStore } from '@/stores/authStore';
import toast from 'react-hot-toast';
import { v4 as uuidv4 } from 'uuid';

export function useWebSocket() {
  const {
    addMessage,
    startStreaming,
    appendToStream,
    endStreaming,
    setConnected,
    isConnected,
  } = useChatStore();

  const { loadHealthProfile } = useAuthStore();
  const sessionIdRef = useRef<string | null>(null);
  const [isOnboarding, setIsOnboarding] = useState(false);

  useEffect(() => {
    // Connect to WebSocket
    wsService.connect()
      .then((sessionId) => {
        sessionIdRef.current = sessionId;
        console.log('WebSocket connected with session:', sessionId);
      })
      .catch((error) => {
        console.error('WebSocket connection failed:', error);
        toast.error('Failed to connect to chat server');
      });

    // Handle connection changes
    const unsubscribeConnection = wsService.onConnectionChange((connected) => {
      setConnected(connected);
      if (!connected) {
        toast.error('Disconnected from server. Reconnecting...');
      }
    });

    // Handle messages
    const unsubscribeMessages = wsService.onMessage((message: WSMessage) => {
      handleWebSocketMessage(message);
    });

    // Cleanup on unmount
    return () => {
      unsubscribeConnection();
      unsubscribeMessages();
      wsService.disconnect();
    };
  }, []);

  const handleWebSocketMessage = useCallback((message: WSMessage) => {
    switch (message.type) {
      case 'connection':
        console.log('Connected:', message.session_id);
        break;

      case 'onboarding_question':
        // Onboarding flow started - show question as assistant message
        setIsOnboarding(true);
        addMessage({
          id: uuidv4(),
          role: 'assistant',
          content: message.question || message.content || '',
          timestamp: new Date(),
        });
        toast('💬 Profile onboarding started', { icon: '👋' });
        break;

      case 'onboarding_complete':
        // Onboarding finished
        setIsOnboarding(false);
        toast.success('🎉 Health profile completed! Your advice will now be personalized.', {
          duration: 5000,
        });
        // Refresh the health profile
        if (loadHealthProfile) {
          loadHealthProfile();
        }
        break;

      case 'profile_saved':
        // Profile has been saved
        console.log('Profile saved successfully');
        if (loadHealthProfile) {
          loadHealthProfile();
        }
        break;

      case 'stream_start':
        startStreaming();
        if (message.metadata?.emergency) {
          toast.error('🚨 EMERGENCY DETECTED', {
            duration: 10000,
          });
        }
        break;

      case 'token':
        if (message.content) {
          appendToStream(message.content);
        }
        break;

      case 'stream_end':
        endStreaming(message.metadata);
        break;

      case 'status':
        // Show status in UI (optional)
        console.log('Status:', message.status, message.details);
        break;

      case 'error':
        endStreaming();
        toast.error(message.message || 'An error occurred');
        break;

      case 'context_retrieved':
        // Sources retrieved
        console.log('Sources:', message.sources);
        break;
    }
  }, [startStreaming, appendToStream, endStreaming, addMessage, loadHealthProfile]);

  const sendMessage = useCallback((content: string, enableAgents = true) => {
    try {
      // Add user message to chat
      addMessage({
        id: uuidv4(),
        role: 'user',
        content,
        timestamp: new Date(),
      });

      // Send via WebSocket
      wsService.sendMessage(content, sessionIdRef.current || undefined, enableAgents);
    } catch (error) {
      console.error('Failed to send message:', error);
      toast.error('Failed to send message');
    }
  }, [addMessage]);

  return {
    sendMessage,
    isConnected,
    isOnboarding,
    sessionId: sessionIdRef.current,
  };
}
