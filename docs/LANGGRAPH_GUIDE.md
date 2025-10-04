# LangGraph Integration Guide

This FastAPI application now includes powerful AI capabilities using LangGraph for building stateful, multi-step AI workflows.

## 🚀 Features

### 1. **Smart Chat Interface** (`/api/v1/ai/chat`)
- Context-aware conversations with memory
- Intent analysis and routing
- Persistent conversation history

### 2. **Multi-Step Task Workflows** (`/api/v1/ai/workflow/task`)
- Complex task breakdown and execution
- Step-by-step progress tracking
- Intelligent planning and execution

### 3. **Conversation Management**
- Get conversation history
- Clear conversations
- Health monitoring

## 📋 Setup

### 1. Environment Variables
Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Add your API keys:
```env
# Option 1: Use Azure OpenAI (recommended if you have Azure setup)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_API_TYPE=azure
OPENAI_API_VERSION=2023-08-01-preview

# Option 2: Use regular OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 2. Get API Keys
- **Azure OpenAI**: [Get from Azure Portal](https://portal.azure.com/) (recommended if you have Azure subscription)
  - Create an Azure OpenAI resource
  - Deploy a GPT model (e.g., gpt-35-turbo)
  - Get your endpoint and API key
- **Regular OpenAI**: [Get from OpenAI Platform](https://platform.openai.com/api-keys) (alternative)
- **LangSmith API Key**: [Get from LangSmith](https://smith.langchain.com/) (Optional - for tracing)

## 🔧 API Endpoints

### Chat Endpoint
```bash
POST /api/v1/ai/chat
```

**Request:**
```json
{
  "message": "Hello! How can you help me?",
  "conversation_id": "user_123"
}
```

**Response:**
```json
{
  "response": "Hello! I'm your AI assistant. How can I help you today?",
  "conversation_id": "user_123",
  "workflow_state": "complete"
}
```

### Task Workflow Endpoint
```bash
POST /api/v1/ai/workflow/task
```

**Request:**
```json
{
  "task": "Plan a weekend trip to Paris",
  "parameters": {
    "budget": "$1000",
    "duration": "2 days"
  }
}
```

**Response:**
```json
{
  "result": "Task completed! Here's your Paris weekend plan...",
  "steps": [
    {
      "step_number": 1,
      "description": "Research best attractions",
      "result": "Top attractions include Eiffel Tower, Louvre...",
      "completed": true
    }
  ],
  "status": "completed"
}
```

### Conversation History
```bash
GET /api/v1/ai/conversations/{conversation_id}
```

### Health Check
```bash
GET /api/v1/ai/health
```

## 🧪 Testing

Run the example test script:

```bash
python examples/test_langgraph.py
```

This will test all endpoints and show you how the LangGraph workflows work.

## 🏗️ How It Works

### 1. **State Management**
Each conversation maintains a `ConversationState` that includes:
- Message history
- Current workflow step
- Context variables
- User input and AI responses

### 2. **Workflow Graphs**
LangGraph creates directed graphs where each node represents a step:

**Chat Workflow:**
```
Start → Analyze Intent → Process Intent → Complete
```

**Task Workflow:**
```
Start → Plan Task → Execute Steps → Summarize → Complete
              ↑           ↓
              └───────────┘ (Loop for multiple steps)
```

### 3. **Intent Analysis**
The system analyzes user messages to determine:
- `greeting`: Welcome messages
- `question`: Information requests
- `task`: Complex multi-step requests
- `goodbye`: Conversation endings

## 🎯 Use Cases

### Simple Chat
Perfect for:
- Customer support
- Q&A systems
- General conversation

### Complex Tasks
Ideal for:
- Project planning
- Research workflows
- Multi-step problem solving
- Tutorial creation

## 🔍 Debugging

### Enable LangSmith Tracing
Set in your `.env`:
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
```

### Check Health Status
```bash
curl http://localhost:8000/api/v1/ai/health
```

### View API Documentation
Open: http://localhost:8000/docs

## 🚀 Next Steps

1. **Custom Workflows**: Create your own LangGraph workflows for specific use cases
2. **Tool Integration**: Add external tools and APIs to workflows
3. **Database Integration**: Store conversation state in your database
4. **Authentication**: Add user authentication to track conversations per user
5. **Streaming**: Implement streaming responses for real-time chat

## 📚 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangSmith Tracing](https://smith.langchain.com/)

Happy building! 🎉