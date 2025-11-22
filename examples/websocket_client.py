#!/usr/bin/env python3
"""
Python WebSocket client for AI Doctor Chatbot
Demonstrates real-time streaming chat
"""
import asyncio
import websockets
import json
import sys
from datetime import datetime


class DoctorChatbotClient:
    """WebSocket client for AI Doctor Chatbot"""

    def __init__(self, url="ws://localhost:8000/api/v1/ws/chat"):
        self.url = url
        self.websocket = None
        self.session_id = None
        self.current_response = []

    async def connect(self):
        """Connect to WebSocket server"""
        print(f"Connecting to {self.url}...")
        self.websocket = await websockets.connect(self.url)
        print("✓ Connected!")

        # Wait for connection confirmation
        response = await self.websocket.recv()
        data = json.loads(response)

        if data.get("type") == "connection":
            self.session_id = data.get("session_id")
            print(f"✓ Session established: {self.session_id}\n")

    async def send_message(self, message, enable_agents=True):
        """Send a message to the chatbot"""
        if not self.websocket:
            raise Exception("Not connected")

        # Send message
        await self.websocket.send(json.dumps({
            "message": message,
            "session_id": self.session_id,
            "enable_agents": enable_agents
        }))

        print(f"\n[You]: {message}\n")
        print("[AI Doctor]: ", end="", flush=True)

        self.current_response = []
        is_streaming = False

        # Receive and process responses
        async for response in self.websocket:
            data = json.loads(response)
            message_type = data.get("type")

            if message_type == "stream_start":
                is_streaming = True
                if data.get("metadata", {}).get("emergency"):
                    print("\n🚨 EMERGENCY DETECTED 🚨\n", end="", flush=True)

            elif message_type == "token":
                # Print token in real-time
                token = data.get("content", "")
                print(token, end="", flush=True)
                self.current_response.append(token)

            elif message_type == "stream_end":
                print("\n")  # New line after streaming
                is_streaming = False
                break

            elif message_type == "status":
                status = data.get("status", "")
                details = data.get("details", {})
                self._print_status(status, details)

            elif message_type == "error":
                print(f"\n❌ Error: {data.get('message')}\n")
                break

            elif message_type == "context_retrieved":
                sources = data.get("sources", [])
                self._print_sources(sources)

        return "".join(self.current_response)

    def _print_status(self, status, details):
        """Print status updates"""
        status_icons = {
            "validating": "🔍",
            "checking_emergency": "🚨",
            "processing": "⚙️",
            "retrieving_context": "📚",
            "generating_response": "💬",
            "running_triage": "🏥",
            "running_diagnostic": "🔬",
            "running_treatment": "💊"
        }

        icon = status_icons.get(status, "•")
        agent = details.get("current_agent", "")

        if agent:
            print(f"\n{icon} {status.replace('_', ' ').title()} ({agent})...", flush=True)
        else:
            print(f"\n{icon} {status.replace('_', ' ').title()}...", flush=True)

    def _print_sources(self, sources):
        """Print retrieved medical sources"""
        if sources:
            print("\n📚 Medical Knowledge Sources:")
            for i, source in enumerate(sources[:3], 1):
                text_preview = source.get("text", "")[:100]
                score = source.get("score", 0)
                print(f"  {i}. {text_preview}... (relevance: {score:.2f})")
            print()

    async def interactive_chat(self):
        """Interactive chat loop"""
        print("\n" + "="*60)
        print("🏥 AI Doctor Chatbot - Interactive Chat")
        print("="*60)
        print("\nType 'quit' or 'exit' to end the conversation")
        print("Type 'help' for usage information\n")

        await self.connect()

        while True:
            try:
                # Get user input
                user_input = input("\n[You]: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nGoodbye! Take care of your health! 👋")
                    break

                if user_input.lower() == 'help':
                    self._print_help()
                    continue

                # Send message and get response
                await self.send_message(user_input)

            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Exiting...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                break

        if self.websocket:
            await self.websocket.close()
            print("✓ Connection closed\n")

    def _print_help(self):
        """Print help information"""
        print("\n" + "-"*60)
        print("HELP - How to use the AI Doctor Chatbot:")
        print("-"*60)
        print("""
This is an AI-powered medical assistant that can help you:
• Assess your symptoms
• Provide differential diagnoses
• Suggest treatment options
• Detect emergencies

⚠️  IMPORTANT:
• This is NOT a substitute for professional medical advice
• Always consult a real doctor for medical decisions
• In emergencies, call 911 immediately

Commands:
• Type your symptoms or health questions naturally
• 'quit' or 'exit' - End the conversation
• 'help' - Show this help message

Examples:
• "I have a headache and fever for 2 days"
• "What should I do for a sprained ankle?"
• "I'm experiencing chest pain" (emergency)
        """)
        print("-"*60)

    async def quick_question(self, question):
        """Ask a single question and get response"""
        await self.connect()
        response = await self.send_message(question)
        await self.websocket.close()
        return response


async def main():
    """Main entry point"""
    client = DoctorChatbotClient()

    # Check if question provided as argument
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"\nQuick Question: {question}\n")
        await client.quick_question(question)
    else:
        # Interactive mode
        await client.interactive_chat()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
