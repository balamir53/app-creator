# React Native Builder Agent Guide

This guide explains how to use the AI-powered React Native Builder Agent to automatically create, build, and debug React Native mobile applications.

## Overview

The React Native Builder Agent is a sophisticated LangGraph-powered service that can:

- 🏗️ **Design app architecture** based on natural language descriptions
- 📱 **Generate React Native components** and screens automatically
- 🔧 **Install dependencies** and manage project structure
- 🐛 **Debug and fix errors** automatically with multiple retry attempts
- 🚀 **Validate builds** and provide next steps for deployment

## API Endpoints

### Build React Native App
```
POST /api/v1/mobile/react-native/build
```

Create a complete React Native app from a description.

**Request Body:**
```json
{
    "app_description": "A todo list app with add, delete, and mark complete functionality",
    "app_name": "MyTodoApp",
    "features": ["Add todos", "Delete todos", "Mark complete", "Local storage"],
    "design_preferences": {
        "theme": "modern",
        "colors": ["#4A90E2", "#F5F5F5"],
        "style": "clean and minimalist"
    },
    "project_id": "my_todo_app"
}
```

**Response:**
```json
{
    "project_id": "my_todo_app",
    "status": "completed",
    "current_step": "complete",
    "generated_files": [
        {
            "path": "App.js",
            "type": "component",
            "content": "import React from 'react'..."
        }
    ],
    "build_logs": ["Project structure created", "Dependencies installed"],
    "errors": [],
    "app_structure": {
        "screens": [{"name": "HomeScreen", "purpose": "Main screen"}],
        "navigation": {"type": "stack", "routes": ["Home"]},
        "dependencies": ["@react-navigation/native"]
    },
    "next_actions": [
        "Run 'npm start' to start Metro bundler",
        "Run 'npx react-native run-android' for Android"
    ]
}
```

### Get Project Details
```
GET /api/v1/mobile/react-native/projects/{project_id}
```

Retrieve details about a generated React Native project.

### Delete Project
```
DELETE /api/v1/mobile/react-native/projects/{project_id}
```

Delete a React Native project and clean up files.

### Health Check
```
GET /api/v1/mobile/react-native/health
```

Check the health of the React Native builder service and environment.

## Workflow Steps

The React Native Builder Agent follows this workflow:

### 1. Plan Architecture
- Analyzes the app description and features
- Designs screen structure and navigation
- Determines required dependencies
- Creates file structure plan

### 2. Generate Project
- Creates project directory structure
- Generates package.json with dependencies
- Sets up folder structure (screens, components, navigation)

### 3. Generate Components
- Creates App.js with navigation setup
- Generates screen components based on architecture
- Includes proper styling and error handling
- Implements responsive design patterns

### 4. Install Dependencies
- Runs `npm install` to install all packages
- Handles timeout and error scenarios
- Logs installation progress

### 5. Validate Build
- Checks for syntax errors
- Validates import/export structure
- Ensures components are properly structured

### 6. Fix Errors (if needed)
- Automatically identifies and fixes common issues
- Retries up to 3 times with different solutions
- Logs all fix attempts and explanations

## Example App Types

### Todo List App
```json
{
    "app_description": "A simple todo list app with add, delete, and mark as complete functionality. Include a clean, modern UI with navigation between a todo list screen and an add todo screen.",
    "app_name": "TodoListApp",
    "features": [
        "Add new todos",
        "Mark todos as complete", 
        "Delete todos",
        "Navigation between screens",
        "Local storage"
    ]
}
```

### Weather App
```json
{
    "app_description": "A weather forecast app that shows current weather and 5-day forecast. Include location services, weather icons, and temperature display.",
    "app_name": "WeatherApp",
    "features": [
        "Current weather",
        "5-day forecast",
        "Location services",
        "Weather icons"
    ]
}
```

### Chat App
```json
{
    "app_description": "A simple chat application with message bubbles, send functionality, and user avatars. Include chat rooms and real-time messaging UI.",
    "app_name": "ChatApp",
    "features": [
        "Message bubbles",
        "Send messages", 
        "User avatars",
        "Chat rooms"
    ]
}
```

## Error Handling

The agent includes sophisticated error handling:

- **Syntax Errors**: Automatically fixes import/export issues, component structure problems
- **Dependency Issues**: Retries installation with different configurations
- **Build Failures**: Analyzes error logs and applies targeted fixes
- **Timeout Handling**: Manages long-running operations with appropriate timeouts

## Generated File Structure

The agent creates a standard React Native project structure:

```
MyApp/
├── package.json                 # Dependencies and scripts
├── App.js                      # Main app component with navigation
├── src/
│   ├── screens/
│   │   ├── HomeScreen.js       # Generated screens
│   │   └── ProfileScreen.js
│   ├── components/
│   │   ├── Header.js           # Reusable components
│   │   └── Button.js
│   └── navigation/
│       └── AppNavigator.js     # Navigation configuration
```

## Environment Requirements

To use the React Native Builder Agent, ensure you have:

- **Node.js** (v16 or higher)
- **npm** or **yarn**
- **React Native CLI** (`npm install -g react-native-cli`)
- **Android Studio** (for Android development)
- **Xcode** (for iOS development, macOS only)

## Running Generated Apps

After the agent creates your app:

1. **Navigate to project directory:**
   ```bash
   cd /tmp/rn_projects/YourAppName
   ```

2. **Start Metro bundler:**
   ```bash
   npm start
   ```

3. **Run on Android:**
   ```bash
   npx react-native run-android
   ```

4. **Run on iOS:**
   ```bash
   npx react-native run-ios
   ```

## Testing the Agent

Use the provided test script to verify the agent functionality:

```bash
cd /Users/yusufziyatemiz/source/app-creator
python examples/test_react_native_builder.py
```

This will test:
- Health check endpoint
- App building with various configurations
- Project management operations
- Error handling scenarios

## Best Practices

1. **Clear Descriptions**: Provide detailed app descriptions for better results
2. **Specific Features**: List specific features you want implemented
3. **Design Preferences**: Include color schemes and styling preferences
4. **Iterative Development**: Start simple and add complexity gradually
5. **Error Review**: Check generated code before deploying to production

## Troubleshooting

### Common Issues

1. **Node.js not found**: Install Node.js v16+ and ensure it's in PATH
2. **npm install fails**: Check internet connection and npm registry access
3. **Build errors**: Review generated code and fix syntax issues manually
4. **Timeout errors**: Increase timeout values for large projects

### Debug Mode

Enable debug logging by setting environment variables:
```bash
export DEBUG_REACT_NATIVE_BUILDER=true
export LOG_LEVEL=debug
```

This provides detailed logs for troubleshooting build issues.

## Advanced Features

### Custom Component Generation
The agent can generate custom components based on specific requirements:

```json
{
    "design_preferences": {
        "custom_components": [
            "SearchBar with autocomplete",
            "Image carousel with dots",
            "Custom button with animations"
        ]
    }
}
```

### Navigation Patterns
Support for different navigation patterns:

- **Stack Navigation**: Linear screen flow
- **Tab Navigation**: Bottom tabs for main sections  
- **Drawer Navigation**: Side menu navigation
- **Mixed Navigation**: Combination of patterns

### State Management
Automatic setup of state management based on app complexity:

- **React Hooks**: For simple state management
- **Context API**: For medium complexity
- **Redux**: For complex state requirements

## API Integration

The agent can generate apps with API integration:

```json
{
    "features": [
        "REST API integration",
        "Authentication flow",
        "Data caching",
        "Offline support"
    ]
}
```

This creates proper API service files and error handling.

## Limitations

- Generates basic React Native apps (not Expo)
- Limited to standard React Native components
- No native module generation
- Requires manual setup for complex integrations
- Database integration requires additional configuration

## Future Enhancements

Planned improvements:
- Expo support
- Native module generation
- Database integration
- CI/CD pipeline setup
- App store deployment automation
- Advanced styling with styled-components
- TypeScript support
- Testing framework setup