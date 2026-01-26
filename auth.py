#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/iDrDex/Library/Python/3.9/lib/python/site-packages')
import json, msal, requests, webbrowser
from pathlib import Path

DIR = Path(__file__).parent
config = json.load(open(DIR / "config.json"))
cache = msal.SerializableTokenCache()

app = msal.PublicClientApplication(config["client_id"],
    authority=f"https://login.microsoftonline.com/{config['tenant_id']}", token_cache=cache)

print("\n" + "="*50)
print("CANONIC EMAIL AUTHENTICATION")
print("="*50)

flow = app.initiate_device_flow(scopes=["Mail.Send", "Mail.ReadWrite", "User.Read"])
print(f"\n1. Go to: {flow['verification_uri']}")
print(f"2. Enter code: {flow['user_code']}")
print("\nOpening browser...")
webbrowser.open(flow['verification_uri'])
print("\nWaiting for you to authenticate...\n")

result = app.acquire_token_by_device_flow(flow)

if "access_token" in result:
    (DIR / ".token_cache.json").write_text(cache.serialize())
    print("SUCCESS! Token saved.\n")
    
    r = requests.get("https://graph.microsoft.com/v1.0/me/messages",
        headers={"Authorization": f"Bearer {result['access_token']}"},
        params={"$top": 10, "$orderby": "receivedDateTime desc", "$select": "subject,from,receivedDateTime,isRead"})
    
    if r.ok:
        print("="*70)
        print("INBOX")
        print("="*70)
        for m in r.json().get("value", []):
            frm = m.get("from", {}).get("emailAddress", {}).get("address", "?")[:28]
            subj = m.get("subject", "")[:35]
            dt = m.get("receivedDateTime", "")[:16].replace("T", " ")
            read = "" if m.get("isRead") else "●"
            print(f"{read:2} {dt} | {frm:28} | {subj}")
        print("="*70)
else:
    print(f"FAILED: {result.get('error_description', result)}")
