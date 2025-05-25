import asyncio
import logging
from typing import Optional
from playwright.async_api import Page

from src.browser.launchers import BrowserLauncher
from src.schemas.browser import BrowserConfig
from src.schemas.email import EmailInput
from src.schemas.enums import BrowserType

logger = logging.getLogger(__name__)

class GmailMailer:
    
    def __init__(self, browser_config: Optional[BrowserConfig] = None, debug_port: int = 9222):
        if browser_config is None:
            browser_config = BrowserConfig(
                browser_name=BrowserType.CHROME,
                headless=False
            )
        
        self.launcher = BrowserLauncher(browser_config)
        self.page: Optional[Page] = None
        self._is_connected = False
    
    async def connect_to_gmail(self) -> bool:
        """Connect to Gmail and navigate to the inbox.
        
        Returns:
            bool: True if successfully connected, False otherwise.
        """
        try:
            print("🚀 Connecting to Gmail...")
            success = await self.launcher.launch(debug_port=9222)
            if not success:
                return False
                
            self.page = await self.launcher.get_page()
            if not self.page:
                return False
                
            await self.page.goto("https://gmail.com")
            await self.page.wait_for_timeout(3000)
            
            try:
                await self.page.wait_for_selector(
                    'div[role="button"][gh="cm"], input[type="email"], div[aria-label*="Compose"]',
                    timeout=10000
                )
                
                login_elements = await self.page.query_selector_all('input[type="email"], input[type="password"]')
                if login_elements:
                    print("⚠️  Please log in to Gmail manually in the browser window")
                    print("   Waiting for you to complete the login process...")
                    
                    await self.page.wait_for_selector(
                        'div[role="button"][gh="cm"], div[aria-label*="Compose"]',
                        timeout=120000
                    )
                    print("✅ Login detected, continuing...")
                
                self._is_connected = True
                print("✅ Successfully connected to Gmail")
                return True
                
            except Exception as e:
                print(f"❌ Failed to detect Gmail interface: {e}")
                return False
        
        except Exception as e:
            print(f"❌ Error connecting to Gmail: {e}")
            return False
    
    async def send_email(self, email_data: EmailInput) -> bool:
        """Send an email through Gmail web interface.
        
        Args:
            email_data: Email data containing recipient, subject, body, etc.
            
        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        if not self._is_connected or not self.page:
            print("❌ Not connected to Gmail. Call connect_to_gmail() first.")
            return False
        
        try:
            print(f"📧 Sending email to {email_data.to}...")
            
            if not await self._click_compose():
                return False
            
            if not await self._fill_recipient(email_data.to):
                return False
            
            if not await self._fill_subject(email_data.subject):
                return False
            
            if not await self._fill_body(email_data.body):
                return False
            
            if email_data.attachments:
                if not await self._add_attachments(email_data.attachments):
                    print("⚠️  Warning: Failed to add attachments, continuing...")
            
            if not await self._click_send():
                return False
            
            print("✅ Email sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
    
    async def _click_compose(self) -> bool:
        """Click the compose button."""
        print("🔍 Looking for compose button...")
        
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
                print(f"  Trying compose selector {i}/{len(compose_selectors)}: {selector}")
                
                element = await self.page.query_selector(selector)
                if not element:
                    print(f"    ❌ Element not found")
                    continue
                
                is_visible = await element.is_visible()
                if not is_visible:
                    print(f"    ❌ Element found but not visible")
                    continue
                
                print(f"    ✅ Element found and visible, clicking...")
                await self.page.click(selector, timeout=3000)
                print(f"✅ Clicked compose button with selector: {selector}")
                
                print("⏳ Waiting for compose window to load...")
                await self.page.wait_for_timeout(3000)
                
                print("🔍 Verifying compose window opened...")
                compose_indicators = [
                    'textarea[aria-label="To"]',
                    'input[aria-label="To"]',
                    'input[aria-label="Subject"]',
                    'div[aria-label="Message Body"]'
                ]
                
                for indicator in compose_indicators:
                    try:
                        await self.page.wait_for_selector(indicator, timeout=2000)
                        print(f"✅ Compose window confirmed - found: {indicator}")
                        return True
                    except:
                        continue
                
                print("⚠️  Compose button clicked but compose window not fully detected")
                return True
                
            except Exception as e:
                print(f"    ❌ Failed: {str(e)[:100]}")
                continue
        
        print("❌ Failed to click compose button with any selector")
        return False
    
    async def _fill_recipient(self, recipient: str) -> bool:
        """Fill the recipient field."""
        print(f"🔍 Looking for recipient field to fill: {recipient}")
        
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
                print(f"  Trying recipient selector {i}/{len(recipient_selectors)}: {selector}")
                
                element = await self.page.query_selector(selector)
                if not element:
                    print(f"    ❌ Element not found")
                    continue
                
                print(f"    ✅ Element found, attempting to fill...")
                
                await self.page.click(selector, timeout=2000)
                await self.page.wait_for_timeout(500)
                
                await self.page.fill(selector, "")
                await self.page.wait_for_timeout(500)
                
                await self.page.fill(selector, recipient)
                await self.page.wait_for_timeout(500)
                
                value = await self.page.input_value(selector)
                if value and recipient in value:
                    print(f"✅ Successfully filled recipient: {recipient}")
                    return True
                else:
                    print(f"    ⚠️  Fill appeared to work but value is: '{value}'")
                    
            except Exception as e:
                print(f"    ❌ Failed: {str(e)[:100]}")
                continue
        
        print(f"❌ Failed to fill recipient field with any selector")
        return False
    
    async def _fill_subject(self, subject: str) -> bool:
        """Fill the subject field."""
        print(f"🔍 Looking for subject field to fill: {subject}")
        
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
        
        print("  Trying to navigate to subject field using Tab...")
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
                                    print(f"    ✅ Found focused subject field after {tab_count} Tab(s)")
                                    
                                    await self.page.keyboard.press('Control+a')
                                    await self.page.wait_for_timeout(200)
                                    await self.page.keyboard.type(subject)
                                    await self.page.wait_for_timeout(500)
                                    
                                    value = await self.page.input_value(selector)
                                    if value and subject in value:
                                        print(f"✅ Successfully filled subject using Tab navigation: {subject}")
                                        return True
                        except:
                            continue
        except Exception as e:
            print(f"    Tab navigation failed: {str(e)[:50]}")
        
        for i, selector in enumerate(subject_selectors, 1):
            try:
                print(f"  Trying subject selector {i}/{len(subject_selectors)}: {selector}")
                
                element = await self.page.query_selector(selector)
                if not element:
                    print(f"    ❌ Element not found")
                    continue
                
                print(f"    ✅ Element found, attempting to fill...")
                
                success = False
                
                try:
                    await self.page.click(selector, timeout=1000)
                    await self.page.wait_for_timeout(300)
                    success = True
                except:
                    print(f"    ⚠️  Click failed, trying focus...")
                
                if not success:
                    try:
                        await self.page.focus(selector)
                        await self.page.wait_for_timeout(300)
                        success = True
                    except:
                        print(f"    ⚠️  Focus failed, trying direct fill...")
                
                if not success:
                    try:
                        await self.page.wait_for_timeout(500)
                        success = True
                    except:
                        print(f"    ⚠️  All focus methods failed, trying fill anyway...")
                        success = True
                
                try:
                    await self.page.fill(selector, "")
                    await self.page.wait_for_timeout(200)
                    await self.page.fill(selector, subject)
                    await self.page.wait_for_timeout(500)
                    
                    value = await self.page.input_value(selector)
                    if value and subject in value:
                        print(f"✅ Successfully filled subject: {subject}")
                        return True
                    else:
                        print(f"    ⚠️  Fill appeared to work but value is: '{value}'")
                        
                        try:
                            await self.page.evaluate(f'document.querySelector("{selector}").value = ""')
                            await self.page.type(selector, subject, delay=50)
                            await self.page.wait_for_timeout(500)
                            
                            value = await self.page.input_value(selector)
                            if value and subject in value:
                                print(f"✅ Successfully filled subject using type: {subject}")
                                return True
                        except Exception as type_error:
                            print(f"    ⚠️  Type method also failed: {str(type_error)[:50]}")
                        
                except Exception as fill_error:
                    print(f"    ❌ Fill failed: {str(fill_error)[:100]}")
                    continue
                    
            except Exception as e:
                print(f"    ❌ Failed: {str(e)[:100]}")
                continue
        
        print("❌ Failed to fill subject field with any selector")
        return False
    
    async def _fill_body(self, body: str) -> bool:
        """Fill the email body."""
        print(f"🔍 Looking for body field to fill: {body[:50]}...")
        
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
        
        print("  Trying to navigate to body field using Tab...")
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
                                    print(f"    ✅ Found focused body field after {tab_count} Tab(s)")
                                    
                                    await self.page.keyboard.press('Control+a')
                                    await self.page.wait_for_timeout(200)
                                    await self.page.keyboard.type(body)
                                    await self.page.wait_for_timeout(500)
                                    
                                    content = await self.page.evaluate(f'document.querySelector("{selector}").textContent || document.querySelector("{selector}").innerText')
                                    if content and body[:20] in content:
                                        print(f"✅ Successfully filled body using Tab navigation")
                                        return True
                        except:
                            continue
        except Exception as e:
            print(f"    Tab navigation failed: {str(e)[:50]}")
        
        for i, selector in enumerate(body_selectors, 1):
            try:
                print(f"  Trying body selector {i}/{len(body_selectors)}: {selector}")
                
                element = await self.page.query_selector(selector)
                if not element:
                    print(f"    ❌ Element not found")
                    continue
                
                print(f"    ✅ Element found, attempting to fill...")
                
                success = False
                
                try:
                    await self.page.click(selector, timeout=1000)
                    await self.page.wait_for_timeout(500)
                    success = True
                except:
                    print(f"    ⚠️  Click failed, trying focus...")
                
                if not success:
                    try:
                        await self.page.focus(selector)
                        await self.page.wait_for_timeout(500)
                        success = True
                    except:
                        print(f"    ⚠️  Focus failed, trying direct fill...")
                
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
                            print(f"✅ Successfully filled body content")
                            return True
                        else:
                            print(f"    ⚠️  Fill appeared to work but content is: '{content[:50] if content else 'empty'}...'")
                            
                            try:
                                await self.page.evaluate(f'document.querySelector("{selector}").focus()')
                                await self.page.keyboard.press('Control+a')
                                await self.page.keyboard.type(body, delay=30)
                                await self.page.wait_for_timeout(500)
                                
                                content = await self.page.evaluate(f'document.querySelector("{selector}").textContent || document.querySelector("{selector}").innerText')
                                if content and body[:20] in content:
                                    print(f"✅ Successfully filled body using keyboard input")
                                    return True
                            except Exception as kb_error:
                                print(f"    ⚠️  Keyboard input also failed: {str(kb_error)[:50]}")
                    except:
                        print(f"    ⚠️  Could not verify content, assuming success")
                        return True
                        
                except Exception as fill_error:
                    print(f"    ❌ Fill failed: {str(fill_error)[:100]}")
                    continue
                    
            except Exception as e:
                print(f"    ❌ Failed: {str(e)[:100]}")
                continue
        
        print("❌ Failed to fill body field with any selector")
        return False
    
    async def _add_attachments(self, attachment_paths: list[str]) -> bool:
        """Add attachments to the email."""
        try:
            attachment_selectors = [
                'div[aria-label*="Attach"]',
                'div[data-tooltip*="Attach"]',
                'input[type="file"]'
            ]
            
            for selector in attachment_selectors:
                try:
                    if selector == 'input[type="file"]':
                        await self.page.set_input_files(selector, attachment_paths)
                    else:
                        await self.page.click(selector)
                        await self.page.wait_for_timeout(1000)
                        await self.page.set_input_files('input[type="file"]', attachment_paths)
                    
                    print(f"✅ Added {len(attachment_paths)} attachment(s)")
                    return True
                except Exception as e:
                    logger.debug(f"Attachment selector {selector} failed: {e}")
                    continue
            
            return False
            
        except Exception as e:
            print(f"❌ Error adding attachments: {e}")
            return False
    
    async def _click_send(self) -> bool:
        """Click the send button."""
        print("🔍 Looking for send button...")
        
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
                print(f"  Trying send selector {i}/{len(send_selectors)}: {selector}")
                
                element = await self.page.query_selector(selector)
                if not element:
                    print(f"    ❌ Element not found")
                    continue
                
                print(f"    ✅ Element found, clicking...")
                await self.page.click(selector, timeout=3000)
                print("✅ Clicked send button")
                
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
                        print("✅ Email send confirmation detected")
                        return True
                    except:
                        continue
                
                print("✅ Send button clicked (assuming success)")
                return True
                
            except Exception as e:
                print(f"    ❌ Failed: {str(e)[:100]}")
                continue
        
        print("❌ Failed to click send button")
        return False
    
    async def close(self):
        """Close the browser connection."""
        if self.launcher:
            await self.launcher.close()
            self._is_connected = False
            print("✅ Disconnected from Gmail")
    
    def terminate(self):
        """Terminate the browser completely."""
        if self.launcher:
            self.launcher.terminate()
            self._is_connected = False
            print("✅ Browser terminated")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect_to_gmail()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()



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