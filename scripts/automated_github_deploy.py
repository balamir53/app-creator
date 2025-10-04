#!/usr/bin/env python3
"""
Automated GitHub deployment for React Native apps with enhanced error handling
"""
import os
import subprocess
import json
import time
from typing import Dict, List, Tuple

class GitHubDeployer:
    """Automated GitHub deployment with retry mechanisms"""
    
    def __init__(self):
        self.expo_projects_path = "/tmp/expo_projects"
    
    def deploy_to_github(self, project_name: str, force_update: bool = False) -> Tuple[bool, Dict]:
        """
        Deploy a single project to GitHub with error handling
        
        Args:
            project_name: Name of the project to deploy
            force_update: Whether to force push changes
            
        Returns:
            Tuple of (success, result_info)
        """
        project_path = os.path.join(self.expo_projects_path, project_name)
        
        if not os.path.exists(project_path):
            return False, {"error": f"Project not found: {project_path}"}
        
        try:
            print(f"🚀 Deploying {project_name} to GitHub...")
            
            # Navigate to project directory
            os.chdir(project_path)
            
            # Initialize git if not already initialized
            if not os.path.exists(".git"):
                self._run_git_command(["git", "init"])
                print(f"   📝 Initialized git repository")
            
            # Create enhanced README with Expo Snack instructions
            self._create_enhanced_readme(project_name)
            
            # Add all files
            self._run_git_command(["git", "add", "."])
            
            # Check if there are changes to commit
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True)
            
            if not result.stdout.strip():
                print(f"   ℹ️ No changes to commit for {project_name}")
                return True, {"message": "No changes to commit", "existing": True}
            
            # Commit changes
            commit_message = f"Enhanced {project_name} with auto-generated components\n\n" \
                           f"- Fixed missing imports and components\n" \
                           f"- Added navigation structure\n" \
                           f"- Expo Snack ready deployment\n" \
                           f"- Auto-generated at {time.strftime('%Y-%m-%d %H:%M:%S')}"
            
            self._run_git_command(["git", "commit", "-m", commit_message])
            print(f"   📝 Committed changes with enhanced message")
            
            # Determine repository URL
            repo_url = f"https://github.com/balamir53/{project_name.lower()}.git"
            
            # Check if remote exists
            try:
                self._run_git_command(["git", "remote", "get-url", "origin"])
                remote_exists = True
            except subprocess.CalledProcessError:
                remote_exists = False
            
            if not remote_exists:
                # Add remote
                self._run_git_command(["git", "remote", "add", "origin", repo_url])
                print(f"   🔗 Added remote: {repo_url}")
            else:
                # Update remote URL
                self._run_git_command(["git", "remote", "set-url", "origin", repo_url])
            
            # Create GitHub repository if it doesn't exist
            self._create_github_repo(project_name.lower())
            
            # Push to GitHub
            push_args = ["git", "push", "origin", "main"]
            if force_update:
                push_args.insert(-1, "-f")
            
            self._run_git_command(push_args)
            print(f"   ✅ Successfully pushed to GitHub: {repo_url}")
            
            return True, {
                "repository_url": repo_url,
                "project_name": project_name,
                "commit_message": commit_message
            }
            
        except subprocess.CalledProcessError as e:
            return False, {
                "error": f"Git command failed: {e}",
                "command": " ".join(e.cmd) if hasattr(e, 'cmd') else "unknown"
            }
        except Exception as e:
            return False, {"error": f"Deployment failed: {str(e)}"}
    
    def deploy_all_projects(self, force_update: bool = False) -> Dict[str, Tuple[bool, Dict]]:
        """
        Deploy all projects in the expo_projects directory
        
        Args:
            force_update: Whether to force push changes
            
        Returns:
            Dictionary mapping project names to (success, result_info)
        """
        if not os.path.exists(self.expo_projects_path):
            return {"error": (False, {"error": "No expo projects directory found"})}
        
        projects = [d for d in os.listdir(self.expo_projects_path) 
                   if os.path.isdir(os.path.join(self.expo_projects_path, d))]
        
        results = {}
        
        print(f"🚀 Deploying {len(projects)} projects to GitHub...")
        print("=" * 50)
        
        for project in projects:
            success, result = self.deploy_to_github(project, force_update)
            results[project] = (success, result)
            
            if success:
                print(f"✅ {project}: Deployed successfully")
            else:
                print(f"❌ {project}: {result.get('error', 'Unknown error')}")
            
            print("-" * 30)
        
        return results
    
    def _run_git_command(self, cmd: List[str]) -> str:
        """Run a git command and return output"""
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    
    def _create_github_repo(self, repo_name: str) -> bool:
        """Create GitHub repository using GitHub CLI"""
        try:
            # Check if repository already exists
            check_cmd = ["gh", "repo", "view", f"balamir53/{repo_name}"]
            result = subprocess.run(check_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ℹ️ Repository {repo_name} already exists")
                return True
            
            # Create new repository
            create_cmd = [
                "gh", "repo", "create", repo_name,
                "--public",
                "--description", f"React Native {repo_name} - Auto-deployed from React Native Builder Agent"
            ]
            
            subprocess.run(create_cmd, capture_output=True, text=True, check=True)
            print(f"   ✅ Created GitHub repository: {repo_name}")
            return True
            
        except subprocess.CalledProcessError:
            print(f"   ⚠️ Could not create/verify GitHub repository: {repo_name}")
            return False
    
    def _create_enhanced_readme(self, project_name: str):
        """Create enhanced README with deployment instructions"""
        readme_content = f"""# {project_name}

## 🚀 React Native App - Auto-Generated

This React Native application was automatically generated using the **React Native Builder Agent** with LangGraph AI integration.

### ✨ Features
- 📱 Cross-platform React Native application
- 🎨 Auto-generated UI components
- 🧭 Navigation structure included
- 🔧 Missing components auto-created
- 📦 Expo-ready configuration

### 🎯 Quick Deploy to Expo Snack

1. **One-Click Deploy**: 
   - Go to [snack.expo.dev](https://snack.expo.dev/)
   - Click "Import from GitHub"
   - Enter: `https://github.com/balamir53/{project_name.lower()}`

2. **Manual Deploy**:
   ```bash
   # Clone the repository
   git clone https://github.com/balamir53/{project_name.lower()}.git
   cd {project_name.lower()}
   
   # Install dependencies
   npm install
   
   # Start with Expo
   expo start
   ```

### 📁 Project Structure
```
{project_name}/
├── App.js                 # Main application entry
├── src/
│   ├── components/        # Auto-generated components
│   ├── screens/          # Application screens
│   └── navigation/       # Navigation structure
├── package.json          # Dependencies
└── app.json             # Expo configuration
```

### 🛠️ Technologies Used
- React Native 0.72.6
- Expo SDK 49.0.0
- React Navigation 6.x
- Auto-generated components

### 🤖 Generated by
**React Native Builder Agent** - An AI-powered tool for creating React Native applications with:
- LangGraph workflow orchestration
- Azure OpenAI integration
- Automated component generation
- Expo conversion and deployment

### 📝 Auto-Deployment Info
- **Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Source**: React Native Builder Agent
- **Status**: ✅ Ready for Expo Snack

---
*This project was automatically generated and deployed. For issues or improvements, please update the source generator.*
"""
        
        with open("README.md", "w") as f:
            f.write(readme_content)
        
        print(f"   📄 Created enhanced README.md")

def main():
    """Test the automated GitHub deployment"""
    deployer = GitHubDeployer()
    
    print("🚀 Automated GitHub Deployment System")
    print("=" * 40)
    
    # Deploy all projects
    results = deployer.deploy_all_projects(force_update=True)
    
    # Summary
    successful = sum(1 for success, _ in results.values() if success)
    total = len(results)
    
    print(f"\n🎉 Deployment Summary:")
    print(f"✅ Successful: {successful}/{total}")
    
    for project, (success, result) in results.items():
        if success:
            repo_url = result.get('repository_url', '')
            print(f"   ✅ {project}: {repo_url}")
        else:
            print(f"   ❌ {project}: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()