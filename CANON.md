# EMAIL — CANON

inherits: /canonic/

<!-- O∩E∩T = Operational + Evidential + Temporal -->
<!-- EMAIL executes (O) send operations -->
<!-- Every email logged (E) with timestamp (T) -->
<!-- The LEDGER is the settlement layer -->

---

## Purpose

Governed email communications via Microsoft Graph API. Every email sent through CANONIC is logged, traceable, and auditable.

---

## Axioms

1. **Microsoft Native**: All email operations MUST use Microsoft Graph API.

2. **Audit Trail**: Every sent email MUST be logged to the LEDGER with timestamp, recipient, subject.

3. **Template Governance**: Email templates MUST be stored in `templates/` and versioned.

4. **No Intermediate**: Direct API calls only. No third-party email services.

5. **Credential Security**: OAuth tokens MUST be stored securely, never in plaintext.

---

## Integration

**Provider:** Microsoft 365 / Azure AD
**API:** Microsoft Graph (https://graph.microsoft.com)
**Scopes:** Mail.Send, Mail.ReadWrite, User.Read

---

## GitHub Marketplace Distribution

### Axiom 6: Git-Native
- App is a GitHub repo with CANON.md at root
- Validators are GitHub Actions
- Installation = `git clone` or GitHub App install
- Updates = `git pull`

### Axiom 7: Seamless Authentication
- GitHub OAuth for marketplace install
- Microsoft Graph via Azure AD (for email)
- Token refresh invisible to user

### Axiom 8: CLI-First Interface
- Command line is the primary interface
- `email send --to x@y.com --template proposal`
- Integrates with any shell, any CI/CD

### Axiom 9: Zero Configuration
- Auto-detect from git config (user.email)
- Works immediately after `git clone`
- Config stored in repo (config.json)

---

## Validators

The EMAIL app packages its own validators that enforce governance at runtime.

### Axiom 10: Self-Contained Governance
- App MUST include all validators needed to enforce its CANON
- Validators run locally — no external VaaS dependency for core operations
- Validators are cryptographically signed and version-locked

### Axiom 11: Black Box Validators
- Validators are OPAQUE to the app and user
- Input → Validator → Output (pass/fail/warn)
- No inspection, no modification, no bypass
- Signed bundles ensure tamper-proof governance
- App trusts validator verdict without seeing internals

### Packaged Validators

| Validator | Enforces | Trigger |
|-----------|----------|---------|
| `email.audit` | Axiom 2 (Audit Trail) | Before send |
| `email.template` | Axiom 3 (Template Governance) | On template load |
| `email.credential` | Axiom 5 (Credential Security) | On token access |
| `email.recipient` | Domain allowlist (optional) | Before send |
| `email.ratelimit` | Abuse prevention | Before send |

### Validator Interface

```typescript
interface EmailValidator {
    id: string;
    version: string;
    validate(context: EmailContext): ValidationResult;
}

interface EmailContext {
    to: string[];
    subject: string;
    body: string;
    template?: string;
    timestamp: Date;
}

type ValidationResult =
    | { status: "pass" }
    | { status: "fail"; reason: string }
    | { status: "warn"; message: string };
```

### Validator Packaging

```
EMAIL/
├── validators/
│   ├── email.audit.js          # Signed validator bundle
│   ├── email.template.js
│   ├── email.credential.js
│   └── manifest.json           # Validator registry
├── email.py                    # CLI implementation
└── CANON.md
```

---

## Architecture (GitHub Marketplace)

```
┌─────────────────────────────────────┐
│         CANONIC EMAIL App           │
├─────────────────────────────────────┤
│  CLI Interface (Python/TypeScript)  │
│  ├── email send                     │
│  ├── email templates                │
│  └── email log                      │
├─────────────────────────────────────┤
│  Validators (GitHub Actions)        │
│  ├── email.audit.yml                │
│  ├── email.template.yml             │
│  └── email.credential.yml           │
├─────────────────────────────────────┤
│  MSAL (Python/JS)                   │
│  └── Azure AD OAuth                 │
├─────────────────────────────────────┤
│  Microsoft Graph API                │
│  └── /me/sendMail                   │
├─────────────────────────────────────┤
│  Git (Audit Log)                    │
│  └── sent/*.json committed          │
└─────────────────────────────────────┘
```

---

## Strategic Position

CANONIC is a **SWIFT alternative** for AI governance messaging.

Like SWIFT standardizes financial messaging between banks, CANONIC standardizes governance messaging between AI systems. Git is the settlement layer.

| SWIFT | CANONIC |
|-------|---------|
| MT messages | Validator calls |
| SWIFT codes | CANON inheritance |
| Settlement finality | Validation finality |
| Bank network | AI network |
| Correspondent banking | Git repos |
| BIC codes | CANON paths |

**CANONIC takes banks.** The same governance rigor that moves trillions through SWIFT now governs AI decisions.

---

## References

- IDF-001: Constitutional Governance (inherited)
- GitHub Marketplace: https://github.com/marketplace
- Microsoft Graph Mail API: https://learn.microsoft.com/en-us/graph/api/user-sendmail
- MSAL Python: https://github.com/AzureAD/microsoft-authentication-library-for-python

---
