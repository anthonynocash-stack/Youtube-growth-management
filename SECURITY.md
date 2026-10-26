# Security policy

## Reporting

Please do not report security issues in public. Use GitHub's private vulnerability reporting for this repository, or contact the maintainers privately.

## Deployment notes

- Use HTTPS and a high-entropy `SESSION_SECRET` in production.
- Restrict OAuth redirect URIs to exact HTTPS origins.
- Do not expose the SQLite database, `.env`, logs, or OAuth tokens publicly.
- The MVP stores refresh tokens locally and is intended for a trusted single-operator deployment. Add encryption at rest, access controls, retention limits, account deletion, and security review before multi-user hosting.
- Read-only YouTube scopes are used for analytics. The upload scope is requested separately. Autopilot stores its explicit consent and publish settings in SQLite and can publish without per-video approval while enabled; protect the database accordingly.
- Rotate and revoke credentials immediately if they are exposed.
- Content topics and creative direction entered in the Content Studio are sent to the configured AI provider. Tell users which provider is configured and review its data retention terms before hosting this for others.
