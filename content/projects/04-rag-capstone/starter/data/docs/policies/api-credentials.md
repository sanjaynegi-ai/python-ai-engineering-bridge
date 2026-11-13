# Policy: API Credentials and Secrets

This policy applies to API keys, passwords, tokens and certificates used by Orbital Logistics systems.

## Rules

- Store secrets in the secret manager. Never store them in source code, in configuration files in repositories, or in tickets, chat messages or documents.
- Rotate API credentials every 90 days, and immediately when someone who had access leaves the team.
- Give each service its own credential, with the narrowest permissions it needs. Shared credentials are not allowed.
- Never log secrets, and never include them in error messages.

## If a secret leaks

Treat a leaked secret as at least a P2 incident. Revoke it first, then create a replacement, then investigate how it leaked. Removing a secret from a repository does not remove it from the history, so revoking it is the only reliable fix. Report the leak to the security team within one hour.
