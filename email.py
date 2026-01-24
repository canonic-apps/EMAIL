#!/usr/bin/env python3
"""
CANONIC EMAIL — Microsoft Graph Native

Governed email sending with full audit trail.
Emails appear in YOUR Outlook sent folder.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add user site-packages for Xcode Python
sys.path.insert(0, str(Path.home() / "Library/Python/3.9/lib/python/site-packages"))

try:
    import msal
    import requests
except ImportError:
    print("Install dependencies: pip3 install msal requests")
    exit(1)

# Paths - use resolve() for iCloud paths
APP_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = APP_DIR / "templates"
SENT_DIR = APP_DIR / "sent"
CONFIG_FILE = APP_DIR / "config.json"
TOKEN_CACHE = APP_DIR / ".token_cache.json"

# Ensure directories exist (lazy - only on first use)
def ensure_dirs():
    TEMPLATES_DIR.mkdir(exist_ok=True)
    SENT_DIR.mkdir(exist_ok=True)

# Microsoft Graph endpoints
GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"
SCOPES = ["Mail.Send", "Mail.ReadWrite", "User.Read"]


def load_config():
    """Load app configuration."""
    if not CONFIG_FILE.exists():
        return None
    return json.loads(CONFIG_FILE.read_text())


def save_config(config):
    """Save app configuration."""
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_msal_app(config):
    """Create MSAL public client app."""
    cache = msal.SerializableTokenCache()
    if TOKEN_CACHE.exists():
        cache.deserialize(TOKEN_CACHE.read_text())

    app = msal.PublicClientApplication(
        config["client_id"],
        authority=f"https://login.microsoftonline.com/{config['tenant_id']}",
        token_cache=cache
    )
    return app, cache


def get_access_token(config):
    """Get access token via device code flow (user signs in)."""
    app, cache = get_msal_app(config)

    # Try to get token from cache first
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]

    # Device code flow - user authenticates via browser
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        print(f"ERROR: {flow.get('error_description', 'Could not initiate auth')}")
        return None

    print("\n" + "="*60)
    print("AUTHENTICATE WITH MICROSOFT")
    print("="*60)
    print(f"\n1. Go to: {flow['verification_uri']}")
    print(f"2. Enter code: {flow['user_code']}")
    print("\nWaiting for authentication...\n")

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        # Save token cache
        TOKEN_CACHE.write_text(cache.serialize())
        print("Authentication successful!\n")
        return result["access_token"]
    else:
        print(f"ERROR: {result.get('error_description', 'Authentication failed')}")
        return None


def send_email(to: str, subject: str, body: str, config: dict):
    """Send email via Microsoft Graph API. Shows up in YOUR Outlook sent folder."""
    token = get_access_token(config)
    if not token:
        return False

    endpoint = f"{GRAPH_ENDPOINT}/me/sendMail"

    message = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [
                {"emailAddress": {"address": to}}
            ]
        },
        "saveToSentItems": True  # This makes it show up in Outlook!
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(endpoint, headers=headers, json=message)

    if response.status_code == 202:
        # Log to sent/
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "to": to,
            "subject": subject,
            "status": "sent",
            "outlook": True
        }
        log_file = SENT_DIR / f"{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{to.split('@')[0]}.json"
        log_file.write_text(json.dumps(log_entry, indent=2))
        print("="*60)
        print("EMAIL SENT")
        print("="*60)
        print(f"To:      {to}")
        print(f"Subject: {subject}")
        print(f"Log:     {log_file.name}")
        print(f"Outlook: Check your Sent folder!")
        print("="*60)
        return True
    else:
        print(f"ERROR: {response.status_code} - {response.text}")
        return False


def load_template(name: str) -> tuple:
    """Load email template, return (subject, body)."""
    template_file = TEMPLATES_DIR / f"{name}.md"
    if not template_file.exists():
        print(f"ERROR: Template not found: {template_file}")
        return None, None

    content = template_file.read_text()
    lines = content.split("\n")
    subject = "CANONIC"
    body_start = 0

    if lines[0].lower().startswith("subject:"):
        subject = lines[0].split(":", 1)[1].strip()
        body_start = 1
        if len(lines) > 1 and lines[1].strip() == "":
            body_start = 2

    body = "\n".join(lines[body_start:])
    return subject, body


def list_templates():
    """List available email templates."""
    templates = list(TEMPLATES_DIR.glob("*.md"))
    if not templates:
        print("No templates found. Add .md files to templates/")
        return
    print("\nAvailable templates:")
    for t in templates:
        print(f"  - {t.stem}")
    print()


def view_log():
    """View sent email log."""
    logs = sorted(SENT_DIR.glob("*.json"), reverse=True)
    if not logs:
        print("No emails sent yet.")
        return
    print("\nSent emails:")
    print("-"*80)
    for log in logs[:20]:
        data = json.loads(log.read_text())
        outlook = "✓ Outlook" if data.get("outlook") else ""
        print(f"  {data['timestamp'][:16]} | {data['to']:30} | {data['subject'][:30]} {outlook}")
    print()


def setup():
    """Interactive setup for Azure AD app."""
    print("\n" + "="*60)
    print("CANONIC EMAIL SETUP")
    print("="*60)
    print("\nStep 1: Register app in Azure Portal")
    print("-"*40)

    os.system('open "https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade"')

    print("""
In Azure Portal:
1. Click 'New registration'
2. Name: CANONIC-EMAIL
3. Supported account types: 'Accounts in this organizational directory only'
4. Redirect URI: Select 'Public client/native' and enter:
   https://login.microsoftonline.com/common/oauth2/nativeclient
5. Click 'Register'

After registration:
- Copy the 'Application (client) ID'
- Copy the 'Directory (tenant) ID'

Then go to 'API permissions':
- Add permission > Microsoft Graph > Delegated permissions
- Add: Mail.Send, Mail.ReadWrite, User.Read
- Click 'Grant admin consent' (if you're admin)
""")

    print("\nStep 2: Enter your credentials")
    print("-"*40)
    client_id = input("Application (client) ID: ").strip()
    tenant_id = input("Directory (tenant) ID: ").strip()

    if client_id and tenant_id:
        config = {
            "client_id": client_id,
            "tenant_id": tenant_id
        }
        save_config(config)
        print(f"\nConfig saved to {CONFIG_FILE}")
        print("\nRun: ./email.py send --to someone@example.com --template atom-proposal")
    else:
        print("\nSetup cancelled. Run ./email.py setup again when ready.")


def main():
    ensure_dirs()  # Create directories on first run
    parser = argparse.ArgumentParser(
        description="CANONIC EMAIL - Microsoft Graph Native",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./email.py setup                                    # First-time setup
  ./email.py send --to avinash@atom.ai --template atom-proposal
  ./email.py templates                                # List templates
  ./email.py log                                      # View sent emails
        """
    )
    subparsers = parser.add_subparsers(dest="command")

    # send command
    send_parser = subparsers.add_parser("send", help="Send an email")
    send_parser.add_argument("--to", required=True, help="Recipient email")
    send_parser.add_argument("--template", help="Template name")
    send_parser.add_argument("--subject", help="Email subject")
    send_parser.add_argument("--body", help="Email body")

    # other commands
    subparsers.add_parser("templates", help="List available templates")
    subparsers.add_parser("log", help="View sent email log")
    subparsers.add_parser("setup", help="Configure Azure AD credentials")
    subparsers.add_parser("logout", help="Clear saved authentication")

    args = parser.parse_args()

    if args.command == "setup":
        setup()
        return

    if args.command == "logout":
        if TOKEN_CACHE.exists():
            TOKEN_CACHE.unlink()
            print("Logged out. Token cache cleared.")
        return

    if args.command == "templates":
        list_templates()
        return

    if args.command == "log":
        view_log()
        return

    if args.command == "send":
        config = load_config()
        if not config:
            print("ERROR: Run ./email.py setup first")
            return

        subject = args.subject
        body = args.body

        if args.template:
            t_subject, t_body = load_template(args.template)
            if t_subject is None:
                return
            subject = subject or t_subject
            body = body or t_body

        if not subject or not body:
            print("ERROR: Provide --template or both --subject and --body")
            return

        send_email(args.to, subject, body, config)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
