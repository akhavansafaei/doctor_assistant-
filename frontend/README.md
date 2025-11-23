# AI Doctor Chatbot - Frontend

Modern React + TypeScript + Tailwind CSS frontend for the AI Doctor Chatbot.

## Features

- ✅ **Full Authentication**: Login, Signup, Forgot Password, Reset Password
- ✅ **ChatGPT-Style Interface**: Real-time streaming chat with WebSocket
- ✅ **User Profile**: Complete health profile management
- ✅ **Settings**: Customizable user preferences
- ✅ **Chat History**: Sidebar with all conversations
- ✅ **Responsive Design**: Mobile, tablet, and desktop support
- ✅ **Dark Mode Ready**: Theme support built-in
- ✅ **Real-time Streaming**: Token-by-token response streaming
- ✅ **Emergency Detection**: Visual alerts for critical conditions

## Tech Stack

- **React 18** with TypeScript
- **Vite** for blazing fast development
- **Tailwind CSS** for styling
- **Zustand** for state management
- **React Router** for navigation
- **Axios** for HTTP requests
- **WebSocket** for real-time chat
- **React Hot Toast** for notifications
- **Lucide React** for icons
- **Framer Motion** for animations

## Quick Start

```bash
# Install dependencies
cd frontend
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev

# Open http://localhost:3000
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── chat/           # Chat-specific components
│   │   ├── ui/             # Generic UI components
│   │   └── layout/         # Layout components
│   ├── pages/              # Page components
│   │   ├── auth/           # Authentication pages
│   │   ├── ChatPage.tsx    # Main chat interface
│   │   ├── ProfilePage.tsx # User profile
│   │   └── SettingsPage.tsx# Settings
│   ├── stores/             # Zustand stores
│   │   ├── authStore.ts    # Authentication state
│   │   └── chatStore.ts    # Chat state
│   ├── services/           # API services
│   │   ├── api.ts          # REST API client
│   │   └── websocket.ts    # WebSocket client
│   ├── hooks/              # Custom React hooks
│   │   └── useWebSocket.ts # WebSocket hook
│   ├── types/              # TypeScript types
│   │   └── index.ts        # All type definitions
│   ├── utils/              # Utility functions
│   ├── App.tsx             # Main app component
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── public/                 # Static assets
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Key Features Implementation

### Authentication

```typescript
// Login
import { useAuthStore } from '@/stores/authStore';

const { login } = useAuthStore();
await login({ username, password });

// Check auth status
const { isAuthenticated, user } = useAuthStore();
```

### Real-time Chat

```typescript
// Use WebSocket hook
import { useWebSocket } from '@/hooks/useWebSocket';

const { sendMessage, isConnected } = useWebSocket();

// Send message
sendMessage("I have a headache");

// Messages are automatically streamed to the chat
```

### Profile Management

```typescript
// Update health profile
import { useAuthStore } from '@/stores/authStore';

const { updateHealthProfile } = useAuthStore();
await updateHealthProfile({
  height_cm: 175,
  chronic_conditions: ['diabetes'],
});
```

## Pages

### Login Page (`/login`)
- Email/username and password fields
- Remember me option
- Link to signup and forgot password
- Form validation

### Signup Page (`/signup`)
- Full name, email, username, password
- Password strength indicator
- Terms and conditions
- Auto-login after signup

### Forgot Password (`/forgot-password`)
- Email input for password reset
- Email verification
- Reset link sent notification

### Chat Page (`/chat`)
- Main chat interface
- Sidebar with conversation history
- Real-time streaming responses
- Emergency detection alerts
- Message formatting (Markdown support)
- Source citations

### Profile Page (`/profile`)
- Personal information
- Health profile (height, weight, blood type)
- Medical history
- Chronic conditions
- Allergies (drug, food, environmental)
- Current medications
- Past surgeries
- Emergency contact

### Settings Page (`/settings`)
- Theme selection (light/dark/auto)
- Notification preferences
- Sound settings
- Auto-play responses
- Show/hide sources
- Enable/disable AI agents
- Account management
- Privacy settings

## Components

### Chat Components

- **ChatInterface**: Main chat UI
- **MessageList**: Displays all messages
- **MessageBubble**: Individual message bubble
- **StreamingMessage**: Real-time token streaming
- **MessageInput**: Text input with send button
- **Sidebar**: Conversation history
- **EmergencyAlert**: Critical condition warnings

### UI Components

- **Button**: Customizable button
- **Input**: Form input field
- **Card**: Container component
- **Modal**: Dialog/popup
- **Avatar**: User avatar
- **Badge**: Status badges
- **Spinner**: Loading indicator
- **Toast**: Notifications

## Styling

Using Tailwind CSS with custom theme:

```javascript
// tailwind.config.js
theme: {
  extend: {
    colors: {
      primary: { /* purple shades */ },
    },
  },
}
```

## State Management

### Auth Store (Zustand)

```typescript
interface AuthState {
  user: User | null;
  healthProfile: HealthProfile | null;
  isAuthenticated: boolean;
  login: (credentials) => Promise<void>;
  logout: () => Promise<void>;
  updateHealthProfile: (data) => Promise<void>;
}
```

### Chat Store (Zustand)

```typescript
interface ChatState {
  conversations: Conversation[];
  messages: Message[];
  isStreaming: boolean;
  sendMessage: (content: string) => void;
  startStreaming: () => void;
  appendToStream: (token: string) => void;
}
```

## WebSocket Integration

```typescript
// Automatic reconnection
// Token streaming
// Status updates
// Error handling
// Session management
```

## Responsive Design

- Mobile-first approach
- Breakpoints: sm, md, lg, xl, 2xl
- Collapsible sidebar on mobile
- Touch-friendly UI elements
- Optimized for all screen sizes

## Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

## Environment Variables

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/api/v1/ws/chat
```

## Deployment

```bash
# Build production bundle
npm run build

# Deploy to Vercel/Netlify/etc
# The dist/ folder contains the static files
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Code splitting
- Lazy loading
- Optimized bundles
- WebSocket connection pooling
- Efficient state updates

## Accessibility

- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support
- Focus management

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](../LICENSE)
