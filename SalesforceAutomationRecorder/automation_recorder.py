"""
Salesforce Automation Recorder - Main Python Framework
Uses Playwright to orchestrate browser automation and capture user interactions
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class SalesforceRecorder:
    """
    Main recorder class that manages browser automation and interaction capture
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the Salesforce Recorder
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.is_recording = False
        self.captured_data: List[Dict] = []
        self.recorder_script = self._load_recorder_script()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found. Using defaults.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "browser": {
                "headless": False,
                "slowMo": 100,
                "viewport": {"width": 1920, "height": 1080}
            },
            "recording": {
                "captureScreenshots": True,
                "highlightColor": "#00ff00",
                "highlightDuration": 500,
                "autoSave": True,
                "outputDirectory": "./recordings"
            }
        }
    
    def _load_recorder_script(self) -> str:
        """Load the JavaScript recorder script"""
        script_path = Path(__file__).parent / "recorder.js"
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Recorder script not found at {script_path}")
    
    async def initialize_browser(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        
        browser_config = self.config.get("browser", {})
        self.browser = await self.playwright.chromium.launch(
            headless=browser_config.get("headless", False),
            slow_mo=browser_config.get("slowMo", 100),
            args=['--start-maximized']  # Start maximized
        )
        
        # Use no viewport to allow full screen
        self.context = await self.browser.new_context(
            no_viewport=True,  # Allow browser to use full screen
            record_video_dir="./recordings/videos" if self.config["recording"].get("captureScreenshots") else None
        )
        
        self.page = await self.context.new_page()
        
        # Inject recorder script on every page load (including after navigation)
        await self.page.add_init_script(self.recorder_script)
        
        # Setup page event listeners to handle navigation
        self.page.on("load", self._on_page_load)
        
        print("[Recorder] Browser initialized successfully")
    
    async def navigate_to_url(self, url: str):
        """
        Navigate to specified URL
        
        Args:
            url: Target URL to navigate to
        """
        if not self.page:
            await self.initialize_browser()
        
        print(f"[Recorder] Navigating to {url}")
        await self.page.goto(url, wait_until="networkidle")
        
        # Wait for page to be fully loaded
        await self.page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)  # Additional wait for dynamic content
        
        print("[Recorder] Page loaded successfully")
    
    async def start_recording(self, url: Optional[str] = None):
        """
        Start recording user interactions
        
        Args:
            url: Optional URL to navigate to before starting recording
        """
        if not self.page:
            await self.initialize_browser()
        
        if url:
            await self.navigate_to_url(url)
        
        # Start the recorder in the browser
        try:
            recorder_ready = await self.page.evaluate("""
                () => {
                    if (window.salesforceRecorder) {
                        window.salesforceRecorder.startRecording();
                        console.log('[Recorder] Started recording');
                        return true;
                    }
                    console.error('[Recorder] salesforceRecorder not found!');
                    return false;
                }
            """)
            
            if not recorder_ready:
                print("[Recorder] ⚠ Warning: Recorder script may not be loaded properly")
            else:
                print("[Recorder] ✓ Recorder script started successfully")
                
        except Exception as e:
            print(f"[Recorder] ⚠ Error starting recorder: {e}")
            
        self.is_recording = True
        
        # Setup message listener for captured interactions
        await self.page.expose_function("pythonCapture", self._handle_capture)
        
        # Inject UI overlay
        await self._inject_ui_overlay()
        
        # Verify UI was injected successfully
        await asyncio.sleep(0.5)
        try:
            ui_exists = await self.page.evaluate("""
                () => {
                    const overlay = document.getElementById('recorder-ui-overlay');
                    if (overlay) {
                        // Flash the overlay to draw attention
                        overlay.style.animation = 'recorderPulse 1s ease-in-out 3';
                        
                        // Add keyframe animation
                        const style = document.createElement('style');
                        style.textContent = `
                            @keyframes recorderPulse {
                                0%, 100% { transform: scale(1); }
                                50% { transform: scale(1.05); box-shadow: 0 0 30px rgba(102, 126, 234, 0.8); }
                            }
                        `;
                        document.head.appendChild(style);
                        return true;
                    }
                    return false;
                }
            """)
            if ui_exists:
                print("[Recorder] ✓ UI overlay injected and visible")
            else:
                print("[Recorder] ⚠ Warning: UI overlay may not be visible")
        except Exception as e:
            print(f"[Recorder] ⚠ Warning: Could not verify UI overlay: {e}")
        
        print("[Recorder] Recording started. Click 'Stop Capture' in the UI to stop.")
        print("[Recorder] All interactions will be captured automatically.")
        print("[Recorder] 🎯 Look for the PURPLE CONTROL PANEL in the top-right corner!")
        print("")
        print("=" * 70)
        print("💡 TIP: You can DRAG the panel to move it out of the way!")
        print("💡 TIP: Click the '−' button to MINIMIZE the panel!")
        print("💡 TIP: Watch the interaction count in the panel increase as you click!")
        print("=" * 70)
        print("")
        print("=" * 70)
        print("⚠️  IMPORTANT: DO NOT CLOSE THIS TERMINAL OR BROWSER MANUALLY!")
        print("=" * 70)
        print("1. Interact with the Salesforce page (click, type, etc.)")
        print("2. Click the RED 'Stop Capture' button in the purple panel")
        print("3. Wait for the recording to save automatically")
        print("=" * 70)
        print("")
        
        # Keep the browser open and monitor for stop signal
        await self._monitor_recording()
    
    async def _inject_ui_overlay(self):
        """Inject control UI overlay into the page"""
        ui_html = self._get_ui_html()
        await self.page.evaluate(f"""
            () => {{
                const overlay = document.createElement('div');
                overlay.id = 'recorder-ui-overlay';
                overlay.innerHTML = `{ui_html}`;
                document.body.appendChild(overlay);
                
                // Make overlay draggable
                let isDragging = false;
                let currentX;
                let currentY;
                let initialX;
                let initialY;
                
                overlay.addEventListener('mousedown', (e) => {{
                    if (e.target.tagName !== 'BUTTON') {{
                        isDragging = true;
                        initialX = e.clientX - overlay.offsetLeft;
                        initialY = e.clientY - overlay.offsetTop;
                    }}
                }});
                
                document.addEventListener('mousemove', (e) => {{
                    if (isDragging) {{
                        e.preventDefault();
                        currentX = e.clientX - initialX;
                        currentY = e.clientY - initialY;
                        overlay.style.left = currentX + 'px';
                        overlay.style.top = currentY + 'px';
                        overlay.style.right = 'auto';
                    }}
                }});
                
                document.addEventListener('mouseup', () => {{
                    isDragging = false;
                }});
                
                // Setup event listeners
                document.getElementById('recorder-minimize-btn').addEventListener('click', () => {{
                    overlay.classList.toggle('minimized');
                    const btn = document.getElementById('recorder-minimize-btn');
                    btn.textContent = overlay.classList.contains('minimized') ? '+' : '−';
                    btn.title = overlay.classList.contains('minimized') ? 'Expand' : 'Minimize';
                }});
                
                document.getElementById('recorder-stop-btn').addEventListener('click', () => {{
                    window.__stopRecording = true;
                }});
                
                document.getElementById('recorder-export-btn').addEventListener('click', () => {{
                    const data = window.salesforceRecorder.getCapturedInteractions();
                    const blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'captured_interactions_' + Date.now() + '.json';
                    a.click();
                }});
                
                // Listen for captures to update count
                window.addEventListener('message', (event) => {{
                    if (event.data.type === 'RECORDER_CAPTURE') {{
                        const count = window.salesforceRecorder.getCapturedInteractions().length;
                        document.getElementById('recorder-count').textContent = count;
                        
                        // Add to list
                        const list = document.getElementById('recorder-list');
                        const item = document.createElement('div');
                        item.className = 'recorder-list-item';
                        item.innerHTML = `
                            <span class="recorder-badge">${{event.data.data.framework}}</span>
                            <strong>${{event.data.data.action}}</strong>: ${{event.data.data.label}}
                        `;
                        list.insertBefore(item, list.firstChild);
                        
                        // Keep only last 10 items
                        while (list.children.length > 10) {{
                            list.removeChild(list.lastChild);
                        }}
                    }}
                }});
            }}
        """)
    
    def _get_ui_html(self) -> str:
        """Get HTML for UI overlay"""
        return """
            <style>
                #recorder-ui-overlay {
                    position: fixed !important;
                    top: 20px !important;
                    right: 20px !important;
                    width: 280px !important;
                    max-width: 280px !important;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                    border-radius: 8px !important;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.3) !important;
                    z-index: 2147483647 !important;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
                    color: white !important;
                    padding: 12px !important;
                    pointer-events: auto !important;
                    cursor: move !important;
                    opacity: 0.95 !important;
                }
                #recorder-ui-overlay:hover {
                    opacity: 1 !important;
                }
                .recorder-header {
                    display: flex;
                    align-items: center;
                    margin-bottom: 15px;
                }
                .recorder-title {
                    font-size: 14px;
                    font-weight: 600;
                    flex: 1;
                }
                .recorder-minimize {
                    background: rgba(255,255,255,0.2) !important;
                    border: none !important;
                    color: white !important;
                    width: 20px !important;
                    height: 20px !important;
                    border-radius: 3px !important;
                    cursor: pointer !important;
                    font-size: 16px !important;
                    line-height: 1 !important;
                    padding: 0 !important;
                    margin-left: 8px !important;
                }
                .recorder-minimize:hover {
                    background: rgba(255,255,255,0.3) !important;
                }
                #recorder-ui-overlay.minimized {
                    width: 120px !important;
                    padding: 8px !important;
                }
                #recorder-ui-overlay.minimized .recorder-stats,
                #recorder-ui-overlay.minimized .recorder-buttons,
                #recorder-ui-overlay.minimized .recorder-list {
                    display: none !important;
                }
                .recorder-status {
                    width: 12px;
                    height: 12px;
                    background: #00ff00;
                    border-radius: 50%;
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
                .recorder-stats {
                    background: rgba(255,255,255,0.1);
                    padding: 12px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                    text-align: center;
                }
                .recorder-count {
                    font-size: 32px;
                    font-weight: 700;
                    margin-bottom: 5px;
                }
                .recorder-label {
                    font-size: 12px;
                    opacity: 0.8;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                .recorder-buttons {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 15px;
                }
                .recorder-btn {
                    flex: 1;
                    padding: 10px;
                    border: none;
                    border-radius: 6px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                    font-size: 14px;
                }
                .recorder-btn-stop {
                    background: #ff4757;
                    color: white;
                }
                .recorder-btn-stop:hover {
                    background: #ff3838;
                    transform: translateY(-2px);
                }
                .recorder-btn-export {
                    background: #2ed573;
                    color: white;
                }
                .recorder-btn-export:hover {
                    background: #26de81;
                    transform: translateY(-2px);
                }
                .recorder-list {
                    max-height: 200px;
                    overflow-y: auto;
                    background: rgba(0,0,0,0.2);
                    border-radius: 8px;
                    padding: 10px;
                }
                .recorder-list-item {
                    background: rgba(255,255,255,0.1);
                    padding: 8px;
                    border-radius: 4px;
                    margin-bottom: 8px;
                    font-size: 12px;
                    line-height: 1.4;
                }
                .recorder-badge {
                    display: inline-block;
                    background: rgba(255,255,255,0.2);
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: 10px;
                    margin-right: 5px;
                }
                .recorder-list::-webkit-scrollbar {
                    width: 6px;
                }
                .recorder-list::-webkit-scrollbar-thumb {
                    background: rgba(255,255,255,0.3);
                    border-radius: 3px;
                }
            </style>
            <div class="recorder-header">
                <div class="recorder-title">🎯 Recorder</div>
                <div class="recorder-status"></div>
                <button class="recorder-minimize" id="recorder-minimize-btn" title="Minimize">−</button>
            </div>
            <div class="recorder-stats">
                <div class="recorder-count" id="recorder-count">0</div>
                <div class="recorder-label">Interactions Captured</div>
            </div>
            <div class="recorder-buttons">
                <button class="recorder-btn recorder-btn-stop" id="recorder-stop-btn">Stop Capture</button>
                <button class="recorder-btn recorder-btn-export" id="recorder-export-btn">Export JSON</button>
            </div>
            <div class="recorder-list" id="recorder-list">
                <div style="text-align: center; opacity: 0.5; padding: 20px;">
                    Start interacting with the page...
                </div>
            </div>
        """
    
    async def _monitor_recording(self):
        """Monitor recording session and wait for stop signal"""
        print("[Recorder] Monitoring started - browser will stay open until you click 'Stop Capture'")
        
        last_count = 0
        
        try:
            while self.is_recording:
                # Wait a bit before checking
                await asyncio.sleep(0.5)
                
                # Periodically check and report interaction count
                try:
                    current_interactions = await self.page.evaluate("""
                        () => {
                            if (window.__recorderData) {
                                return window.__recorderData;
                            }
                            return [];
                        }
                    """)
                    
                    # Sync with Python's captured_data
                    if current_interactions:
                        for interaction in current_interactions:
                            if interaction not in self.captured_data:
                                self.captured_data.append(interaction)
                    
                    current_count = len(self.captured_data)
                    
                    if current_count > last_count:
                        print(f"[Recorder] ✓ Captured {current_count} interactions so far...")
                        last_count = current_count
                except Exception:
                    pass  # Ignore errors during count check
                
                # Check if page is still open
                try:
                    if self.page.is_closed():
                        print("[Recorder] Browser was closed by user")
                        break
                except Exception:
                    print("[Recorder] Page check failed - browser may be closed")
                    break
                
                # Check if stop button was clicked
                try:
                    stop_signal = await self.page.evaluate("window.__stopRecording || false")
                    if stop_signal:
                        print("[Recorder] Stop signal received from UI")
                        await self.stop_recording()
                        break
                except Exception as e:
                    # Check if it's a navigation error (which is OK) or a real error
                    error_msg = str(e)
                    if "Execution context was destroyed" in error_msg or "navigation" in error_msg.lower():
                        # This is expected during page navigation - continue monitoring
                        print("[Recorder] Page is navigating... continuing to monitor")
                        await asyncio.sleep(1)  # Wait a bit longer for navigation to complete
                        continue
                    else:
                        # Real error - page might be closed
                        print(f"[Recorder] Cannot check stop signal: {e}")
                        break
                
        except Exception as e:
            print(f"[Recorder] Error during monitoring: {e}")
            try:
                if not self.page.is_closed():
                    await self.stop_recording()
            except Exception:
                pass
    
    async def _on_page_load(self, page):
        """Handle page load/navigation events"""
        if not self.is_recording:
            return
        
        try:
            print(f"[Recorder] Page navigated to: {page.url}")
            
            # CRITICAL: Retrieve interactions BEFORE they're lost
            try:
                current_interactions = await self.page.evaluate("""
                    () => {
                        if (window.__recorderData) {
                            return window.__recorderData;
                        }
                        return [];
                    }
                """)
                
                # Merge with our stored data
                if current_interactions:
                    # Add any new interactions we don't have yet
                    for interaction in current_interactions:
                        if interaction not in self.captured_data:
                            self.captured_data.append(interaction)
                    
                    print(f"[Recorder] Preserved {len(self.captured_data)} interactions across navigation")
            except Exception as e:
                print(f"[Recorder] Could not retrieve interactions before navigation: {e}")
            
            # Wait for page to be ready
            await asyncio.sleep(1.5)
            
            # Restart the recorder on the new page and restore data
            try:
                await self.page.evaluate(f"""
                    (savedData) => {{
                        // Restore the saved interactions
                        window.__recorderData = savedData || [];
                        
                        if (window.salesforceRecorder) {{
                            // Point to the restored data
                            window.salesforceRecorder.capturedInteractions = window.__recorderData;
                            window.salesforceRecorder.startRecording();
                            console.log('[Recorder] Restarted recording with ' + window.__recorderData.length + ' interactions');
                        }}
                    }}
                """, self.captured_data)
                
                print(f"[Recorder] ✓ Restored {len(self.captured_data)} interactions on new page")
            except Exception as e:
                print(f"[Recorder] Could not restart recorder: {e}")
            
            # Re-inject UI overlay after navigation
            await self._inject_ui_overlay()
            
            # Update the UI counter
            try:
                await self.page.evaluate(f"""
                    () => {{
                        const counter = document.getElementById('recorder-count');
                        if (counter) {{
                            counter.textContent = {len(self.captured_data)};
                        }}
                    }}
                """)
            except Exception:
                pass
            
            # Verify and animate
            ui_exists = await self.page.evaluate("""
                () => {
                    const overlay = document.getElementById('recorder-ui-overlay');
                    if (overlay) {
                        overlay.style.animation = 'recorderPulse 1s ease-in-out 2';
                        return true;
                    }
                    return false;
                }
            """)
            
            if ui_exists:
                print("[Recorder] ✓ UI overlay re-injected after navigation")
            else:
                print("[Recorder] ⚠ Warning: UI overlay not visible after navigation")
                
        except Exception as e:
            print(f"[Recorder] Error handling page navigation: {e}")
    
    async def _handle_capture(self, data: Dict):
        """Handle captured interaction data from browser"""
        self.captured_data.append(data)
    
    async def stop_recording(self):
        """Stop recording and retrieve captured data"""
        if not self.is_recording:
            print("[Recorder] Recording is not active")
            return
        
        print("[Recorder] Stopping recording...")
        
        try:
            # Check if page is still open
            if not self.page.is_closed():
                # Stop recorder in browser
                await self.page.evaluate("window.salesforceRecorder.stopRecording()")
                
                # Retrieve all captured data
                captured = await self.page.evaluate("window.salesforceRecorder.getCapturedInteractions()")
                self.captured_data = captured
            else:
                print("[Recorder] Page was closed, using cached data")
        except Exception as e:
            print(f"[Recorder] Error retrieving data: {e}")
        
        self.is_recording = False
        
        print(f"[Recorder] Recording stopped. Captured {len(self.captured_data)} interactions.")
        
        # Auto-save if configured
        if self.config["recording"].get("autoSave", True):
            output_dir = self.config["recording"].get("outputDirectory", "./recordings")
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/recording_{timestamp}.json"
            self.export_json(filename)
    
    def export_json(self, filename: str):
        """
        Export captured interactions to JSON file
        
        Args:
            filename: Output filename
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.captured_data, f, indent=2, ensure_ascii=False)
            
            print(f"[Recorder] Exported {len(self.captured_data)} interactions to {filename}")
            return filename
        except Exception as e:
            print(f"[Recorder] Error exporting JSON: {e}")
            return None
    
    def get_captured_data(self) -> List[Dict]:
        """Get captured interaction data"""
        return self.captured_data
    
    async def close(self):
        """Close browser and cleanup"""
        try:
            if self.is_recording:
                await self.stop_recording()
            
            if self.context:
                try:
                    await self.context.close()
                except Exception:
                    pass  # Already closed
            
            if self.browser:
                try:
                    if self.browser.is_connected():
                        await self.browser.close()
                except Exception:
                    pass  # Already closed
            
            if self.playwright:
                try:
                    await self.playwright.stop()
                except Exception:
                    pass
            
            print("[Recorder] Browser closed")
        except Exception as e:
            print(f"[Recorder] Error during cleanup: {e}")
    
    async def run_interactive_session(self, url: str):
        """
        Run an interactive recording session
        
        Args:
            url: URL to start recording from
        """
        try:
            await self.start_recording(url)
        except KeyboardInterrupt:
            print("\n[Recorder] Interrupted by user")
        finally:
            await self.close()


async def main():
    """Main entry point for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Salesforce Automation Recorder")
    parser.add_argument("--url", required=True, help="Salesforce URL to record")
    parser.add_argument("--output", default=None, help="Output JSON filename")
    parser.add_argument("--config", default="config.json", help="Config file path")
    
    args = parser.parse_args()
    
    recorder = SalesforceRecorder(config_path=args.config)
    
    try:
        await recorder.run_interactive_session(args.url)
        
        # Export if output specified
        if args.output:
            recorder.export_json(args.output)
        
    except Exception as e:
        print(f"[Recorder] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await recorder.close()


if __name__ == "__main__":
    asyncio.run(main())
