# Credential Rotation and Revocation Runbook

Issue link: #48

## Scope
SQL-auth credential lifecycle for desktop app access to Azure SQL.

## Ownership and escalation
- Primary owner: application operator/admin.
- Escalation: engineering owner for database/app failures after rotation.

## Rotation cadence
- Scheduled rotation every 90 days.
- Immediate rotation on suspected compromise or staff offboarding event.

## Planned rotation procedure
1. Create/update SQL credential in Azure SQL with least privilege.
2. Confirm credential can connect with `SELECT 1` from test client.
3. Update app Settings password on production workstation.
4. Click `Test Connection` and confirm success.
5. Execute smoke sale transaction in non-business hours.
6. Confirm Sales History readback and receipt generation/reprint.
7. Revoke old credential after validation completes.

## Emergency revocation procedure
1. Disable/revoke compromised credential immediately.
2. Create emergency replacement credential.
3. Update Settings on all active client machines.
4. Confirm connectivity and checkout path.
5. Record incident timeline and actions taken.

## Logging and redaction policy
- Never log plaintext passwords.
- Avoid sharing full connection strings in tickets.
- Redact secrets from screenshots and support exports.

## Validation checklist after rotation
- [ ] `Test Connection` successful
- [ ] Checkout finalize succeeds
- [ ] Receipt generated
- [ ] Sales History query succeeds
- [ ] No credential-related errors in logs