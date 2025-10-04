#!/usr/bin/env python3
"""
Intelligent error detection and parsing for Expo Snack deployments
"""
import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ErrorType(Enum):
    MISSING_MODULE = "missing_module"
    MISSING_COMPONENT = "missing_component"
    IMPORT_ERROR = "import_error"
    SYNTAX_ERROR = "syntax_error"
    NAVIGATION_ERROR = "navigation_error"
    DEPENDENCY_ERROR = "dependency_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class ParsedError:
    """Structured representation of a parsed error"""
    type: ErrorType
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    missing_module: Optional[str] = None
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False

class ErrorParser:
    """Parse and categorize different types of Expo Snack errors"""
    
    def __init__(self):
        self.error_patterns = {
            # Missing module patterns
            ErrorType.MISSING_MODULE: [
                r"Unable to resolve module ['\"]([^'\"]+)['\"]",
                r"Module not found: Error: Can't resolve ['\"]([^'\"]+)['\"]",
                r"Cannot resolve dependency ['\"]([^'\"]+)['\"]"
            ],
            
            # Import error patterns
            ErrorType.IMPORT_ERROR: [
                r"SyntaxError: Cannot use import statement outside a module",
                r"Import error: (.+)",
                r"Failed to import ['\"]([^'\"]+)['\"]"
            ],
            
            # Navigation errors
            ErrorType.NAVIGATION_ERROR: [
                r"NavigationContainer.*not found",
                r"@react-navigation.*not found",
                r"createStackNavigator.*not found",
                r"Navigation.*is not defined"
            ],
            
            # Syntax errors
            ErrorType.SYNTAX_ERROR: [
                r"SyntaxError: (.+)",
                r"Unexpected token (.+)",
                r"Parse error: (.+)"
            ],
            
            # Dependency errors
            ErrorType.DEPENDENCY_ERROR: [
                r"Package ['\"]([^'\"]+)['\"] not found",
                r"Module ['\"]([^'\"]+)['\"] is not installed",
                r"Cannot find module ['\"]([^'\"]+)['\"]"
            ]
        }
    
    def parse_errors(self, error_messages: List[str]) -> List[ParsedError]:
        """
        Parse a list of error messages into structured ParsedError objects
        
        Args:
            error_messages: Raw error messages from Expo Snack
            
        Returns:
            List of ParsedError objects
        """
        parsed_errors = []
        
        for message in error_messages:
            parsed_error = self._parse_single_error(message)
            parsed_errors.append(parsed_error)
        
        return parsed_errors
    
    def _parse_single_error(self, message: str) -> ParsedError:
        """Parse a single error message"""
        message_clean = message.strip()
        
        # Try to match against known patterns
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_clean, re.IGNORECASE)
                if match:
                    return self._create_parsed_error(error_type, message_clean, match)
        
        # If no pattern matches, return unknown error
        return ParsedError(
            type=ErrorType.UNKNOWN_ERROR,
            message=message_clean,
            auto_fixable=False
        )
    
    def _create_parsed_error(self, error_type: ErrorType, message: str, match: re.Match) -> ParsedError:
        """Create a ParsedError with type-specific handling"""
        
        if error_type == ErrorType.MISSING_MODULE:
            missing_module = match.group(1)
            
            # Determine if it's a local component or external dependency
            if missing_module.startswith('./') or missing_module.startswith('../') or missing_module.startswith('src/'):
                return ParsedError(
                    type=ErrorType.MISSING_COMPONENT,
                    message=message,
                    missing_module=missing_module,
                    suggested_fix=f"Create missing component: {missing_module}",
                    auto_fixable=True
                )
            else:
                return ParsedError(
                    type=ErrorType.DEPENDENCY_ERROR,
                    message=message,
                    missing_module=missing_module,
                    suggested_fix=f"Add dependency: {missing_module}",
                    auto_fixable=True
                )
        
        elif error_type == ErrorType.NAVIGATION_ERROR:
            return ParsedError(
                type=error_type,
                message=message,
                suggested_fix="Add React Navigation dependencies and setup",
                auto_fixable=True
            )
        
        elif error_type == ErrorType.SYNTAX_ERROR:
            return ParsedError(
                type=error_type,
                message=message,
                suggested_fix="Fix syntax errors in code",
                auto_fixable=False
            )
        
        return ParsedError(
            type=error_type,
            message=message,
            auto_fixable=False
        )

class ErrorAnalyzer:
    """Analyze errors and provide fix recommendations"""
    
    def __init__(self):
        self.parser = ErrorParser()
    
    def analyze_deployment_errors(self, raw_errors: List[Dict]) -> Dict:
        """
        Analyze deployment errors and provide actionable insights
        
        Args:
            raw_errors: Raw error data from Expo Snack API
            
        Returns:
            Analysis report with categorized errors and fix suggestions
        """
        # Extract error messages
        error_messages = []
        for error in raw_errors:
            if isinstance(error, dict):
                error_messages.append(error.get('message', str(error)))
            else:
                error_messages.append(str(error))
        
        # Parse errors
        parsed_errors = self.parser.parse_errors(error_messages)
        
        # Categorize errors
        categorized = self._categorize_errors(parsed_errors)
        
        # Generate fix plan
        fix_plan = self._generate_fix_plan(parsed_errors)
        
        return {
            "total_errors": len(parsed_errors),
            "auto_fixable_errors": len([e for e in parsed_errors if e.auto_fixable]),
            "error_categories": categorized,
            "parsed_errors": parsed_errors,
            "fix_plan": fix_plan,
            "success_probability": self._estimate_success_probability(parsed_errors)
        }
    
    def _categorize_errors(self, errors: List[ParsedError]) -> Dict[str, int]:
        """Categorize errors by type"""
        categories = {}
        for error in errors:
            error_type = error.type.value
            categories[error_type] = categories.get(error_type, 0) + 1
        return categories
    
    def _generate_fix_plan(self, errors: List[ParsedError]) -> List[Dict]:
        """Generate step-by-step fix plan"""
        fix_steps = []
        
        # Group auto-fixable errors
        auto_fixable = [e for e in errors if e.auto_fixable]
        
        for error in auto_fixable:
            if error.type == ErrorType.MISSING_COMPONENT:
                fix_steps.append({
                    "step": f"Create missing component: {error.missing_module}",
                    "action": "create_component",
                    "target": error.missing_module,
                    "priority": "high"
                })
            
            elif error.type == ErrorType.DEPENDENCY_ERROR:
                fix_steps.append({
                    "step": f"Add dependency: {error.missing_module}",
                    "action": "add_dependency",
                    "target": error.missing_module,
                    "priority": "medium"
                })
            
            elif error.type == ErrorType.NAVIGATION_ERROR:
                fix_steps.append({
                    "step": "Fix navigation setup",
                    "action": "fix_navigation",
                    "target": "navigation_config",
                    "priority": "high"
                })
        
        # Manual fixes for non-auto-fixable errors
        manual_fixes = [e for e in errors if not e.auto_fixable]
        for error in manual_fixes:
            fix_steps.append({
                "step": f"Manual fix required: {error.type.value}",
                "action": "manual_review",
                "target": error.message,
                "priority": "low"
            })
        
        return sorted(fix_steps, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)
    
    def _estimate_success_probability(self, errors: List[ParsedError]) -> float:
        """Estimate probability of successful auto-fix"""
        if not errors:
            return 1.0
        
        auto_fixable_count = len([e for e in errors if e.auto_fixable])
        total_count = len(errors)
        
        # Base probability on ratio of auto-fixable errors
        base_probability = auto_fixable_count / total_count
        
        # Adjust based on error types
        for error in errors:
            if error.type in [ErrorType.SYNTAX_ERROR, ErrorType.UNKNOWN_ERROR]:
                base_probability *= 0.5  # Reduce probability for hard-to-fix errors
            elif error.type in [ErrorType.MISSING_COMPONENT, ErrorType.NAVIGATION_ERROR]:
                base_probability *= 1.2  # Increase for easily fixable errors
        
        return min(base_probability, 1.0)

def main():
    """Test the error analysis system"""
    analyzer = ErrorAnalyzer()
    
    # Sample error messages for testing
    test_errors = [
        {"message": "Unable to resolve module 'src/navigation/AppNavigator.js'"},
        {"message": "Unable to resolve module './Header'"},
        {"message": "Module not found: Error: Can't resolve '@react-navigation/native'"},
        {"message": "SyntaxError: Unexpected token '}'"},
    ]
    
    print("🔍 Error Analysis System Test")
    print("=" * 40)
    
    analysis = analyzer.analyze_deployment_errors(test_errors)
    
    print(f"📊 Analysis Results:")
    print(f"   Total Errors: {analysis['total_errors']}")
    print(f"   Auto-fixable: {analysis['auto_fixable_errors']}")
    print(f"   Success Probability: {analysis['success_probability']:.1%}")
    
    print(f"\n📋 Error Categories:")
    for category, count in analysis['error_categories'].items():
        print(f"   {category}: {count}")
    
    print(f"\n🔧 Fix Plan:")
    for i, step in enumerate(analysis['fix_plan'], 1):
        print(f"   {i}. {step['step']} ({step['priority']} priority)")

if __name__ == "__main__":
    main()