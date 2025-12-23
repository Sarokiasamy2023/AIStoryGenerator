"""
Salesforce MFA Login Test - Single Browser
===========================================
This script runs Salesforce login with MFA on a single Chrome browser.

Flow:
- Open Chrome browser
- Navigate to Salesforce login page
- Enter credentials
- Enter TOTP MFA code
- Verify successful login
- Keep browser open for 3 minutes after successful validation
"""

import json
import logging
import os
import time
import asyncio
import re
import pyotp
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright.async_api import TimeoutError as PlaywrightAsyncTimeoutError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('salesforce_mfa_test.log'),
        logging.StreamHandler()
    ]
)


@dataclass
class TestResult:
    test_name: str
    status: str
    start_time: str
    end_time: str = ""
    duration_seconds: float = 0
    error: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


# DCP Environment configurations
DCP_ENVIRONMENTS = {
    'dcp-external': {
        'name': 'DCP External (UAT)',
        'base_url': 'https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s',
        'email': 'sarokiasamy@dmigs.com',
        'password': 'SilluSujuCoco2023$$$',
        'totp_secret': 'FXZCVNVSPGFQNDYZ3JCDIKZAYRPQXRUL'
    },
    'dcp-internal': {
        'name': 'DCP Internal (UAT)',
        'base_url': 'https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/',
        'email': 'sarokiasamy@dmigs.com.dcp.dcpuat',  # Update with actual internal credentials
        'password': 'Grantee@123',  # Update with actual internal credentials
        'totp_secret': 'QW5QZ3BFWRYF2R732N46BB4BEIFQMK5I'  # Update with actual internal TOTP
    }
}


POST_LOGIN_DISAGREE_SELECTOR = 'text=/I Disagree/i'
POST_LOGIN_DISAGREE_TOGGLE_SELECTORS = [
    'role=switch[name=/I\s*Disagree/i]',
    'role=checkbox[name=/I\s*Disagree/i]',
    'label:has-text("I Disagree")',
    'text=/I\s*Disagree/i',
]
POST_LOGIN_NEXT_SELECTORS = [
    'button:has-text("Next")',
    'input[value="Next"]',
    'button:text-is("Next")',
    '//button[contains(text(), "Next")]',
    '//input[@value="Next"]',
    'button.nextButton',
    'input.nextButton',
]
POST_LOGIN_FINISH_SELECTORS = [
    'button:has-text("Finish")',
    'xpath=//button[normalize-space()="Finish"]',
    'xpath=//button[contains(text(),"Finish")]',
    'xpath=//*[contains(@class,"button") and contains(text(),"Finish")] ',
    'xpath=//input[@value="Finish"]',
    'text=Finish',
    'button.slds-button:has-text("Finish")',
]


def normalize_environment_key(environment: str) -> str:
    key = (environment or '').strip().lower()
    if not key:
        return 'dcp-external'
    if key in ('none', 'no', 'false', '0'):
        return 'none'
    key = key.replace('_', '-').replace(' ', '-')
    # Common variants
    if key in ('dcp-external', 'external', 'dcp-external-uat', 'dcp-uat-external'):
        return 'dcp-external'
    if key in ('dcp-internal', 'internal', 'dcp-internal-uat', 'dcp-uat-internal'):
        return 'dcp-internal'
    return key


class SalesforceMFALogin:
    """
    Runs Salesforce MFA login test on a single Chrome browser.
    Supports multiple DCP environments (external/internal).
    """
    
    def __init__(self, headless: bool = False, environment: str = 'dcp-external', hold_browser: bool = True, browser: str = 'chrome'):
        # Get environment configuration
        environment = normalize_environment_key(environment)
        env_config = DCP_ENVIRONMENTS.get(environment, DCP_ENVIRONMENTS['dcp-external'])
        
        # Salesforce credentials from environment config
        self.environment = environment
        self.env_name = env_config['name']
        self.base_url = env_config['base_url']
        self.email = env_config['email']
        self.password = env_config['password']
        self.totp_secret = env_config['totp_secret']
        
        self.headless = headless
        self.hold_browser = hold_browser  # Whether to keep browser open after login
        self.browser = browser  # Browser type: chrome, chromium, edge, firefox
        self.screenshots_dir = "screenshots_salesforce"
        self.storage_state_file = "dcp_session_state.json"  # File to save browser state
        self.result = None
        
        # Create screenshots directory
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        logging.info("="*60)
        logging.info(f"Salesforce MFA Login - {self.env_name}")
        logging.info(f"Environment: {environment}")
        logging.info(f"Target URL: {self.base_url}")
        logging.info(f"Email: {self.email}")
        logging.info(f"Screenshots: {self.screenshots_dir}")
        logging.info("="*60)

    def take_screenshot(self, page, name: str) -> str:
        """Take a screenshot with timestamp."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.screenshots_dir}/{name}_{timestamp}.png"
            page.screenshot(path=filename)
            logging.info(f"Screenshot saved: {filename}")
            return filename
        except Exception as e:
            logging.error(f"Screenshot failed: {str(e)}")
            return ""

    def check_login_success(self, page) -> bool:
        """Check if login was successful."""
        try:
            try:
                logout_loc = page.locator('text=/Log\s*Out/i').first
                if logout_loc.is_visible(timeout=1500):
                    logging.info("Logout text visible - treating as successful login")
                    return True
            except Exception:
                pass

            # Check URL for success indicators
            current_url = page.url.lower()
            if 'lightning' in current_url or 'home' in current_url or 'setup' in current_url:
                # Some Salesforce redirects include 'lightningLoginFlow' even after auth.
                if 'login.salesforce.com' not in current_url:
                    logging.info(f"URL indicates likely successful login: {current_url}")
                    return True
            
            # Check if we're no longer on the login page
            if 'login.salesforce.com' not in current_url and 'salesforce.com' in current_url:
                logging.info(f"Redirected away from login: {current_url}")
                return True
                
            return False
            
        except Exception as e:
            logging.error(f"Error checking login success: {str(e)}")
            return False

    def handle_post_login_steps(self, page):
        """
        Handle post-login dialogs/wizards that may appear after MFA validation.
        Clicks: "I Disagree" -> "Next" -> "Finish"
        """
        logging.info("="*50)
        logging.info("[POST-LOGIN] Handling post-login steps...")
        
        # Step 1: Click "I Disagree" button if present
        try:
            logging.info("[POST-LOGIN] Waiting 2 seconds before looking for 'I Disagree' button...")
            page.wait_for_timeout(2000)
            
            logging.info("[POST-LOGIN] Looking for 'I Disagree' toggle...")
            clicked_disagree = False
            for selector in POST_LOGIN_DISAGREE_TOGGLE_SELECTORS:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=2500):
                        btn.click(force=True)
                        clicked_disagree = True
                        logging.info(f"[POST-LOGIN] ✓ Clicked 'I Disagree' using: {selector}")
                        self.take_screenshot(page, "06_clicked_disagree")
                        page.wait_for_timeout(2000)
                        break
                except Exception:
                    continue
        except Exception as e:
            logging.info(f"[POST-LOGIN] 'I Disagree' button not found or not needed: {e}")
        
        # Step 2: Click "Next" button if present
        try:
            logging.info("[POST-LOGIN] Looking for 'Next' button...")
            for selector in POST_LOGIN_NEXT_SELECTORS:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=3000):
                        btn.click()
                        logging.info("[POST-LOGIN] ✓ Clicked 'Next' button")
                        self.take_screenshot(page, "07_clicked_next")
                        page.wait_for_timeout(2000)
                        break
                except:
                    continue
        except Exception as e:
            logging.info(f"[POST-LOGIN] 'Next' button not found or not needed: {e}")
        
        # Step 3: Click "Finish" button if present
        try:
            logging.info("[POST-LOGIN] Looking for 'Finish' button...")
            page.wait_for_timeout(2000)  # Wait for modal to fully render
            
            clicked = False
            for selector in POST_LOGIN_FINISH_SELECTORS:
                try:
                    logging.info(f"[POST-LOGIN] Trying Finish selector: {selector}")
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=3000):
                        # Force click to ensure it works
                        btn.click(force=True)
                        logging.info(f"[POST-LOGIN] ✓ Clicked 'Finish' button using: {selector}")
                        self.take_screenshot(page, "08_clicked_finish")
                        page.wait_for_timeout(2000)
                        clicked = True
                        break
                except Exception as e:
                    logging.info(f"[POST-LOGIN] Selector {selector} failed: {e}")
                    continue
            
            if not clicked:
                logging.warning("[POST-LOGIN] Could not click Finish button with any selector")
        except Exception as e:
            logging.info(f"[POST-LOGIN] 'Finish' button not found or not needed: {e}")
        
        logging.info("[POST-LOGIN] Post-login steps completed")
        logging.info("="*50)

    def run_test(self) -> TestResult:
        """
        Run MFA login test:
        1. Open browser and navigate to login page
        2. Enter credentials
        3. Enter TOTP code
        4. Verify successful login
        5. Keep browser open for 3 minutes after successful validation
        """
        start_time = datetime.now()
        result = TestResult(
            test_name="Salesforce MFA Login",
            status="started",
            start_time=start_time.isoformat(),
            details={"mfa_validated": False, "attempts": 0}
        )
        
        logging.info("="*60)
        logging.info("STARTING SALESFORCE MFA LOGIN TEST")
        logging.info("="*60)
        
        with sync_playwright() as p:
            # Launch browser based on selected type
            logging.info(f"Launching {self.browser} browser...")
            
            if self.browser == 'firefox':
                browser = p.firefox.launch(
                    headless=self.headless,
                    args=['--start-maximized'] if not self.headless else []
                )
            elif self.browser == 'edge':
                # Edge uses Chromium engine
                edge_paths = [
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                ]
                edge_path = None
                for path in edge_paths:
                    if os.path.exists(path):
                        edge_path = path
                        break
                
                if edge_path:
                    browser = p.chromium.launch(
                        headless=self.headless,
                        executable_path=edge_path,
                        args=['--start-maximized']
                    )
                else:
                    logging.warning("Edge not found, using Chromium")
                    browser = p.chromium.launch(
                        headless=self.headless,
                        args=['--start-maximized']
                    )
            elif self.browser in ('chrome', 'chrome-headless'):
                # Find Chrome executable
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                ]
                
                chrome_path = None
                for path in chrome_paths:
                    if os.path.exists(path):
                        chrome_path = path
                        break
                
                if chrome_path:
                    browser = p.chromium.launch(
                        headless=self.headless or self.browser == 'chrome-headless',
                        executable_path=chrome_path,
                        args=['--start-maximized']
                    )
                else:
                    logging.warning("Chrome not found, using Chromium")
                    browser = p.chromium.launch(
                        headless=self.headless or self.browser == 'chrome-headless',
                        args=['--start-maximized']
                    )
            else:
                # Default to Chromium
                browser = p.chromium.launch(
                    headless=self.headless,
                    args=['--start-maximized']
                )
            
            context = browser.new_context(no_viewport=True)
            page = context.new_page()
            logging.info("Browser launched")
            
            try:
                # Navigate to login page
                logging.info(f"Navigating to: {self.base_url}")
                page.goto(self.base_url, wait_until='networkidle', timeout=30000)
                self.take_screenshot(page, "01_login_page")

                if self.environment == 'dcp-external':
                    try:
                        xms = page.locator('text=/XMS UAT/i').first
                        if xms.is_visible(timeout=5000):
                            try:
                                with page.expect_popup(timeout=7000) as popup_info:
                                    xms.click()
                                popup_page = popup_info.value
                                popup_page.wait_for_load_state('domcontentloaded', timeout=30000)
                                page = popup_page
                                logging.info(f"Clicked 'XMS UAT' (popup). Now on: {page.url}")
                            except PlaywrightTimeoutError:
                                logging.info("Clicked 'XMS UAT' (same tab)")
                                page.wait_for_load_state('networkidle', timeout=30000)

                            self.take_screenshot(page, "01b_clicked_xms_uat")
                    except Exception as e:
                        logging.info(f"'XMS UAT' click not performed: {e}")

                # ===== STEP 1: Enter credentials =====
                logging.info("Waiting for login form...")

                try:
                    sign_in_selectors = [
                        'role=tab[name=/Sign\s*in/i]',
                        'button:has-text("Sign in")',
                        'text=/^Sign\s*in$/i',
                    ]
                    for sel in sign_in_selectors:
                        try:
                            el = page.locator(sel).first
                            if el.is_visible(timeout=1500):
                                el.click()
                                page.wait_for_timeout(750)
                                break
                        except Exception:
                            continue
                except Exception:
                    pass
                
                # Wait for username field
                username_selectors = [
                    'input#username',
                    'input[name="username"]',
                    'input#user_email',
                    'input[name="user[email]"]',
                    'input[autocomplete="username"]',
                    'input[type="email"]',
                ]
                username_field = None

                try:
                    email_by_label = page.get_by_label(re.compile(r'^\s*Email\s*address\s*$', re.I)).first
                    if email_by_label.is_visible(timeout=8000):
                        username_field = '__by_label__'
                        email_by_label.fill(self.email)
                        logging.info("Found email field by label: Email address")
                except Exception:
                    pass
                
                for sel in username_selectors:
                    try:
                        page.wait_for_selector(sel, state='visible', timeout=10000)
                        username_field = sel
                        logging.info(f"Found username field: {sel}")
                        break
                    except:
                        continue
                
                if not username_field:
                    raise Exception("Could not find username field")
                
                logging.info("Entering credentials...")

                # Fill email (if not already filled by label)
                if username_field != '__by_label__':
                    page.fill(username_field, self.email)
                    page.wait_for_timeout(300)
                
                # Fill password
                password_selectors = [
                    'input#password',
                    'input[name="pw"]',
                    'input#user_password',
                    'input[name="user[password]"]',
                    'input[autocomplete="current-password"]',
                    'input[type="password"]',
                ]

                try:
                    password_by_label = page.get_by_label(re.compile(r'^\s*Password\s*$', re.I)).first
                    if password_by_label.is_visible(timeout=4000):
                        password_by_label.fill(self.password)
                        logging.info("Found password field by label: Password")
                    else:
                        raise Exception("Password label not visible")
                except Exception:
                    for sel in password_selectors:
                        try:
                            if page.locator(sel).is_visible(timeout=2000):
                                page.fill(sel, self.password)
                                logging.info(f"Found password field: {sel}")
                                break
                        except:
                            continue
                
                page.wait_for_timeout(300)
                self.take_screenshot(page, "02_credentials_filled")
                
                # Click login button
                logging.info("Clicking login button...")
                login_selectors = [
                    'input#Login',
                    'button#Login',
                    'button:has-text("Submit")',
                    'input[value="Submit"]',
                    'input[type="submit"]',
                    'button[type="submit"]',
                ]
                for sel in login_selectors:
                    try:
                        btn = page.locator(sel).first
                        if btn.is_visible(timeout=2000):
                            btn.click()
                            logging.info(f"Clicked login button: {sel}")
                            break
                    except:
                        continue
                
                page.wait_for_timeout(3000)
                self.take_screenshot(page, "03_after_login_click")
                
                # ===== STEP 2: Enter TOTP code =====
                logging.info("Looking for MFA input...")
                
                # Salesforce MFA input selectors
                mfa_selectors = [
                    'input#emc',
                    'input[name="emc"]',
                    'input#tc',
                    'input[name="tc"]',
                    'input[type="text"][inputmode="numeric"]',
                    'input[name="verificationCode"]',
                    'input[placeholder*="code"]',
                    'input[placeholder*="Code"]',
                ]
                
                mfa_selector = None
                for sel in mfa_selectors:
                    try:
                        mfa_field = page.locator(sel)
                        if mfa_field.is_visible(timeout=3000):
                            mfa_selector = sel
                            logging.info(f"Found MFA field: {sel}")
                            break
                    except:
                        continue
                
                if not mfa_selector:
                    # Maybe already logged in?
                    if self.check_login_success(page):
                        result.details["mfa_validated"] = True
                        result.details["attempts"] = 0
                        result.status = "success"
                        logging.info("[SUCCESS] Already logged in - no MFA required!")
                        self.take_screenshot(page, "04_already_logged_in")
                    else:
                        raise Exception("Could not find MFA input field")
                else:
                    # Try up to 3 times with fresh TOTP codes
                    max_attempts = 3
                    attempt = 0
                    validated = False
                    
                    while not validated and attempt < max_attempts:
                        attempt += 1
                        
                        # Generate fresh TOTP code - wait for fresh window
                        totp = pyotp.TOTP(self.totp_secret)
                        
                        # Wait until we're at the start of a fresh 30-second window
                        time_remaining = totp.interval - (time.time() % totp.interval)
                        if time_remaining < 10:  # Less than 10 seconds left in current window
                            logging.info(f"Waiting {time_remaining:.1f}s for fresh TOTP window...")
                            time.sleep(time_remaining + 1)  # Wait for new window
                        
                        mfa_code = totp.now()
                        time_remaining = totp.interval - (time.time() % totp.interval)
                        logging.info(f"Attempt {attempt}: Generated TOTP = {mfa_code} (valid for {time_remaining:.0f}s)")
                        
                        # Clear and enter code
                        mfa_field = page.locator(mfa_selector)
                        mfa_field.fill("")
                        page.wait_for_timeout(100)
                        mfa_field.fill(mfa_code)
                        
                        self.take_screenshot(page, f"04_mfa_code_attempt_{attempt}")
                        
                        # Submit
                        submit_selectors = [
                            'input#save',
                            'button#save',
                            'button:has-text("Submit")',
                            'input[value="Submit"]',
                            'input[type="submit"]',
                            'button[type="submit"]',
                            'input.button',
                        ]
                        
                        for submit_sel in submit_selectors:
                            try:
                                submit_btn = page.locator(submit_sel).first
                                if submit_btn.is_visible(timeout=1000):
                                    submit_btn.click()
                                    break
                            except:
                                continue
                        
                        page.wait_for_timeout(3000)
                        
                        # Check if validated
                        if self.check_login_success(page):
                            validated = True
                            result.details["mfa_validated"] = True
                            result.details["attempts"] = attempt
                            result.status = "success"
                            logging.info(f"[SUCCESS] MFA VALIDATED on attempt {attempt}!")
                            self.take_screenshot(page, "05_login_success")
                            
                            # Post-login steps: Handle any dialogs/wizards
                            self.handle_post_login_steps(page)
                        else:
                            # Some environments route through a post-login banner flow
                            self.handle_post_login_steps(page)
                            if self.check_login_success(page):
                                validated = True
                                result.details["mfa_validated"] = True
                                result.details["attempts"] = attempt
                                result.status = "success"
                                logging.info(f"[SUCCESS] Post-login flow completed on attempt {attempt}!")
                                self.take_screenshot(page, "05_login_success_post_login")
                            else:
                                logging.info(f"Attempt {attempt} failed, retrying...")
                                page.wait_for_timeout(3000)
                    
                    if not validated:
                        result.status = "failed"
                        result.error = f"MFA validation failed after {max_attempts} attempts"
                        logging.info("[FAILED] MFA validation failed")
                        self.take_screenshot(page, "05_login_failed")
                
                # Keep browser open if successful and hold_browser is True
                if result.status == "success":
                    logging.info("="*50)
                    logging.info("[HOLD] Login successful!")
                    
                    # Save browser storage state (cookies, localStorage) for reuse
                    try:
                        context.storage_state(path=self.storage_state_file)
                        logging.info(f"[SAVE] Browser session saved to {self.storage_state_file}")
                        result.details['storage_state_file'] = self.storage_state_file
                    except Exception as e:
                        logging.warning(f"Could not save storage state: {e}")
                    
                    if self.hold_browser:
                        logging.info("[HOLD] Keeping browser open for 3 minutes...")
                        logging.info("[HOLD] You can interact with the browser now.")
                        logging.info("="*50)
                        time.sleep(180)
                        logging.info("[CLOSE] 3 minutes elapsed. Closing browser...")
                    else:
                        logging.info("[DONE] Login complete. Closing browser...")
                        logging.info("="*50)
                
            except PlaywrightTimeoutError as e:
                result.status = "timeout"
                result.error = f"Timeout: {str(e)}"
                logging.error(f"Timeout error: {str(e)}")
                self.take_screenshot(page, "error_timeout")
                
            except Exception as e:
                result.status = "error"
                result.error = str(e)
                logging.error(f"Error: {str(e)}")
                self.take_screenshot(page, "error_exception")
            
            finally:
                # Close browser
                try:
                    context.close()
                    browser.close()
                except:
                    pass
        
        end_time = datetime.now()
        result.end_time = end_time.isoformat()
        result.duration_seconds = round((end_time - start_time).total_seconds(), 2)
        self.result = result
        return result

    def save_results(self) -> str:
        """Save test results to JSON file."""
        if not self.result:
            return ""
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"salesforce_mfa_test_{timestamp}.json"
        
        results_data = {
            "test_run": {
                "timestamp": timestamp,
                "target_url": self.base_url,
                "email": self.email,
            },
            "result": {
                "test_name": self.result.test_name,
                "status": self.result.status,
                "start_time": self.result.start_time,
                "end_time": self.result.end_time,
                "duration_seconds": self.result.duration_seconds,
                "error": self.result.error,
                "details": self.result.details,
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logging.info(f"Results saved to: {filename}")
        return filename

    def print_summary(self):
        """Print test summary."""
        if not self.result:
            return
            
        print("\n" + "="*60)
        print("SALESFORCE MFA LOGIN TEST SUMMARY")
        print("="*60)
        
        status_icon = "[PASS]" if self.result.status == "success" else "[FAIL]"
        print(f"{status_icon} {self.result.test_name}")
        print(f"    Duration: {self.result.duration_seconds}s")
        if self.result.error:
            print(f"    Error: {self.result.error}")
        if self.result.details.get("mfa_validated"):
            print(f"    MFA Validated: Yes (Attempt {self.result.details.get('attempts', 'N/A')})")
        
        print("="*60)


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("SALESFORCE MFA LOGIN TEST")
    print("="*60)
    print("This will open a Chrome browser and perform MFA login.")
    print("Browser will stay open 3 minutes after successful validation.")
    print("="*60 + "\n")
    
    runner = SalesforceMFALogin(headless=False)
    
    try:
        result = runner.run_test()
        runner.save_results()
        runner.print_summary()
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        logging.error(f"Test execution failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()


async def login_with_mfa_async(
    page,
    environment: str = 'dcp-external',
    target_url: str = '',
    progress: Optional[Callable[[str, str, Dict[str, Any]], Awaitable[None]]] = None,
) -> bool:
    env_key = normalize_environment_key(environment)
    if env_key == 'none':
        return True
    env_config = DCP_ENVIRONMENTS.get(env_key, DCP_ENVIRONMENTS['dcp-external'])

    email = env_config['email']
    password = env_config['password']
    totp_secret = env_config['totp_secret']

    async def emit(level: str, message: str, details: Optional[Dict[str, Any]] = None):
        if not progress:
            return
        try:
            await progress(level, message, details or {})
        except Exception:
            return

    nav_url = target_url or env_config['base_url']
    if nav_url:
        await emit('info', f'🔐 MFA: Navigating to {nav_url}', {'env': env_key})
        await page.goto(nav_url, wait_until='networkidle')

    original_page = page
    if env_key == 'dcp-external':
        try:
            xms = page.locator('text=/XMS UAT/i').first
            if await xms.is_visible(timeout=5000):
                await emit('info', "🔐 MFA: Clicking 'XMS UAT'", {'env': env_key})
                try:
                    async with page.expect_popup(timeout=7000) as popup_info:
                        await xms.click()
                    popup_page = await popup_info.value
                    await popup_page.wait_for_load_state('domcontentloaded')
                    page = popup_page
                except PlaywrightAsyncTimeoutError:
                    await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(1000)

                try:
                    login_gov_selectors = [
                        'text=/login\.gov/i',
                        'role=button[name=/login\.gov/i]',
                        'a:has-text("LOGIN.GOV")',
                        'button:has-text("LOGIN.GOV")',
                        'img[alt*="login" i]',
                        'img[src*="login" i]',
                    ]
                    for sel in login_gov_selectors:
                        try:
                            loc = page.locator(sel).first
                            if await loc.is_visible(timeout=2500):
                                await emit('info', "🔐 MFA: Clicking 'login.gov'", {'env': env_key, 'selector': sel})
                                await loc.click()
                                await page.wait_for_timeout(1000)
                                break
                        except Exception:
                            continue
                except Exception:
                    pass

                try:
                    agree_selectors = [
                        'role=button[name=/agree/i]',
                        'button:has-text("Agree")',
                        'text=/^Agree$/i',
                        'a:has-text("Agree")',
                        'input[value="Agree" i]',
                        'role=button[name=/i\s*agree/i]',
                        'button:has-text("I Agree")',
                        'text=/I\s*Agree/i',
                    ]
                    for sel in agree_selectors:
                        try:
                            loc = page.locator(sel).first
                            if await loc.is_visible(timeout=2500):
                                await emit('info', "🔐 MFA: Clicking 'Agree'", {'env': env_key, 'selector': sel})
                                await loc.click()
                                await page.wait_for_timeout(1000)
                                break
                        except Exception:
                            continue
                except Exception:
                    pass
        except Exception:
            pass

    async def check_login_success_async() -> bool:
        try:
            # Don't treat the identity verification page as a successful login.
            try:
                current_url = (page.url or '').lower()
                if '/identity/verification' in current_url or 'totpverification' in current_url:
                    return False
            except Exception:
                pass

            try:
                verify_hdr = page.locator('text=/Verify\s+Your\s+Identity/i').first
                if await verify_hdr.is_visible(timeout=800):
                    return False
            except Exception:
                pass

            try:
                logout_loc = page.locator('text=/Log\s*Out/i').first
                if await logout_loc.is_visible(timeout=1500):
                    return True
            except Exception:
                pass

            current_url = (page.url or '').lower()
            if ('lightning' in current_url or 'home' in current_url or 'setup' in current_url) and 'login.salesforce.com' not in current_url:
                return True
            if 'login.salesforce.com' not in current_url and 'salesforce.com' in current_url:
                return True
            return False
        except Exception:
            return False

    async def handle_post_login_steps_async():
        step_wait_ms = 2000 if env_key == 'dcp-external' else 1000

        async def click_first_visible(selectors: List[str], timeout_ms: int = 1500, force: bool = False) -> bool:
            frames = []
            try:
                frames = list(page.frames)
            except Exception:
                frames = []
            if not frames:
                frames = [page.main_frame]

            for frame in frames:
                for selector in selectors:
                    try:
                        loc = frame.locator(selector).first
                        if await loc.is_visible(timeout=timeout_ms):
                            if force:
                                await loc.click(force=True)
                            else:
                                await loc.click()
                            return True
                    except Exception:
                        continue
            return False

        try:
            if env_key != 'dcp-external':
                await page.wait_for_timeout(step_wait_ms)

            toggled = await click_first_visible(POST_LOGIN_DISAGREE_TOGGLE_SELECTORS, timeout_ms=2000, force=True)
            if not toggled:
                agree_toggle_selectors = [
                    'role=switch[name=/I\s*Agree/i]',
                    'role=checkbox[name=/I\s*Agree/i]',
                    'label:has-text("I Agree")',
                    'text=/I\s*Agree/i',
                ]
                toggled = await click_first_visible(agree_toggle_selectors, timeout_ms=2000, force=True)

            # DCP-external requirement: after clicking I Disagree (or fallback), wait 2 seconds.
            if env_key == 'dcp-external' and toggled:
                await page.wait_for_timeout(2000)
            else:
                await page.wait_for_timeout(step_wait_ms)
        except Exception:
            pass

        try:
            if env_key != 'dcp-external':
                await page.wait_for_timeout(step_wait_ms)

            if await click_first_visible(POST_LOGIN_NEXT_SELECTORS, timeout_ms=2000, force=False):
                # DCP-external requirement: after clicking Next, wait 2 seconds.
                if env_key == 'dcp-external':
                    await page.wait_for_timeout(2000)
                else:
                    await page.wait_for_timeout(step_wait_ms)
        except Exception:
            pass

        try:
            await page.wait_for_timeout(step_wait_ms)
            if await click_first_visible(POST_LOGIN_FINISH_SELECTORS, timeout_ms=2500, force=True):
                await page.wait_for_timeout(step_wait_ms)
        except Exception:
            pass

    try:
        try:
            sign_in_selectors = [
                'role=tab[name=/Sign\s*in/i]',
                'button:has-text("Sign in")',
                'text=/^Sign\s*in$/i',
            ]
            for sel in sign_in_selectors:
                try:
                    el = page.locator(sel).first
                    if await el.is_visible(timeout=1200):
                        await el.click()
                        await page.wait_for_timeout(750)
                        break
                except Exception:
                    continue
        except Exception:
            pass

        email_filled = False
        try:
            email_by_label = page.get_by_label(re.compile(r'^\s*Email\s*address\s*$', re.I)).first
            if await email_by_label.is_visible(timeout=8000):
                await emit('info', '🔐 MFA: Filling email/username', {'env': env_key})
                await email_by_label.fill(email)
                email_filled = True
        except Exception:
            pass

        username_selectors = [
            'input#username',
            'input[name="username"]',
            'input#user_email',
            'input[name="user[email]"]',
            'input[autocomplete="username"]',
            'input[type="email"]',
        ]
        username_sel = None
        for sel in username_selectors:
            try:
                loc = page.locator(sel).first
                if await loc.is_visible(timeout=1500):
                    username_sel = sel
                    break
            except Exception:
                continue

        if not username_sel and not email_filled:
            return await check_login_success_async()

        if username_sel and not email_filled:
            await emit('info', '🔐 MFA: Filling username', {'env': env_key})
            await page.fill(username_sel, email)
            await page.wait_for_timeout(1000)

        try:
            password_by_label = page.get_by_label(re.compile(r'^\s*Password\s*$', re.I)).first
            if await password_by_label.is_visible(timeout=4000):
                await emit('info', '🔐 MFA: Filling password', {'env': env_key})
                await password_by_label.fill(password)
                await page.wait_for_timeout(1000)
            else:
                raise Exception("Password label not visible")
        except Exception:
            password_selectors = [
                'input#password',
                'input[name="pw"]',
                'input#user_password',
                'input[name="user[password]"]',
                'input[autocomplete="current-password"]',
                'input[type="password"]',
            ]
            for sel in password_selectors:
                try:
                    loc = page.locator(sel).first
                    if await loc.is_visible(timeout=1500):
                        await emit('info', '🔐 MFA: Filling password', {'env': env_key})
                        await page.fill(sel, password)
                        await page.wait_for_timeout(1000)
                        break
                except Exception:
                    continue

        login_selectors = [
            'input#Login',
            'button#Login',
            'button:has-text("Submit")',
            'input[value="Submit"]',
            'input[type="submit"]',
            'button[type="submit"]',
        ]

        if env_key == 'dcp-internal':
            login_selectors = [
                'button:has-text("Log In to Sandbox")',
                'input[value*="Log In to Sandbox" i]',
                'text=/Log\s*In\s*to\s*Sandbox/i',
            ] + login_selectors
        for sel in login_selectors:
            try:
                btn = page.locator(sel).first
                if await btn.is_visible(timeout=1500):
                    await emit('info', f'🔐 MFA: Clicking login ({"Log In to Sandbox" if env_key == "dcp-internal" else "Login"})', {'env': env_key})
                    await btn.click()
                    break
            except Exception:
                continue

        await page.wait_for_timeout(2000 if env_key == 'dcp-internal' else 2500)

        if await check_login_success_async():
            await handle_post_login_steps_async()
            return True

        # DCP-external sometimes shows the banner agreement flow before any
        # "login success" signals (like Log Out). Attempt to complete it anyway.
        if env_key == 'dcp-external':
            try:
                await emit('info', '🔐 MFA: Checking for banner agreement flow', {'env': env_key})
                await handle_post_login_steps_async()
                await page.wait_for_timeout(2000)
                if await check_login_success_async():
                    return True
            except Exception:
                pass

        mfa_selectors = [
            'input#emc',
            'input[name="emc"]',
            'input#tc',
            'input[name="tc"]',
            'input#smc',
            'input[type="text"][inputmode="numeric"]',
            'input[name="verificationCode"]',
            'input[aria-label*="Verification Code" i]',
            'input[placeholder*="Verification" i]',
            'input[placeholder*="code" i]',
        ]

        mfa_sel = None
        for sel in mfa_selectors:
            try:
                loc = page.locator(sel).first
                if await loc.is_visible(timeout=2000):
                    mfa_sel = sel
                    break
            except Exception:
                continue

        if not mfa_sel:
            return await check_login_success_async()

        submit_selectors = [
            'input#save',
            'button#save',
            'button:has-text("Submit")',
            'input[value="Submit"]',
            'input[type="submit"]',
            'button[type="submit"]',
            'input.button',
        ]

        if env_key == 'dcp-internal':
            submit_selectors = [
                'button:has-text("Verify")',
                'button:text-is("Verify")',
                'input[value="Verify"]',
            ] + submit_selectors

        max_attempts = 3
        totp = pyotp.TOTP(totp_secret)
        for _ in range(max_attempts):
            time_remaining = totp.interval - (time.time() % totp.interval)
            if time_remaining < 10:
                await asyncio.sleep(time_remaining + 1)

            code = totp.now()
            await emit('info', '🔐 MFA: Entering verification code (TOTP)', {'env': env_key})
            await page.fill(mfa_sel, "")
            await page.fill(mfa_sel, code)
            if env_key == 'dcp-external':
                await page.wait_for_timeout(2000)

            for submit_sel in submit_selectors:
                try:
                    btn = page.locator(submit_sel).first
                    if await btn.is_visible(timeout=1000):
                        await emit('info', f'🔐 MFA: Clicking {"Verify" if env_key == "dcp-internal" else "Submit"}', {'env': env_key})
                        await btn.click()
                        break
                except Exception:
                    continue

            await page.wait_for_timeout(2000 if env_key in ('dcp-internal', 'dcp-external') else 2500)

            # DCP-external frequently lands on the banner agreement screen after TOTP submit.
            # Run the post-login steps regardless of "success" state, then re-check.
            if env_key == 'dcp-external':
                try:
                    await emit('info', '🔐 MFA: Completing banner agreement steps', {'env': env_key})
                    await handle_post_login_steps_async()
                    await page.wait_for_timeout(2000)
                except Exception:
                    pass

            if await check_login_success_async():
                await handle_post_login_steps_async()
                return True

            await page.wait_for_timeout(1500)

        return False

    except PlaywrightAsyncTimeoutError:
        ok = await check_login_success_async()
        if ok and page is not original_page:
            try:
                await original_page.bring_to_front()
            except Exception:
                pass
            try:
                await original_page.reload(wait_until='networkidle')
            except Exception:
                pass
        return ok

    finally:
        if page is not original_page:
            try:
                await original_page.bring_to_front()
            except Exception:
                pass
            try:
                await original_page.reload(wait_until='networkidle')
            except Exception:
                pass
