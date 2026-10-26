# CreatorFlow

CreatorFlow is an open-source, policy-aware YouTube channel operations workspace. It connects to a creator's own YouTube account, summarizes performance, organizes original video ideas, and turns analytics into practical experiments for improving audience retention and discovery.

It does **not** promise or manufacture subscribers, views, watch time, or revenue. It has no bots, engagement exchanges, view buying, comment spam, scraped content pipeline, or unattended publishing. Growth suggestions are hypotheses; creators decide what to make and publish.

## What is included

- Google OAuth sign-in and read-only YouTube channel/Analytics integration.
- A dashboard for channel performance and content planning.
- A local SQLite editorial calendar with idea, draft, review, and published states.
- An AI Content Studio that creates a full video production pack: original script, scene-by-scene storyboard, narration, honest title options, thumbnail direction, description, chapters, and a Shorts cut-down. Packs can be downloaded as Markdown.
- An opt-in Autopilot that selects distinct topics from your channel profile, creates and renders videos, and uploads them on your chosen cadence after you grant specific upload consent and choose visibility/audience settings.
- Experiment recommendations based on available metrics (for example, compare retention and click-through rate before changing a thumbnail or opening).
- A policy checklist that flags risky growth tactics and repetitive/low-value formats for human review.
- Docker and local development setup.

## Quick start

Requirements: Python 3.11+, FFmpeg and ffprobe, a Google Cloud project with YouTube Data API v3 and YouTube Analytics API enabled, and an OpenAI-compatible provider with chat completions and speech endpoints for script and voice generation. The speech provider must support `/audio/speech` and the selected model/voice. The included Docker image installs FFmpeg and fonts.

1. Create OAuth 2.0 credentials of type **Web application**. Add `http://localhost:8000/auth/callback` as an authorized redirect URI.
2. Copy `.env.example` to `.env` and provide the OAuth client ID and secret, a long random `SESSION_SECRET`, plus the AI provider settings described below.
3. Run:

   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\Activate.ps1
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

4. Set `AI_API_BASE_URL`, `AI_API_KEY`, `AI_MODEL`, and `AI_TTS_MODEL` in `.env` to enable script and voice generation. The endpoint should expose compatible `/chat/completions` and `/audio/speech` routes; set `AI_TTS_VOICE` if your provider uses a different voice name.
5. Open <http://localhost:8000>, connect YouTube, use **Create content** to generate a production pack, then select **Render narrated MP4**. For scheduled no-touch operation, go to **Autopilot**, authorize upload access, enter your channel profile, set cadence/visibility/audience, check the explicit consent boxes, and enable it.

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
| `AI_API_BASE_URL` | Base URL of an OpenAI-compatible chat and speech provider |
| `AI_API_KEY` | Provider key; kept server-side and never exposed to the browser |
| `AI_MODEL` | Model name accepted by the configured provider |
| `AI_TTS_MODEL` | Speech generation model accepted by the configured provider |
| `AI_TTS_VOICE` | Speech voice name; defaults to `alloy` |
| `VIDEO_OUTPUT_DIR` | Local directory for generated MP4 files |
| `FFMPEG_BINARY` / `FFPROBE_BINARY` | Executable names or paths for FFmpeg tools |

Autopilot runs as an in-process background scheduler and expects one application worker to stay running with persistent storage. It creates at most one video per configured interval. It requests the YouTube upload OAuth scope separately from read-only analytics scopes. Each upload includes the synthetic-media disclosure flag. You can stop future runs in the dashboard or disconnect the Google account. Uploading publicly is an explicit setting; no per-video review happens while Autopilot is enabled.

Never commit `.env`, OAuth credentials, AI provider keys, access tokens, or creator data. Content prompts are sent to the AI provider configured by the operator; check that provider's privacy and retention terms. Production deployments must use HTTPS, a managed secret store, a persistent encrypted database volume, and a reviewed privacy policy.

## Privacy and permissions

The app requests read-only OAuth permissions for analytics. It requests YouTube upload access only when you choose to authorize scheduled publishing. Tokens and generated MP4 files are stored locally for this MVP. For a public multi-user deployment, replace this storage with encrypted per-user secrets, implement account deletion and retention controls, publish the included privacy notice/terms for your deployment, and complete Google's OAuth verification requirements. Do not deploy this demo as a public service without that work.

## Rendered videos

The renderer creates an MP4 with generated narration and original visual cards based on the script. It does not fetch stock footage or clone a creator's voice. Replace or supplement the cards with original or licensed visuals where the story benefits from footage. For Docker, persist the database and renders with `docker run --rm -p 8000:8000 --env-file .env -v creatorflow-data:/data creatorflow`.

## Policy-aware operating rules

- Growth must come from useful, original videos and authentic viewer interest.
- Never buy, exchange, automate, or incentivize views, likes, comments, subscribers, or watch time.
- Do not mass-produce near-identical videos or reuse other creators' work with only superficial changes.
- Disclose altered or synthetic media when YouTube requires it; respect copyright, privacy, and community guidelines.
- Keep a human in the loop for scripts, thumbnails, metadata, sponsorship claims, and every upload.
- Rendered videos use an AI voiceover and original designed visual cards. They are draft assets, not verified facts or a substitute for original footage. Verify claims and sources, personalize the creator's perspective, replace cards where footage would add value, and review synthetic-media disclosure requirements before publishing.
- No tool can guarantee YouTube policy compliance, monetization approval, audience growth, or revenue.

See [POLICY.md](POLICY.md), [SECURITY.md](SECURITY.md), and [docs/roadmap.md](docs/roadmap.md).
You can also read [TERMS.md](TERMS.md) and [PRIVACY.md](PRIVACY.md).

## License

MIT. See [LICENSE](LICENSE).
