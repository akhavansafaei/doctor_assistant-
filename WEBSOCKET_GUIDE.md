# WebSocket Streaming Chat Guide

Real-time streaming chat with token-by-token generation for the AI Doctor Chatbot.

---

## Overview

The WebSocket implementation provides:
- **Real-time token streaming** - See AI responses as they're generated
- **Live status updates** - Track agent workflow progress
- **Emergency detection** - Instant emergency notifications
- **Bidirectional communication** - Interactive conversation flow
- **Session management** - Persistent conversations across messages

---

## Quick Start

### 1. HTML/JavaScript Client

The easiest way to get started is with the provided HTML client:

```bash
# Open in browser
open examples/websocket_client.html

# Or serve with Python
cd examples
python3 -m http.server 8080
# Then open http://localhost:8080/websocket_client.html
```

### 2. Python Client

Interactive command-line client:

```bash
# Interactive mode
python examples/websocket_client.py

# Quick question
python examples/websocket_client.py "I have a headache and fever"
```

---

## WebSocket Protocol

### Connection

```
ws://localhost:8000/api/v1/ws/chat
```

### Message Types

#### 1. Client → Server

```json
{
    "message": "I have a persistent cough",
    "session_id": "optional-session-id",
    "enable_agents": true,
    "patient_profile": {
        "age": 30,
        "chronic_conditions": []
    }
}
```

#### 2. Server → Client

**Connection Confirmation:**
```json
{
    "type": "connection",
    "status": "connected",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

**Stream Start:**
```json
{
    "type": "stream_start",
    "timestamp": "2024-01-15T10:30:01Z",
    "metadata": {
        "workflow": "multi_agent",
        "agents": ["triage", "diagnostic", "treatment"]
    }
}
```

**Token (Streaming):**
```json
{
    "type": "token",
    "content": "Based",
    "timestamp": "2024-01-15T10:30:01.100Z"
}
```

**Status Update:**
```json
{
    "type": "status",
    "status": "running_diagnostic",
    "details": {
        "current_agent": "diagnostic"
    },
    "timestamp": "2024-01-15T10:30:05Z"
}
```

**Stream End:**
```json
{
    "type": "stream_end",
    "timestamp": "2024-01-15T10:30:15Z",
    "metadata": {
        "agents_completed": ["triage", "diagnostic", "treatment"],
        "session_id": "550e8400-e29b-41d4-a716-446655440000"
    }
}
```

**Error:**
```json
{
    "type": "error",
    "error_type": "validation_error",
    "message": "Message cannot be empty",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## JavaScript Example

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/chat');

ws.onopen = () => {
    console.log('Connected!');
};

// Handle incoming messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    switch (data.type) {
        case 'connection':
            console.log('Session ID:', data.session_id);
            break;

        case 'stream_start':
            console.log('Response started...');
            document.getElementById('response').textContent = '';
            break;

        case 'token':
            // Append token in real-time
            const responseDiv = document.getElementById('response');
            responseDiv.textContent += data.content;
            break;

        case 'stream_end':
            console.log('Response complete!');
            break;

        case 'status':
            console.log('Status:', data.status);
            break;

        case 'error':
            console.error('Error:', data.message);
            break;
    }
};

// Send message
function sendMessage(message) {
    ws.send(JSON.stringify({
        message: message,
        enable_agents: true
    }));
}

// Example usage
sendMessage("I have a fever and sore throat");
```

---

## Python Example

```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8000/api/v1/ws/chat"

    async with websockets.connect(uri) as websocket:
        # Wait for connection
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Connected! Session: {data['session_id']}")

        # Send message
        await websocket.send(json.dumps({
            "message": "I have chest pain",
            "enable_agents": True
        }))

        # Receive streaming response
        print("AI Doctor: ", end="", flush=True)

        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "token":
                print(data["content"], end="", flush=True)

            elif data["type"] == "stream_end":
                print("\n")
                break

            elif data["type"] == "error":
                print(f"\nError: {data['message']}")
                break

asyncio.run(chat())
```

---

## React Example

```jsx
import React, { useState, useEffect, useRef } from 'react';

function ChatBot() {
    const [messages, setMessages] = useState([]);
    const [currentResponse, setCurrentResponse] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const wsRef = useRef(null);

    useEffect(() => {
        // Connect to WebSocket
        const ws = new WebSocket('ws://localhost:8000/api/v1/ws/chat');

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'stream_start') {
                setIsStreaming(true);
                setCurrentResponse('');
            }
            else if (data.type === 'token') {
                setCurrentResponse(prev => prev + data.content);
            }
            else if (data.type === 'stream_end') {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: currentResponse
                }]);
                setCurrentResponse('');
                setIsStreaming(false);
            }
        };

        wsRef.current = ws;

        return () => ws.close();
    }, []);

    const sendMessage = (message) => {
        wsRef.current.send(JSON.stringify({
            message: message,
            enable_agents: true
        }));

        setMessages(prev => [...prev, {
            role: 'user',
            content: message
        }]);
    };

    return (
        <div className="chatbot">
            <div className="messages">
                {messages.map((msg, i) => (
                    <div key={i} className={msg.role}>
                        {msg.content}
                    </div>
                ))}
                {isStreaming && (
                    <div className="assistant streaming">
                        {currentResponse}
                        <span className="cursor">|</span>
                    </div>
                )}
            </div>
            <input
                type="text"
                onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                        sendMessage(e.target.value);
                        e.target.value = '';
                    }
                }}
            />
        </div>
    );
}
```

---

## Status Messages

The WebSocket sends status updates during processing:

| Status | Description |
|--------|-------------|
| `validating` | Validating user input |
| `checking_emergency` | Checking for emergency conditions |
| `processing` | General processing |
| `retrieving_context` | Fetching medical knowledge |
| `generating_response` | LLM is generating response |
| `running_triage` | Triage agent assessing severity |
| `running_diagnostic` | Diagnostic agent analyzing symptoms |
| `running_treatment` | Treatment agent preparing recommendations |

---

## Error Handling

```javascript
ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = (event) => {
    if (event.wasClean) {
        console.log('Connection closed cleanly');
    } else {
        console.error('Connection died');
        // Attempt reconnection
        setTimeout(connect, 5000);
    }
};
```

---

## Advanced Features

### With User Authentication

```
ws://localhost:8000/api/v1/ws/chat/{user_id}
```

This endpoint automatically loads the user's health profile.

### Context Passing

Include patient profile for personalized responses:

```json
{
    "message": "I'm feeling dizzy",
    "patient_profile": {
        "age": 45,
        "chronic_conditions": ["diabetes", "hypertension"],
        "current_medications": [
            {"name": "Metformin", "dose": "1000mg"}
        ],
        "allergies": {
            "drug": ["penicillin"]
        }
    }
}
```

### Session Continuity

Provide `session_id` to continue a previous conversation:

```json
{
    "message": "The pain is now worse",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Performance Tips

### Client-Side

1. **Batch UI Updates**: Don't update DOM for every token
   ```javascript
   let buffer = '';
   let updateTimer;

   ws.onmessage = (event) => {
       const data = JSON.parse(event.data);
       if (data.type === 'token') {
           buffer += data.content;

           clearTimeout(updateTimer);
           updateTimer = setTimeout(() => {
               updateUI(buffer);
               buffer = '';
           }, 100);
       }
   };
   ```

2. **Connection Pooling**: Reuse WebSocket connections

3. **Reconnection Strategy**: Implement exponential backoff

### Server-Side

The server automatically:
- Streams tokens as they're generated
- Sends compressed messages when possible
- Manages connection lifecycle

---

## Security Considerations

1. **Authentication**: Implement token-based auth for production
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/api/v1/ws/chat', {
       headers: {
           'Authorization': `Bearer ${token}`
       }
   });
   ```

2. **Rate Limiting**: Server implements rate limiting per connection

3. **Input Validation**: All messages are validated before processing

4. **CORS**: Configure allowed origins in `.env`

---

## Debugging

### Enable Detailed Logging

```javascript
ws.onmessage = (event) => {
    console.log('Received:', event.data);
    // ... handle message
};

ws.send = function(data) {
    console.log('Sending:', data);
    WebSocket.prototype.send.call(this, data);
};
```

### Check Connection State

```javascript
console.log('WebSocket state:', ws.readyState);
// 0: CONNECTING
// 1: OPEN
// 2: CLOSING
// 3: CLOSED
```

### Monitor Network

Use browser DevTools Network tab → WS tab to see WebSocket frames.

---

## Production Deployment

### Nginx Configuration

```nginx
location /api/v1/ws/ {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;

    # Timeouts
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
}
```

### SSL/TLS

```javascript
const ws = new WebSocket('wss://your-domain.com/api/v1/ws/chat');
```

---

## Testing

```bash
# Test with websocat
websocat ws://localhost:8000/api/v1/ws/chat

# Send message
{"message": "I have a fever", "enable_agents": true}
```

---

## Troubleshooting

### Connection Refused

- Ensure backend is running: `docker-compose up -d`
- Check port 8000 is accessible
- Verify WebSocket endpoint in code

### No Response

- Check server logs: `docker-compose logs -f backend`
- Verify message format is correct
- Check enable_agents is true

### Broken Streaming

- Ensure LLM supports streaming (set in agent initialization)
- Check callback handlers are properly configured
- Verify network isn't buffering WebSocket frames

---

## Examples Directory

- `examples/websocket_client.html` - Full-featured web client
- `examples/websocket_client.py` - Python CLI client
- `examples/react_chat.jsx` - React component (coming soon)

---

**For more information, see [README.md](./README.md) or [API Documentation](http://localhost:8000/api/docs)**
