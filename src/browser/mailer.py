from typing import Optional, List
from playwright.async_api import Page

from src.browser.launchers import BrowserLauncher
from src.schemas.browser import BrowserConfig
from src.schemas.email import EmailInput
from src.schemas.enums import BrowserType
from src.utils.logger import get_logger

logger = get_logger(__name__)

class GmailMailer:
    """Gmail automation class for sending emails through the web interface.
    
    Supports Chrome and Firefox on Windows and Linux only.
    No attachment support.
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
    
    async def connect_to_gmail(self) -> bool:
        """Connect to Gmail and navigate to the inbox.
        
        Returns:
            bool: True if successfully connected, False otherwise.
        """
        try:
            logger.info("🚀 Connecting to Gmail...")
            
            
            if not self.page:
                
                success = await self.launcher.launch(debug_port=self.debug_port)
                if not success:
                    logger.error("Failed to launch browser")
                    return False
                    
                self.page = await self.launcher.get_page()
                if not self.page:
                    logger.error("Failed to get browser page")
                    return False
            
            
            logger.info("Navigating to Gmail...")
            try:
                
                await self.page.goto("https://gmail.com", wait_until="networkidle", timeout=30000)
            except Exception as e:
                logger.warning(f"Navigation with networkidle failed: {e}")
                try:
                    
                    await self.page.goto("https://gmail.com", wait_until="domcontentloaded", timeout=15000)
                    logger.info("Navigation successful with domcontentloaded")
                except Exception as e2:
                    logger.warning(f"Navigation with domcontentloaded also failed: {e2}")
                    
                    await self.page.goto("https://gmail.com", timeout=10000)
                    logger.info("Navigation completed without waiting")
            
            
            await self.page.wait_for_timeout(3000)
            
            
            try:
                
                await self.page.wait_for_selector(
                    'div[role="button"][gh="cm"], input[type="email"], div[aria-label*="Compose"]',
                    timeout=10000
                )
                
                
                login_elements = await self.page.query_selector_all('input[type="email"], input[type="password"]')
                if login_elements:
                    logger.warning("⚠️  Please log in to Gmail manually in the browser window")
                    logger.info("   Waiting for you to complete the login process...")
                    
                    
                    await self.page.wait_for_selector(
                        'div[role="button"][gh="cm"], div[aria-label*="Compose"]',
                        timeout=120000  
                    )
                    logger.info("✅ Login detected, continuing...")
                
                self._is_connected = True
                logger.info("✅ Successfully connected to Gmail")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to detect Gmail interface: {e}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error connecting to Gmail: {e}")
            return False
    
    async def send_email(self, email_data: EmailInput) -> bool:
        """Send an email through Gmail web interface.
        
        Args:
            email_data: Email data containing recipient, subject, body.
            
        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        if not self._is_connected or not self.page:
            logger.error("❌ Not connected to Gmail. Call connect_to_gmail() first.")
            return False
        
        try:
            logger.info(f"📧 Sending email to {email_data.to}...")
            
            
            if not await self._click_compose():
                return False
            
            
            if not await self._fill_recipient(email_data.to):
                return False
            
            
            if not await self._fill_subject(email_data.subject):
                return False
            
            
            if not await self._fill_body(email_data.body):
                return False
            
            
            if not await self._click_send():
                return False
            
            logger.info("✅ Email sent successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending email: {e}")
            return False
    
    async def _click_compose(self) -> bool:
        """Click the compose button."""
        logger.debug("🔍 Looking for compose button...")
        
        compose_selectors = [
            'div[role="button"][gh="cm"]',
            'div[role="button"][aria-label*="Compose"]',
            'div[role="button"][aria-label*="نوشتن"]',  
            'div[role="button"][aria-label*="Rediger"]',  
            'div[role="button"][aria-label*="Escribir"]',  
            'div.T-I.T-I-KE.L3',
            'div[data-tooltip*="Compose"]',
            'div[jsaction*="dlrqf"]',
            'div[jscontroller="eIu7Db"]'
        ]
        
        for i, selector in enumerate(compose_selectors, 1):
            try:
                logger.debug(f"  Trying compose selector {i}/{len(compose_selectors)}: {selector}")
                
                
                element = await self.page.query_selector(selector)
                if not element:
                    logger.debug(f"    ❌ Element not found")
                    continue
                
                
                is_visible = await element.is_visible()
                if not is_visible:
                    logger.debug(f"    ❌ Element found but not visible")
                    continue
                
                logger.debug(f"    ✅ Element found and visible, clicking...")
                await self.page.click(selector, timeout=3000)
                logger.info(f"✅ Clicked compose button with selector: {selector}")
                
                
                logger.debug("⏳ Waiting for compose window to load...")
                await self.page.wait_for_timeout(3000)
                
                
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
                return True  
                
            except Exception as e:
                logger.debug(f"    ❌ Failed: {str(e)[:100]}")
                continue
        
        logger.error("❌ Failed to click compose button with any selector")
        return False
    
    async def _fill_recipient(self, recipient: str) -> bool:
        """Fill the recipient field."""
        logger.debug(f"🔍 Looking for recipient field to fill: {recipient}")
        
        
        await self.page.wait_for_timeout(2000)
        
        recipient_selectors = [
            
            'input[aria-label="گیرندگان در فیلد «به»"]',
            'input.agP.aFw',
            'input[id*=":tx"]',
            
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
            
            'input[placeholder*="To"]',
            'input[placeholder*="به"]'
        ]
        
        for i, selector in enumerate(recipient_selectors, 1):
            try:
                logger.debug(f"  Trying recipient selector {i}/{len(recipient_selectors)}: {selector}")
                
                
                element = await self.page.query_selector(selector)
                if not element:
                    logger.debug(f"    ❌ Element not found")
                    continue
                
                logger.debug(f"    ✅ Element found, attempting to fill...")
                
                
                await self.page.click(selector, timeout=2000)
                await self.page.wait_for_timeout(500)
                
                
                await self.page.fill(selector, "")
                await self.page.wait_for_timeout(500)
                
                
                await self.page.fill(selector, recipient)
                await self.page.wait_for_timeout(500)
                
                
                value = await self.page.input_value(selector)
                if value and recipient in value:
                    logger.info(f"✅ Successfully filled recipient: {recipient}")
                    return True
                else:
                    logger.debug(f"    ⚠️  Fill appeared to work but value is: '{value}'")
                    
            except Exception as e:
                logger.debug(f"    ❌ Failed: {str(e)[:100]}")
                continue
        
        logger.error(f"❌ Failed to fill recipient field with any selector")
        return False
    
    async def _fill_subject(self, subject: str) -> bool:
        """Fill the subject field."""
        logger.debug(f"🔍 Looking for subject field to fill: {subject}")
        
        
        await self.page.wait_for_timeout(3000)
        
        subject_selectors = [
            
            'input[aria-label="موضوع"]',
            'input[name="subjectbox"]',
            'input.aoT',
            'input[id*=":q3"]',
            
            'input[aria-label="Subject"]',
            'input[aria-label*="Subject"]',
            'div[aria-label="Subject"] input',
            'input[placeholder*="Subject"]',
            'input[placeholder*="subject"]',
            'input[data-hovercard-id="subject"]',
            
            'input[placeholder*="موضوع"]'
        ]
        
        
        logger.debug("  Trying to navigate to subject field using Tab...")
        try:
            
            for tab_count in range(1, 5):  
                await self.page.keyboard.press('Tab')
                await self.page.wait_for_timeout(500)
                
                
                focused_element = await self.page.evaluate('document.activeElement')
                if focused_element:
                    
                    for selector in subject_selectors[:4]:  
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
        
        
        for i, selector in enumerate(subject_selectors, 1):
            try:
                logger.debug(f"  Trying subject selector {i}/{len(subject_selectors)}: {selector}")
                
                
                element = await self.page.query_selector(selector)
                if not element:
                    logger.debug(f"    ❌ Element not found")
                    continue
                
                logger.debug(f"    ✅ Element found, attempting to fill...")
                
                
                success = False
                
                
                try:
                    await self.page.click(selector, timeout=1000)
                    await self.page.wait_for_timeout(300)
                    success = True
                except:
                    logger.debug(f"    ⚠️  Click failed, trying focus...")
                
                
                if not success:
                    try:
                        await self.page.focus(selector)
                        await self.page.wait_for_timeout(300)
                        success = True
                    except:
                        logger.debug(f"    ⚠️  Focus failed, trying direct fill...")
                
                
                if not success:
                    try:
                        await self.page.wait_for_timeout(500)
                        success = True
                    except:
                        logger.debug(f"    ⚠️  All focus methods failed, trying fill anyway...")
                        success = True
                
                
                try:
                    
                    await self.page.fill(selector, "")
                    await self.page.wait_for_timeout(200)
                    await self.page.fill(selector, subject)
                    await self.page.wait_for_timeout(500)
                    
                    
                    value = await self.page.input_value(selector)
                    if value and subject in value:
                        logger.info(f"✅ Successfully filled subject: {subject}")
                        return True
                    else:
                        logger.debug(f"    ⚠️  Fill appeared to work but value is: '{value}'")
                        
                        
                        try:
                            await self.page.evaluate(f'document.querySelector("{selector}").value = ""')
                            await self.page.type(selector, subject, delay=50)
                            await self.page.wait_for_timeout(500)
                            
                            value = await self.page.input_value(selector)
                            if value and subject in value:
                                logger.info(f"✅ Successfully filled subject using type: {subject}")
                                return True
                        except Exception as type_error:
                            logger.debug(f"    ⚠️  Type method also failed: {str(type_error)[:50]}")
                        
                except Exception as fill_error:
                    logger.debug(f"    ❌ Fill failed: {str(fill_error)[:100]}")
                    continue
                    
            except Exception as e:
                logger.debug(f"    ❌ Failed: {str(e)[:100]}")
                continue
        
        logger.error("❌ Failed to fill subject field with any selector")
        return False
    
    async def _fill_body(self, body: str) -> bool:
        """Fill the email body."""
        logger.debug(f"🔍 Looking for body field to fill: {body[:50]}...")
        
        
        await self.page.wait_for_timeout(2000)
        
        body_selectors = [
            
            'div[aria-label="متن پیام"]',
            'div.Am.aiL.Al.editable.LW-avf.tS-tW',
            
            'div[aria-label="Message Body"]',
            'div[role="textbox"][aria-label*="Message"]',
            'div[contenteditable="true"][aria-label*="Message"]',
            'div[g_editable="true"]',
            'div[aria-label*="Message Body"]',
            'div[contenteditable="true"]',
            'div[role="textbox"]',
            'div[contenteditable="true"][role="textbox"]',
            
            'div[contenteditable="true"].editable'
        ]
        
        
        logger.debug("  Trying to navigate to body field using Tab...")
        try:
            
            for tab_count in range(1, 4):  
                await self.page.keyboard.press('Tab')
                await self.page.wait_for_timeout(500)
                
                
                focused_element = await self.page.evaluate('document.activeElement')
                if focused_element:
                    
                    for selector in body_selectors[:4]:  
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
        
        
        for i, selector in enumerate(body_selectors, 1):
            try:
                logger.debug(f"  Trying body selector {i}/{len(body_selectors)}: {selector}")
                
                
                element = await self.page.query_selector(selector)
                if not element:
                    logger.debug(f"    ❌ Element not found")
                    continue
                
                logger.debug(f"    ✅ Element found, attempting to fill...")
                
                
                success = False
                
                
                try:
                    await self.page.click(selector, timeout=1000)
                    await self.page.wait_for_timeout(500)
                    success = True
                except:
                    logger.debug(f"    ⚠️  Click failed, trying focus...")
                
                
                if not success:
                    try:
                        await self.page.focus(selector)
                        await self.page.wait_for_timeout(500)
                        success = True
                    except:
                        logger.debug(f"    ⚠️  Focus failed, trying direct fill...")
                
                
                try:
                    
                    try:
                        await self.page.fill(selector, body)
                        await self.page.wait_for_timeout(500)
                    except:
                        
                        try:
                            await self.page.evaluate(f'document.querySelector("{selector}").innerHTML = ""')
                            await self.page.type(selector, body, delay=20)
                            await self.page.wait_for_timeout(500)
                        except:
                            
                            escaped_body = body.replace('"', '\\"').replace('\n', '<br>')
                            await self.page.evaluate(f'document.querySelector("{selector}").innerHTML = "{escaped_body}"')
                            await self.page.wait_for_timeout(500)
                    
                    
                    try:
                        content = await self.page.evaluate(f'document.querySelector("{selector}").textContent || document.querySelector("{selector}").innerText')
                        if content and body[:20] in content:
                            logger.info(f"✅ Successfully filled body content")
                            return True
                        else:
                            logger.debug(f"    ⚠️  Fill appeared to work but content is: '{content[:50] if content else 'empty'}...'")
                            
                            
                            try:
                                await self.page.evaluate(f'document.querySelector("{selector}").focus()')
                                await self.page.keyboard.press('Control+a')
                                await self.page.keyboard.type(body, delay=30)
                                await self.page.wait_for_timeout(500)
                                
                                content = await self.page.evaluate(f'document.querySelector("{selector}").textContent || document.querySelector("{selector}").innerText')
                                if content and body[:20] in content:
                                    logger.info(f"✅ Successfully filled body using keyboard input")
                                    return True
                            except Exception as kb_error:
                                logger.debug(f"    ⚠️  Keyboard input also failed: {str(kb_error)[:50]}")
                    except:
                        logger.debug(f"    ⚠️  Could not verify content, assuming success")
                        return True
                        
                except Exception as fill_error:
                    logger.debug(f"    ❌ Fill failed: {str(fill_error)[:100]}")
                    continue
                    
            except Exception as e:
                logger.debug(f"    ❌ Failed: {str(e)[:100]}")
                continue
        
        logger.error("❌ Failed to fill body field with any selector")
        return False
    
    async def _click_send(self) -> bool:
        """Click the send button."""
        logger.debug("🔍 Looking for send button...")
        
        send_selectors = [
            
            'div[role="button"][aria-label*="ارسال"]',
            'div[aria-label="ارسال"]',
            'div[data-tooltip*="ارسال"]',
            
            'div[role="button"][aria-label*="Send"]',
            'div[aria-label="Send"]',
            'div[data-tooltip*="Send"]',
            'div[aria-label*="Send"]',
            'div.T-I.J-J5-Ji.aoO.v7.T-I-atl.L3',
            'div[jsaction*="send"]',
            
            'button[type="submit"]',
            'div[role="button"]:has-text("Send")',
            'div[role="button"]:has-text("ارسال")'
        ]
        
        for i, selector in enumerate(send_selectors, 1):
            try:
                logger.debug(f"  Trying send selector {i}/{len(send_selectors)}: {selector}")
                
                
                element = await self.page.query_selector(selector)
                if not element:
                    logger.debug(f"    ❌ Element not found")
                    continue
                
                logger.debug(f"    ✅ Element found, clicking...")
                await self.page.click(selector, timeout=3000)
                logger.info("✅ Clicked send button")
                
                
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
                        continue
                
                
                logger.info("✅ Send button clicked (assuming success)")
                return True
                
            except Exception as e:
                logger.debug(f"    ❌ Failed: {str(e)[:100]}")
                continue
        
        logger.error("❌ Failed to click send button")
        return False
    
    async def close(self):
        """Close the browser connection."""
        if self.launcher:
            await self.launcher.close()
            self._is_connected = False
            logger.info("✅ Disconnected from Gmail")
    
    async def terminate(self):
        """Terminate the browser completely."""
        if self.launcher:
            await self.launcher.terminate()
            self._is_connected = False
            logger.info("✅ Browser terminated")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect_to_gmail()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.terminate()



async def send_gmail(email_data: EmailInput, browser_config: Optional[BrowserConfig] = None) -> bool:
    """Send an email through Gmail web interface.
    
    Args:
        email_data: Email data containing recipient, subject, body, etc.
        browser_config: Optional browser configuration.
        
    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    async with GmailMailer(browser_config) as mailer:
        return await mailer.send_email(email_data) 