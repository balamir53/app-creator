#!/usr/bin/env python3
"""
Enhanced component auto-generation with error-based fixes
"""
import os
import re
import shutil
from typing import Dict, List, Optional
from error_analyzer import ParsedError, ErrorType

class SmartComponentGenerator:
    """Generate components based on error analysis and context"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.src_path = os.path.join(project_path, 'src')
        
        # Component templates for different app types
        self.component_templates = {
            "calculator": self._get_calculator_templates(),
            "todo": self._get_todo_templates(),
            "weather": self._get_weather_templates(),
            "generic": self._get_generic_templates()
        }
    
    def fix_errors_with_components(self, parsed_errors: List[ParsedError]) -> Dict[str, bool]:
        """
        Generate components to fix parsed errors
        
        Args:
            parsed_errors: List of parsed errors from error analyzer
            
        Returns:
            Dictionary mapping fix actions to success status
        """
        fix_results = {}
        
        # Detect app type from project context
        app_type = self._detect_app_type()
        
        for error in parsed_errors:
            if error.auto_fixable and error.type == ErrorType.MISSING_COMPONENT:
                success = self._create_missing_component(error, app_type)
                fix_results[f"create_{error.missing_module}"] = success
            
            elif error.auto_fixable and error.type == ErrorType.NAVIGATION_ERROR:
                success = self._fix_navigation_setup()
                fix_results["fix_navigation"] = success
            
            elif error.auto_fixable and error.type == ErrorType.DEPENDENCY_ERROR:
                success = self._add_missing_dependency(error.missing_module)
                fix_results[f"add_dep_{error.missing_module}"] = success
        
        return fix_results
    
    def _detect_app_type(self) -> str:
        """Detect the type of app based on file content and names"""
        app_indicators = {
            "calculator": ["calculator", "calc", "math", "number", "operation"],
            "todo": ["todo", "task", "list", "item", "complete"],
            "weather": ["weather", "forecast", "temperature", "location", "climate"]
        }
        
        # Check file names and content
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.js'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read().lower()
                        
                        for app_type, indicators in app_indicators.items():
                            if any(indicator in content for indicator in indicators):
                                return app_type
                            if any(indicator in file.lower() for indicator in indicators):
                                return app_type
                    except:
                        continue
        
        return "generic"
    
    def _create_missing_component(self, error: ParsedError, app_type: str) -> bool:
        """Create a missing component based on error and app type"""
        try:
            module_path = error.missing_module
            
            # Clean up the module path
            if module_path.startswith('./'):
                module_path = module_path[2:]
            elif module_path.startswith('../'):
                module_path = module_path[3:]
            elif module_path.startswith('src/'):
                module_path = module_path[4:]
            
            # Determine component name and directory
            component_name = os.path.basename(module_path)
            component_dir = os.path.dirname(module_path)
            
            # Create full directory path
            if component_dir:
                full_dir = os.path.join(self.src_path, component_dir)
            else:
                full_dir = os.path.join(self.src_path, 'components')
            
            os.makedirs(full_dir, exist_ok=True)
            
            # Generate component content
            component_content = self._generate_component_content(component_name, app_type)
            
            # Write component file
            component_file = os.path.join(full_dir, f"{component_name}.js")
            with open(component_file, 'w') as f:
                f.write(component_content)
            
            print(f"   ✅ Created component: {component_name}.js")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to create component {error.missing_module}: {str(e)}")
            return False
    
    def _generate_component_content(self, component_name: str, app_type: str) -> str:
        """Generate component content based on name and app type"""
        templates = self.component_templates.get(app_type, self.component_templates["generic"])
        
        # Try to match component name to specific templates
        name_lower = component_name.lower()
        
        for template_name, template_func in templates.items():
            if template_name in name_lower or name_lower in template_name:
                return template_func(component_name)
        
        # Fallback to generic component
        return self._generate_generic_component(component_name)
    
    def _fix_navigation_setup(self) -> bool:
        """Fix navigation setup issues"""
        try:
            # Create navigation directory if it doesn't exist
            nav_dir = os.path.join(self.src_path, 'navigation')
            os.makedirs(nav_dir, exist_ok=True)
            
            # Create AppNavigator if it doesn't exist
            app_navigator_path = os.path.join(nav_dir, 'AppNavigator.js')
            if not os.path.exists(app_navigator_path):
                nav_content = self._get_navigation_template()
                with open(app_navigator_path, 'w') as f:
                    f.write(nav_content)
                print("   ✅ Created AppNavigator.js")
            
            # Update package.json dependencies
            self._update_package_dependencies()
            
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to fix navigation: {str(e)}")
            return False
    
    def _add_missing_dependency(self, dependency: str) -> bool:
        """Add missing dependency to package.json"""
        try:
            package_json_path = os.path.join(self.project_path, 'package.json')
            
            if os.path.exists(package_json_path):
                import json
                
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                # Add common dependency versions
                dependency_versions = {
                    "@react-navigation/native": "^6.0.0",
                    "@react-navigation/stack": "^6.0.0",
                    "react-native-screens": "~3.22.0",
                    "react-native-safe-area-context": "4.6.3",
                    "react-native-vector-icons": "^10.0.0",
                    "@react-native-async-storage/async-storage": "^1.19.0"
                }
                
                if dependency in dependency_versions:
                    package_data.setdefault("dependencies", {})[dependency] = dependency_versions[dependency]
                    
                    with open(package_json_path, 'w') as f:
                        json.dump(package_data, f, indent=2)
                    
                    print(f"   ✅ Added dependency: {dependency}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ Failed to add dependency {dependency}: {str(e)}")
            return False
    
    def _get_calculator_templates(self) -> Dict:
        """Get calculator-specific component templates"""
        return {
            "header": lambda name: f'''import React from 'react';
import {{ View, Text, StyleSheet }} from 'react-native';

const {name} = ({{ title = "Calculator", ...props }}) => {{
  return (
    <View style={{styles.container}}>
      <Text style={{styles.title}}>{"{title}"}</Text>
      {{props.children}}
    </View>
  );
}};

const styles = StyleSheet.create({{
  container: {{
    padding: 20,
    paddingTop: 40,
    backgroundColor: '#000',
    alignItems: 'center',
  }},
  title: {{
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  }},
}});

export default {name};
''',
            "content": lambda name: f'''import React, {{ useState }} from 'react';
import {{ View, Text, StyleSheet, TouchableOpacity }} from 'react-native';

const {name} = (props) => {{
  const [display, setDisplay] = useState('0');
  const [operation, setOperation] = useState(null);
  const [waitingForInput, setWaitingForInput] = useState(false);

  const numbers = [
    ['C', '±', '%', '÷'],
    ['7', '8', '9', '×'],
    ['4', '5', '6', '−'],
    ['1', '2', '3', '+'],
    ['0', '.', '=']
  ];

  const handlePress = (value) => {{
    if (value === 'C') {{
      setDisplay('0');
      setOperation(null);
      setWaitingForInput(false);
    }} else if (['+', '−', '×', '÷'].includes(value)) {{
      setOperation(value);
      setWaitingForInput(true);
    }} else if (value === '=') {{
      // Perform calculation
      setWaitingForInput(true);
    }} else {{
      if (waitingForInput) {{
        setDisplay(value);
        setWaitingForInput(false);
      }} else {{
        setDisplay(display === '0' ? value : display + value);
      }}
    }}
  }};

  return (
    <View style={{styles.container}}>
      <View style={{styles.display}}>
        <Text style={{styles.displayText}}>{"{display}"}</Text>
      </View>
      
      <View style={{styles.buttonContainer}}>
        {{numbers.map((row, rowIndex) => (
          <View key={{rowIndex}} style={{styles.row}}>
            {{row.map((button) => (
              <TouchableOpacity
                key={{button}}
                style={{[
                  styles.button,
                  button === '0' ? styles.zeroButton : null,
                  ['÷', '×', '−', '+', '='].includes(button) ? styles.operatorButton : null
                ]}}
                onPress={{() => handlePress(button)}}
              >
                <Text style={{[
                  styles.buttonText,
                  ['÷', '×', '−', '+', '='].includes(button) ? styles.operatorText : null
                ]}}>
                  {"{button}"}
                </Text>
              </TouchableOpacity>
            ))}}
          </View>
        ))}}
      </View>
      {{props.children}}
    </View>
  );
}};

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    backgroundColor: '#000',
  }},
  display: {{
    flex: 1,
    justifyContent: 'flex-end',
    alignItems: 'flex-end',
    padding: 20,
    backgroundColor: '#000',
  }},
  displayText: {{
    fontSize: 64,
    color: '#fff',
    fontWeight: '200',
  }},
  buttonContainer: {{
    padding: 10,
  }},
  row: {{
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  }},
  button: {{
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#333',
    justifyContent: 'center',
    alignItems: 'center',
  }},
  zeroButton: {{
    width: 170,
  }},
  operatorButton: {{
    backgroundColor: '#ff9500',
  }},
  buttonText: {{
    fontSize: 32,
    color: '#fff',
    fontWeight: '400',
  }},
  operatorText: {{
    color: '#fff',
  }},
}});

export default {name};
'''
        }
    
    def _get_todo_templates(self) -> Dict:
        """Get todo-specific component templates"""
        return {
            "todoitem": lambda name: f'''import React from 'react';
import {{ View, Text, StyleSheet, TouchableOpacity }} from 'react-native';

const {name} = ({{ todo, onToggle, onDelete, ...props }}) => {{
  return (
    <View style={{[styles.container, todo?.completed && styles.completed]}}>
      <TouchableOpacity
        style={{styles.textContainer}}
        onPress={{() => onToggle && onToggle(todo?.id)}}
      >
        <Text style={{[styles.text, todo?.completed && styles.completedText]}}>
          {"{todo?.text || 'Todo item'}"}
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity
        style={{styles.deleteButton}}
        onPress={{() => onDelete && onDelete(todo?.id)}}
      >
        <Text style={{styles.deleteText}}>×</Text>
      </TouchableOpacity>
      {{props.children}}
    </View>
  );
}};

const styles = StyleSheet.create({{
  container: {{
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    marginVertical: 5,
    backgroundColor: '#fff',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: {{ width: 0, height: 1 }},
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 2,
  }},
  completed: {{
    backgroundColor: '#f8f9fa',
    opacity: 0.7,
  }},
  textContainer: {{
    flex: 1,
  }},
  text: {{
    fontSize: 16,
    color: '#333',
  }},
  completedText: {{
    textDecorationLine: 'line-through',
    color: '#666',
  }},
  deleteButton: {{
    padding: 10,
    marginLeft: 10,
  }},
  deleteText: {{
    fontSize: 20,
    color: '#ff4757',
    fontWeight: 'bold',
  }},
}});

export default {name};
''',
            "todolist": lambda name: f'''import React from 'react';
import {{ View, StyleSheet, ScrollView }} from 'react-native';

const {name} = ({{ children, ...props }}) => {{
  return (
    <ScrollView style={{styles.container}} contentContainerStyle={{styles.content}}>
      {{children}}
    </ScrollView>
  );
}};

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    backgroundColor: '#f8f9fa',
  }},
  content: {{
    padding: 10,
  }},
}});

export default {name};
'''
        }
    
    def _get_weather_templates(self) -> Dict:
        """Get weather-specific component templates"""
        return {
            "weathericon": lambda name: f'''import React from 'react';
import {{ View, Text, StyleSheet }} from 'react-native';

const {name} = ({{ condition = "sunny", size = 48, ...props }}) => {{
  const getWeatherIcon = (condition) => {{
    const icons = {{
      sunny: '☀️',
      cloudy: '☁️',
      rainy: '🌧️',
      snowy: '❄️',
      stormy: '⛈️'
    }};
    return icons[condition] || '🌤️';
  }};

  return (
    <View style={{styles.container}}>
      <Text style={{[styles.icon, {{ fontSize: size }}]}}>
        {"{getWeatherIcon(condition)}"}
      </Text>
      {{props.children}}
    </View>
  );
}};

const styles = StyleSheet.create({{
  container: {{
    alignItems: 'center',
  }},
  icon: {{
    fontSize: 48,
  }},
}});

export default {name};
''',
            "temperature": lambda name: f'''import React from 'react';
import {{ View, Text, StyleSheet }} from 'react-native';

const {name} = ({{ temperature = 20, unit = "°C", ...props }}) => {{
  return (
    <View style={{styles.container}}>
      <Text style={{styles.temperature}}>
        {"{temperature}{unit}"}
      </Text>
      {{props.children}}
    </View>
  );
}};

const styles = StyleSheet.create({{
  container: {{
    alignItems: 'center',
  }},
  temperature: {{
    fontSize: 48,
    fontWeight: 'bold',
    color: '#2c3e50',
  }},
}});

export default {name};
'''
        }
    
    def _get_generic_templates(self) -> Dict:
        """Get generic component templates"""
        return {}
    
    def _generate_generic_component(self, component_name: str) -> str:
        """Generate a generic component"""
        return f'''import React from 'react';
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
'''
    
    def _get_navigation_template(self) -> str:
        """Get navigation template"""
        return '''import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { View, Text, StyleSheet } from 'react-native';

const Stack = createStackNavigator();

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
          options={{ title: 'App' }}
        />
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
'''
    
    def _update_package_dependencies(self) -> bool:
        """Update package.json with required dependencies"""
        try:
            import json
            package_json_path = os.path.join(self.project_path, 'package.json')
            
            if os.path.exists(package_json_path):
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                # Add navigation dependencies
                nav_deps = {
                    "@react-navigation/native": "^6.0.0",
                    "@react-navigation/stack": "^6.0.0",
                    "react-native-screens": "~3.22.0",
                    "react-native-safe-area-context": "4.6.3"
                }
                
                package_data.setdefault("dependencies", {}).update(nav_deps)
                
                with open(package_json_path, 'w') as f:
                    json.dump(package_data, f, indent=2)
                
                return True
            
            return False
            
        except Exception:
            return False

def main():
    """Test the smart component generator"""
    print("🎨 Smart Component Generator Test")
    print("=" * 40)
    
    # This would normally be called from the main automation pipeline
    print("✅ Smart Component Generator ready for integration")

if __name__ == "__main__":
    main()