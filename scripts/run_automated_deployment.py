#!/usr/bin/env python3
"""
Enhanced Automated Deployment Pipeline Launcher
Integrates all components with comprehensive logging
"""
import sys
import time
from typing import Dict

# Import our automation modules
from automated_deployment_pipeline import AutomatedDeploymentPipeline, DeploymentResult
from deployment_logger import DeploymentLogger
from error_analyzer import ParsedError

class EnhancedDeploymentPipeline:
    """Enhanced pipeline with integrated logging"""
    
    def __init__(self, max_retry_attempts: int = 3):
        self.logger = DeploymentLogger()
        self.pipeline = AutomatedDeploymentPipeline(max_retry_attempts)
        self.max_retry_attempts = max_retry_attempts
    
    def deploy_project_with_monitoring(self, project_name: str) -> DeploymentResult:
        """Deploy project with comprehensive monitoring"""
        self.logger.start_project_deployment(project_name)
        
        result = DeploymentResult(success=False, errors=[], fixes_applied={})
        
        for attempt in range(1, self.max_retry_attempts + 1):
            self.logger.log_deployment_attempt(project_name, attempt, self.max_retry_attempts)
            result.attempts = attempt
            
            # GitHub deployment with timing
            start_time = time.time()
            github_success, github_result = self.pipeline._deploy_to_github(project_name)
            github_duration = time.time() - start_time
            
            self.logger.log_github_deployment(
                project_name, github_success, github_duration, 
                github_result if not github_success else None
            )
            
            if not github_success:
                continue
            
            result.github_url = github_result.get('repository_url', '')
            
            # Snack deployment with timing
            start_time = time.time()
            snack_success, snack_result = self.pipeline._deploy_to_snack(result.github_url, project_name)
            snack_duration = time.time() - start_time
            
            self.logger.log_snack_deployment(
                project_name, snack_success, snack_duration,
                snack_result.get('url', '') if snack_success else "",
                snack_result if not snack_success else None
            )
            
            if not snack_success:
                continue
            
            result.snack_url = snack_result.get('url', '')
            result.snack_id = snack_result.get('snack_id', '')
            
            # Error checking with timing
            start_time = time.time()
            deployment_success, errors = self.pipeline._check_deployment_errors(result.snack_id)
            error_check_duration = time.time() - start_time
            
            if deployment_success:
                result.success = True
                self.logger.log_error_analysis(project_name, 0, 0, error_check_duration)
                break
            
            # Error analysis with timing
            start_time = time.time()
            analysis = self.pipeline.error_analyzer.analyze_deployment_errors(errors)
            error_analysis_duration = time.time() - start_time
            
            result.errors = analysis['parsed_errors']
            
            self.logger.log_error_analysis(
                project_name, 
                analysis['total_errors'], 
                analysis['auto_fixable_errors'], 
                error_analysis_duration
            )
            
            # Log detailed errors
            self.logger.log_error_details(project_name, result.errors)
            
            if analysis['auto_fixable_errors'] == 0:
                break
            
            # Apply fixes with timing
            start_time = time.time()
            fixes_applied = self.pipeline._apply_auto_fixes(project_name, result.errors)
            fix_duration = time.time() - start_time
            
            result.fixes_applied.update(fixes_applied)
            successful_fixes = sum(1 for success in fixes_applied.values() if success)
            
            self.logger.log_fix_application(
                project_name, 
                len(fixes_applied), 
                successful_fixes, 
                fix_duration
            )
            
            if successful_fixes == 0:
                break
        
        self.logger.finish_project_deployment(project_name, result.success)
        return result
    
    def deploy_all_projects_with_monitoring(self) -> Dict[str, DeploymentResult]:
        """Deploy all projects with comprehensive monitoring"""
        import os
        
        expo_projects_path = "/tmp/expo_projects"
        
        if not os.path.exists(expo_projects_path):
            self.logger.main_logger.error("No expo projects directory found")
            return {}
        
        projects = [d for d in os.listdir(expo_projects_path) 
                   if os.path.isdir(os.path.join(expo_projects_path, d))]
        
        if not projects:
            self.logger.main_logger.error("No projects found in expo projects directory")
            return {}
        
        self.logger.main_logger.info(f"Starting automated deployment for {len(projects)} projects")
        
        results = {}
        
        for project in projects:
            self.logger.main_logger.info(f"Processing {project}")
            result = self.deploy_project_with_monitoring(project)
            results[project] = result
        
        # Generate session report
        self.logger.print_session_summary()
        
        return results

def main():
    """Main entry point for the enhanced deployment pipeline"""
    print("🚀 Enhanced Automated Deployment Pipeline")
    print("=" * 60)
    print("🎯 Features:")
    print("  📤 Automated GitHub deployment")
    print("  📱 Expo Snack integration with error monitoring")
    print("  🔍 Intelligent error detection and parsing")
    print("  🔧 Automatic component generation and fixes")
    print("  🔄 Smart retry mechanism with progressive fixes")
    print("  📊 Comprehensive logging and performance metrics")
    print("  📈 Session reports and analytics")
    print("=" * 60)
    
    # Get command line arguments
    max_retries = 3
    if len(sys.argv) > 1:
        try:
            max_retries = int(sys.argv[1])
        except ValueError:
            print("⚠️ Invalid retry count, using default: 3")
    
    print(f"🔄 Maximum retry attempts: {max_retries}")
    print()
    
    # Create and run pipeline
    pipeline = EnhancedDeploymentPipeline(max_retry_attempts=max_retries)
    
    try:
        results = pipeline.deploy_all_projects_with_monitoring()
        
        # Final summary
        successful = sum(1 for result in results.values() if result.success)
        total = len(results)
        
        print(f"\n🎉 Final Results:")
        print(f"✅ Success: {successful}/{total} projects")
        
        if successful > 0:
            print(f"\n📱 Live Expo Snack URLs:")
            for project, result in results.items():
                if result.success and result.snack_url:
                    print(f"  🔗 {project}: {result.snack_url}")
        
        if successful < total:
            print(f"\n❌ Failed Projects:")
            for project, result in results.items():
                if not result.success:
                    error_count = len(result.errors) if result.errors else 0
                    print(f"  ❌ {project}: {error_count} errors after {result.attempts} attempts")
        
        print(f"\n📊 Logs and metrics saved to: /tmp/deployment_logs/")
        
        return 0 if successful == total else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Deployment interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Deployment failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)