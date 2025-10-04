"""
LangGraph workflow router for AI-powered endpoints using Azure OpenAI
"""
from typing import Dict, Any, List
from typing_extensions import TypedDict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from app.core.config import settings
import json

router = APIRouter()

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    workflow_state: str

class WorkflowRequest(BaseModel):
    task: str
    parameters: Dict[str, Any] = {}

class WorkflowResponse(BaseModel):
    result: str
    steps: List[Dict[str, Any]]
    status: str

# Simple in-memory storage for conversations (use Redis/DB in production)
conversations = {}

# Define the state schema for our LangGraph workflow
class ConversationState(TypedDict):
    messages: List[Dict[str, str]]
    current_step: str
    context: Dict[str, Any]
    user_input: str
    ai_response: str

def create_llm():
    """Create and return an LLM instance (Azure OpenAI or regular OpenAI)"""
    # Check if Azure OpenAI is configured
    if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
        return AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.OPENAI_API_VERSION,
            azure_deployment="gpt-35-turbo",  # Change this to match your deployment name
            temperature=0.7
        )
    # Fall back to regular OpenAI
    elif settings.OPENAI_API_KEY:
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
    else:
        raise ValueError("No OpenAI API key configured. Please set either AZURE_OPENAI_API_KEY or OPENAI_API_KEY")

def analyze_intent(state: ConversationState) -> ConversationState:
    """Analyze user intent and determine next action"""
    llm = create_llm()
    
    prompt = f"""
    Analyze the user's message and determine their intent.
    User message: {state['user_input']}
    
    Classify the intent as one of:
    - greeting: User is greeting or starting conversation
    - question: User is asking a question
    - task: User wants to perform a specific task
    - goodbye: User is ending the conversation
    
    Respond with just the intent category.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    intent = response.content.strip().lower()
    
    # Create a new state with updated values
    new_context = state['context'].copy()
    new_context["intent"] = intent
    
    return {
        "messages": state['messages'],
        "current_step": "process_intent",
        "context": new_context,
        "user_input": state['user_input'],
        "ai_response": state['ai_response']
    }

def process_intent(state: ConversationState) -> ConversationState:
    """Process the user's intent and generate appropriate response"""
    llm = create_llm()
    intent = state['context'].get("intent", "question")
    
    ai_response = ""
    
    if intent == "greeting":
        ai_response = "Hello! I'm your AI assistant. How can I help you today?"
    elif intent == "goodbye":
        ai_response = "Goodbye! Have a great day!"
    else:
        # For questions and tasks, use the LLM to generate a response
        conversation_history = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in state['messages'][-5:]  # Last 5 messages for context
        ])
        
        prompt = f"""
        Based on the conversation history and the user's current message, provide a helpful response.
        
        Conversation history:
        {conversation_history}
        
        Current user message: {state['user_input']}
        
        Provide a helpful and contextual response.
        """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        ai_response = response.content
    
    # Add messages to conversation history
    new_messages = state['messages'].copy()
    new_messages.append({"role": "user", "content": state['user_input']})
    new_messages.append({"role": "assistant", "content": ai_response})
    
    return {
        "messages": new_messages,
        "current_step": "complete",
        "context": state['context'],
        "user_input": state['user_input'],
        "ai_response": ai_response
    }

def create_conversation_workflow():
    """Create a LangGraph workflow for conversations"""
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("analyze_intent", analyze_intent)
    workflow.add_node("process_intent", process_intent)
    
    # Add edges
    workflow.add_edge("analyze_intent", "process_intent")
    workflow.add_edge("process_intent", END)
    
    # Set entry point
    workflow.set_entry_point("analyze_intent")
    
    return workflow.compile()

# Multi-step task workflow
def plan_task(state: ConversationState) -> ConversationState:
    """Plan how to execute a complex task"""
    llm = create_llm()
    
    prompt = f"""
    Break down this task into 3-5 specific steps:
    Task: {state.user_input}
    
    Return a JSON list of steps, each with 'step_number', 'description', and 'estimated_time'.
    Example: [{{"step_number": 1, "description": "Research the topic", "estimated_time": "5 minutes"}}]
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    new_context = state.context.copy()
    
    try:
        steps = json.loads(response.content)
        new_context["task_steps"] = steps
        new_context["current_step_index"] = 0
        current_step = "execute_steps"
    except json.JSONDecodeError:
        new_context["task_steps"] = [{"step_number": 1, "description": "Unable to parse task", "estimated_time": "N/A"}]
        current_step = "complete"
    
    return ConversationState(
        messages=state.messages,
        current_step=current_step,
        context=new_context,
        user_input=state.user_input,
        ai_response=state.ai_response
    )

def execute_steps(state: ConversationState) -> ConversationState:
    """Execute task steps one by one"""
    steps = state.context.get("task_steps", [])
    current_index = state.context.get("current_step_index", 0)
    new_context = state.context.copy()
    
    if current_index < len(steps):
        current_step = steps[current_index]
        llm = create_llm()
        
        prompt = f"""
        Execute this step of the task:
        Step {current_step['step_number']}: {current_step['description']}
        
        Provide a detailed response for completing this step.
        """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        
        step_result = {
            "step": current_step,
            "result": response.content,
            "completed": True
        }
        
        if "step_results" not in new_context:
            new_context["step_results"] = []
        new_context["step_results"].append(step_result)
        
        new_context["current_step_index"] += 1
        
        # Check if more steps remain
        if new_context["current_step_index"] < len(steps):
            next_step = "execute_steps"  # Continue to next step
        else:
            next_step = "summarize_task"
    else:
        next_step = "summarize_task"
    
    return ConversationState(
        messages=state.messages,
        current_step=next_step,
        context=new_context,
        user_input=state.user_input,
        ai_response=state.ai_response
    )

def summarize_task(state: ConversationState) -> ConversationState:
    """Summarize the completed task"""
    step_results = state.context.get("step_results", [])
    
    summary = "Task completed! Here's what was accomplished:\n\n"
    for i, result in enumerate(step_results, 1):
        summary += f"Step {i}: {result['step']['description']}\n"
        summary += f"Result: {result['result'][:100]}...\n\n"
    
    return ConversationState(
        messages=state.messages,
        current_step="complete",
        context=state.context,
        user_input=state.user_input,
        ai_response=summary
    )

def create_task_workflow():
    """Create a LangGraph workflow for complex tasks"""
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("plan_task", plan_task)
    workflow.add_node("execute_steps", execute_steps)
    workflow.add_node("summarize_task", summarize_task)
    
    # Add edges
    workflow.add_edge("plan_task", "execute_steps")
    workflow.add_edge("execute_steps", "execute_steps")  # Self-loop for multiple steps
    workflow.add_edge("execute_steps", "summarize_task")
    workflow.add_edge("summarize_task", END)
    
    # Set entry point
    workflow.set_entry_point("plan_task")
    
    return workflow.compile()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Simple chat endpoint using LangGraph workflow"""
    try:
        # Get or create conversation state
        if request.conversation_id not in conversations:
            conversations[request.conversation_id] = {
                "messages": [],
                "current_step": "start",
                "context": {},
                "user_input": "",
                "ai_response": ""
            }
        
        current_state = conversations[request.conversation_id]
        
        # Create a new state with the user input
        state: ConversationState = {
            "messages": current_state["messages"],
            "current_step": "start",
            "context": current_state["context"],
            "user_input": request.message,
            "ai_response": ""
        }
        
        # Create and run the workflow
        workflow = create_conversation_workflow()
        result = workflow.invoke(state)
        
        # Update stored conversation
        conversations[request.conversation_id] = result
        
        return ChatResponse(
            response=result["ai_response"],
            conversation_id=request.conversation_id,
            workflow_state=result["current_step"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.post("/workflow/task", response_model=WorkflowResponse)
async def execute_task_workflow(request: WorkflowRequest):
    """Execute a complex task using a simple LLM call for now"""
    try:
        llm = create_llm()
        
        prompt = f"""
        Break down and execute this task step by step:
        Task: {request.task}
        Parameters: {request.parameters}
        
        Provide a detailed response that includes:
        1. Planning the task
        2. Executing each step
        3. A summary of results
        
        Format your response clearly with numbered steps.
        """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Create a simple step structure
        steps = [
            {
                "step_number": 1,
                "description": "Task planning and analysis",
                "result": "Task analyzed and broken down into steps",
                "completed": True
            },
            {
                "step_number": 2,
                "description": "Task execution",
                "result": response.content[:200] + "...",
                "completed": True
            }
        ]
        
        return WorkflowResponse(
            result=response.content,
            steps=steps,
            status="completed"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")

@router.get("/conversations/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """Get conversation history for a specific conversation"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    state = conversations[conversation_id]
    return {
        "conversation_id": conversation_id,
        "messages": state["messages"],
        "current_step": state["current_step"],
        "context": state["context"]
    }

@router.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear a specific conversation"""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": f"Conversation {conversation_id} cleared"}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

@router.get("/health")
async def langgraph_health():
    """Health check for LangGraph services"""
    try:
        # Test LLM connection
        llm = create_llm()
        llm.invoke([HumanMessage(content="Hello")])
        
        return {
            "status": "healthy",
            "llm_connected": True,
            "active_conversations": len(conversations)
        }
    except Exception as e:
        return {
            "status": "error",
            "llm_connected": False,
            "error": str(e),
            "active_conversations": len(conversations)
        }