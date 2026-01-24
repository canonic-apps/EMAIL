# EMAIL

Governed email app for CANONIC. Microsoft Graph native.

## Status

**Building** — Azure AD app registration required

## Setup

### 1. Azure AD App Registration

```bash
# Go to Azure Portal
open "https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade"
```

Register new app:
- Name: `CANONIC-EMAIL`
- Supported account types: Single tenant (or multi if needed)
- Redirect URI: `http://localhost:3000/callback` (for dev)

### 2. API Permissions

Add these Graph permissions:
- `Mail.Send` (Delegated or Application)
- `Mail.ReadWrite` (if storing drafts)
- `User.Read` (for user info)

### 3. Configure Credentials

After registration, save to `.env`:
```
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

### 4. Install Dependencies

```bash
pip install msal requests
```

## Usage

```bash
# Send email
./email.py send --to "avinash@atomadvantage.ai" --template "atom-proposal"

# List templates
./email.py templates

# View sent log
./email.py log
```

## Templates

Stored in `templates/`:
- `atom-proposal.md` — ATOM partnership options
- (add more as needed)

## Governance

All emails logged to `sent/` with:
- Timestamp
- Recipient
- Subject
- Template used
- Message ID from Graph API

---
