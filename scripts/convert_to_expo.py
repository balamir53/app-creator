#!/usr/bin/env python3
"""
Convert React Native Builder Agent apps to Expo format for online testing
"""
import os
import json
import shutil
import re

def find_missing_imports(file_content):
    """Find all import statements that reference local files"""
    # Pattern for relative imports like ./Component or ../navigation/AppNavigator
    relative_pattern = r"import\s+[^']*from\s+['\"]\.\.?\/([^'\"]+)['\"]"
    # Pattern for src/ imports like src/navigation/AppNavigator
    src_pattern = r"import\s+[^']*from\s+['\"]src\/([^'\"]+)['\"]"
    
    relative_imports = re.findall(relative_pattern, file_content)
    src_imports = re.findall(src_pattern, file_content)
    
    return relative_imports + src_imports

def create_missing_component(component_name, components_dir, app_context=""):
    """Create a missing React Native component with context-aware content"""
    
    # Handle navigation components
    if "navigation" in component_name.lower() or "navigator" in component_name.lower():
        component_content = """import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { View, Text, StyleSheet } from 'react-native';

// Import your main screen components here
// import HomeScreen from '../screens/HomeScreen';
// import CalculatorScreen from '../screens/CalculatorScreen';

const Stack = createStackNavigator();

// Placeholder screen component
const MainScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Main Screen</Text>
      <Text style={styles.subtitle}>Add your app content here</Text>
    </View>
  );
};

const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Main">
        <Stack.Screen 
          name="Main" 
          component={MainScreen}
          options={{ title: 'Calculator App' }}
        />
        {/* Add more screens here */}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  text: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
  },
});

export default AppNavigator;
"""
    # Create context-specific components
    elif component_name.lower() == "header":
        component_content = """import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const Header = ({ title = "App", ...props }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      {props.children}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 20,
    paddingTop: 40,
    backgroundColor: '#f8f9fa',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#343a40',
  },
});

export default Header;
"""
    elif component_name.lower() == "content":
        component_content = """import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

const Content = ({ displayValue = "0", onNumberPress, onOperationPress, onClearPress, ...props }) => {
  const numbers = [
    ['C', '±', '%', '÷'],
    ['7', '8', '9', '×'],
    ['4', '5', '6', '−'],
    ['1', '2', '3', '+'],
    ['0', '.', '=']
  ];

  const handlePress = (value) => {
    if (value === 'C' && onClearPress) {
      onClearPress();
    } else if (['÷', '×', '−', '+', '='].includes(value) && onOperationPress) {
      onOperationPress(value);
    } else if (['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.'].includes(value) && onNumberPress) {
      onNumberPress(value);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.display}>
        <Text style={styles.displayText}>{displayValue}</Text>
      </View>
      
      <View style={styles.buttonContainer}>
        {numbers.map((row, rowIndex) => (
          <View key={rowIndex} style={styles.row}>
            {row.map((button) => (
              <TouchableOpacity
                key={button}
                style={[
                  styles.button,
                  button === '0' ? styles.zeroButton : null,
                  ['÷', '×', '−', '+', '='].includes(button) ? styles.operatorButton : null
                ]}
                onPress={() => handlePress(button)}
              >
                <Text style={[
                  styles.buttonText,
                  ['÷', '×', '−', '+', '='].includes(button) ? styles.operatorText : null
                ]}>
                  {button}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        ))}
      </View>
      {props.children}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  display: {
    flex: 1,
    justifyContent: 'flex-end',
    alignItems: 'flex-end',
    padding: 20,
    backgroundColor: '#000',
  },
  displayText: {
    fontSize: 64,
    color: '#fff',
    fontWeight: '200',
  },
  buttonContainer: {
    padding: 10,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  button: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#333',
    justifyContent: 'center',
    alignItems: 'center',
  },
  zeroButton: {
    width: 170,
  },
  operatorButton: {
    backgroundColor: '#ff9500',
  },
  buttonText: {
    fontSize: 32,
    color: '#fff',
    fontWeight: '400',
  },
  operatorText: {
    color: '#fff',
  },
});

export default Content;
"""
    elif component_name.lower() in ["todoitem", "todo-item"]:
        component_content = """import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

const TodoItem = ({ todo, markAsComplete, deleteTodo, ...props }) => {
  return (
    <View style={[styles.container, todo?.completed && styles.completed]}>
      <TouchableOpacity
        style={styles.textContainer}
        onPress={() => markAsComplete && markAsComplete(todo?.id)}
      >
        <Text style={[styles.text, todo?.completed && styles.completedText]}>
          {todo?.text || "Todo item"}
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity
        style={styles.deleteButton}
        onPress={() => deleteTodo && deleteTodo(todo?.id)}
      >
        <Text style={styles.deleteText}>×</Text>
      </TouchableOpacity>
      {props.children}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    marginVertical: 5,
    backgroundColor: '#fff',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 2,
  },
  completed: {
    backgroundColor: '#f8f9fa',
    opacity: 0.7,
  },
  textContainer: {
    flex: 1,
  },
  text: {
    fontSize: 16,
    color: '#333',
  },
  completedText: {
    textDecorationLine: 'line-through',
    color: '#666',
  },
  deleteButton: {
    padding: 10,
    marginLeft: 10,
  },
  deleteText: {
    fontSize: 20,
    color: '#ff4757',
    fontWeight: 'bold',
  },
});

export default TodoItem;
"""
    elif component_name.lower() in ["todolist", "todo-list"]:
        component_content = """import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';

const TodoList = ({ children, ...props }) => {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {children}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  content: {
    padding: 10,
  },
});

export default TodoList;
"""
    else:
        # Generic component fallback
        component_content = f"""import React from 'react';
import {{ View, Text, StyleSheet }} from 'react-native';

const {component_name} = (props) => {{
  return (
    <View style={{styles.container}}>
      <Text style={{styles.text}}>{component_name} Component</Text>
      {{props.children}}
    </View>
  );
}};

const styles = StyleSheet.create({{
  container: {{
    padding: 10,
    alignItems: 'center',
  }},
  text: {{
    fontSize: 16,
    fontWeight: 'bold',
  }},
}});

export default {component_name};
"""
    
    component_file = os.path.join(components_dir, f"{component_name}.js")
    os.makedirs(components_dir, exist_ok=True)
    
    with open(component_file, 'w') as f:
        f.write(component_content)
    
    print(f"   📄 Created missing component: {component_name}.js")

def fix_missing_imports(src_path):
    """Fix missing imports by creating placeholder components"""
    print("   🔧 Checking for missing imports...")
    
    missing_components = set()
    navigation_imports = set()
    
    # Check all JavaScript files for missing imports
    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file.endswith('.js'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Find local imports
                local_imports = find_missing_imports(content)
                
                for import_path in local_imports:
                    # Handle different import patterns
                    if import_path.startswith('navigation/'):
                        # Navigation import like 'src/navigation/AppNavigator'
                        nav_dir = os.path.join(src_path, 'navigation')
                        nav_file = os.path.join(nav_dir, f"{os.path.basename(import_path)}.js")
                        if not os.path.exists(nav_file):
                            navigation_imports.add(os.path.basename(import_path))
                    else:
                        # Regular component import
                        resolved_path = os.path.join(os.path.dirname(file_path), f"{import_path}.js")
                        if not os.path.exists(resolved_path):
                            # Also check in src directory
                            src_resolved_path = os.path.join(src_path, f"{import_path}.js")
                            if not os.path.exists(src_resolved_path):
                                component_name = os.path.basename(import_path)
                                missing_components.add(component_name)
    
    # Create missing navigation components
    if navigation_imports:
        navigation_dir = os.path.join(src_path, 'navigation')
        for nav_component in navigation_imports:
            create_missing_component(nav_component, navigation_dir, src_path)
    
    # Create missing regular components
    if missing_components:
        components_dir = os.path.join(src_path, 'components')
        for component_name in missing_components:
            create_missing_component(component_name, components_dir, src_path)
        
        # Update import paths in files
        fix_import_paths(src_path, missing_components, navigation_imports)
    elif navigation_imports:
        # Only navigation imports need fixing
        fix_import_paths(src_path, set(), navigation_imports)
    else:
        print("   ✅ No missing imports found")

def fix_import_paths(src_path, missing_components, navigation_imports=set()):
    """Update import paths to point to the correct directories"""
    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file.endswith('.js'):
                file_path = os.path.join(root, file)
                
                with open(file_path, 'r') as f:
                    content = f.read()
                
                updated_content = content
                
                # Fix import paths for missing components
                for component in missing_components:
                    # Replace relative imports with components directory imports
                    old_import = f"from './{component}'"
                    new_import = f"from '../components/{component}'"
                    updated_content = updated_content.replace(old_import, new_import)
                
                # Fix navigation imports
                for nav_component in navigation_imports:
                    # Replace src/navigation imports
                    old_src_import = f"from 'src/navigation/{nav_component}'"
                    new_src_import = f"from './navigation/{nav_component}'"
                    updated_content = updated_content.replace(old_src_import, new_src_import)
                    
                    # Also handle relative navigation imports if any
                    old_rel_import = f"from '../navigation/{nav_component}'"
                    new_rel_import = f"from './navigation/{nav_component}'"
                    updated_content = updated_content.replace(old_rel_import, new_rel_import)
                
                # Write back if changed
                if updated_content != content:
                    with open(file_path, 'w') as f:
                        f.write(updated_content)
                    print(f"   🔧 Fixed imports in {os.path.relpath(file_path, src_path)}")

def convert_to_expo(project_path, app_name):
    """Convert a React Native app to Expo format"""
    print(f"🔄 Converting {app_name} to Expo format...")
    
    if not os.path.exists(project_path):
        print(f"❌ Project path not found: {project_path}")
        return False
    
    expo_path = f"/tmp/expo_projects/{app_name}"
    os.makedirs(expo_path, exist_ok=True)
    
    # Create Expo app.json
    app_json = {
        "expo": {
            "name": app_name,
            "slug": app_name.lower(),
            "version": "1.0.0",
            "orientation": "portrait",
            "icon": "./assets/icon.png",
            "userInterfaceStyle": "light",
            "splash": {
                "image": "./assets/splash.png",
                "resizeMode": "contain",
                "backgroundColor": "#ffffff"
            },
            "platforms": ["ios", "android", "web"],
            "assetBundlePatterns": ["**/*"],
            "ios": {
                "supportsTablet": True
            },
            "android": {
                "adaptiveIcon": {
                    "foregroundImage": "./assets/adaptive-icon.png",
                    "backgroundColor": "#FFFFFF"
                }
            },
            "web": {
                "favicon": "./assets/favicon.png"
            }
        }
    }
    
    with open(f"{expo_path}/app.json", 'w') as f:
        json.dump(app_json, f, indent=2)
    
    # Read original package.json
    with open(f"{project_path}/package.json", 'r') as f:
        original_package = json.load(f)
    
    # Create Expo-compatible package.json
    expo_package = {
        "name": app_name.lower(),
        "version": "1.0.0",
        "main": "node_modules/expo/AppEntry.js",
        "scripts": {
            "start": "expo start",
            "android": "expo start --android",
            "ios": "expo start --ios",
            "web": "expo start --web"
        },
        "dependencies": {
            "expo": "~49.0.0",
            "expo-status-bar": "~1.6.0",
            "react": "18.2.0",
            "react-native": "0.72.6",
            "@react-navigation/native": "^6.0.0",
            "@react-navigation/stack": "^6.0.0",
            "react-native-screens": "~3.22.0",
            "react-native-safe-area-context": "4.6.3"
        },
        "devDependencies": {
            "@babel/core": "^7.20.0"
        },
        "private": True
    }
    
    # Add original dependencies (filtered for Expo compatibility)
    compatible_deps = [
        "react-native-vector-icons",
        "async-storage",
        "react-native-location"
    ]
    
    for dep in original_package.get("dependencies", {}):
        if dep in compatible_deps:
            expo_package["dependencies"][dep] = original_package["dependencies"][dep]
    
    with open(f"{expo_path}/package.json", 'w') as f:
        json.dump(expo_package, f, indent=2)
    
    # Convert App.js to Expo format
    original_app_path = f"{project_path}/App.js"
    expo_app_path = f"{expo_path}/App.js"
    
    if os.path.exists(original_app_path):
        with open(original_app_path, 'r') as f:
            app_content = f.read()
        
        # Check for navigation imports in App.js and fix them before copying
        app_imports = find_missing_imports(app_content)
        navigation_files = []
        
        for import_path in app_imports:
            if 'navigation/' in import_path:
                nav_file = import_path.replace('src/', '')  # Remove src/ prefix
                navigation_files.append(os.path.basename(nav_file))
        
        # Create navigation directory and files if needed
        if navigation_files:
            nav_dir = os.path.join(expo_path, 'src', 'navigation')
            os.makedirs(nav_dir, exist_ok=True)
            for nav_file in navigation_files:
                create_missing_component(nav_file, nav_dir, expo_path)
        
        # Fix navigation imports in App.js content
        fixed_app_content = app_content
        for nav_file in navigation_files:
            old_import = f"from './src/navigation/{nav_file}'"
            new_import = f"from './src/navigation/{nav_file}'"
            fixed_app_content = fixed_app_content.replace(old_import, new_import)
        
        # Add Expo StatusBar import
        expo_app_content = """import { StatusBar } from 'expo-status-bar';
import React from 'react';
""" + fixed_app_content.replace("import React from 'react';", "").strip()
        
        # Add StatusBar component to the main render
        if "export default" in expo_app_content:
            expo_app_content = expo_app_content.replace(
                "export default",
                "// Add StatusBar for Expo\n// <StatusBar style=\"auto\" />\n\nexport default"
            )
        
        with open(expo_app_path, 'w') as f:
            f.write(expo_app_content)
    
    # Copy src directory
    if os.path.exists(f"{project_path}/src"):
        shutil.copytree(f"{project_path}/src", f"{expo_path}/src", dirs_exist_ok=True)
        
        # Fix missing component imports
        fix_missing_imports(f"{expo_path}/src")
    
    # Create basic assets directory
    assets_path = f"{expo_path}/assets"
    os.makedirs(assets_path, exist_ok=True)
    
    print(f"✅ {app_name} converted to Expo format at: {expo_path}")
    print(f"📁 Expo project location: {expo_path}")
    return True

def create_snack_instructions(project_path, app_name):
    """Create instructions for uploading to Expo Snack"""
    print(f"\n📱 Instructions for {app_name} on Expo Snack:")
    print("=" * 50)
    print("1. Go to https://snack.expo.dev/")
    print("2. Create a new Snack")
    print("3. Replace App.js with:")
    
    app_js_path = f"{project_path}/App.js"
    if os.path.exists(app_js_path):
        with open(app_js_path, 'r') as f:
            content = f.read()
        print("```javascript")
        print(content[:500] + "..." if len(content) > 500 else content)
        print("```")
    
    print("\n4. Copy files from src/ directory:")
    src_path = f"{project_path}/src"
    if os.path.exists(src_path):
        for root, dirs, files in os.walk(src_path):
            for file in files:
                if file.endswith('.js'):
                    rel_path = os.path.relpath(os.path.join(root, file), project_path)
                    print(f"   📄 {rel_path}")
    
    print("\n5. Install dependencies in Snack:")
    package_path = f"{project_path}/package.json"
    if os.path.exists(package_path):
        with open(package_path, 'r') as f:
            package = json.load(f)
        deps = package.get("dependencies", {})
        for dep, version in deps.items():
            if dep not in ["react", "react-native"]:
                print(f"   📦 {dep}")

def main():
    """Main function to convert React Native projects"""
    print("🔄 React Native to Expo Converter")
    print("=" * 40)
    
    rn_projects_path = "/tmp/rn_projects"
    
    if not os.path.exists(rn_projects_path):
        print("❌ No React Native projects found in /tmp/rn_projects")
        return
    
    # List available projects
    projects = [d for d in os.listdir(rn_projects_path) 
                if os.path.isdir(os.path.join(rn_projects_path, d))]
    
    if not projects:
        print("❌ No React Native projects found")
        return
    
    print(f"📱 Found {len(projects)} React Native projects:")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {project}")
    
    # Convert all projects
    for project in projects:
        project_path = os.path.join(rn_projects_path, project)
        convert_to_expo(project_path, project)
        create_snack_instructions(project_path, project)
        print("\n" + "-" * 50 + "\n")
    
    print("🎉 Conversion completed!")
    print("\n📋 Next Steps:")
    print("1. Use Expo CLI: cd /tmp/expo_projects/[AppName] && expo start")
    print("2. Upload to Expo Snack: https://snack.expo.dev/")
    print("3. Test on device with Expo Go app")

if __name__ == "__main__":
    main()