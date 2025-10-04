#!/usr/bin/env python3
"""
Automated deployment pipeline with error detection and auto-fixing
GitHub → Expo Snack → Error Detection → Auto-Fix → Retry
"""
import os
import time
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Import our custom modules
from expo_snack_api import ExpoSnackAPI
from automated_github_deploy import GitHubDeployer
from error_analyzer import ErrorAnalyzer, ParsedError
from smart_component_generator import SmartComponentGenerator

@dataclass
class DeploymentResult:
    """Result of a deployment attempt"""
    success: bool
    github_url: str = ""
    snack_url: str = ""
    snack_id: str = ""
    errors: List[ParsedError] = None
    fixes_applied: Dict[str, bool] = None
    attempts: int = 0

class AutomatedDeploymentPipeline:
    """Complete automated deployment pipeline with error fixing"""
    
    def __init__(self, max_retry_attempts: int = 3):
        self.github_deployer = GitHubDeployer()
        self.snack_api = ExpoSnackAPI()
        self.error_analyzer = ErrorAnalyzer()
        self.max_retry_attempts = max_retry_attempts
    
    def deploy_project_with_auto_fix(self, project_name: str) -> DeploymentResult:
        """
        Deploy a project with automatic error detection and fixing
        
        Args:
            project_name: Name of the project to deploy
            
        Returns:
            DeploymentResult with full deployment information
        """
        print(f"🚀 Starting automated deployment for {project_name}")
        print("=" * 60)
        
        result = DeploymentResult(success=False, errors=[], fixes_applied={})
        
        for attempt in range(1, self.max_retry_attempts + 1):
            result.attempts = attempt
            
            print(f"\n📋 Deployment Attempt {attempt}/{self.max_retry_attempts}")
            print("-" * 40)
            
            # Step 1: Deploy to GitHub
            github_success, github_result = self._deploy_to_github(project_name)
            if not github_success:
                print(f"❌ GitHub deployment failed: {github_result.get('error', 'Unknown error')}")
                continue
            
            result.github_url = github_result.get('repository_url', '')
            print(f"✅ GitHub deployment successful: {result.github_url}")
            
            # Step 2: Deploy to Expo Snack
            snack_success, snack_result = self._deploy_to_snack(result.github_url, project_name)
            if not snack_success:
                print(f"❌ Snack deployment failed: {snack_result.get('error', 'Unknown error')}")
                continue
            
            result.snack_url = snack_result.get('url', '')
            result.snack_id = snack_result.get('snack_id', '')
            print(f"✅ Snack deployment successful: {result.snack_url}")
            
            # Step 3: Check for errors
            deployment_success, errors = self._check_deployment_errors(result.snack_id)
            if deployment_success:
                result.success = True
                print("🎉 Deployment completed successfully with no errors!")
                break
            
            # Step 4: Analyze and fix errors
            print(f"🔍 Found errors, analyzing for auto-fix...")
            analysis = self.error_analyzer.analyze_deployment_errors(errors)
            result.errors = analysis['parsed_errors']
            
            print(f"📊 Error Analysis:")
            print(f"   Total errors: {analysis['total_errors']}")
            print(f"   Auto-fixable: {analysis['auto_fixable_errors']}")
            print(f"   Success probability: {analysis['success_probability']:.1%}")
            
            if analysis['auto_fixable_errors'] == 0:
                print("❌ No auto-fixable errors found. Manual intervention required.")
                break
            
            # Step 5: Apply fixes
            fixes_applied = self._apply_auto_fixes(project_name, result.errors)
            result.fixes_applied.update(fixes_applied)
            
            successful_fixes = sum(1 for success in fixes_applied.values() if success)
            print(f"🔧 Applied {successful_fixes}/{len(fixes_applied)} fixes")
            
            if successful_fixes == 0:
                print("❌ No fixes could be applied. Manual intervention required.")
                break
            
            print(f"🔄 Retrying deployment with fixes...")
            time.sleep(2)  # Brief pause before retry
        
        # Final result summary
        self._print_deployment_summary(result)
        return result
    
    def deploy_all_projects_with_auto_fix(self) -> Dict[str, DeploymentResult]:
        """Deploy all projects with auto-fixing"""
        expo_projects_path = "/tmp/expo_projects"
        
        if not os.path.exists(expo_projects_path):
            print("❌ No expo projects directory found")
            return {}
        
        projects = [d for d in os.listdir(expo_projects_path) 
                   if os.path.isdir(os.path.join(expo_projects_path, d))]
        
        if not projects:
            print("❌ No projects found in expo projects directory")
            return {}
        
        print(f"🚀 Automated deployment pipeline for {len(projects)} projects")
        print("=" * 60)
        
        results = {}
        
        for project in projects:
            print(f"\n🎯 Processing {project}")
            result = self.deploy_project_with_auto_fix(project)
            results[project] = result
            
            print(f"\n{'✅' if result.success else '❌'} {project}: {'SUCCESS' if result.success else 'FAILED'}")
            print("-" * 60)
        
        # Overall summary
        self._print_overall_summary(results)
        return results
    
    def _deploy_to_github(self, project_name: str) -> Tuple[bool, Dict]:
        """Deploy project to GitHub"""
        print("📤 Deploying to GitHub...")
        return self.github_deployer.deploy_to_github(project_name, force_update=True)
    
    def _deploy_to_snack(self, github_url: str, project_name: str) -> Tuple[bool, Dict]:
        """Deploy project to Expo Snack"""
        print("📱 Deploying to Expo Snack...")
        return self.snack_api.create_snack_from_github(github_url, project_name)
    
    def _check_deployment_errors(self, snack_id: str) -> Tuple[bool, List[Dict]]:
        """Check for deployment errors"""
        print("🔍 Checking for deployment errors...")
        return self.snack_api.wait_for_deployment(snack_id, timeout=60)
    
    def _apply_auto_fixes(self, project_name: str, errors: List[ParsedError]) -> Dict[str, bool]:
        """Apply automatic fixes for detected errors"""
        print("🔧 Applying automatic fixes...")
        
        project_path = os.path.join("/tmp/expo_projects", project_name)
        component_generator = SmartComponentGenerator(project_path)
        
        return component_generator.fix_errors_with_components(errors)
    
    def _print_deployment_summary(self, result: DeploymentResult):
        """Print summary of deployment result"""
        print(f"\n📋 Deployment Summary")
        print("=" * 30)
        print(f"Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
        print(f"Attempts: {result.attempts}/{self.max_retry_attempts}")
        
        if result.github_url:
            print(f"GitHub: {result.github_url}")
        
        if result.snack_url:
            print(f"Expo Snack: {result.snack_url}")
        
        if result.errors:
            print(f"Errors found: {len(result.errors)}")
            for error in result.errors:
                print(f"  - {error.type.value}: {error.message[:50]}...")
        
        if result.fixes_applied:
            successful_fixes = sum(1 for success in result.fixes_applied.values() if success)
            print(f"Fixes applied: {successful_fixes}/{len(result.fixes_applied)}")
    
    def _print_overall_summary(self, results: Dict[str, DeploymentResult]):
        """Print overall summary of all deployments"""
        print(f"\n🎉 Overall Deployment Summary")
        print("=" * 50)
        
        successful = sum(1 for result in results.values() if result.success)
        total = len(results)
        
        print(f"Success Rate: {successful}/{total} ({successful/total:.1%})")
        
        print(f"\n📱 Successful Deployments:")
        for project, result in results.items():
            if result.success:
                print(f"  ✅ {project}: {result.snack_url}")
        
        print(f"\n❌ Failed Deployments:")
        for project, result in results.items():
            if not result.success:
                error_count = len(result.errors) if result.errors else 0
                print(f"  ❌ {project}: {error_count} errors after {result.attempts} attempts")

def main():
    """Run the automated deployment pipeline"""
    pipeline = AutomatedDeploymentPipeline(max_retry_attempts=3)
    
    print("🚀 Automated Deployment Pipeline with Auto-Fix")
    print("=" * 60)
    print("Features:")
    print("  📤 Automated GitHub deployment")
    print("  📱 Expo Snack integration")
    print("  🔍 Error detection and analysis")
    print("  🔧 Automatic component generation")
    print("  🔄 Retry mechanism with fixes")
    print("=" * 60)
    
    # Deploy all projects
    results = pipeline.deploy_all_projects_with_auto_fix()
    
    # Save results for future reference
    results_file = "/tmp/deployment_results.json"
    try:
        serializable_results = {}
        for project, result in results.items():
            serializable_results[project] = {
                "success": result.success,
                "github_url": result.github_url,
                "snack_url": result.snack_url,
                "attempts": result.attempts,
                "error_count": len(result.errors) if result.errors else 0
            }
        
        with open(results_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"\n📄 Results saved to: {results_file}")
        
    except Exception as e:
        print(f"⚠️ Could not save results: {str(e)}")

if __name__ == "__main__":
    main()