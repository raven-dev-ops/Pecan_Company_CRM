# Security Decision: Azure Authentication Approach

Issue link: #10

## Decision for MVP
Use SQL authentication with least-privilege app credential.

## Rationale
- Keeps desktop deployment simple for first production release.
- Avoids Entra dependency and token lifecycle complexity during MVP.

## Hardening path (post-MVP)
- Evaluate Entra ID authentication for central credential governance.
- Tighten network model (private networking/API layer as needed).

## Non-negotiable controls for MVP
- Dedicated app login (not admin credentials).
- Least privileges only on application tables/stored procedures.
- Credential storage protected on Windows host.
- No credentials committed to source control.