"""
Allure report service for generating professional test reports
"""
import json
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from models.test_models import TestResult


class AllureReportService:
    def __init__(self, output_dir: str):
        self.allure_results_dir = Path(output_dir) / "allure-results"
        self.allure_results_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, test_result: TestResult, video_path: str = None):
        """Generate Allure-compatible JSON report"""
        try:
            print(f"\n📊 Generating Allure report for: {test_result.ScenarioName}")
            
            test_uuid = str(uuid.uuid4())
            history_id = self._get_history_id(test_result.ScenarioName)
            
            # Create main test result
            allure_result = {
                "uuid": test_uuid,
                "historyId": history_id,
                "name": test_result.ScenarioName,
                "description": f"Automated test execution for {test_result.ScenarioName}",
                "status": "passed" if test_result.Status == "Passed" else "failed",
                "statusDetails": {
                    "message": test_result.ErrorMessage or "",
                    "trace": test_result.StackTrace or ""
                },
                "stage": "finished",
                "start": int(test_result.StartTime.timestamp() * 1000),
                "stop": int(test_result.EndTime.timestamp() * 1000) if test_result.EndTime else int(datetime.now().timestamp() * 1000),
                "labels": [
                    {"name": "suite", "value": "Playwright Tests"},
                    {"name": "framework", "value": "Playwright"},
                    {"name": "language", "value": "Python"},
                    {"name": "feature", "value": test_result.ScenarioName},
                    {"name": "severity", "value": "critical"}
                ],
                "links": [],
                "parameters": [],
                "steps": self._generate_steps(test_result),
                "attachments": self._generate_attachments(test_result, video_path)
            }
            
            # Write result file
            result_file = self.allure_results_dir / f"{test_uuid}-result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(allure_result, f, indent=2, ensure_ascii=False)
            
            # Generate environment info
            self._generate_environment_info()
            
            # Generate categories
            self._generate_categories()
            
            print(f"✅ Allure Results: {self.allure_results_dir}")
            
            # Show console logs summary
            if test_result.ConsoleLogs:
                error_count = sum(1 for log in test_result.ConsoleLogs if log.Type == "error")
                warning_count = sum(1 for log in test_result.ConsoleLogs if log.Type == "warning")
                print(f"  📝 Console Logs: {len(test_result.ConsoleLogs)} total ({error_count} errors, {warning_count} warnings)")
            
            print(f"\n💡 To view Allure report, run: allure serve \"{self.allure_results_dir}\"")
        
        except Exception as e:
            print(f"❌ Failed to generate Allure report: {e}")

    def _generate_steps(self, test_result: TestResult):
        """Generate Allure steps from test results"""
        steps = []
        
        for step_result in test_result.StepResults:
            sub_steps = []
            
            for action_result in step_result.ActionResults:
                action_attachments = []
                
                # Add screenshot as attachment
                if action_result.ScreenshotPath and Path(action_result.ScreenshotPath).exists():
                    screenshot_name = self._copy_attachment(action_result.ScreenshotPath, "image/png")
                    if screenshot_name:
                        action_attachments.append({
                            "name": f"Screenshot: {action_result.Element}",
                            "source": screenshot_name,
                            "type": "image/png"
                        })
                
                sub_steps.append({
                    "name": f"{action_result.Action} - {action_result.Element}",
                    "status": "passed" if action_result.Status == "Passed" else "failed",
                    "statusDetails": {
                        "message": action_result.ErrorMessage or ""
                    },
                    "stage": "finished",
                    "start": int(action_result.Timestamp.timestamp() * 1000),
                    "stop": int((action_result.Timestamp.timestamp() + 0.5) * 1000),
                    "steps": [],
                    "attachments": action_attachments
                })
            
            steps.append({
                "name": f"Step {step_result.StepOrder}: {step_result.PageName}",
                "status": "passed" if step_result.Status == "Passed" else "failed",
                "statusDetails": {
                    "message": step_result.ErrorMessage or ""
                },
                "stage": "finished",
                "start": int(step_result.StartTime.timestamp() * 1000),
                "stop": int(step_result.EndTime.timestamp() * 1000) if step_result.EndTime else int(datetime.now().timestamp() * 1000),
                "steps": sub_steps,
                "attachments": []
            })
        
        return steps

    def _generate_attachments(self, test_result: TestResult, video_path: str = None):
        """Generate attachments for Allure report"""
        attachments = []
        
        # Add video
        if video_path and Path(video_path).exists():
            video_name = self._copy_attachment(video_path, "video/webm")
            if video_name:
                attachments.append({
                    "name": "Test Execution Video",
                    "source": video_name,
                    "type": "video/webm"
                })
        
        # Add console logs
        if test_result.ConsoleLogs:
            logs_content = "=== BROWSER CONSOLE LOGS ===\n\n"
            
            error_count = sum(1 for log in test_result.ConsoleLogs if log.Type == "error")
            warning_count = sum(1 for log in test_result.ConsoleLogs if log.Type == "warning")
            info_count = len(test_result.ConsoleLogs) - error_count - warning_count
            
            logs_content += f"Summary: {error_count} errors, {warning_count} warnings, {info_count} info/log messages\n"
            logs_content += "═══════════════════════════════════════════════════════════════\n\n"
            
            # Group by type
            errors = [log for log in test_result.ConsoleLogs if log.Type == "error"]
            warnings = [log for log in test_result.ConsoleLogs if log.Type == "warning"]
            others = [log for log in test_result.ConsoleLogs if log.Type not in ["error", "warning"]]
            
            if errors:
                logs_content += "🔴 ERRORS:\n"
                logs_content += "─────────────────────────────────────────────────────────────────\n"
                for log in errors:
                    logs_content += f"[{log.Timestamp:%H:%M:%S}] {log.Text}\n"
                    if log.Location:
                        logs_content += f"  📍 {log.Location}\n"
                    logs_content += "\n"
            
            if warnings:
                logs_content += "\n🟡 WARNINGS:\n"
                logs_content += "─────────────────────────────────────────────────────────────────\n"
                for log in warnings:
                    logs_content += f"[{log.Timestamp:%H:%M:%S}] {log.Text}\n"
                    if log.Location:
                        logs_content += f"  📍 {log.Location}\n"
                    logs_content += "\n"
            
            if others:
                logs_content += "\n🔵 INFO/LOG:\n"
                logs_content += "─────────────────────────────────────────────────────────────────\n"
                for log in others:
                    logs_content += f"[{log.Timestamp:%H:%M:%S}] [{log.Type.upper()}] {log.Text}\n"
                    if log.Location:
                        logs_content += f"  📍 {log.Location}\n"
                    logs_content += "\n"
            
            # Save logs file
            logs_filename = f"{uuid.uuid4()}-attachment.txt"
            logs_file = self.allure_results_dir / logs_filename
            with open(logs_file, 'w', encoding='utf-8') as f:
                f.write(logs_content)
            
            attachments.append({
                "name": f"Browser Console Logs ({error_count} errors, {warning_count} warnings)",
                "source": logs_filename,
                "type": "text/plain"
            })
        
        return attachments

    def _copy_attachment(self, source_path: str, mime_type: str) -> str:
        """Copy attachment to allure-results directory"""
        try:
            source = Path(source_path)
            if not source.exists():
                return ""
            
            extension = source.suffix
            attachment_name = f"{uuid.uuid4()}{extension}"
            dest_path = self.allure_results_dir / attachment_name
            shutil.copy2(source, dest_path)
            return attachment_name
        except Exception as e:
            print(f"  ⚠️ Failed to copy attachment {source_path}: {e}")
            return ""

    def _generate_environment_info(self):
        """Generate environment.properties file"""
        env_file = self.allure_results_dir / "environment.properties"
        if not env_file.exists():
            import platform
            import sys
            env_info = f"""Browser=Chromium
Framework=Playwright
Language=Python {sys.version.split()[0]}
OS={platform.system()} {platform.release()}
Machine={platform.node()}
"""
            with open(env_file, 'w') as f:
                f.write(env_info)

    def _generate_categories(self):
        """Generate categories.json file"""
        categories_file = self.allure_results_dir / "categories.json"
        if not categories_file.exists():
            categories = [
                {
                    "name": "Element Not Found",
                    "matchedStatuses": ["failed"],
                    "messageRegex": ".*not found.*|.*timeout.*|.*locator.*"
                },
                {
                    "name": "JavaScript Errors",
                    "matchedStatuses": ["failed"],
                    "messageRegex": ".*javascript.*|.*console.*error.*"
                },
                {
                    "name": "Salesforce Errors",
                    "matchedStatuses": ["failed"],
                    "messageRegex": ".*salesforce.*|.*lightning.*"
                }
            ]
            
            with open(categories_file, 'w') as f:
                json.dump(categories, f, indent=2)

    def _get_history_id(self, scenario_name: str) -> str:
        """Generate consistent history ID for trend tracking"""
        import base64
        return base64.b64encode(scenario_name.encode()).decode()
