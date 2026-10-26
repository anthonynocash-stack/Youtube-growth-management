# CreatorFlow privacy notice

CreatorFlow is designed for a trusted, single-operator deployment. Before hosting it for other people, publish a privacy policy for your service, explain any changes, and complete the required Google/YouTube verification and security work.

CreatorFlow uses [YouTube API Services](https://developers.google.com/youtube/terms/api-services-terms-of-service). Google processes authentication and API requests under the [Google Privacy Policy](https://policies.google.com/privacy).

## Data used

- Google OAuth tokens are stored in the local SQLite database so the app can access the connected channel. Read-only scopes are requested for analytics. YouTube upload scope is requested separately and only when you choose to enable publishing.
- Channel analytics, video topics, generated scripts, content packs, Autopilot settings, and YouTube upload IDs are stored locally in SQLite. Rendered MP4 files are stored in `VIDEO_OUTPUT_DIR`.
- Topics and creative direction submitted to Content Studio or Autopilot are sent to the operator-configured AI provider for text generation. Narration is sent to that provider's speech endpoint. Review its retention and privacy terms.
- Google and YouTube receive OAuth/API requests, video files, titles, descriptions, tags, audience settings, privacy settings, and the synthetic-media disclosure when you upload through Autopilot.

## Control and deletion

Disconnecting removes the locally stored OAuth token and stops Autopilot. To erase all local CreatorFlow data, stop the service, delete the configured SQLite database and the `VIDEO_OUTPUT_DIR`, then revoke the app's access in [Google Account permissions](https://security.google.com/settings/security/permissions). This does not delete videos already uploaded to YouTube; manage those in YouTube Studio.

Do not expose the database or rendered-video folder publicly. Keep OAuth and AI provider secrets out of the repository and use encrypted storage and access controls for hosted deployments.
