#!/usr/bin/env python3
"""
Expo Snack API Integration for automated deployment and error monitoring
"""
import requests
import json
import time
import os
import re
from typing import Dict, List, Optional, Tuple

class ExpoSnackAPI:
    """Client for interacting with Expo Snack API"""
    
    def __init__(self):
        self.base_url = "https://snack.expo.dev/api/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'React-Native-Builder-Agent/1.0'
        })
    
    def create_snack_from_github(self, github_url: str, app_name: str) -> Tuple[bool, Dict]:
        """
        Create a new Snack from GitHub repository
        
        Args:
            github_url: GitHub repository URL
            app_name: Name for the Snack
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Extract owner and repo from GitHub URL
            # https://github.com/balamir53/calculatorapp -> balamir53/calculatorapp
            match = re.search(r'github\.com/([^/]+)/([^/]+)', github_url)
            if not match:
                return False, {"error": "Invalid GitHub URL format"}
            
            owner, repo = match.groups()
            repo = repo.replace('.git', '')  # Remove .git if present
            
            payload = {
                "name": app_name,
                "description": f"React Native app: {app_name}",
                "files": {},
                "dependencies": {
                    "expo": "~49.0.0",
                    "react": "18.2.0",
                    "react-native": "0.72.6",
                    "@react-navigation/native": "^6.0.0",
                    "@react-navigation/stack": "^6.0.0"
                },
                "sdkVersion": "49.0.0"
            }
            
            # Get files from GitHub repository
            github_files = self._fetch_github_files(owner, repo)
            if github_files:
                payload["files"] = github_files
            
            response = self.session.post(f"{self.base_url}/snacks", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                snack_id = data.get('id')
                snack_url = f"https://snack.expo.dev/{snack_id}"
                
                return True, {
                    "snack_id": snack_id,
                    "url": snack_url,
                    "name": app_name,
                    "data": data
                }
            else:
                return False, {
                    "error": f"Failed to create Snack: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return False, {"error": f"Exception creating Snack: {str(e)}"}
    
    def check_snack_errors(self, snack_id: str) -> Tuple[bool, List[Dict]]:
        """
        Check for errors in a Snack deployment
        
        Args:
            snack_id: The Snack ID to check
            
        Returns:
            Tuple of (has_errors, error_list)
        """
        try:
            # Get Snack status and logs
            response = self.session.get(f"{self.base_url}/snacks/{snack_id}")
            
            if response.status_code != 200:
                return True, [{"type": "api_error", "message": f"Failed to fetch Snack: {response.status_code}"}]
            
            data = response.json()
            
            # Check for compilation errors, runtime errors, etc.
            errors = []
            
            # Parse different types of errors from Snack response
            if 'errors' in data:
                for error in data['errors']:
                    errors.append({
                        "type": "compilation_error",
                        "message": error.get('message', ''),
                        "file": error.get('loc', {}).get('filename', ''),
                        "line": error.get('loc', {}).get('line', 0)
                    })
            
            # Check for module resolution errors in logs
            logs = data.get('logs', [])
            for log in logs:
                if 'Unable to resolve module' in log.get('message', ''):
                    module_match = re.search(r"Unable to resolve module '([^']+)'", log['message'])
                    if module_match:
                        missing_module = module_match.group(1)
                        errors.append({
                            "type": "missing_module",
                            "message": log['message'],
                            "missing_module": missing_module,
                            "file": log.get('filename', '')
                        })
            
            return len(errors) > 0, errors
            
        except Exception as e:
            return True, [{"type": "exception", "message": f"Error checking Snack: {str(e)}"}]
    
    def _fetch_github_files(self, owner: str, repo: str) -> Dict:
        """
        Fetch files from GitHub repository using GitHub API
        
        Args:
            owner: GitHub repository owner
            repo: Repository name
            
        Returns:
            Dictionary of files for Snack
        """
        try:
            github_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
            
            files = {}
            
            # Fetch main files
            response = requests.get(github_api_url)
            if response.status_code == 200:
                contents = response.json()
                
                for item in contents:
                    if item['type'] == 'file' and item['name'].endswith('.js'):
                        file_response = requests.get(item['download_url'])
                        if file_response.status_code == 200:
                            files[item['name']] = {
                                "type": "CODE",
                                "contents": file_response.text
                            }
            
            # Fetch src directory
            src_response = requests.get(f"{github_api_url}/src")
            if src_response.status_code == 200:
                self._fetch_directory_files(f"{github_api_url}/src", "src", files)
            
            return files
            
        except Exception as e:
            print(f"   ⚠️ Error fetching GitHub files: {str(e)}")
            return {}
    
    def _fetch_directory_files(self, api_url: str, path_prefix: str, files: Dict):
        """Recursively fetch files from a directory"""
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                contents = response.json()
                
                for item in contents:
                    file_path = f"{path_prefix}/{item['name']}"
                    
                    if item['type'] == 'file' and item['name'].endswith('.js'):
                        file_response = requests.get(item['download_url'])
                        if file_response.status_code == 200:
                            files[file_path] = {
                                "type": "CODE",
                                "contents": file_response.text
                            }
                    elif item['type'] == 'dir':
                        self._fetch_directory_files(item['url'], file_path, files)
                        
        except Exception as e:
            print(f"   ⚠️ Error fetching directory {path_prefix}: {str(e)}")

    def wait_for_deployment(self, snack_id: str, timeout: int = 60) -> Tuple[bool, List[Dict]]:
        """
        Wait for Snack deployment to complete and check for errors
        
        Args:
            snack_id: The Snack ID to monitor
            timeout: Maximum time to wait in seconds
            
        Returns:
            Tuple of (success, errors)
        """
        print(f"   ⏳ Waiting for Snack deployment to complete...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            has_errors, errors = self.check_snack_errors(snack_id)
            
            if not has_errors:
                print(f"   ✅ Deployment successful!")
                return True, []
            
            # Check if errors are deployment-related (temporary) or actual code errors
            actual_errors = [e for e in errors if e['type'] != 'api_error']
            if actual_errors:
                print(f"   ❌ Found {len(actual_errors)} errors in deployment")
                return False, actual_errors
            
            time.sleep(5)  # Wait 5 seconds before checking again
        
        print(f"   ⏰ Timeout waiting for deployment")
        return False, [{"type": "timeout", "message": "Deployment timeout"}]

def main():
    """Test the Expo Snack API integration"""
    api = ExpoSnackAPI()
    
    # Test with the calculator app
    github_url = "https://github.com/balamir53/calculatorapp"
    app_name = "CalculatorApp-Test"
    
    print("🚀 Testing Expo Snack API Integration")
    print("=" * 40)
    
    print(f"📱 Creating Snack from GitHub: {github_url}")
    success, result = api.create_snack_from_github(github_url, app_name)
    
    if success:
        snack_id = result['snack_id']
        snack_url = result['url']
        
        print(f"✅ Snack created successfully!")
        print(f"   🆔 Snack ID: {snack_id}")
        print(f"   🔗 URL: {snack_url}")
        
        # Wait for deployment and check for errors
        deploy_success, errors = api.wait_for_deployment(snack_id)
        
        if deploy_success:
            print("🎉 Deployment completed successfully!")
        else:
            print("❌ Deployment failed with errors:")
            for error in errors:
                print(f"   🐛 {error['type']}: {error['message']}")
    else:
        print(f"❌ Failed to create Snack: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()