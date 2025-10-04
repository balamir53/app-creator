"""
Example usage of the LangGraph FastAPI integration with Azure OpenAI

This script demonstrates how to use the LangGraph endpoints
Make sure to set your Azure OpenAI credentials in the .env file first!

Required environment variables:
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_ENDPOINT
- OPENAI_API_VERSION
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1/ai"

async def test_chat_endpoint():
    """Test the simple chat endpoint"""
    print("🤖 Testing Chat Endpoint...")
    
    async with httpx.AsyncClient() as client:
        # Test greeting
        response = await client.post(
            f"{BASE_URL}/chat",
            json={
                "message": "Hello! How are you?",
                "conversation_id": "test_conversation"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat Response: {result['response']}")
            print(f"📝 Workflow State: {result['workflow_state']}")
        else:
            print(f"❌ Chat failed: {response.status_code} - {response.text}")
        
        # Test question
        response = await client.post(
            f"{BASE_URL}/chat",
            json={
                "message": "What is the capital of France?",
                "conversation_id": "test_conversation"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Question Response: {result['response']}")
        else:
            print(f"❌ Question failed: {response.status_code} - {response.text}")

async def test_task_workflow():
    """Test the complex task workflow"""
    print("\n🔄 Testing Task Workflow...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BASE_URL}/workflow/task",
            json={
                "task": "Plan a weekend trip to Paris",
                "parameters": {
                    "budget": "$1000",
                    "duration": "2 days"
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Task Result: {result['result'][:200]}...")
            print(f"📊 Status: {result['status']}")
            print(f"📋 Steps Completed: {len(result['steps'])}")
            
            for i, step in enumerate(result['steps'], 1):
                print(f"   Step {i}: {step['description']}")
        else:
            print(f"❌ Task workflow failed: {response.status_code} - {response.text}")

async def test_conversation_history():
    """Test conversation history endpoint"""
    print("\n📚 Testing Conversation History...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/conversations/test_conversation")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {len(result['messages'])} messages in conversation")
            for msg in result['messages'][-2:]:  # Show last 2 messages
                print(f"   {msg['role']}: {msg['content'][:100]}...")
        else:
            print(f"❌ History failed: {response.status_code} - {response.text}")

async def test_health_check():
    """Test the health check endpoint"""
    print("\n🏥 Testing Health Check...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Service Status: {result['status']}")
            print(f"🔗 LLM Connected: {result['llm_connected']}")
            print(f"💬 Active Conversations: {result['active_conversations']}")
        else:
            print(f"❌ Health check failed: {response.status_code} - {response.text}")

async def main():
    """Run all tests"""
    print("🚀 Starting LangGraph FastAPI Integration Tests")
    print("=" * 50)
    
    try:
        await test_health_check()
        await test_chat_endpoint()
        await test_task_workflow()
        await test_conversation_history()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("💡 Try these endpoints in your browser:")
        print("   📖 API Docs: http://localhost:8000/docs")
        print(f"   🤖 Chat: POST {BASE_URL}/chat")
        print(f"   🔄 Workflow: POST {BASE_URL}/workflow/task")
        
    except httpx.ConnectError:
        print("❌ Could not connect to FastAPI server.")
        print("💡 Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())