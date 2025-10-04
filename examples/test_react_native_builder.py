#!/usr/bin/env python3
"""
Test script for React Native Builder Agent
"""
import requests
import time

BASE_URL = "http://localhost:8000/api/v1/mobile"

def test_react_native_builder():
    """Test the React Native Builder Agent"""
    print("🔨 Testing React Native Builder Agent...")
    
    # Test health check
    print("\n1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/react-native/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Service Status: {health['status']}")
            print(f"   Node.js: {health.get('node_version', 'Not available')}")
            print(f"   NPM: {health.get('npm_version', 'Not available')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test React Native app building
    print("\n2. Building React Native App")
    
    app_request = {
        "app_description": "A simple todo list app with add, delete, and mark as complete functionality. Include a clean, modern UI with navigation between a todo list screen and an add todo screen.",
        "app_name": "TodoListApp",
        "features": [
            "Add new todos",
            "Mark todos as complete",
            "Delete todos",
            "Navigation between screens",
            "Local storage"
        ],
        "design_preferences": {
            "theme": "modern",
            "colors": ["#4A90E2", "#F5F5F5", "#333333"],
            "style": "clean and minimalist"
        },
        "project_id": "test_todo_app"
    }
    
    try:
        print("   Sending build request...")
        response = requests.post(
            f"{BASE_URL}/react-native/build",
            json=app_request,
            timeout=180  # 3 minute timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Build Status: {result['status']}")
            print(f"   Current Step: {result['current_step']}")
            print(f"   Files Generated: {len(result['generated_files'])}")
            
            # Show generated files
            print("\n   Generated Files:")
            for file in result['generated_files']:
                print(f"   📄 {file['path']} ({file['type']})")
            
            # Show build logs
            print("\n   Build Logs:")
            for log in result['build_logs'][-5:]:  # Last 5 logs
                print(f"   📝 {log}")
            
            # Show errors if any
            if result['errors']:
                print("\n   Errors:")
                for error in result['errors']:
                    print(f"   ❌ {error}")
            
            # Show next actions
            if result['next_actions']:
                print("\n   Next Actions:")
                for action in result['next_actions']:
                    print(f"   👉 {action}")
                    
        else:
            print(f"❌ Build failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Build request timed out")
    except Exception as e:
        print(f"❌ Build error: {e}")
    
    # Test getting project details
    print("\n3. Getting Project Details")
    try:
        response = requests.get(f"{BASE_URL}/react-native/projects/test_todo_app")
        if response.status_code == 200:
            project = response.json()
            print(f"✅ Project: {project['app_name']}")
            print(f"   Status: {project['status']}")
            print(f"   Files: {project['files_generated']}")
            print(f"   Path: {project['project_path']}")
        else:
            print(f"❌ Failed to get project: {response.status_code}")
    except Exception as e:
        print(f"❌ Project details error: {e}")

def test_different_app_types():
    """Test different types of React Native apps"""
    print("\n\n🚀 Testing Different App Types...")
    
    app_types = [
        {
            "name": "WeatherApp",
            "description": "A weather forecast app that shows current weather and 5-day forecast. Include location services, weather icons, and temperature display.",
            "features": ["Current weather", "5-day forecast", "Location services", "Weather icons"],
            "project_id": "weather_app"
        },
        {
            "name": "ChatApp", 
            "description": "A simple chat application with message bubbles, send functionality, and user avatars. Include chat rooms and real-time messaging UI.",
            "features": ["Message bubbles", "Send messages", "User avatars", "Chat rooms"],
            "project_id": "chat_app"
        }
    ]
    
    for app in app_types:
        print(f"\n🔨 Building {app['name']}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/react-native/build",
                json=app,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {app['name']}: {result['status']}")
                print(f"   Files: {len(result['generated_files'])}")
            else:
                print(f"❌ {app['name']} failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {app['name']} error: {e}")

if __name__ == "__main__":
    print("🎯 React Native Builder Agent Test Suite")
    print("=" * 50)
    
    # Wait a moment for the server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    test_react_native_builder()
    test_different_app_types()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
    print("\nTo run the generated React Native apps:")
    print("1. cd /tmp/rn_projects/[AppName]")
    print("2. npm start")
    print("3. npx react-native run-android (or run-ios)")