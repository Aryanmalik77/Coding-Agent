"""Verification script for EmailInterface."""

import os
from coding_agent.bus.email import EmailInterface

def verify_email():
    print("--- Verifying Email Reporting System ---")
    
    # Credentials from environment
    email_user = os.getenv("EMAIL_USER", "")
    email_password = os.getenv("EMAIL_PASSWORD", "")
    
    interface = EmailInterface(email_user, email_password)
    
    subject = "Verification: Coding Agent Email Bus"
    body = """
# Verification Report
The Email Reporting System has been initialized successfully.

## Capabilities
- Bypass Telegram 4096 char limit
- Markdown support
- Dedicated recipient routing

Status: OPERATIONAL
"""
    
    print(f"Sending test email to {email_user}...")
    success = interface.send_report(subject, body, email_user)
    
    if success:
        print("[SUCCESS] Email delivered. Credentials valid.")
    else:
        print("[FAILURE] Email delivery failed. Check credentials or 'Less Secure Apps' settings.")

if __name__ == "__main__":
    verify_email()
