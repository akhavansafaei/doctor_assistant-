# Frontend Setup Guide

## What's Been Created

A complete React + TypeScript + Tailwind CSS frontend foundation with:

### ✅ Completed Structure
1. **Project Configuration**
   - Vite + React + TypeScript setup
   - Tailwind CSS with custom theme
   - Path aliases (@/ for src/)
   - ESLint + TypeScript configuration

2. **State Management** (Zustand)
   - `authStore.ts` - Authentication & user management
   - `chatStore.ts` - Chat messages & conversations

3. **Services**
   - `api.ts` - REST API client with interceptors
   - `websocket.ts` - WebSocket client with auto-reconnect

4. **Hooks**
   - `useWebSocket.ts` - WebSocket integration for chat

5. **Types**
   - Complete TypeScript definitions for all entities

6. **Routing**
   - React Router setup with protected routes
   - Authentication flow

## Installation & Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env with your backend URL
# VITE_API_URL=http://localhost:8000
# VITE_WS_URL=ws://localhost:8000/api/v1/ws/chat

# Start development server
npm run dev

# Open http://localhost:3000
```

## Missing Files (To Be Created)

Due to message length constraints, you'll need to create the following page components:

### 1. Authentication Pages

**frontend/src/pages/auth/LoginPage.tsx**
```typescript
// Full login page with form validation
// Email/username + password
// Remember me checkbox
// Links to signup and forgot password
```

**frontend/src/pages/auth/SignupPage.tsx**
```typescript
// Registration form
// Full name, email, username, password
// Password confirmation
// Auto-login after signup
```

**frontend/src/pages/auth/ForgotPasswordPage.tsx**
```typescript
// Password reset request
// Email input
// Send reset link
```

### 2. Main Pages

**frontend/src/pages/ChatPage.tsx**
```typescript
// Main chat interface (ChatGPT-style)
// Sidebar with conversation history
// Chat messages with streaming
// Message input
// Real-time WebSocket integration
```

**frontend/src/pages/ProfilePage.tsx**
```typescript
// User profile management
// Personal info editor
// Health profile form
// Medical history
```

**frontend/src/pages/SettingsPage.tsx**
```typescript
// App settings
// Theme, notifications
// AI agent settings
// Account management
```

### 3. Chat Components

**frontend/src/components/chat/ChatInterface.tsx**
```typescript
// Main chat container
// Layout with sidebar
```

**frontend/src/components/chat/Sidebar.tsx**
```typescript
// Conversation list
// New chat button
// Search conversations
```

**frontend/src/components/chat/MessageList.tsx**
```typescript
// Scrollable message container
// Auto-scroll to bottom
// Loading states
```

**frontend/src/components/chat/MessageBubble.tsx**
```typescript
// Individual message UI
// User vs Assistant styling
// Markdown rendering
// Source citations
```

**frontend/src/components/chat/MessageInput.tsx**
```typescript
// Text input with send button
// Auto-resize textarea
// Keyboard shortcuts
```

**frontend/src/components/chat/StreamingMessage.tsx**
```typescript
// Real-time token streaming display
// Blinking cursor
// Smooth append animation
```

## Quick Component Templates

### Login Page Template

```typescript
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await login({ username, password });
      toast.success('Welcome back!');
      navigate('/chat');
    } catch (error) {
      toast.error('Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-primary-700">
      <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md">
        <h1 className="text-3xl font-bold text-center mb-8">AI Doctor Chatbot</h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="mt-6 text-center space-y-2">
          <Link to="/forgot-password" className="text-primary-600 hover:underline text-sm">
            Forgot password?
          </Link>
          <div>
            <span className="text-gray-600">Don't have an account? </span>
            <Link to="/signup" className="text-primary-600 hover:underline font-semibold">
              Sign up
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### Chat Page Template

```typescript
import { useEffect } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useChatStore } from '@/stores/chatStore';
import Sidebar from '@/components/chat/Sidebar';
import MessageList from '@/components/chat/MessageList';
import MessageInput from '@/components/chat/MessageInput';

export default function ChatPage() {
  const { sendMessage, isConnected } = useWebSocket();
  const { messages, isStreaming } = useChatStore();

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold">AI Doctor Assistant</h1>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-600">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </header>

        {/* Messages */}
        <MessageList messages={messages} isStreaming={isStreaming} />

        {/* Input */}
        <MessageInput onSend={sendMessage} disabled={!isConnected || isStreaming} />
      </div>
    </div>
  );
}
```

## Additional Dependencies Needed

```bash
npm install uuid
npm install @types/uuid --save-dev
```

## Running the Full Stack

```bash
# Terminal 1 - Backend
cd backend
docker-compose up -d

# Terminal 2 - Frontend
cd frontend
npm run dev

# Open http://localhost:3000
```

## Next Steps

1. **Create all page components** using the templates above
2. **Create chat UI components** (MessageBubble, Sidebar, etc.)
3. **Add form validation** using React Hook Form or Formik
4. **Implement responsive design** for mobile/tablet
5. **Add animations** using Framer Motion
6. **Create UI component library** (Button, Input, Modal, etc.)
7. **Add error boundaries** for better error handling
8. **Implement theme switching** (light/dark mode)

## Resources

- **Tailwind Components**: https://tailwindui.com/
- **React Router**: https://reactrouter.com/
- **Zustand Docs**: https://docs.pmnd.rs/zustand/
- **WebSocket Guide**: ../WEBSOCKET_GUIDE.md

## Pro Tips

1. **Use ChatGPT UI as reference** - Study https://chat.openai.com for UX patterns
2. **Mobile-first design** - Start with mobile layout, then expand
3. **Accessibility** - Use semantic HTML and ARIA labels
4. **Performance** - Lazy load components, optimize re-renders
5. **Testing** - Add tests for critical user flows

---

**The foundation is ready! Now build the beautiful UI components and pages.** 🚀
