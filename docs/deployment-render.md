# Always-on cloud deployment (Render)

This deployment keeps CreatorFlow running when the creator's computer is off. It uses the repository's Dockerfile, one web instance, and a persistent disk mounted at `/data`. The in-process APScheduler therefore runs continuously with the app process and its SQLite database and rendered MP4 files survive normal deploys/restarts.

## Deploy

1. Push this branch and open the repository in Render.
2. Choose **New > Blueprint** and select this repository and the `creatorflow/safe-approval-workflow` branch.
3. Review the `render.yaml` plan before creating the service. The blueprint requests a paid Starter web service and a 10 GB persistent disk; confirm the current price and region in Render before approving.
4. In the service's Environment settings, provide:
   - `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from a Google OAuth 2.0 **Web application** client.
   - `GOOGLE_REDIRECT_URI` set to the exact HTTPS callback URL for the deployed service: `https://<your-render-service-host>/auth/callback`.
   - `AI_API_BASE_URL`, `AI_API_KEY`, `AI_MODEL`, and `AI_TTS_MODEL` for an OpenAI-compatible provider that supports both chat completions and speech generation.
   - Optionally set `AI_TTS_VOICE`.
5. In Google Cloud Console, enable YouTube Data API v3 and YouTube Analytics API. Add the exact deployed callback URL above to the OAuth client's **Authorized redirect URIs**, then save.
6. Redeploy after setting the environment variables. Open the HTTPS service URL, accept the app terms, connect the YouTube account, then separately authorize the YouTube upload scope.
7. Configure Autopilot with the channel niche, audience, original angle, format, runtime, cadence, **Public** visibility, and the correct Made for Kids setting. Review the terms and explicit unattended-upload consent, then enable Autopilot.

## Important operating limits

- Keep exactly one running application instance. The current scheduler and SQLite design are single-instance; do not scale horizontally or add extra workers.
- Do not remove the persistent disk. It contains the database, OAuth token data, and rendered videos.
- The service must remain running and the disk must remain attached. A local PC shutdown will not stop cloud processing.
- The service plan and persistent disk are paid infrastructure; check Render's current pricing before deployment. This blueprint does not create a Render account, enter secrets, authorize Google, or turn Autopilot on.
- Keep all API keys and OAuth secrets in Render's encrypted environment settings, never in Git.
- Public uploads can go live without per-video approval once Autopilot is enabled. The channel owner remains responsible for topic quality, factual accuracy, rights, audience designation, disclosures, and ongoing monitoring. Disable Autopilot in the dashboard to stop future scheduled uploads.
- A cloud host does not guarantee that every generation or upload succeeds. CreatorFlow records an error status and schedules a retry after failures.
