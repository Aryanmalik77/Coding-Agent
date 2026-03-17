"""Telegram channel integration for the coding agent."""

import asyncio
import httpx
import os
from pathlib import Path
from loguru import logger
from typing import Optional, Any
from coding_agent.bus.email import EmailInterface

class TelegramInterface:
    """
    Interface for Telegram channel integration.
    Allows the coding agent to receive tasks and report progress via Telegram.
    """

    def __init__(self, bot_token: str, workspace_path: str):
        self.bot_token = bot_token
        self.workspace_path = workspace_path
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self._running = False
        self._last_update_id = 0
        self.agent: Optional[Any] = None
        # Credentials fetched from environment variables
        self.email_interface = EmailInterface(
            os.getenv("EMAIL_USER", ""), 
            os.getenv("EMAIL_PASSWORD", "")
        )

    async def start(self):
        """Start the Telegram polling loop."""
        from coding_agent.core.agent import CodingAgent
        from pathlib import Path
        
        self.agent = CodingAgent(Path(self.workspace_path))
        self._running = True
        logger.info("Telegram Gateway started. Polling for tasks...")
        
        async with httpx.AsyncClient() as client:
            while self._running:
                try:
                    await self._poll_updates(client)
                except Exception as e:
                    logger.error(f"Telegram polling error: {e}")
                await asyncio.sleep(2)

    async def _poll_updates(self, client: httpx.AsyncClient):
        """Poll for new messages from Telegram."""
        params = {"offset": self._last_update_id + 1, "timeout": 30}
        response = await client.get(f"{self.api_url}/getUpdates", params=params, timeout=35.0)
        
        if response.status_code == 200:
            updates = response.json().get("result", [])
            for update in updates:
                self._last_update_id = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"]["text"]
                    user = update["message"]["from"].get("username", "Unknown")
                    
                    # Log with distinct pulse prefix
                    safe_text = (text[:50] + "...") if len(text) > 50 else text
                    logger.info(f"[TASK-IN] From @{user}: {safe_text}")
                    await self.send_update(chat_id, f"🚀 Task Received: {text}\nProcessing...")
                    
                    # Execute the task
                    try:
                        logger.info(f"[PROCESS] Executing agent core for: {safe_text}")
                        if not self.agent:
                            raise ValueError("CodingAgent not initialized. Call start() first.")
                        
                        result = await self.agent.run_task(text)
                        logger.info(f"[TASK-OUT] Completed: {safe_text}")
                        response_text = f"✅ Task Completed!\n\nResult:\n{result or '[Task processed by Coding Agent]'}"
                    except Exception as e:
                        logger.error(f"[TASK-ERR] Failed: {safe_text} -> {e}")
                        response_text = f"❌ Task Failed: {str(e)}"
                    
                    # Check if email override is requested or if message is likely too long
                    should_email = "email" in text.lower() or len(response_text) > 3500
                    
                    if should_email:
                        subject = f"Coding Agent Report: {safe_text}"
                        recipient = os.getenv("RECIPIENT_EMAIL", "recipient@example.com")
                        success = self.email_interface.send_report(subject, response_text, recipient)
                        
                        # Local Fallback: Always save the full report to the workspace
                        report_id = "".join(filter(str.isalnum, safe_text[:20]))
                        local_report_path = Path(self.workspace_path) / "reports" / f"report_{report_id}.md"
                        local_report_path.parent.mkdir(parents=True, exist_ok=True)
                        local_report_path.write_text(response_text, encoding="utf-8")
                        
                        if success:
                            recipient_addr = os.getenv("RECIPIENT_EMAIL", "recipient@example.com")
                            email_note = f"\n\n📧 Full result has been emailed to {recipient_addr}"
                        else:
                            email_note = f"\n\n⚠️ Email failed (Check App Password). Full result saved locally to: reports/{local_report_path.name}"
                            
                        if len(response_text) > 3500:
                            truncated_part = str(response_text)[:3500]
                            response_text = f"{truncated_part}... [TRUNCATED] ...{email_note}"
                        else:
                            response_text = f"{response_text}{email_note}"
                    
                    await self.send_update(chat_id, response_text)

    async def send_update(self, chat_id: int, message: str):
        """Send a message back to the Telegram chat with length monitoring."""
        if not self._running:
            return
            
        # Telegram has a 4096 character limit
        # We truncate slightly below to be safe with any added formatting
        if len(message) > 4000:
            logger.warning(f"Message to {chat_id} too long ({len(message)} chars). Truncating.")
            msg_chunk = str(message)[:3900]
            message = f"{msg_chunk}\n\n... [TRUNCATED FOR TELEGRAM LIMITS] ..."
            
        logger.info(f"Sending Telegram update to {chat_id} ({len(message)} chars)")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_url}/sendMessage",
                    json={"chat_id": chat_id, "text": message},
                    timeout=10.0
                )
                response.raise_for_status()
            except Exception as e:
                error_body = ""
                if hasattr(e, 'response') and e.response:
                    error_body = f" | Response: {e.response.text}"
                logger.error(f"Failed to send Telegram message: {e}{error_body}")

    def stop(self):
        """Stop the interface."""
        self._running = False
        if self.agent:
            self.agent.shutdown()
        logger.info("Telegram interface stopped.")
