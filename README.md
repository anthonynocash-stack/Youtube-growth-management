# CreatorFlow

CreatorFlow is an open-source, policy-aware YouTube channel operations workspace. It connects to a creator's own YouTube account, summarizes performance, organizes original video ideas, and turns analytics into practical experiments for improving audience retention and discovery.

It does **not** promise or manufacture subscribers, views, watch time, or revenue. It has no bots, engagement exchanges, view buying, comment spam, scraped content pipeline, or unattended publishing. Growth suggestions are hypotheses; creators decide what to make and publish.

## What is included

- Google OAuth sign-in and read-only YouTube channel/Analytics integration.
- A dashboard for channel performance and content planning.
- A local SQLite editorial calendar with idea, draft, review, and published states.
- An AI Content Studio that creates a full video production pack: original script, scene-by-scene storyboard, narration, honest title options, thumbnail direction, description, chapters, and a Shorts cut-down. Packs can be downloaded as Markdown.
- Experiment recommendations based on available metrics (for example, compare retention and click-through rate before changing a thumbnail or opening).
- A policy checklist that flags risky growth tactics and repetitive/low-value formats for human review.
- Docker and local development setup.

## Quick start

Requirements: Python 3.11+, a Google Cloud project with YouTube Data API v3 and YouTube Analytics API enabled, and an OpenAI-compatible chat completions provider for AI content generation.

1. Create OAuth 2.0 credentials of type **Web application**. Add `http://localhost:8000/auth/callback` as an authorized redirect URI.
2. Copy `.env.example` to `.env` and provide the OAuth client ID and secret plus a long random `SESSION_SECRET`.
3. Run:

   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\Activate.ps1
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

4. Set `AI_API_BASE_URL`, `AI_API_KEY`, and `AI_MODEL` in `.env` to enable the Content Studio. The endpoint should expose a compatible `/chat/completions` route.
5. Open <http://localhost:8000>, connect YouTube, or use **Create content** to generate a production pack.

Without OAuth credentials, the dashboard opens in demo mode. Demo values are labeled and are never sent to YouTube.

## Configuration

| Variable | Purpose |
| --- | --- |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `GOOGLE_REDIRECT_URI` | OAuth callback; default is localhost |
| `SESSION_SECRET` | Secret used to sign browser sessions |
| `DATABASE_PATH` | SQLite database path; default `creatorflow.db` |
| `APP_ENV` | Set to `production` to disable debug behavior |
| `AI_API_BASE_URL` | Base URL of an OpenAI-compatible chat completions provider |
| `AI_API_KEY` | Provider key; kept server-side and never exposed to the browser |
| `AI_MODEL` | Model name accepted by the configured provider |

Never commit `.env`, OAuth credentials, AI provider keys, access tokens, or creator data. Content prompts are sent to the AI provider configured by the operator; check that provider's privacy and retention terms. Production deployments must use HTTPS, a managed secret store, a persistent encrypted database volume, and a reviewed privacy policy.

## Privacy and permissions

The app requests the minimum OAuth permissions required to read channel and analytics data. Tokens are stored locally in SQLite for this MVP. For a public multi-user deployment, replace this storage with encrypted per-user secrets, implement account deletion and retention controls, and complete Google's OAuth verification requirements. Do not deploy this demo as a public service without that work.

## Policy-aware operating rules

- Growth must come from useful, original videos and authentic viewer interest.
- Never buy, exchange, automate, or incentivize views, likes, comments, subscribers, or watch time.
- Do not mass-produce near-identical videos or reuse other creators' work with only superficial changes.
- Disclose altered or synthetic media when YouTube requires it; respect copyright, privacy, and community guidelines.
- Keep a human in the loop for scripts, thumbnails, metadata, sponsorship claims, and every upload.
- AI-generated packs are drafts for production, not verified facts or finished rendered video. Verify claims and sources, personalize the creator's voice and experience, create or license the planned visuals, and review disclosures before publishing.
- No tool can guarantee YouTube policy compliance, monetization approval, audience growth, or revenue.

See [POLICY.md](POLICY.md), [SECURITY.md](SECURITY.md), and [docs/roadmap.md](docs/roadmap.md).

## License

MIT. See [LICENSE](LICENSE).
