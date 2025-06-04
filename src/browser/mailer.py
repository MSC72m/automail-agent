import time
import asyncio
from typing import Optional, Dict, List, Tuple
from urllib.parse import urlencode
from playwright.async_api import Page, Locator

from src.core.logger import get_logger
from src.browser.interfaces.mailer_interfaces import IMailer
from src.browser.lunchers import BrowserLauncher
from src.schemas.browser import BrowserConfig
from src.schemas.email import EmailInput
from src.core.enums import BrowserType
from src.schemas.config import config

logger = get_logger(__name__)


class ElementFinder:
    """Strategy for finding and interacting with web elements using multiple selectors."""
    
    def __init__(self, page: Page):
        self.page = page
    
    async def find_and_click(self, selectors: List[str], description: str, timeout: int = 3000) -> bool:
        """Find element using multiple selectors and click it."""
        logger.debug(f"🔍 Looking for {description}...")
        
        for i, selector in enumerate(selectors, 1):
            try:
                logger.debug(f"  Trying selector {i}/{len(selectors)}: {selector}")
                
                element = await self.page.query_selector(selector)
                if not element:
                    logger.debug(f"    ❌ Element not found")
                    continue
                
                is_visible = await element.is_visible()
                if not is_visible:
                    logger.debug(f"    ❌ Element found but not visible")
                    continue
                
                logger.debug(f"    ✅ Element found and visible, clicking...")
                await self.page.click(selector, timeout=timeout)
                logger.info(f"✅ Clicked {description} with selector: {selector}")
                return True
                
            except Exception as e:
                logger.debug(f"    ❌ Failed: {str(e)[:100]}")
                continue
        
        logger.error(f"❌ Failed to find and click {description}")
        return False
    
    async def find_and_fill_input(self, selectors: List[str], value: str, description: str) -> bool:
        """Find input element and fill it with value."""
        logger.debug(f"🔍 Looking for {description} to fill: {value}")
        
        await self.page.wait_for_timeout(2000)
        
        for i, selector in enumerate(selectors, 1):
            try:
                logger.debug(f"  Trying selector {i}/{len(selectors)}: {selector}")
                
                element = await self.page.query_selector(selector)
                if not element:
                    logger.debug(f"    ❌ Element not found")
                    continue
                
                logger.debug(f"    ✅ Element found, attempting to fill...")
                
                # Try to interact with the element
                await self.page.click(selector, timeout=2000)
                await self.page.wait_for_timeout(500)
                
                # Clear and fill
                await self.page.fill(selector, "")
                await self.page.wait_for_timeout(500)
                await self.page.fill(selector, value)
                await self.page.wait_for_timeout(500)
                
                # Verify
                input_value = await self.page.input_value(selector)
                if input_value and value in input_value:
                    logger.info(f"✅ Successfully filled {description}: {value}")
                    return True
                else:
                    logger.debug(f"    ⚠️  Fill appeared to work but value is: '{input_value}'")
                    
            except Exception as e:
                logger.debug(f"    ❌ Failed: {str(e)[:100]}")
                continue
        
        logger.error(f"❌ Failed to fill {description}")
        return False
    
    async def find_and_fill_contenteditable(self, selectors: List[str], content: str, description: str) -> bool:
        """Find contenteditable element and fill it with content."""
        logger.debug(f"🔍 Looking for {description} to fill: {content[:50]}...")
        
        await self.page.wait_for_timeout(2000)
        
        for i, selector in enumerate(selectors, 1):
            try:
                logger.debug(f"  Trying selector {i}/{len(selectors)}: {selector}")
                
                element = await self.page.query_selector(selector)
                if not element:
                    logger.debug(f"    ❌ Element not found")
                    continue
                
                logger.debug(f"    ✅ Element found, attempting to fill...")
                
                await self.page.click(selector, timeout=1000)
                await self.page.wait_for_timeout(500)
                
                # Try different filling methods
                try:
                    await self.page.fill(selector, content)
                    await self.page.wait_for_timeout(500)
                except:
                    try:
                        await self.page.evaluate(f'document.querySelector("{selector}").innerHTML = ""')
                        await self.page.type(selector, content, delay=20)
                        await self.page.wait_for_timeout(500)
                    except:
                        escaped_content = content.replace('"', '\\"').replace('\n', '<br>')
                        await self.page.evaluate(f'document.querySelector("{selector}").innerHTML = "{escaped_content}"')
                        await self.page.wait_for_timeout(500)
                
                # Verify content
                try:
                    text_content = await self.page.evaluate(f'document.querySelector("{selector}").textContent || document.querySelector("{selector}").innerText')
                    if text_content and content[:20] in text_content:
                        logger.info(f"✅ Successfully filled {description}")
                        return True
                    else:
                        logger.debug(f"    ⚠️  Fill appeared to work but content is: '{text_content[:50] if text_content else 'empty'}...'")
                        
                        # Fallback: keyboard input
                        try:
                            await self.page.evaluate(f'document.querySelector("{selector}").focus()')
                            await self.page.keyboard.press('Control+a')
                            await self.page.keyboard.type(content, delay=30)
                            await self.page.wait_for_timeout(500)
                            
                            text_content = await self.page.evaluate(f'document.querySelector("{selector}").textContent || document.querySelector("{selector}").innerText')
                            if text_content and content[:20] in text_content:
                                logger.info(f"✅ Successfully filled {description} using keyboard input")
                                return True
                        except Exception as kb_error:
                            logger.debug(f"    ⚠️  Keyboard input also failed: {str(kb_error)[:50]}")
                except:
                    logger.debug(f"    ⚠️  Could not verify content, assuming success")
                    return True
                    
            except Exception as e:
                logger.debug(f"    ❌ Failed: {str(e)[:100]}")
                continue
        
        logger.error(f"❌ Failed to fill {description}")
        return False


class GmailSelectors:
    """Container for Gmail element selectors."""
    
    COMPOSE_SELECTORS = [
        'div[role="button"][gh="cm"]',
        'div[role="button"][aria-label*="Compose"]',
        'div[role="button"][aria-label*="نوشتن"]',  # Persian
        'div[role="button"][aria-label*="Rediger"]',  # Danish
        'div[role="button"][aria-label*="Escribir"]',  # Spanish
        'div.T-I.T-I-KE.L3',
        'div[data-tooltip*="Compose"]',
        'div[jsaction*="dlrqf"]',
        'div[jscontroller="eIu7Db"]'
    ]
    
    RECIPIENT_SELECTORS = [
        # Persian/localized
        'input[aria-label="گیرندگان در فیلد «به»"]',
        'input.agP.aFw',
        'input[id*=":tx"]',
        # English
        'textarea[aria-label="To"]',
        'input[aria-label="To"]',
        'textarea[name="to"]',
        'div[aria-label="To"] textarea',
        'div[aria-label="To"] input',
        'textarea[aria-label*="To"]',
        'input[aria-label*="To"]',
        'div[role="combobox"][aria-label*="To"]',
        'div[data-hovercard-id="to"] textarea',
        'div[data-hovercard-id="to"] input',
        # Placeholders
        'input[placeholder*="To"]',
        'input[placeholder*="به"]'
    ]
    
    SUBJECT_SELECTORS = [
        # Persian/localized
        'input[aria-label="موضوع"]',
        'input[name="subjectbox"]',
        'input.aoT',
        'input[id*=":q3"]',
        # English
        'input[aria-label="Subject"]',
        'input[aria-label*="Subject"]',
        'div[aria-label="Subject"] input',
        'input[placeholder*="Subject"]',
        'input[placeholder*="subject"]',
        'input[data-hovercard-id="subject"]',
        # Persian placeholders
        'input[placeholder*="موضوع"]'
    ]
    
    BODY_SELECTORS = [
        # Persian/localized
        'div[aria-label="متن پیام"]',
        'div.Am.aiL.Al.editable.LW-avf.tS-tW',
        # English
        'div[aria-label="Message Body"]',
        'div[role="textbox"][aria-label*="Message"]',
        'div[contenteditable="true"][aria-label*="Message"]',
        'div[g_editable="true"]',
        'div[aria-label*="Message Body"]',
        'div[contenteditable="true"]',
        'div[role="textbox"]',
        'div[contenteditable="true"][role="textbox"]',
        # Generic
        'div[contenteditable="true"].editable'
    ]
    
    SEND_SELECTORS = [
        # Persian/localized
        'div[role="button"][aria-label*="ارسال"]',
        'div[aria-label="ارسال"]',
        'div[data-tooltip*="ارسال"]',
        # English
        'div[role="button"][aria-label*="Send"]',
        'div[aria-label="Send"]',
        'div[data-tooltip*="Send"]',
        'div[aria-label*="Send"]',
        'div.T-I.J-J5-Ji.aoO.v7.T-I-atl.L3',
        'div[jsaction*="send"]',
        # Generic
        'button[type="submit"]',
        'div[role="button"]:has-text("Send")',
        'div[role="button"]:has-text("ارسال")'
    ]


class GmailFormFiller:
    """Handles filling Gmail compose form fields."""
    
    def __init__(self, page: Page):
        self.page = page
        self.finder = ElementFinder(page)
    
    async def fill_recipient(self, recipient: str) -> bool:
        """Fill the recipient field."""
        return await self.finder.find_and_fill_input(
            GmailSelectors.RECIPIENT_SELECTORS, 
            recipient, 
            "recipient field"
        )
    
    async def fill_subject(self, subject: str) -> bool:
        """Fill the subject field with Tab navigation fallback."""
        # Try Tab navigation first for better reliability
        logger.debug("  Trying to navigate to subject field using Tab...")
        try:
            for tab_count in range(1, 5):
                await self.page.keyboard.press('Tab')
                await self.page.wait_for_timeout(500)
                
                # Check if we focused a subject field
                for selector in GmailSelectors.SUBJECT_SELECTORS[:4]:
                    try:
                        element = await self.page.query_selector(selector)
                        if element:
                            is_focused = await self.page.evaluate(f'document.activeElement === document.querySelector("{selector}")')
                            if is_focused:
                                logger.debug(f"    ✅ Found focused subject field after {tab_count} Tab(s)")
                                
                                await self.page.keyboard.press('Control+a')
                                await self.page.wait_for_timeout(200)
                                await self.page.keyboard.type(subject)
                                await self.page.wait_for_timeout(500)
                                
                                value = await self.page.input_value(selector)
                                if value and subject in value:
                                    logger.info(f"✅ Successfully filled subject using Tab navigation: {subject}")
                                    return True
                    except:
                        continue
        except Exception as e:
            logger.debug(f"    Tab navigation failed: {str(e)[:50]}")
        
        # Fallback to regular selector-based approach
        return await self.finder.find_and_fill_input(
            GmailSelectors.SUBJECT_SELECTORS, 
            subject, 
            "subject field"
        )
    
    async def fill_body(self, body: str) -> bool:
        """Fill the email body with Tab navigation fallback."""
        # Try Tab navigation first
        logger.debug("  Trying to navigate to body field using Tab...")
        try:
            for tab_count in range(1, 4):
                await self.page.keyboard.press('Tab')
                await self.page.wait_for_timeout(500)
                
                # Check if we focused a body field
                for selector in GmailSelectors.BODY_SELECTORS[:4]:
                    try:
                        element = await self.page.query_selector(selector)
                        if element:
                            is_focused = await self.page.evaluate(f'document.activeElement === document.querySelector("{selector}")')
                            if is_focused:
                                logger.debug(f"    ✅ Found focused body field after {tab_count} Tab(s)")
                                
                                await self.page.keyboard.press('Control+a')
                                await self.page.wait_for_timeout(200)
                                await self.page.keyboard.type(body)
                                await self.page.wait_for_timeout(500)
                                
                                content = await self.page.evaluate(f'document.querySelector("{selector}").textContent || document.querySelector("{selector}").innerText')
                                if content and body[:20] in content:
                                    logger.info(f"✅ Successfully filled body using Tab navigation")
                                    return True
                    except:
                        continue
        except Exception as e:
            logger.debug(f"    Tab navigation failed: {str(e)[:50]}")
        
        # Fallback to regular selector-based approach
        return await self.finder.find_and_fill_contenteditable(
            GmailSelectors.BODY_SELECTORS, 
            body, 
            "body field"
        )


class GmailConnector:
    """Handles Gmail connection and navigation."""
    
    def __init__(self, page: Page):
        self.page = page
    
    async def connect_to_gmail(self) -> bool:
        """Connect to Gmail and navigate to the inbox."""
        try:
            logger.info("🚀 Connecting to Gmail...")
            
            # Navigate to Gmail
            logger.info("Navigating to Gmail...")
            try:
                await self.page.goto("https://gmail.com", wait_until="networkidle", timeout=config.browser_timeout)
            except Exception as e:
                logger.warning(f"Navigation with networkidle failed: {e}")
                try:
                    await self.page.goto("https://gmail.com", wait_until="domcontentloaded", timeout=config.browser_timeout // 2)
                    logger.info("Navigation successful with domcontentloaded")
                except Exception as e2:
                    logger.warning(f"Navigation with domcontentloaded also failed: {e2}")
                    await self.page.goto("https://gmail.com", timeout=config.browser_timeout // 3)
                    logger.info("Navigation completed without waiting")
            
            # Wait for page to settle
            await self.page.wait_for_timeout(3000)
            
            # Check if we're in Gmail and handle login if needed
            try:
                await self.page.wait_for_selector(
                    'div[role="button"][gh="cm"], input[type="email"], div[aria-label*="Compose"]',
                    timeout=10000
                )
                
                # Check if login is required
                login_elements = await self.page.query_selector_all('input[type="email"], input[type="password"]')
                if login_elements:
                    logger.warning("⚠️  Please log in to Gmail manually in the browser window")
                    logger.info("   Waiting for you to complete the login process...")
                    
                    # Wait for login to complete
                    await self.page.wait_for_selector(
                        'div[role="button"][gh="cm"], div[aria-label*="Compose"]',
                        timeout=120000  # 2 minutes
                    )
                    logger.info("✅ Login detected, continuing...")
                
                logger.info("✅ Successfully connected to Gmail")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to detect Gmail interface: {e}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error connecting to Gmail: {e}")
            return False


class EmailSender:
    """Orchestrates the email sending process using Command pattern."""
    
    def __init__(self, page: Page):
        self.page = page
        self.finder = ElementFinder(page)
        self.form_filler = GmailFormFiller(page)
    
    async def send_email(self, email_data: EmailInput) -> bool:
        """Send an email through Gmail web interface."""
        logger.info(f"📧 Sending email to {email_data.to}...")
        
        # Execute email sending steps
        steps = [
            ("click_compose", self._click_compose),
            ("fill_recipient", lambda: self.form_filler.fill_recipient(email_data.to)),
            ("fill_subject", lambda: self.form_filler.fill_subject(email_data.subject)),
            ("fill_body", lambda: self.form_filler.fill_body(email_data.body)),
            ("click_send", self._click_send)
        ]
        
        for step_name, step_func in steps:
            try:
                success = await step_func()
                if not success:
                    logger.error(f"❌ Failed at step: {step_name}")
                    return False
            except Exception as e:
                logger.error(f"❌ Error in step {step_name}: {e}")
                return False
        
        logger.info("✅ Email sent successfully!")
        return True
    
    async def _click_compose(self) -> bool:
        """Click the compose button."""
        success = await self.finder.find_and_click(
            GmailSelectors.COMPOSE_SELECTORS, 
            "compose button"
        )
        
        if success:
            # Wait for compose window to load
            logger.debug("⏳ Waiting for compose window to load...")
            await self.page.wait_for_timeout(3000)
            
            # Verify compose window opened
            logger.debug("🔍 Verifying compose window opened...")
            compose_indicators = [
                'textarea[aria-label="To"]',
                'input[aria-label="To"]',
                'input[aria-label="Subject"]',
                'div[aria-label="Message Body"]'
            ]
            
            for indicator in compose_indicators:
                try:
                    await self.page.wait_for_selector(indicator, timeout=2000)
                    logger.info(f"✅ Compose window confirmed - found: {indicator}")
                    return True
                except:
                    continue
            
            logger.warning("⚠️  Compose button clicked but compose window not fully detected")
            return True  # Assume success if we got this far
        
        return success
    
    async def _click_send(self) -> bool:
        """Click the send button."""
        success = await self.finder.find_and_click(
            GmailSelectors.SEND_SELECTORS, 
            "send button"
        )
        
        if success:
            # Wait and check for send confirmation
            await self.page.wait_for_timeout(3000)
            
            success_indicators = [
                'div[aria-label*="sent"]',
                'div[aria-label*="Message sent"]',
                'span:has-text("Message sent")',
                'div[aria-label*="ارسال شد"]',
                'span:has-text("ارسال شد")'
            ]
            
            for indicator in success_indicators:
                try:
                    await self.page.wait_for_selector(indicator, timeout=2000)
                    logger.info("✅ Email send confirmation detected")
                    return True
                except:
                    logger.info(f"Could not find success indicator: {indicator}")
                    continue
            
            logger.info("✅ Send button clicked (assuming success)")
            return True
        
        return success


class GmailMailer(IMailer):
    """Gmail automation facade class for sending emails through the web interface.
    
    Supports Chrome and Firefox on Windows and Linux only.
    No attachment support for now!
    """
    
    def __init__(self, browser_config: Optional[BrowserConfig] = None, debug_port: int = 9222):
        """Initialize the Gmail mailer.
        
        Args:
            browser_config: Browser configuration. Defaults to Chrome non-headless.
            debug_port: Debug port for Chrome CDP connection.
        """
        if browser_config is None:
            browser_config = BrowserConfig(
                browser_name=BrowserType.CHROME,
                headless=False
            )
        
        self.launcher = BrowserLauncher(browser_config)
        self.debug_port = debug_port
        self.page: Optional[Page] = None
        self._is_connected = False
        
        # Components (initialized when page is available)
        self._connector: Optional[GmailConnector] = None
        self._sender: Optional[EmailSender] = None
    
    async def connect_to_gmail(self) -> bool:
        """Connect to Gmail and navigate to the inbox."""
        try:
            if not self.page:
                success = await self.launcher.launch(debug_port=self.debug_port)
                if not success:
                    logger.error("Failed to launch browser")
                    return False
                    
                self.page = await self.launcher.get_page()
                if not self.page:
                    logger.error("Failed to get browser page")
                    return False
            
            self._connector = GmailConnector(self.page)
            self._sender = EmailSender(self.page)
            
            # Connect to Gmail
            success = await self._connector.connect_to_gmail()
            if success:
                self._is_connected = True
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error connecting to Gmail: {e}")
            return False
    
    async def send_email(self, email_data: EmailInput) -> bool:
        """Send an email through Gmail web interface."""
        if not self._is_connected or not self.page or not self._sender:
            logger.error("❌ Not connected to Gmail. Call connect_to_gmail() first.")
            return False
        
        try:
            return await self._sender.send_email(email_data)
        except Exception as e:
            logger.error(f"❌ Error sending email: {e}")
            return False
    
    async def terminate(self) -> bool:
        """Terminate the browser completely."""
        try:
            logger.info("🔥 Terminating browser...")
            if self.launcher:
                await self.launcher.terminate()
                logger.info("✅ Browser terminated")
                self._is_connected = False
                self.page = None
                self._connector = None
                self._sender = None
                self.launcher = None
                self.debug_port = None
                return True
        except Exception as e:
            logger.error(f"❌ Error terminating browser: {e}")
            return False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect_to_gmail()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if not await self.terminate():
            logger.error("❌ Failed to terminate browser")
            raise RuntimeError("Failed to terminate browser")