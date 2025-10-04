#!/usr/bin/env python3
"""
Comprehensive logging and monitoring for the automated deployment pipeline
"""
import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class DeploymentMetrics:
    """Metrics for deployment tracking"""
    project_name: str
    start_time: datetime
    end_time: datetime = None
    total_duration: float = 0.0
    github_deploy_time: float = 0.0
    snack_deploy_time: float = 0.0
    error_analysis_time: float = 0.0
    fix_application_time: float = 0.0
    attempts: int = 0
    errors_found: int = 0
    fixes_applied: int = 0
    success: bool = False

class DeploymentLogger:
    """Enhanced logging system for deployment pipeline"""
    
    def __init__(self, log_directory: str = "/tmp/deployment_logs"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)
        
        # Create session ID for this deployment run
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Setup loggers
        self.setup_loggers()
        
        # Metrics tracking
        self.deployment_metrics: Dict[str, DeploymentMetrics] = {}
        self.session_start_time = datetime.now()
    
    def setup_loggers(self):
        """Setup different types of loggers"""
        
        # Main deployment logger
        self.main_logger = logging.getLogger('deployment')
        self.main_logger.setLevel(logging.INFO)
        
        # Error logger
        self.error_logger = logging.getLogger('errors')
        self.error_logger.setLevel(logging.ERROR)
        
        # Metrics logger
        self.metrics_logger = logging.getLogger('metrics')
        self.metrics_logger.setLevel(logging.INFO)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        )
        simple_formatter = logging.Formatter('%(asctime)s | %(message)s')
        
        # Main log file
        main_handler = logging.FileHandler(
            self.log_directory / f"deployment_{self.session_id}.log"
        )
        main_handler.setFormatter(detailed_formatter)
        self.main_logger.addHandler(main_handler)
        
        # Error log file
        error_handler = logging.FileHandler(
            self.log_directory / f"errors_{self.session_id}.log"
        )
        error_handler.setFormatter(detailed_formatter)
        self.error_logger.addHandler(error_handler)
        
        # Metrics log file
        metrics_handler = logging.FileHandler(
            self.log_directory / f"metrics_{self.session_id}.log"
        )
        metrics_handler.setFormatter(simple_formatter)
        self.metrics_logger.addHandler(metrics_handler)
        
        # Console handler for main logger
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(simple_formatter)
        self.main_logger.addHandler(console_handler)
    
    def start_project_deployment(self, project_name: str):
        """Start tracking a project deployment"""
        self.deployment_metrics[project_name] = DeploymentMetrics(
            project_name=project_name,
            start_time=datetime.now()
        )
        
        self.main_logger.info(f"🚀 Started deployment for {project_name}")
        self.metrics_logger.info(f"PROJECT_START | {project_name}")
    
    def log_github_deployment(self, project_name: str, success: bool, duration: float, details: Dict = None):
        """Log GitHub deployment results"""
        status = "SUCCESS" if success else "FAILED"
        self.main_logger.info(f"📤 GitHub deployment {status} for {project_name} ({duration:.2f}s)")
        
        if project_name in self.deployment_metrics:
            self.deployment_metrics[project_name].github_deploy_time = duration
        
        if not success and details:
            self.error_logger.error(f"GitHub deployment failed for {project_name}: {details}")
        
        self.metrics_logger.info(f"GITHUB_DEPLOY | {project_name} | {status} | {duration:.2f}s")
    
    def log_snack_deployment(self, project_name: str, success: bool, duration: float, snack_url: str = "", details: Dict = None):
        """Log Expo Snack deployment results"""
        status = "SUCCESS" if success else "FAILED"
        self.main_logger.info(f"📱 Snack deployment {status} for {project_name} ({duration:.2f}s)")
        
        if success and snack_url:
            self.main_logger.info(f"   🔗 Snack URL: {snack_url}")
        
        if project_name in self.deployment_metrics:
            self.deployment_metrics[project_name].snack_deploy_time = duration
        
        if not success and details:
            self.error_logger.error(f"Snack deployment failed for {project_name}: {details}")
        
        self.metrics_logger.info(f"SNACK_DEPLOY | {project_name} | {status} | {duration:.2f}s")
    
    def log_error_analysis(self, project_name: str, errors_found: int, auto_fixable: int, duration: float):
        """Log error analysis results"""
        self.main_logger.info(f"🔍 Error analysis for {project_name}: {errors_found} errors, {auto_fixable} auto-fixable ({duration:.2f}s)")
        
        if project_name in self.deployment_metrics:
            metrics = self.deployment_metrics[project_name]
            metrics.error_analysis_time = duration
            metrics.errors_found = errors_found
        
        self.metrics_logger.info(f"ERROR_ANALYSIS | {project_name} | {errors_found} | {auto_fixable} | {duration:.2f}s")
    
    def log_fix_application(self, project_name: str, fixes_attempted: int, fixes_successful: int, duration: float):
        """Log fix application results"""
        self.main_logger.info(f"🔧 Fix application for {project_name}: {fixes_successful}/{fixes_attempted} successful ({duration:.2f}s)")
        
        if project_name in self.deployment_metrics:
            metrics = self.deployment_metrics[project_name]
            metrics.fix_application_time = duration
            metrics.fixes_applied = fixes_successful
        
        self.metrics_logger.info(f"FIX_APPLICATION | {project_name} | {fixes_successful}/{fixes_attempted} | {duration:.2f}s")
    
    def log_deployment_attempt(self, project_name: str, attempt: int, max_attempts: int):
        """Log deployment attempt"""
        self.main_logger.info(f"📋 Deployment attempt {attempt}/{max_attempts} for {project_name}")
        
        if project_name in self.deployment_metrics:
            self.deployment_metrics[project_name].attempts = attempt
        
        self.metrics_logger.info(f"ATTEMPT | {project_name} | {attempt}/{max_attempts}")
    
    def finish_project_deployment(self, project_name: str, success: bool):
        """Finish tracking a project deployment"""
        if project_name not in self.deployment_metrics:
            return
        
        metrics = self.deployment_metrics[project_name]
        metrics.end_time = datetime.now()
        metrics.total_duration = (metrics.end_time - metrics.start_time).total_seconds()
        metrics.success = success
        
        status = "SUCCESS" if success else "FAILED"
        self.main_logger.info(f"🏁 Deployment {status} for {project_name} (Total: {metrics.total_duration:.2f}s)")
        
        self.metrics_logger.info(f"PROJECT_END | {project_name} | {status} | {metrics.total_duration:.2f}s")
    
    def log_error_details(self, project_name: str, errors: List[Any]):
        """Log detailed error information"""
        self.error_logger.error(f"Detailed errors for {project_name}:")
        
        for i, error in enumerate(errors, 1):
            if hasattr(error, 'type') and hasattr(error, 'message'):
                self.error_logger.error(f"  {i}. {error.type.value}: {error.message}")
            else:
                self.error_logger.error(f"  {i}. {str(error)}")
    
    def generate_session_report(self) -> Dict:
        """Generate comprehensive session report"""
        session_end_time = datetime.now()
        session_duration = (session_end_time - self.session_start_time).total_seconds()
        
        total_projects = len(self.deployment_metrics)
        successful_projects = sum(1 for m in self.deployment_metrics.values() if m.success)
        
        report = {
            "session_id": self.session_id,
            "session_start": self.session_start_time.isoformat(),
            "session_end": session_end_time.isoformat(),
            "session_duration": session_duration,
            "total_projects": total_projects,
            "successful_projects": successful_projects,
            "success_rate": successful_projects / total_projects if total_projects > 0 else 0,
            "projects": {}
        }
        
        # Add project details
        for project_name, metrics in self.deployment_metrics.items():
            report["projects"][project_name] = asdict(metrics)
            # Convert datetime objects to ISO format
            if metrics.start_time:
                report["projects"][project_name]["start_time"] = metrics.start_time.isoformat()
            if metrics.end_time:
                report["projects"][project_name]["end_time"] = metrics.end_time.isoformat()
        
        # Save report to file
        report_file = self.log_directory / f"session_report_{self.session_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.main_logger.info(f"📊 Session report saved: {report_file}")
        
        return report
    
    def print_session_summary(self):
        """Print a user-friendly session summary"""
        report = self.generate_session_report()
        
        print(f"\n📊 Deployment Session Summary")
        print("=" * 50)
        print(f"Session ID: {report['session_id']}")
        print(f"Duration: {report['session_duration']:.1f} seconds")
        print(f"Success Rate: {report['successful_projects']}/{report['total_projects']} ({report['success_rate']:.1%})")
        
        print(f"\n📈 Project Performance:")
        for project_name, metrics in report['projects'].items():
            status = "✅" if metrics['success'] else "❌"
            print(f"  {status} {project_name}: {metrics['total_duration']:.1f}s, {metrics['attempts']} attempts")
        
        print(f"\n📁 Logs saved to: {self.log_directory}")
        
        # Performance insights
        if report['total_projects'] > 0:
            avg_duration = sum(m['total_duration'] for m in report['projects'].values()) / report['total_projects']
            print(f"\n⏱️ Average deployment time: {avg_duration:.1f}s")
            
            total_errors = sum(m['errors_found'] for m in report['projects'].values())
            total_fixes = sum(m['fixes_applied'] for m in report['projects'].values())
            if total_errors > 0:
                print(f"🔧 Fix success rate: {total_fixes}/{total_errors} ({total_fixes/total_errors:.1%})")

def create_deployment_monitor():
    """Factory function to create a deployment monitor"""
    return DeploymentLogger()

def main():
    """Test the logging system"""
    logger = DeploymentLogger()
    
    print("📝 Testing Deployment Logger")
    print("=" * 40)
    
    # Simulate a deployment session
    logger.start_project_deployment("TestApp")
    time.sleep(0.1)
    logger.log_github_deployment("TestApp", True, 2.5)
    time.sleep(0.1)
    logger.log_snack_deployment("TestApp", False, 1.2, details={"error": "Test error"})
    time.sleep(0.1)
    logger.log_error_analysis("TestApp", 3, 2, 0.8)
    time.sleep(0.1)
    logger.log_fix_application("TestApp", 2, 2, 1.5)
    time.sleep(0.1)
    logger.finish_project_deployment("TestApp", True)
    
    # Generate report
    logger.print_session_summary()

if __name__ == "__main__":
    main()