"""
UI Server for Real Test Execution with Learning
Shows real browser tests executing with learning and playback
Enhanced with Gemini AI for intelligent selector generation and learning
"""

from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
import httpx
import subprocess
from enhanced_test_executor import EnhancedTestExecutor
from gemini_enhanced_executor import GeminiEnhancedExecutor
from gemini_locator import get_gemini_locator
from gemini_selector_ai import get_gemini_ai
from allure_helper import create_allure_step, create_attachment_from_file, write_allure_result
from data_consumer import get_data_consumer, reset_data_consumer
from gherkin_step_generator import GherkinStepGenerator
from docx_step_pattern_parser import DocxStepPatternParser
from docx_screenshot_ocr import DocxScreenshotOCRAnalyzer
from docx_hybrid_analyzer import DocxHybridAnalyzer
from pdf_document_analyzer import PdfDocumentAnalyzer
from pdf_testcase_generator import PdfTestCaseGenerator
from ai_gherkin_converter import get_ai_gherkin_converter

app = FastAPI(title="Real Test Execution with Learning")

PROJECT_ROOT = Path(__file__).parent


def _latest_mtime_ms(path: Path, glob_pattern: str) -> int:
    latest = 0
    try:
        for p in path.glob(glob_pattern):
            try:
                ts = int(p.stat().st_mtime * 1000)
                if ts > latest:
                    latest = ts
            except Exception:
                continue
    except Exception:
        return 0
    return latest


def _get_allure_freshness() -> dict:
    results_dir = PROJECT_ROOT / "allure-results"
    report_dir = PROJECT_ROOT / "allure-report"
    return {
        "results_latest_mtime_ms": _latest_mtime_ms(results_dir, "*-result.json"),
        "report_suites_mtime_ms": int((report_dir / "data" / "suites.json").stat().st_mtime * 1000) if (report_dir / "data" / "suites.json").exists() else 0,
        "report_index_mtime_ms": int((report_dir / "index.html").stat().st_mtime * 1000) if (report_dir / "index.html").exists() else 0,
    }


async def _generate_allure_html_report() -> dict:
    """Best-effort: generate Allure HTML report from current allure-results.

    Uses the bundled Allure CLI under ./Allure/bin/allure.bat.
    """
    allure_bat = PROJECT_ROOT / "Allure" / "bin" / "allure.bat"
    results_dir = PROJECT_ROOT / "allure-results"
    report_dir = PROJECT_ROOT / "allure-report"

    if not allure_bat.exists():
        return {"ok": False, "reason": "allure_cli_missing", "stdout": "", "stderr": "", "freshness": _get_allure_freshness()}
    if not results_dir.exists():
        return {"ok": False, "reason": "results_dir_missing", "stdout": "", "stderr": "", "freshness": _get_allure_freshness()}

    cmd = [str(allure_bat), "generate", str(results_dir), "-o", str(report_dir), "--clean"]
    try:
        proc = await asyncio.to_thread(
            subprocess.run,
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout or "",
            "stderr": proc.stderr or "",
            "freshness": _get_allure_freshness(),
        }
    except Exception:
        return {"ok": False, "reason": "exception", "stdout": "", "stderr": "", "freshness": _get_allure_freshness()}

# Serve static assets (e.g., logo) from the ui folder
static_dir = Path(__file__).parent / "ui"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections
active_connections = []
parallel_connections = []
current_executor = None
parallel_executors = {}

# Initialize Gemini AI
gemini_locator = get_gemini_locator()

# Initialize analysis modules
gherkin_generator = GherkinStepGenerator()
docx_step_parser = DocxStepPatternParser()
docx_ocr_analyzer = DocxScreenshotOCRAnalyzer()
docx_hybrid_analyzer = DocxHybridAnalyzer()
pdf_analyzer = PdfDocumentAnalyzer()
pdf_testcase_generator = PdfTestCaseGenerator()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve real test execution dashboard"""
    html_file = Path(__file__).parent / "ui" / "real_test_dashboard.html"
    if html_file.exists():
        return html_file.read_text(encoding='utf-8')
    return "<h1>Dashboard not found</h1>"

@app.get("/parallel-execution", response_class=HTMLResponse)
async def parallel_execution():
    """Serve parallel execution page"""
    html_file = Path(__file__).parent / "ui" / "parallel_execution.html"
    if html_file.exists():
        return html_file.read_text(encoding='utf-8')
    return "<h1>Parallel Execution page not found</h1>"

@app.get("/gherkin-analysis", response_class=HTMLResponse)
async def gherkin_analysis_page():
    """Serve Gherkin Analysis page for converting Gherkin scenarios to test steps."""
    html_file = Path(__file__).parent / "ui" / "gherkin_analysis.html"
    if html_file.exists():
        return html_file.read_text(encoding='utf-8')
    return "<h1>Gherkin Analysis page not found</h1>"

@app.get("/word-analysis", response_class=HTMLResponse)
async def word_analysis_page():
    """Serve Word Analysis page for DOCX step pattern parsing."""
    html_file = Path(__file__).parent / "ui" / "word_analysis.html"
    if html_file.exists():
        return html_file.read_text(encoding='utf-8')
    return "<h1>Word Analysis page not found</h1>"

@app.get("/pdf-analysis", response_class=HTMLResponse)
async def pdf_analysis_page():
    """Serve PDF Analysis page for PDF test case generation."""
    html_file = Path(__file__).parent / "ui" / "pdf_analysis.html"
    if html_file.exists():
        return html_file.read_text(encoding='utf-8')
    return "<h1>PDF Analysis page not found</h1>"

@app.get("/api/gemini-status")
async def gemini_status():
    """Check Gemini AI status"""
    return JSONResponse({
        'enabled': gemini_locator.enabled if gemini_locator else False,
        'api_key_set': bool(os.getenv('GEMINI_API_KEY')),
        'vision_supported': True
    })

@app.get("/api/allure-summary")
async def allure_summary():
    freshness = _get_allure_freshness()
    # Keep summary in sync with the HTML report. If results are newer, regenerate first.
    if freshness.get("results_latest_mtime_ms", 0) > max(
        freshness.get("report_suites_mtime_ms", 0),
        freshness.get("report_index_mtime_ms", 0),
    ):
        await _generate_allure_html_report()

    results_dir = PROJECT_ROOT / "allure-results"
    total = 0
    passed = 0
    failed = 0
    last_failed_name = None
    last_failed_message = None
    last_failed_stop = 0
    last_failed_uuid = None
    # Track last failed testcase UID from generated Allure HTML (for deep links)
    last_failed_report_uid = None
    last_failed_report_start = 0

    if results_dir.exists() and results_dir.is_dir():
        for result_file in results_dir.glob("*.json"):
            try:
                data = json.loads(result_file.read_text(encoding="utf-8"))
            except Exception:
                continue

            status = str(data.get("status", "")).lower()
            if not status:
                continue

            total += 1
            if status == "passed":
                passed += 1
            elif status in ("failed", "broken"):
                failed += 1

                # Track the most recent failed test and its reason
                test_name = (
                    data.get("name")
                    or data.get("fullName")
                    or result_file.stem
                )

                message = ""
                status_details = data.get("statusDetails") or {}
                if isinstance(status_details, dict):
                    message = status_details.get("message") or ""

                if not message:
                    # Fallback: use the last failed step name if present
                    for step in data.get("steps", []):
                        if str(step.get("status", "")).lower() == "failed":
                            step_name = step.get("name") or ""
                            if step_name:
                                message = f"Failed step: {step_name}"
                            else:
                                message = "A step failed."
                            break

                if not message:
                    message = "Failure (see Allure report for details)."

                # Prefer Allure's stop timestamp; fall back to file mtime
                try:
                    stop_ts = int(data.get("stop") or 0)
                except Exception:
                    stop_ts = 0
                if not stop_ts:
                    try:
                        stop_ts = int(result_file.stat().st_mtime * 1000)
                    except Exception:
                        stop_ts = 0

                if stop_ts >= last_failed_stop:
                    last_failed_stop = stop_ts
                    last_failed_name = test_name
                    last_failed_message = message
                    # Keep raw result UUID as a fallback
                    last_failed_uuid = data.get("uuid")

    # If an Allure HTML report exists, prefer its testcase UID for deep-linking
    try:
        report_suites_path = PROJECT_ROOT / "allure-report" / "data" / "suites.json"
        if report_suites_path.exists():
            suites_data = json.loads(report_suites_path.read_text(encoding="utf-8"))
            for container in suites_data.get("children", []):
                for test_case in container.get("children", []):
                    status = str(test_case.get("status", "")).lower()
                    if status not in ("failed", "broken"):
                        continue
                    time_info = test_case.get("time", {}) or {}
                    try:
                        start_ts = int(time_info.get("start") or 0)
                    except Exception:
                        start_ts = 0
                    if start_ts >= last_failed_report_start:
                        last_failed_report_start = start_ts
                        last_failed_report_uid = test_case.get("uid") or last_failed_report_uid
                        # Optionally refresh the name from the report structure
                        last_failed_name = test_case.get("name") or last_failed_name
    except Exception:
        # If the report structure is missing or unreadable, silently ignore
        pass

    # Prefer the UID from the generated report when available so the
    # frontend can deep-link to /allure-report#/testcase/{uid}.
    if last_failed_report_uid:
        last_failed_uuid = last_failed_report_uid

    others = total - passed - failed
    if others < 0:
        others = 0

    last_failed_url = None
    if last_failed_uuid:
        last_failed_url = f"/allure-report/index.html#/testcase/{last_failed_uuid}"

    return JSONResponse({
        "total": total,
        "passed": passed,
        "failed": failed,
        "others": others,
        "last_failed_name": last_failed_name,
        "last_failed_message": last_failed_message,
        "last_failed_uuid": last_failed_uuid,
        "last_failed_url": last_failed_url,
    })


@app.post("/api/regenerate-allure-report")
async def regenerate_allure_report():
    """Force regenerate the Allure HTML report and return diagnostics."""
    diag = await _generate_allure_html_report()
    return JSONResponse(diag)

@app.post("/api/gemini-generate-selectors")
async def generate_selectors_with_gemini(request: dict):
    """Generate selectors using Gemini AI"""
    if not gemini_locator or not gemini_locator.enabled:
        return JSONResponse({'error': 'Gemini AI not configured'}, status_code=400)
    
    action = request.get('action', 'click')
    description = request.get('description', '')
    page_context = request.get('context', 'Salesforce Lightning Web Component')
    
    screenshot_path = None
    test_status = "passed"
    try:
        selectors = gemini_locator.generate_selector(action, description, page_context)
        return JSONResponse({
            'success': True,
            'selectors': selectors,
            'count': len(selectors)
        })
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)

@app.websocket("/ws/test")
async def websocket_test(websocket: WebSocket):
    """WebSocket for real-time test updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        await websocket.send_json({
            'type': 'connected',
            'message': 'Connected to test executor'
        })
        
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.websocket("/ws/parallel-test")
async def websocket_parallel_test(websocket: WebSocket):
    """WebSocket for parallel test updates"""
    await websocket.accept()
    parallel_connections.append(websocket)
    
    try:
        await websocket.send_json({
            'type': 'connected',
            'message': 'Connected to parallel test executor'
        })
        
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if websocket in parallel_connections:
            parallel_connections.remove(websocket)

async def broadcast_message(message: dict):
    """Broadcast message to all connected clients"""
    for connection in active_connections[:]:
        try:
            await connection.send_json(message)
        except:
            active_connections.remove(connection)

async def broadcast_parallel_message(message: dict):
    """Broadcast message to all parallel test clients"""
    for connection in parallel_connections[:]:
        try:
            await connection.send_json(message)
        except:
            parallel_connections.remove(connection)

@app.post("/api/execute-test")
async def execute_test(request: dict):
    """Execute real test with plain text steps"""
    global current_executor
    
    url = request.get('url', '')
    steps = request.get('steps', [])
    headless = request.get('headless', False)
    use_ai = request.get('use_ai', False)  # Check if AI should be used
    browser = request.get('browser', 'chromium')
    recovery_steps = request.get('recovery_steps', []) or []
    recovery_enabled = request.get('recovery_enabled', False)
    positive_scenarios = request.get('positive_scenarios', 5)
    negative_scenarios = request.get('negative_scenarios', 5)
    data_type = request.get('data_type', 'positive')
    mfa_option = request.get('mfa_option', 'none')
    if browser == 'chrome-headless':
        headless = True
    
    if not url or not steps:
        return JSONResponse({'error': 'URL and steps required'}, status_code=400)
    
    # Start test execution in background
    asyncio.create_task(
        run_test_with_updates(
            url,
            steps,
            headless,
            use_ai,
            browser,
            recovery_steps if recovery_enabled else [],
            positive_scenarios,
            negative_scenarios,
            data_type,
            mfa_option
        )
    )
    
    return JSONResponse({'status': 'started', 'total_steps': len(steps), 'use_ai': use_ai, 'browser': browser})


@app.get("/api/data-status")
async def get_data_status():
    """Get current data consumption status"""
    data_consumer = get_data_consumer()
    
    return JSONResponse({
        'data_exists': data_consumer.data_exists(),
        'usage': data_consumer.get_usage_summary()
    })


@app.post("/api/reset-data-usage")
async def reset_data_usage():
    """Reset data usage tracking (all rows become available again)"""
    data_consumer = get_data_consumer()
    data_consumer.usage_data = {"used_rows": [], "last_used_index": -1}
    data_consumer._save_usage()
    try:
        data_consumer.reset_used_flags_in_csv()
    except Exception:
        pass
    
    return JSONResponse({
        'status': 'reset',
        'message': 'Data usage tracking reset. All rows are now available.',
        'usage': data_consumer.get_usage_summary()
    })


@app.post("/api/generate-data")
async def generate_data(request: dict = None):
    """Generate test data from schema"""
    num_rows = 100
    if request:
        num_rows = request.get('num_rows', 100)
    
    # Data generation requires a live Playwright page so DatasetGenerator can crawl the current form.
    # This endpoint can't generate without a page context.
    return JSONResponse({
        'status': 'error',
        'message': 'Data generation requires a live form page. Run a test with placeholders to auto-generate outputs/data.csv via DatasetGenerator.'
    }, status_code=400)


async def run_test_with_updates(url: str, steps: list, headless: bool, use_ai: bool = False, browser: str = "chromium", recovery_steps = None, positive_scenarios: int = 5, negative_scenarios: int = 5, data_type: str = 'positive', mfa_option: str = 'none'):
    """Run test and broadcast updates with automatic data consumption"""
    global current_executor
    test_start_time = datetime.now()
    allure_steps = []
    test_status = "passed"
    screenshot_path = None
    if recovery_steps is None:
        recovery_steps = []
    
    # Reset data consumer for fresh data selection each test run
    reset_data_consumer()
    data_consumer = get_data_consumer()
    
    # Use Gemini-enhanced executor if AI is requested and available
    if use_ai:
        gemini_ai = get_gemini_ai()
        if gemini_ai.is_available():
            current_executor = GeminiEnhancedExecutor()
            await broadcast_message({
                'type': 'log_entry',
                'level': 'info',
                'message': '🤖 Using Gemini AI Enhanced Executor',
                'details': {'ai_enabled': True}
            })
        else:
            current_executor = EnhancedTestExecutor()
            await broadcast_message({
                'type': 'log_entry',
                'level': 'warning',
                'message': '⚠️ Gemini AI not available, using standard executor',
                'details': {'ai_enabled': False}
            })
    else:
        current_executor = EnhancedTestExecutor()
    current_executor.last_failure_screenshot = None
    
    # Set data generation parameters
    current_executor.set_data_generation_params(positive_scenarios, negative_scenarios, data_type)
    
    # Store all test steps in executor for context
    current_executor.all_test_steps = steps
    
    # Check if any step has placeholders and initialize data
    has_placeholders = any(current_executor.has_placeholder(step) for step in steps)
    data_row_index = -1
    
    if has_placeholders:
        await broadcast_message({
            'type': 'log_entry',
            'level': 'info',
            'message': '📊 Detected placeholders in test steps, checking data...',
            'details': {}
        })
        
        # Check if data.csv exists
        if data_consumer.data_exists():
            row, idx = data_consumer.get_next_available_row_by_type(data_type)
            if row:
                data_row_index = idx
                usage = data_consumer.get_usage_summary()
                await broadcast_message({
                    'type': 'log_entry',
                    'level': 'info',
                    'message': f'📊 Using data row {idx + 1} ({usage["available_rows"]} rows available)',
                    'details': {'row_index': idx, 'available': usage['available_rows']}
                })
            else:
                await broadcast_message({
                    'type': 'log_entry',
                    'level': 'warning',
                    'message': '⚠️ All data rows used. Resetting...',
                    'details': {}
                })
        else:
            await broadcast_message({
                'type': 'log_entry',
                'level': 'warning',
                'message': '📝 data.csv not found. Will attempt to generate when needed.',
                'details': {}
            })
    
    # Send start message
    await broadcast_message({
        'type': 'test_start',
        'url': url,
        'total_steps': len(steps)
    })
    
    try:
        # Start browser
        await current_executor.start_browser(url, headless, browser)
        await broadcast_message({
            'type': 'browser_started',
            'url': url
        })

        if mfa_option and str(mfa_option).lower() != 'none':
            try:
                await broadcast_message({
                    'type': 'log_entry',
                    'level': 'info',
                    'message': f'🔐 MFA option selected: {mfa_option}. Attempting Salesforce login...',
                    'details': {'mfa_option': mfa_option}
                })

                from salesforce_mfa_login import login_with_mfa_async

                async def _mfa_progress(level: str, message: str, details: dict):
                    await broadcast_message({
                        'type': 'log_entry',
                        'level': level or 'info',
                        'message': message,
                        'details': details or {},
                    })

                ok = await login_with_mfa_async(
                    current_executor.page,
                    environment=str(mfa_option).lower(),
                    target_url=url,
                    progress=_mfa_progress,
                )
                if ok:
                    await broadcast_message({
                        'type': 'log_entry',
                        'level': 'success',
                        'message': '✅ Salesforce MFA login completed',
                        'details': {'mfa_option': mfa_option}
                    })
                else:
                    await broadcast_message({
                        'type': 'log_entry',
                        'level': 'warning',
                        'message': '⚠️ Salesforce MFA login was not confirmed as successful. Continuing test execution...',
                        'details': {'mfa_option': mfa_option}
                    })
            except Exception as e:
                await broadcast_message({
                    'type': 'log_entry',
                    'level': 'error',
                    'message': f'❌ Salesforce MFA login failed: {str(e)}',
                    'details': {'mfa_option': mfa_option}
                })

        await asyncio.sleep(1)
        
        # Execute each step
        for i, step in enumerate(steps, 1):
            step_start_time = datetime.now()
            try:
                current_executor.current_step_index = i - 1
            except Exception:
                pass
            await broadcast_message({
                'type': 'step_start',
                'step_number': i,
                'step_text': step
            })
            
            # Check for learned selector
            parsed = current_executor.parse_plain_text_step(step)
            if parsed and 'target' in parsed:
                target_key = parsed['target'].lower().replace(' ', '_')
                if target_key in current_executor.learned_selectors:
                    learned = current_executor.learned_selectors[target_key]
                    await broadcast_message({
                        'type': 'using_learned',
                        'step_number': i,
                        'target': parsed['target'],
                        'selector': learned['selector'],
                        'success_count': learned['success_count']
                    })
            
            # Execute step and broadcast logs in real-time
            log_start_index = len(current_executor.execution_log)
            success = await current_executor.execute_step(step)
            step_stop_time = datetime.now()
            allure_steps.append(
                create_allure_step(
                    name=f"Step {i}: {step}",
                    status='passed' if success else 'failed',
                    start_time=step_start_time,
                    stop_time=step_stop_time,
                )
            )
            
            # Broadcast all new log entries
            new_logs = current_executor.execution_log[log_start_index:]
            for log_entry in new_logs:
                await broadcast_message({
                    'type': 'log_entry',
                    'level': log_entry['level'],
                    'message': log_entry['message'],
                    'details': log_entry.get('details', {})
                })
            
            if success:
                # Get the selector that was used
                if parsed and 'target' in parsed:
                    target_key = parsed['target'].lower().replace(' ', '_')
                    if target_key in current_executor.learned_selectors:
                        learned = current_executor.learned_selectors[target_key]
                        
                        await broadcast_message({
                            'type': 'step_success',
                            'step_number': i,
                            'selector': learned['selector'],
                            'was_learned': learned['success_count'] > 1
                        })
                        
                        if learned['success_count'] == 1:
                            await broadcast_message({
                                'type': 'selector_learned',
                                'step_number': i,
                                'target': parsed['target'],
                                'selector': learned['selector']
                            })
            else:
                await broadcast_message({
                    'type': 'step_failed',
                    'step_number': i
                })
                # Stop execution on failure
                test_status = "failed"
                await broadcast_message({
                    'type': 'test_stopped',
                    'reason': f'Step {i} failed - stopping execution',
                    'failed_step': step
                })
                break  # Exit the loop
            
            await asyncio.sleep(0.5)
        
        # If test failed and recovery steps are defined, execute recovery scenario
        if test_status == "failed" and recovery_steps:
            await broadcast_message({
                'type': 'log_entry',
                'level': 'recovery',
                'message': '🛟 Starting recovery scenario',
                'details': {'steps': len(recovery_steps)}
            })
            for idx, rec_step in enumerate(recovery_steps, 1):
                rec_start_time = datetime.now()
                await broadcast_message({
                    'type': 'log_entry',
                    'level': 'recovery',
                    'message': f'🛟 Recovery step {idx}: {rec_step}',
                    'details': {}
                })
                log_start_index = len(current_executor.execution_log)
                rec_success = await current_executor.execute_step(rec_step)
                rec_stop_time = datetime.now()
                allure_steps.append(
                    create_allure_step(
                        name=f"Recovery {idx}: {rec_step}",
                        status='passed' if rec_success else 'failed',
                        start_time=rec_start_time,
                        stop_time=rec_stop_time,
                    )
                )
                new_logs = current_executor.execution_log[log_start_index:]
                for log_entry in new_logs:
                    await broadcast_message({
                        'type': 'log_entry',
                        'level': log_entry['level'],
                        'message': log_entry['message'],
                        'details': log_entry.get('details', {})
                    })

            await broadcast_message({
                'type': 'log_entry',
                'level': 'recovery',
                'message': '🛟 Recovery scenario completed',
                'details': {}
            })

        # Take screenshot (best-effort; do not fail the test if this fails)
        try:
            screenshot_path = f"test_result.png"
            await current_executor.page.screenshot(path=screenshot_path)
        except Exception as e_screenshot:
            screenshot_path = None
            current_executor.log('warning', f'Final screenshot failed: {str(e_screenshot)}')
        
        await current_executor.stop_browser()
        
        # Mark data row as used after successful test completion
        if test_status == "passed" and has_placeholders and data_row_index >= 0:
            data_consumer.mark_row_as_used(data_row_index)
            await broadcast_message({
                'type': 'log_entry',
                'level': 'info',
                'message': f'✓ Data row {data_row_index + 1} marked as used',
                'details': {'row_index': data_row_index}
            })
        
        # Send completion with performance metrics
        usage_summary = data_consumer.get_usage_summary() if has_placeholders else {}
        await broadcast_message({
            'type': 'test_complete',
            'learned_selectors': len(current_executor.learned_selectors),
            'performance_metrics': current_executor.performance_metrics,
            'data_usage': usage_summary
        })

        # Write Allure result for this test
        test_stop_time = datetime.now()
        attachments = []
        failure_screenshot = getattr(current_executor, "last_failure_screenshot", None)
        if failure_screenshot:
            attachment = create_attachment_from_file(
                failure_screenshot,
                name="Failure screenshot",
                mime_type="image/png",
            )
            if attachment:
                attachments.append(attachment)
        if screenshot_path:
            attachment = create_attachment_from_file(
                screenshot_path,
                name="Final screenshot",
                mime_type="image/png",
            )
            if attachment:
                attachments.append(attachment)

        write_allure_result(
            test_name="Real Test Execution",
            full_name=f"Real Test Execution: {url}",
            status=test_status,
            start_time=test_start_time,
            stop_time=test_stop_time,
            steps=allure_steps,
            labels=[
                {"name": "suite", "value": "Real Test Dashboard"},
                {"name": "browser", "value": browser},
            ],
            attachments=attachments,
            parameters=[{"name": "url", "value": url}],
        )

        report_diag = await _generate_allure_html_report()
        if report_diag.get("ok"):
            await broadcast_message({
                'type': 'log_entry',
                'level': 'success',
                'message': '📊 Allure HTML report updated',
                'details': report_diag.get('freshness', {})
            })
        else:
            await broadcast_message({
                'type': 'log_entry',
                'level': 'warning',
                'message': '⚠️ Allure HTML report not updated (missing CLI or generation failed)',
                'details': report_diag.get('freshness', {})
            })
        
    except Exception as e:
        await broadcast_message({
            'type': 'test_error',
            'error': str(e)
        })
        if current_executor.browser:
            await current_executor.stop_browser()
        # Also write a failed Allure result capturing steps executed so far
        test_stop_time = datetime.now()
        attachments = []
        failure_screenshot = getattr(current_executor, "last_failure_screenshot", None)
        if failure_screenshot:
            attachment = create_attachment_from_file(
                failure_screenshot,
                name="Failure screenshot",
                mime_type="image/png",
            )
            if attachment:
                attachments.append(attachment)
        write_allure_result(
            test_name="Real Test Execution",
            full_name=f"Real Test Execution: {url}",
            status="failed",
            start_time=test_start_time,
            stop_time=test_stop_time,
            steps=allure_steps,
            labels=[
                {"name": "suite", "value": "Real Test Dashboard"},
                {"name": "browser", "value": browser},
            ],
            attachments=attachments,
            parameters=[{"name": "url", "value": url}],
            status_details=str(e),
        )

        report_diag = await _generate_allure_html_report()
        if report_diag.get("ok"):
            await broadcast_message({
                'type': 'log_entry',
                'level': 'success',
                'message': '📊 Allure HTML report updated',
                'details': report_diag.get('freshness', {})
            })
        else:
            await broadcast_message({
                'type': 'log_entry',
                'level': 'warning',
                'message': '⚠️ Allure HTML report not updated (missing CLI or generation failed)',
                'details': report_diag.get('freshness', {})
            })

@app.get("/api/learned-selectors")
async def get_learned_selectors():
    """Get all learned selectors"""
    executor = EnhancedTestExecutor()
    summary = executor.get_learned_selectors_summary()
    return JSONResponse(summary)

@app.delete("/api/learned-selectors")
async def clear_learned_selectors():
    """Clear all learned selectors"""
    learning_db = Path("test_learning.json")
    if learning_db.exists():
        learning_db.unlink()
    return JSONResponse({'status': 'cleared'})

@app.post("/api/execute-parallel-tests")
async def execute_parallel_tests(request: dict):
    """Execute multiple tests in parallel"""
    global parallel_executors
    
    tests = request.get('tests', [])
    headless = request.get('headless', False)
    use_ai = request.get('use_ai', False)
    
    if not tests:
        return JSONResponse({'error': 'No tests provided'}, status_code=400)
    
    # Clear previous executors
    parallel_executors = {}
    
    # Start all tests in parallel and track completion
    asyncio.create_task(run_all_parallel_tests(tests, headless, use_ai))
    
    return JSONResponse({
        'status': 'started',
        'total_tests': len(tests)
    })

async def run_all_parallel_tests(tests: list, headless: bool, use_ai: bool = False):
    """Run all parallel tests and track completion"""
    tasks = []
    results = []
    
    for test_data in tests:
        task = asyncio.create_task(run_parallel_test_tracked(test_data, headless, use_ai, results))
        tasks.append(task)
    
    # Wait for all tests to complete
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # Send completion message
    successful = sum(1 for r in results if r.get('success', False))
    await broadcast_parallel_message({
        'type': 'all_complete',
        'total': len(tests),
        'successful': successful,
        'failed': len(tests) - successful
    })

async def run_parallel_test_tracked(test_data: dict, headless: bool, use_ai: bool, results: list):
    """Run a single test and track result"""
    instance = test_data['instance']
    try:
        await run_parallel_test(test_data, headless, use_ai)
        results.append({'instance': instance, 'success': True})
    except Exception as e:
        results.append({'instance': instance, 'success': False, 'error': str(e)})

async def run_parallel_test(test_data: dict, headless: bool, use_ai: bool = False):
    """Run a single test in parallel"""
    global parallel_executors
    
    instance = test_data['instance']
    url = test_data['url']
    username = test_data.get('username', '')
    password = test_data.get('password', '')
    steps = test_data['steps']
    browser = test_data.get('browser', 'chromium')
    recovery_steps = test_data.get('recovery_steps', []) or []
    instance_headless = headless or browser == 'chrome-headless'
    test_start_time = datetime.now()
    allure_steps = []
    test_status = "passed"
    
    # Create executor for this instance
    if use_ai:
        gemini_ai = get_gemini_ai()
        if gemini_ai.is_available():
            executor = GeminiEnhancedExecutor()
        else:
            executor = EnhancedTestExecutor()
    else:
        executor = EnhancedTestExecutor()
    executor.last_failure_screenshot = None
    parallel_executors[instance] = executor
    
    try:
        # Send start message
        await broadcast_parallel_message({
            'type': 'parallel_start',
            'instance': instance,
            'url': url
        })
        
        # Start browser
        await executor.start_browser(url, instance_headless, browser)
        
        # Add login steps if credentials provided
        if username and password:
            await broadcast_parallel_message({
                'type': 'parallel_step',
                'instance': instance,
                'step_number': 0,
                'step_text': f'Login with {username}'
            })
            # You can add login logic here if needed
        
        await asyncio.sleep(1)
        
        test_start_time = datetime.now()
        
        # Execute each step
        for i, step in enumerate(steps, 1):
            await broadcast_parallel_message({
                'type': 'parallel_step',
                'instance': instance,
                'step_number': i,
                'step_text': step
            })
            
            step_start_time = datetime.now()
            success = await executor.execute_step(step)
            step_stop_time = datetime.now()
            step_elapsed = (step_stop_time - step_start_time).total_seconds()
            executor.performance_metrics['step_timings'].append({
                'step': step,
                'time': step_elapsed,
                'success': success
            })

            allure_steps.append(
                create_allure_step(
                    name=f"Instance {instance} - Step {i}: {step}",
                    status='passed' if success else 'failed',
                    start_time=step_start_time,
                    stop_time=step_stop_time,
                )
            )
            
            if success:
                await broadcast_parallel_message({
                    'type': 'parallel_step_success',
                    'instance': instance,
                    'step_number': i
                })
            else:
                await broadcast_parallel_message({
                    'type': 'parallel_step_failed',
                    'instance': instance,
                    'step_number': i
                })
                # Continue execution even if a step fails
                test_status = "failed"
            
            await asyncio.sleep(0.5)
        
        # If instance failed and recovery steps are defined, execute recovery scenario
        if test_status == "failed" and recovery_steps:
            await broadcast_parallel_message({
                'type': 'parallel_log',
                'instance': instance,
                'kind': 'recovery',
                'message': '🛟 Starting recovery scenario'
            })
            for idx, rec_step in enumerate(recovery_steps, 1):
                rec_start_time = datetime.now()
                await broadcast_parallel_message({
                    'type': 'parallel_log',
                    'instance': instance,
                    'kind': 'recovery',
                    'message': f'🛟 Recovery step {idx}: {rec_step}'
                })
                rec_success = await executor.execute_step(rec_step)
                rec_stop_time = datetime.now()
                allure_steps.append(
                    create_allure_step(
                        name=f"Instance {instance} - Recovery {idx}: {rec_step}",
                        status='passed' if rec_success else 'failed',
                        start_time=rec_start_time,
                        stop_time=rec_stop_time,
                    )
                )

            await broadcast_parallel_message({
                'type': 'parallel_log',
                'instance': instance,
                'kind': 'recovery',
                'message': '🛟 Recovery scenario completed'
            })

        # Calculate total time
        total_elapsed = (datetime.now() - test_start_time).total_seconds()
        executor.performance_metrics['total_time'] = total_elapsed
        
        # Take screenshot
        screenshot_path = f"parallel_test_instance_{instance}.png"
        await executor.page.screenshot(path=screenshot_path)
        
        await executor.stop_browser()
        
        # Send completion with performance metrics
        await broadcast_parallel_message({
            'type': 'parallel_complete',
            'instance': instance,
            'learned_selectors': len(executor.learned_selectors),
            'performance_metrics': executor.performance_metrics
        })

        # Write Allure result for this parallel instance
        test_stop_time = datetime.now()
        attachments = []
        failure_screenshot = getattr(executor, "last_failure_screenshot", None)
        if failure_screenshot:
            attachment = create_attachment_from_file(
                failure_screenshot,
                name=f"Instance {instance} failure screenshot",
                mime_type="image/png",
            )
            if attachment:
                attachments.append(attachment)
        attachment = create_attachment_from_file(
            screenshot_path,
            name=f"Instance {instance} screenshot",
            mime_type="image/png",
        )
        if attachment:
            attachments.append(attachment)

        write_allure_result(
            test_name=f"Parallel Instance {instance}",
            full_name=f"Parallel Instance {instance}: {url}",
            status=test_status,
            start_time=test_start_time,
            stop_time=test_stop_time,
            steps=allure_steps,
            labels=[
                {"name": "suite", "value": "Parallel Execution"},
                {"name": "thread", "value": str(instance)},
                {"name": "browser", "value": browser},
            ],
            attachments=attachments,
            parameters=[{"name": "url", "value": url}],
        )
        
    except Exception as e:
        await broadcast_parallel_message({
            'type': 'parallel_error',
            'instance': instance,
            'error': str(e)
        })
        if executor.browser:
            await executor.stop_browser()
        # Also write a failed Allure result capturing steps executed so far
        test_stop_time = datetime.now()
        attachments = []
        failure_screenshot = getattr(executor, "last_failure_screenshot", None)
        if failure_screenshot:
            attachment = create_attachment_from_file(
                failure_screenshot,
                name=f"Instance {instance} failure screenshot",
                mime_type="image/png",
            )
            if attachment:
                attachments.append(attachment)
        write_allure_result(
            test_name=f"Parallel Instance {instance}",
            full_name=f"Parallel Instance {instance}: {url}",
            status="failed",
            start_time=test_start_time,
            stop_time=test_stop_time,
            steps=allure_steps,
            labels=[
                {"name": "suite", "value": "Parallel Execution"},
                {"name": "thread", "value": str(instance)},
                {"name": "browser", "value": browser},
            ],
            attachments=attachments,
            parameters=[{"name": "url", "value": url}],
            status_details=str(e),
        )
    finally:
        # Remove executor
        if instance in parallel_executors:
            del parallel_executors[instance]

@app.post("/api/stop-parallel-tests")
async def stop_parallel_tests():
    """Stop all parallel tests"""
    global parallel_executors
    
    for instance, executor in parallel_executors.items():
        try:
            if executor.browser:
                await executor.stop_browser()
        except:
            pass
    
    parallel_executors = {}
    
    return JSONResponse({'status': 'stopped'})

# Gherkin Analysis API
@app.post("/api/convert-gherkin-steps")
async def convert_gherkin_steps(request: dict) -> JSONResponse:
    """Convert Gherkin scenario text to executable test steps using OpenAI API."""
    try:
        gherkin_text = request.get("gherkin_text", "")
        use_parameters = request.get("use_parameters", True)
        
        if not gherkin_text:
            return JSONResponse(
                status_code=400,
                content={"error": "Please provide Gherkin text."}
            )
        
        # Try AI-powered conversion first
        ai_converter = get_ai_gherkin_converter()
        
        if ai_converter.is_available():
            try:
                print("Using OpenAI API for Gherkin conversion...")
                result = await ai_converter.convert_gherkin_to_steps(gherkin_text, use_parameters)
                return JSONResponse(content=result)
            except Exception as e:
                print(f"OpenAI API error: {str(e)}, falling back to local generator")
                # Fall through to local generator
        else:
            print("OpenAI API key not configured, using local generator")
        
        # Fallback to local generator
        generator = GherkinStepGenerator(use_parameters=use_parameters)
        result = generator.parse_and_generate(gherkin_text)
        result['source'] = 'GherkinStepGenerator'
        return JSONResponse(content=result)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Gherkin conversion failed: {str(e)}"}
        )

# Word Analysis APIs
@app.post("/api/analyze-docx-steps")
async def analyze_docx_steps(docx_file: UploadFile = File(...)) -> JSONResponse:
    """Analyze DOCX file and extract test steps using pattern parsing."""
    filename = docx_file.filename or "uploaded.docx"
    if not (filename.lower().endswith(".doc") or filename.lower().endswith(".docx")):
        return JSONResponse({'error': 'Only Word files (.doc, .docx) are allowed'}, status_code=400)

    try:
        temp_dir = Path(__file__).parent / "temp"
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / filename

        with open(temp_path, "wb") as f:
            f.write(await docx_file.read())

        steps = docx_step_parser.parse_docx(str(temp_path))
        temp_path.unlink(missing_ok=True)

        return JSONResponse({
            'total_steps': len(steps),
            'steps': steps
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={'error': f'DOCX analysis failed: {str(e)}'}
        )

@app.post("/api/analyze-docx-ocr-steps")
async def analyze_docx_ocr_steps(docx_file: UploadFile = File(...)) -> JSONResponse:
    """Analyze DOCX screenshots via OCR to generate concrete steps."""
    filename = docx_file.filename or "uploaded.docx"
    if not (filename.lower().endswith(".doc") or filename.lower().endswith(".docx")):
        return JSONResponse({'error': 'Only Word files (.doc, .docx) are allowed'}, status_code=400)

    try:
        temp_dir = Path(__file__).parent / "temp"
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / filename

        with open(temp_path, "wb") as f:
            f.write(await docx_file.read())

        steps = docx_ocr_analyzer.analyze(str(temp_path))
        temp_path.unlink(missing_ok=True)

        return JSONResponse({
            'total_steps': len(steps),
            'steps': steps
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={'error': f'OCR analysis failed: {str(e)}'}
        )

@app.post("/api/analyze-docx-hybrid-steps")
async def analyze_docx_hybrid_steps(docx_file: UploadFile = File(...)) -> JSONResponse:
    """Analyze DOCX using hybrid approach (pattern + OCR)."""
    filename = docx_file.filename or "uploaded.docx"
    if not (filename.lower().endswith(".doc") or filename.lower().endswith(".docx")):
        return JSONResponse({'error': 'Only Word files (.doc, .docx) are allowed'}, status_code=400)

    try:
        temp_dir = Path(__file__).parent / "temp"
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / filename

        with open(temp_path, "wb") as f:
            f.write(await docx_file.read())

        result = docx_hybrid_analyzer.analyze(str(temp_path))
        temp_path.unlink(missing_ok=True)

        return JSONResponse(content=result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Hybrid analysis failed: {str(e)}"}
        )

# PDF Analysis APIs
@app.post("/api/analyze-pdf")
async def analyze_pdf(pdf_file: UploadFile = File(...)) -> JSONResponse:
    """Analyze PDF and extract test steps."""
    filename = pdf_file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf"):
        return JSONResponse({'error': 'Only PDF files are allowed'}, status_code=400)

    try:
        temp_dir = Path(__file__).parent / "temp"
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / filename

        with open(temp_path, "wb") as f:
            f.write(await pdf_file.read())

        result = pdf_analyzer.analyze(str(temp_path))
        temp_path.unlink(missing_ok=True)

        return JSONResponse(content=result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={'error': f'PDF analysis failed: {str(e)}'}
        )

@app.post("/api/generate-pdf-testcases")
async def generate_pdf_testcases(pdf_file: UploadFile = File(...)) -> JSONResponse:
    """Generate test cases from PDF."""
    filename = pdf_file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf"):
        return JSONResponse({'error': 'Only PDF files are allowed'}, status_code=400)

    try:
        temp_dir = Path(__file__).parent / "temp"
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / filename

        with open(temp_path, "wb") as f:
            f.write(await pdf_file.read())

        result = pdf_testcase_generator.generate(str(temp_path))
        temp_path.unlink(missing_ok=True)

        return JSONResponse(content=result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={'error': f'PDF test case generation failed: {str(e)}'}
        )

def run_server(port: int = 8888):
    """Run the server"""
    print(f"""
    ============================================================
         Real Test Execution with Learning & Playback
    ============================================================
    
    Dashboard: http://localhost:{port}
    Parallel Execution: http://localhost:{port}/parallel-execution
    Gherkin Analysis: http://localhost:{port}/gherkin-analysis
    Word Analysis: http://localhost:{port}/word-analysis
    PDF Analysis: http://localhost:{port}/pdf-analysis
    
    Features:
    [+] Plain text test steps
    [+] Real browser execution
    [+] Automatic selector learning
    [+] Selector reuse on 2nd run
    [+] Live execution view
    [+] Parallel test execution
    [+] Gherkin to test steps conversion
    [+] DOCX analysis with OCR & hybrid
    [+] PDF test case generation
    
    Press Ctrl+C to stop
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=port)


@app.get("/allure-report", response_class=HTMLResponse)
async def allure_report():
    """Serve Allure HTML report if it has been generated.

    We redirect to /allure-report/index.html so that all relative asset
    paths (styles.css, app.js, plugin/*) resolve under /allure-report/.
    """
    freshness = _get_allure_freshness()
    # If results are newer than the generated report, rebuild it on-demand.
    if freshness.get("results_latest_mtime_ms", 0) > max(
        freshness.get("report_suites_mtime_ms", 0),
        freshness.get("report_index_mtime_ms", 0),
    ):
        await _generate_allure_html_report()

    report_index = PROJECT_ROOT / "allure-report" / "index.html"
    if report_index.exists():
        # Redirect so the browser URL ends with /allure-report/index.html
        # and relative asset URLs resolve to /allure-report/*
        return HTMLResponse(status_code=307, headers={"Location": "/allure-report/index.html"})

    return HTMLResponse(
        content=(
            "<h2>Allure report not found</h2>"
            "<p>Generate it by running:</p>"
            "<pre>allure generate allure-results -o allure-report --clean</pre>"
            "<p>from the project root, then refresh this page.</p>"
        ),
        status_code=200,
    )


@app.get("/allure-report/{path:path}")
async def allure_report_static(path: str):
    """Serve static assets for the Allure HTML report (CSS, JS, plugins)."""
    report_dir = PROJECT_ROOT / "allure-report"
    file_path = report_dir / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    return HTMLResponse(status_code=404, content="Not found")

if __name__ == "__main__":
    run_server()
