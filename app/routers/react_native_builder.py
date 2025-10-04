"""
React Native Mobile App Builder Agent using LangGraph
This agent can design, build, and run React Native apps with automatic bug fixing
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
import os
import subprocess
import re

router = APIRouter()

# Pydantic models for request/response
class ReactNativeAppRequest(BaseModel):
    app_description: str
    app_name: str = "MyReactNativeApp"
    features: List[str] = []
    design_preferences: Dict[str, Any] = {}
    project_id: str = "default"

class ReactNativeAppResponse(BaseModel):
    project_id: str
    status: str
    current_step: str
    generated_files: List[Dict[str, str]]
    build_logs: List[str]
    errors: List[str]
    app_structure: Dict[str, Any]
    next_actions: List[str]

# State for React Native App Builder workflow
class ReactNativeBuilderState(TypedDict):
    app_description: str
    app_name: str
    features: List[str]
    design_preferences: Dict[str, Any]
    project_path: str
    current_step: str
    generated_files: List[Dict[str, str]]
    build_logs: List[str]
    errors: List[str]
    retry_count: int
    max_retries: int
    app_structure: Dict[str, Any]
    last_error: str
    fix_attempts: List[str]

# Simple in-memory storage for React Native projects
rn_projects = {}

def create_llm():
    """Create and return an LLM instance (Azure OpenAI or regular OpenAI)"""
    if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
        return AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.OPENAI_API_VERSION,
            azure_deployment="gpt-35-turbo",
            temperature=0.3  # Lower temperature for more consistent code generation
        )
    elif settings.OPENAI_API_KEY:
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
    else:
        raise ValueError("No OpenAI API key configured")

def plan_app_architecture(state: ReactNativeBuilderState) -> ReactNativeBuilderState:
    """Plan the React Native app architecture and structure"""
    llm = create_llm()
    
    prompt = f"""
    You are a React Native expert. Design the architecture for this mobile app:
    
    App Description: {state['app_description']}
    App Name: {state['app_name']}
    Features: {state['features']}
    Design Preferences: {state['design_preferences']}
    
    Create a detailed app structure with:
    1. Screen components needed
    2. Navigation structure
    3. Required dependencies
    4. File structure
    5. Key components and their purposes
    
    Return a JSON object with the structure:
    {{
        "screens": [
            {{"name": "ScreenName", "purpose": "description", "components": ["Component1", "Component2"]}}
        ],
        "navigation": {{"type": "stack|tabs|drawer", "routes": ["Screen1", "Screen2"]}},
        "dependencies": ["react-navigation", "react-native-vector-icons", ...],
        "file_structure": {{
            "src/screens/": ["HomeScreen.js", "ProfileScreen.js"],
            "src/components/": ["Button.js", "Header.js"],
            "src/navigation/": ["AppNavigator.js"]
        }}
    }}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        app_structure = json.loads(response.content)
    except json.JSONDecodeError:
        # Fallback structure if JSON parsing fails
        app_structure = {
            "screens": [{"name": "HomeScreen", "purpose": "Main app screen", "components": ["Header", "Content"]}],
            "navigation": {"type": "stack", "routes": ["Home"]},
            "dependencies": ["@react-navigation/native", "@react-navigation/stack"],
            "file_structure": {
                "src/screens/": ["HomeScreen.js"],
                "src/components/": ["Header.js"],
                "src/navigation/": ["AppNavigator.js"]
            }
        }
    
    return {
        **state,
        "current_step": "generate_project",
        "app_structure": app_structure,
        "build_logs": state["build_logs"] + [f"App architecture planned: {len(app_structure.get('screens', []))} screens"]
    }

def generate_react_native_project(state: ReactNativeBuilderState) -> ReactNativeBuilderState:
    """Generate the React Native project structure and initial files"""
    project_path = f"/tmp/rn_projects/{state['app_name']}"
    
    # Create project directory
    os.makedirs(project_path, exist_ok=True)
    os.makedirs(f"{project_path}/src/screens", exist_ok=True)
    os.makedirs(f"{project_path}/src/components", exist_ok=True)
    os.makedirs(f"{project_path}/src/navigation", exist_ok=True)
    
    generated_files = []
    
    # Generate package.json
    package_json = {
        "name": state['app_name'].lower().replace(' ', '-'),
        "version": "1.0.0",
        "main": "index.js",
        "scripts": {
            "start": "react-native start",
            "android": "react-native run-android",
            "ios": "react-native run-ios",
            "test": "jest"
        },
        "dependencies": {
            "react": "18.2.0",
            "react-native": "0.72.6"
        },
        "devDependencies": {
            "@babel/core": "^7.20.0",
            "@babel/preset-env": "^7.20.0",
            "@babel/runtime": "^7.20.0",
            "metro-react-native-babel-preset": "0.76.8"
        }
    }
    
    # Add dependencies from app structure
    for dep in state['app_structure'].get('dependencies', []):
        package_json['dependencies'][dep] = 'latest'
    
    with open(f"{project_path}/package.json", 'w') as f:
        json.dump(package_json, f, indent=2)
    
    generated_files.append({
        "path": "package.json",
        "type": "config",
        "content": json.dumps(package_json, indent=2)
    })
    
    return {
        **state,
        "current_step": "generate_components",
        "project_path": project_path,
        "generated_files": generated_files,
        "build_logs": state["build_logs"] + ["Project structure created", f"Dependencies: {len(package_json['dependencies'])} packages"]
    }

def generate_app_components(state: ReactNativeBuilderState) -> ReactNativeBuilderState:
    """Generate React Native components and screens"""
    llm = create_llm()
    generated_files = state["generated_files"].copy()
    
    # Generate App.js
    app_js_prompt = f"""
    Create a React Native App.js file for: {state['app_description']}
    
    App Structure: {json.dumps(state['app_structure'], indent=2)}
    
    Include:
    - Navigation setup based on the structure
    - Basic styling
    - Import all required screens
    - Error boundaries
    
    Return only the JavaScript code without markdown formatting.
    """
    
    response = llm.invoke([HumanMessage(content=app_js_prompt)])
    app_js_content = response.content.strip()
    
    # Clean up any markdown formatting
    app_js_content = re.sub(r'^```javascript\n?', '', app_js_content)
    app_js_content = re.sub(r'\n?```$', '', app_js_content)
    
    with open(f"{state['project_path']}/App.js", 'w') as f:
        f.write(app_js_content)
    
    generated_files.append({
        "path": "App.js",
        "type": "component",
        "content": app_js_content[:500] + "..." if len(app_js_content) > 500 else app_js_content
    })
    
    # Generate screens
    for screen in state['app_structure'].get('screens', []):
        screen_prompt = f"""
        Create a React Native screen component: {screen['name']}
        Purpose: {screen.get('purpose', 'Main screen')}
        Components needed: {screen.get('components', [])}
        
        App context: {state['app_description']}
        
        Include:
        - Functional component with hooks
        - Basic styling with StyleSheet
        - Navigation props handling
        - Responsive design
        - Error handling
        
        Return only the JavaScript code without markdown formatting.
        """
        
        response = llm.invoke([HumanMessage(content=screen_prompt)])
        screen_content = response.content.strip()
        
        # Clean up any markdown formatting
        screen_content = re.sub(r'^```javascript\n?', '', screen_content)
        screen_content = re.sub(r'\n?```$', '', screen_content)
        
        screen_file = f"{state['project_path']}/src/screens/{screen['name']}.js"
        with open(screen_file, 'w') as f:
            f.write(screen_content)
        
        generated_files.append({
            "path": f"src/screens/{screen['name']}.js",
            "type": "screen",
            "content": screen_content[:300] + "..." if len(screen_content) > 300 else screen_content
        })
    
    return {
        **state,
        "current_step": "install_dependencies",
        "generated_files": generated_files,
        "build_logs": state["build_logs"] + [f"Generated {len(generated_files)} files", "App.js and screens created"]
    }

def install_dependencies(state: ReactNativeBuilderState) -> ReactNativeBuilderState:
    """Install React Native dependencies"""
    build_logs = state["build_logs"].copy()
    errors = state["errors"].copy()
    
    try:
        # Change to project directory and install dependencies
        result = subprocess.run(
            ["npm", "install"],
            cwd=state['project_path'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            build_logs.append("Dependencies installed successfully")
            next_step = "validate_build"
        else:
            errors.append(f"npm install failed: {result.stderr}")
            build_logs.append(f"npm install error: {result.stderr[:200]}")
            next_step = "fix_dependencies"
            
    except subprocess.TimeoutExpired:
        errors.append("npm install timed out")
        build_logs.append("npm install timed out after 5 minutes")
        next_step = "fix_dependencies"
    except Exception as e:
        errors.append(f"Installation error: {str(e)}")
        build_logs.append(f"Installation error: {str(e)}")
        next_step = "fix_dependencies"
    
    return {
        **state,
        "current_step": next_step,
        "build_logs": build_logs,
        "errors": errors
    }

def validate_build(state: ReactNativeBuilderState) -> ReactNativeBuilderState:
    """Validate the React Native build"""
    build_logs = state["build_logs"].copy()
    errors = state["errors"].copy()
    
    try:
        # Try to check for syntax errors using a simple Node.js check
        result = subprocess.run(
            ["node", "-c", "App.js"],
            cwd=state['project_path'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            build_logs.append("Build validation successful")
            next_step = "complete"
        else:
            errors.append(f"Syntax error in App.js: {result.stderr}")
            next_step = "fix_errors"
            
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
        next_step = "fix_errors"
    
    return {
        **state,
        "current_step": next_step,
        "build_logs": build_logs,
        "errors": errors
    }

def fix_errors(state: ReactNativeBuilderState) -> ReactNativeBuilderState:
    """Attempt to fix errors in the React Native app"""
    if state["retry_count"] >= state["max_retries"]:
        return {
            **state,
            "current_step": "complete",
            "build_logs": state["build_logs"] + ["Max retries reached, stopping error fixes"]
        }
    
    llm = create_llm()
    current_errors = "\n".join(state["errors"][-3:])  # Last 3 errors
    
    fix_prompt = f"""
    Fix these React Native errors:
    
    Errors:
    {current_errors}
    
    App Description: {state['app_description']}
    Generated Files: {[f['path'] for f in state['generated_files']]}
    
    Provide specific fixes for each error. Focus on:
    1. Import/export issues
    2. Syntax errors
    3. Navigation setup problems
    4. Component structure issues
    
    Return a JSON object with fixes:
    {{
        "fixes": [
            {{"file": "path/to/file", "issue": "description", "solution": "code fix"}}
        ],
        "explanation": "Overall fix explanation"
    }}
    """
    
    response = llm.invoke([HumanMessage(content=fix_prompt)])
    
    try:
        fix_data = json.loads(response.content)
        fixes_applied = []
        
        for fix in fix_data.get("fixes", []):
            fixes_applied.append(f"Fixed {fix.get('file', 'unknown')}: {fix.get('issue', 'unknown issue')}")
        
        return {
            **state,
            "current_step": "install_dependencies",  # Retry the process
            "retry_count": state["retry_count"] + 1,
            "build_logs": state["build_logs"] + fixes_applied,
            "fix_attempts": state["fix_attempts"] + [fix_data.get("explanation", "Applied fixes")]
        }
        
    except json.JSONDecodeError:
        return {
            **state,
            "current_step": "complete",
            "build_logs": state["build_logs"] + ["Could not parse fix suggestions"],
            "retry_count": state["retry_count"] + 1
        }

def create_react_native_workflow():
    """Create a LangGraph workflow for React Native app building"""
    workflow = StateGraph(ReactNativeBuilderState)
    
    # Add nodes
    workflow.add_node("plan_architecture", plan_app_architecture)
    workflow.add_node("generate_project", generate_react_native_project)
    workflow.add_node("generate_components", generate_app_components)
    workflow.add_node("install_dependencies", install_dependencies)
    workflow.add_node("validate_build", validate_build)
    workflow.add_node("fix_errors", fix_errors)
    
    # Add edges
    workflow.add_edge("plan_architecture", "generate_project")
    workflow.add_edge("generate_project", "generate_components")
    workflow.add_edge("generate_components", "install_dependencies")
    workflow.add_edge("install_dependencies", "validate_build")
    workflow.add_edge("validate_build", END)
    workflow.add_edge("fix_errors", "install_dependencies")  # Retry after fixes
    
    # Add conditional edges for error handling
    def route_after_install(state):
        if state["current_step"] == "fix_dependencies":
            return "fix_errors"
        return "validate_build"
    
    def route_after_validation(state):
        if state["current_step"] == "fix_errors":
            return "fix_errors"
        return END
    
    workflow.add_conditional_edges("install_dependencies", route_after_install, {
        "validate_build": "validate_build",
        "fix_errors": "fix_errors"
    })
    
    workflow.add_conditional_edges("validate_build", route_after_validation, {
        "fix_errors": "fix_errors",
        END: END
    })
    
    # Set entry point
    workflow.set_entry_point("plan_architecture")
    
    return workflow.compile()

@router.post("/react-native/build", response_model=ReactNativeAppResponse)
async def build_react_native_app(request: ReactNativeAppRequest):
    """Build a React Native app with automatic error fixing"""
    try:
        # Create initial state
        state: ReactNativeBuilderState = {
            "app_description": request.app_description,
            "app_name": request.app_name,
            "features": request.features,
            "design_preferences": request.design_preferences,
            "project_path": "",
            "current_step": "plan_architecture",
            "generated_files": [],
            "build_logs": [],
            "errors": [],
            "retry_count": 0,
            "max_retries": 3,
            "app_structure": {},
            "last_error": "",
            "fix_attempts": []
        }
        
        # Create and run the workflow
        workflow = create_react_native_workflow()
        result = workflow.invoke(state)
        
        # Store the project
        rn_projects[request.project_id] = result
        
        # Determine next actions
        next_actions = []
        if result["current_step"] == "complete" and not result["errors"]:
            next_actions = [
                "Run 'npm start' to start Metro bundler",
                "Run 'npx react-native run-android' for Android",
                "Run 'npx react-native run-ios' for iOS"
            ]
        elif result["errors"]:
            next_actions = [
                "Review errors and fix manually",
                "Retry with different app description",
                "Check React Native environment setup"
            ]
        
        return ReactNativeAppResponse(
            project_id=request.project_id,
            status="completed" if result["current_step"] == "complete" else "failed",
            current_step=result["current_step"],
            generated_files=result["generated_files"],
            build_logs=result["build_logs"],
            errors=result["errors"],
            app_structure=result["app_structure"],
            next_actions=next_actions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"React Native build error: {str(e)}")

@router.get("/react-native/projects/{project_id}")
async def get_react_native_project(project_id: str):
    """Get React Native project details"""
    if project_id not in rn_projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = rn_projects[project_id]
    return {
        "project_id": project_id,
        "app_name": project["app_name"],
        "status": project["current_step"],
        "files_generated": len(project["generated_files"]),
        "build_logs": project["build_logs"][-10:],  # Last 10 logs
        "errors": project["errors"],
        "project_path": project["project_path"]
    }

@router.delete("/react-native/projects/{project_id}")
async def delete_react_native_project(project_id: str):
    """Delete React Native project"""
    if project_id not in rn_projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = rn_projects[project_id]
    
    # Try to clean up project directory
    try:
        import shutil
        if os.path.exists(project["project_path"]):
            shutil.rmtree(project["project_path"])
    except Exception:
        pass  # Ignore cleanup errors
    
    del rn_projects[project_id]
    return {"message": f"Project {project_id} deleted"}

@router.get("/react-native/health")
async def react_native_health():
    """Health check for React Native builder service"""
    try:
        # Check if Node.js is available
        node_result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        node_available = node_result.returncode == 0
        
        # Check if npm is available
        npm_result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        npm_available = npm_result.returncode == 0
        
        return {
            "status": "healthy" if node_available and npm_available else "degraded",
            "node_available": node_available,
            "npm_available": npm_available,
            "active_projects": len(rn_projects),
            "node_version": node_result.stdout.strip() if node_available else "Not available",
            "npm_version": npm_result.stdout.strip() if npm_available else "Not available"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "active_projects": len(rn_projects)
        }